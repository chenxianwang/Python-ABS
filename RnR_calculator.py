# -*- coding: utf-8 -*-
"""
Created on Mon Jun 18 18:06:09 2018

@author: Jonah.Chen
"""

import pandas as pd
import numpy as np
#from asset_pool_cf_adjust import adjust_cashflow
from abs_util.util_general import *
from abs_util.util_cf import *
from abs_util.util_sr import *
from Waterfall import *
from ACF_adjuster import *
from Accounts.AssetPoolAccount import AssetPoolAccount

logger = get_logger(__name__)

class RnR_calculator():
    
    def __init__(self,cf_original,dt_param,fee_rate_param,scenario,tranches_ABC):
        
        self.cf_original = cf_original
        self.dt_param = dt_param
        self.fee_rate_param = fee_rate_param
        self.scenario = scenario
        self.tranches_ABC = tranches_ABC

    def calculator(self):
    
        cf_original = self.cf_original
        dt_param = self.dt_param
        fee_rate_param = self.fee_rate_param
        scenario = self.scenario
        tranches_ABC = self.tranches_ABC
        
        logger.info('loop_scenarios...')
        Cover_ratio_Senior = []
        Cover_ratio_Mezz = []
        NPV_asset_pool = []
        NPV_originator = []
        basic_info = []
        scenario_id_list = []
       
        for scenario_id in scenario.keys():
            logger.info("Looping {0} ....".format(scenario_id))
            #cf_adjusted = adjust_cashflow(cf_original,data_c,scenario_id,param,scenario,redemption_flag)
            ACFa = ACF_adjuster(ProjectName,cf_original,supplement_assets_params,scenario,scenario_id,dt_param,fee_rate_param)
            cf_adjusted = ACFa.adjust_ACF()

            AP_Acc = AssetPoolAccount(cf_adjusted)
            
            WF = Waterfall(AP_Acc.recylce_principal,AP_Acc.recylce_interest,dt_param,fee_rate_param)
            
            WF.run_Accounts(tranches_ABC)
            
            BasicInfo = WF.BasicInfo_calculator(scenario_id,tranches_ABC)
            basic_info.append(BasicInfo)
            
            tranches_calc_CR = WF.CR_calculator()
            Cover_ratio_Senior.append(tranches_calc_CR[0])
            Cover_ratio_Mezz.append(tranches_calc_CR[1])
            
            NPVs = WF.NPV_calculator()
            NPV_asset_pool.append(NPVs[0])
            NPV_originator.append(NPVs[1])
            
            scenario_id_list.append(scenario_id)
                
        save_to_excel(basic_info,'RnR_basic_info',wb_name)
        
        out_scenarios = pd.DataFrame({'scenarios_id': scenario_id_list,
                                      'Cover_ratio_Senior':Cover_ratio_Senior,
                                      'Cover_ratio_Mezz':Cover_ratio_Mezz,
                                      'NPV_asset_poolo': NPV_asset_pool,
                                      'NPV_originator': NPV_originator,
    #                                  'scenarios_weight': scenarios_weight
                                     })
        
        save_to_excel(out_scenarios,'RnR_CR',wb_name)
        
        scenarios_weight = []
        for key in scenario.keys():
            scenarios_weight.append(scenario[key]['scenario_weight'])
        
        SD_NPV_originator = SD_with_weight(NPV_originator,scenarios_weight)
        SD_NPV_asset_pool = SD_with_weight(NPV_asset_pool,scenarios_weight)
        
        RnR = SD_NPV_originator / SD_NPV_asset_pool
        
        return RnR
