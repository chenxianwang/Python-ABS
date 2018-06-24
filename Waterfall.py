# -*- coding: utf-8 -*-
"""
Created on Mon Jun 18 16:48:57 2018

@author: Jonah.Chen
"""

import pandas as pd
import numpy as np
import datetime
from abs_util.util_general import *
from abs_util.util_cf import *
from abs_util.util_sr import *
from dateutil.relativedelta import relativedelta
from Params import *
from Accounts.BondPrinAccount import BondPrinAccount
from Accounts.FeesAccount import FeesAccount
from Accounts.TaxAccount import TaxAccount

logger = get_logger(__name__)

class Waterfall():
    
    def __init__(self,cash_flow,dt_param,fee_rate_param):

        self.prepared_cf = cash_flow
        self.dt_param = dt_param
        self.fee_rate_param = fee_rate_param
        self.tranches_cf = pd.DataFrame()

    def run_Accounts(self,tranches_ABC): # Initalizing BondsCashFlow
        
        prepared_cf = self.prepared_cf
        
        #preissue_FAcc = FeesAccount('pre_issue',fees)
        tax_Acc = TaxAccount('tax',fees)
        trustee_FAcc = FeesAccount('trustee',fees)
        trust_m_FAcc = FeesAccount('trust_management',fees)
        service_FAcc = FeesAccount('service',fees)
        A_IAcc = FeesAccount('A',fees)
        B_IAcc = FeesAccount('B',fees)
        C_IAcc = FeesAccount('C',fees)
    
        A_PAcc = BondPrinAccount('A',tranches_ABC)
        B_PAcc = BondPrinAccount('B',tranches_ABC)
        C_PAcc = BondPrinAccount('C',tranches_ABC)
        EE_Acc = BondPrinAccount('EE',tranches_ABC)

        logger.info('run_term_by_term...')
        #preissue_FAcc
        for date_pay_index,date_pay in enumerate(dates_pay):
            
            #logger.info('dates_pay is {0}'.format(date_pay))
            pay_for_fee = tax_Acc.pay(date_pay,[prepared_cf[prepared_cf['date_recycle_end'] == dates_recycle[date_pay_index]]['amount_recycled_interest'].sum(),0][B_PAcc.iBalance(date_pay) == 0])
            pay_for_fee += trustee_FAcc.pay(date_pay,A_PAcc.iBalance(date_pay) + B_PAcc.iBalance(date_pay))
            pay_for_fee += trust_m_FAcc.pay(date_pay,A_PAcc.iBalance(date_pay) + B_PAcc.iBalance(date_pay))
            pay_for_fee += service_FAcc.pay(date_pay,A_PAcc.iBalance(date_pay) + B_PAcc.iBalance(date_pay))
            
            pay_for_fee += A_IAcc.pay(date_pay,A_PAcc.iBalance(date_pay))
            pay_for_fee += B_IAcc.pay(date_pay,B_PAcc.iBalance(date_pay))
            pay_for_fee += C_IAcc.pay(date_pay,C_PAcc.iBalance(date_pay))
            
            interest_transfer_to_prin = prepared_cf[prepared_cf['date_recycle_end'] == dates_recycle[date_pay_index]]['amount_recycled_interest'].sum() - pay_for_fee
            amount_available_for_prin = prepared_cf[prepared_cf['date_recycle_end'] == dates_recycle[date_pay_index]]['amount_recycled_principal'].sum() + interest_transfer_to_prin
            
            #logger.info('amount_available_for_prin is {0}'.format(amount_available_for_prin))
            amount_available_for_prin = A_PAcc.pay_then_ToNext(date_pay,amount_available_for_prin)
            amount_available_for_prin = B_PAcc.pay_then_ToNext(date_pay,amount_available_for_prin)
            amount_available_for_prin = C_PAcc.pay_then_ToNext(date_pay,amount_available_for_prin)
            
            amount_available_for_prin = EE_Acc.pay_then_ToNext(date_pay,amount_available_for_prin)
            
            #logger.info('Loop Done for {0}'.format(date_pay))
        
        A_Principal_wf = pd.DataFrame(list(A_PAcc.receive.items()), columns=['date_pay', 'amount_pay_A_principal'])
        B_Principal_wf = pd.DataFrame(list(B_PAcc.receive.items()), columns=['date_pay', 'amount_pay_B_principal'])
        C_Principal_wf = pd.DataFrame(list(C_PAcc.receive.items()), columns=['date_pay', 'amount_pay_C_principal'])
        EE_wf = pd.DataFrame(list(EE_Acc.receive.items()), columns=['date_pay', 'amount_pay_EE_principal'])
        
        A_Interest_wf = pd.DataFrame(list(A_IAcc.receive.items()), columns=['date_pay', 'amount_pay_A_interest'])
        B_Interest_wf = pd.DataFrame(list(B_IAcc.receive.items()), columns=['date_pay', 'amount_pay_B_interest'])
        C_Interest_wf = pd.DataFrame(list(C_IAcc.receive.items()), columns=['date_pay', 'amount_pay_C_interest'])
        service_fee_wf = pd.DataFrame(list(service_FAcc.receive.items()), columns=['date_pay', 'fee_service'])
        tax_wf = pd.DataFrame(list(tax_Acc.receive.items()), columns=['date_pay', 'fee_tax'])
        trustee_wf = pd.DataFrame(list(trustee_FAcc.receive.items()), columns=['date_pay', 'fee_trustee'])
        trust_m_wf = pd.DataFrame(list(trust_m_FAcc.receive.items()), columns=['date_pay', 'fee_trust_m'])
        
        A_Balance_wf = pd.DataFrame(list(A_PAcc.balance.items()), columns=['date_pay', 'amount_outstanding_A_principal'])
        B_Balance_wf = pd.DataFrame(list(B_PAcc.balance.items()), columns=['date_pay', 'amount_outstanding_B_principal'])
        C_Balance_wf = pd.DataFrame(list(C_PAcc.balance.items()), columns=['date_pay', 'amount_outstanding_C_principal'])
        EE_Balance_wf = pd.DataFrame(list(EE_Acc.balance.items()), columns=['date_pay', 'amount_outstanding_EE_principal'])
        
        wf = prepared_cf.merge(A_Principal_wf,left_on='date_interest_calc_end',right_on='date_pay',how='outer')\
                        .merge(B_Principal_wf,left_on='date_interest_calc_end',right_on='date_pay',how='outer')\
                        .merge(C_Principal_wf,left_on='date_interest_calc_end',right_on='date_pay',how='outer')\
                        .merge(EE_wf,left_on='date_interest_calc_end',right_on='date_pay',how='outer')\
                        .merge(A_Interest_wf,left_on='date_interest_calc_end',right_on='date_pay',how='outer')\
                        .merge(B_Interest_wf,left_on='date_interest_calc_end',right_on='date_pay',how='outer')\
                        .merge(C_Interest_wf,left_on='date_interest_calc_end',right_on='date_pay',how='outer')\
                        .merge(service_fee_wf,left_on='date_interest_calc_end',right_on='date_pay',how='outer')\
                        .merge(tax_wf,left_on='date_interest_calc_end',right_on='date_pay',how='outer')\
                        .merge(trustee_wf,left_on='date_interest_calc_end',right_on='date_pay',how='outer')\
                        .merge(trust_m_wf,left_on='date_interest_calc_end',right_on='date_pay',how='outer')\
                        .merge(A_Balance_wf,left_on='date_interest_calc_end',right_on='date_pay',how='outer')\
                        .merge(B_Balance_wf,left_on='date_interest_calc_end',right_on='date_pay',how='outer')\
                        .merge(C_Balance_wf,left_on='date_interest_calc_end',right_on='date_pay',how='outer')\
                        .merge(EE_Balance_wf,left_on='date_interest_calc_end',right_on='date_pay',how='outer')
                        
        
        logger.info('total principal payment is {0}'.format(sum(wf[['amount_pay_A_principal','amount_pay_B_principal','amount_pay_C_principal']].sum())))
        
        self.tranches_cf = wf
        wf.to_csv('wf.csv')
    
    def BasicInfo_calculator(self,scenario_id,tranches_ABC):
        tranches_cf = self.tranches_cf
        dt_param = self.dt_param
        
        #logger.info('scenario_id is ',scenario_id)
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
                WA_pay = tranches_cf['amount_pay_' + _tranche_name + '_principal'] * tranches_cf['years_interest_calc_cumulative']
                WA_term.append(sum(WA_pay) / sum(tranches_cf['amount_pay_' + _tranche_name + '_principal']))
                date_maturity_predict.append(tranches_cf.iloc[tranches_cf['amount_outstanding_' + _tranche_name + '_principal'].idxmin()]['date_interest_calc_end'])
                maturity_term.append((date_maturity_predict[_tranche_index] - dt_param['dt_effective']).days / days_in_a_year)
        
        tranche_basic_info = pd.DataFrame({'name_tranche':name_tranche,
                                           'WA_term':WA_term,
                                           'date_maturity_predict':date_maturity_predict,
                                           'maturity_term':maturity_term,
                                           'scenario_id': scenario_id
                                          })
    
        return tranche_basic_info
    
    def CR_calculator(self):
        tranches_cf = self.tranches_cf
        Cover_ratio_Senior = tranches_cf['amount_recycled_total'].sum() / sum(tranches_cf[['amount_pay_A_principal','amount_pay_A_interest']].sum())
        Cover_ratio_Mezz = (tranches_cf['amount_recycled_total'].sum() - sum(tranches_cf[['amount_pay_A_principal','amount_pay_A_interest']].sum()) ) / sum(tranches_cf[['amount_pay_B_principal','amount_pay_B_interest']].sum())
        return Cover_ratio_Senior,Cover_ratio_Mezz
    
    def NPV_calculator(self):
        tranches_cf = self.tranches_cf
        fee_rate_param = self.fee_rate_param
        
        NPV_asset_pool = np.npv(rate_discount / 12,tranches_cf['amount_recycled_total']) / (1 + rate_discount / 12 )
        
        total_pay_to_Originator = tranches_cf['amount_pay_C_principal'] + tranches_cf['amount_pay_C_interest'] + tranches_cf['amount_pay_EE_principal']+ tranches_cf['fee_service']
        NPV_originator = np.npv(rate_discount / 12,total_pay_to_Originator) / (1 + rate_discount / 12 )  #
        
        return NPV_asset_pool,NPV_originator