# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 12:01:12 2017

@author: Jonah.Chen
"""
import pandas as pd
import numpy as np
from asset_pool_cf_adjust import adjust_cashflow
from util import save_to_excel,save_to_mysql,SD_with_weight,get_logger
from tranches_cf import prepare_tranches_cf,initializing_accounts,run_term_by_term

logger = get_logger(__name__)

def loop_scenarios(cf_original,data_c,param,scenario,tranches_ABC,redemption_flag):

    Cover_ratio_Senior = []
    Cover_ratio_Mezz = []
    NPV_asset_pool = []
    NPV_originator = []
    tranche_basic_info_list = []
    scenario_id_list = []
    
    amount_total_issuance = cf_original['amount_principal'].sum()
    for key in tranches_ABC.keys():
        tranches_ABC[key]['amount'] = amount_total_issuance * tranches_ABC[key]['ptg']
    
    for scenario_id in scenario.keys():
        
        cf_adjusted = adjust_cashflow(cf_original,data_c,scenario_id,param,scenario,redemption_flag)
        
        tranches_calculate_results = tranches_cf_calculate(cf_adjusted,scenario_id,param,tranches_ABC)
        
        tranche_basic_info_list.append(tranches_calculate_results[0])
        Cover_ratio_Senior.append(tranches_calculate_results[1])
        Cover_ratio_Mezz.append(tranches_calculate_results[2])
        NPV_asset_pool.append(tranches_calculate_results[3])
        NPV_originator.append(tranches_calculate_results[4])
        
        scenario_id_list.append(scenario_id)
            
    RnR = RnR_calculator(scenario,NPV_originator,NPV_asset_pool)
    
    logger.info('RnR is: %s' % RnR)
    df_RnR = pd.DataFrame({'RnR':[RnR]})
    
    out_scenarios = pd.DataFrame({'scenarios_id': scenario_id_list,
                                  'Cover_ratio_Senior':Cover_ratio_Senior,
                                  'Cover_ratio_Mezz':Cover_ratio_Mezz,
                                  'NPV_asset_poolo': NPV_asset_pool,
                                  'NPV_originator': NPV_originator,
#                                  'scenarios_weight': scenarios_weight
                                 })
    
    save_to_excel(tranche_basic_info_list,'tranche_basic_info')
    save_to_excel([out_scenarios,df_RnR],'tranches_analysis')
    
def tranches_cf_calculate(cash_flow,scenario_id,param,tranches_ABC):
    
    tranches_cf = prepare_tranches_cf(cash_flow,param)
    tranches_cf = initializing_accounts(tranches_cf,param,tranches_ABC)
    tranches_cf = run_term_by_term(tranches_cf,param,tranches_ABC)
    
    name_tranche = []
    for _tranche_name in tranches_ABC.keys():
        name_tranche.append(_tranche_name)
        
    WA_term = []
    date_maturity_predict = []
    maturity_term = []
    
    for _tranche_index,_tranche_name in enumerate(name_tranche):
        if tranches_ABC[_tranche_name]['ptg'] == 0:
            WA_term.append('-')
            date_maturity_predict.append('-')
            maturity_term.append('-')
        else:
            WA_term.append(sum(tranches_cf['amount_pay_' + _tranche_name + '_principal'] * tranches_cf['years_interest_calc_cumulative']) / sum(tranches_cf['amount_pay_' + _tranche_name + '_principal']))
            date_maturity_predict.append(tranches_cf.iloc[tranches_cf['amount_outstanding_' + _tranche_name + '_principal_end'].idxmin()]['date_interest_calc_end'])
            maturity_term.append((date_maturity_predict[_tranche_index] - param['dt_effective']).days/param['days_in_a_year'])
    
    tranche_basic_info = pd.DataFrame({'name_tranche':name_tranche,
                                       'WA_term':WA_term,
                                       'date_maturity_predict':date_maturity_predict,
                                       'maturity_term':maturity_term,
                                       'scenario_id': scenario_id
                                      })

    Cover_ratio_Senior = tranches_cf['amount_recycled_total'].sum() / tranches_cf['amount_pay_Senior'].sum()
    Cover_ratio_Mezz = (tranches_cf['amount_recycled_total'].sum() - tranches_cf['amount_pay_Senior'].sum() ) / tranches_cf['amount_pay_Mezz'].sum()
    
    NPV_asset_pool = np.npv(param['rate_discount'] / 12,tranches_cf['amount_recycled_total']) / (1 + param['rate_discount'] / 12 )
    NPV_originator = np.npv(param['rate_discount'] / 12,(tranches_cf['amount_pay_Sub'] + tranches_cf['amount_extra_earning'] + tranches_cf['fee_service'])) / (1 + param['rate_discount'] / 12 )
    
    return tranche_basic_info,Cover_ratio_Senior,Cover_ratio_Mezz,NPV_asset_pool,NPV_originator

def RnR_calculator(scenario,NPV_originator,NPV_asset_pool):

    scenarios_weight = []
    for key in scenario.keys():
        scenarios_weight.append(scenario[key]['scenario_weight'])
    
    SD_NPV_originator = SD_with_weight(NPV_originator,scenarios_weight)
    SD_NPV_asset_pool = SD_with_weight(NPV_asset_pool,scenarios_weight)
    
    return SD_NPV_originator / SD_NPV_asset_pool

            