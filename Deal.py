# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 21:21:44 2018

@author: Jonah.Chen
"""

import sys
import os
from copy import deepcopy
from constant import *
from Params import *
import pandas as pd
import numpy as np
from abs_util.util_general import *
from abs_util.util_cf import *
from abs_util.util_sr import *
from dateutil.relativedelta import relativedelta
import datetime
from ReverseSelection import ReverseSelection
from Statistics import Statistics
from AssetsCashFlow import AssetsCashFlow
from APCF_adjuster import APCF_adjuster
from Accounts.AssetPoolAccount import AssetPoolAccount
from Waterfall import Waterfall

low_memory=False

logger = get_logger(__name__)

class Deal():
    
    def __init__(self,name,AP,date_trust_effective,recycle_adjust_factor,scenarios):
        
        self.name = name
        self.date_pool_cut = AP.date_pool_cut
        self.date_trust_effective = date_trust_effective
        self.scenarios = scenarios
        
        self.AP = AP
        self.asset_pool = pd.DataFrame()
        self.apcf_original = pd.DataFrame()
        self.apcf_structure = pd.DataFrame()
        
        self.recycle_adjust_factor = recycle_adjust_factor
        
        self.apcf_original_adjusted = {}
        
        self.waterfall = {}
        self.wf_BasicInfo = {}
        self.wf_CoverRatio = {}
        self.wf_NPVs = {}
        
        self.RnR = 0
     
    def get_AssetPool(self):
        self.asset_pool = self.AP.get_AP()
        self.asset_pool['Credit_Score'] = self.asset_pool['Credit_Score_15'].round(3)
        
    def add_Columns(self):
        self.asset_pool = self.AP.add_Columns_From()
        
    def run_ReverseSelection(self,iTarget,group_d):

        self.asset_pool['ReverseSelection_Flag'] = self.asset_pool[group_d[0]].astype(str) + self.asset_pool[group_d[1]].astype(str) + self.asset_pool[group_d[2]].astype(str) #+ self.asset_pool[group_d[3]].astype(str)
#         
        RS = ReverseSelection(self.asset_pool[['No_Contract','Interest_Rate','Credit_Score','Amount_Outstanding_yuan','LoanRemainTerm','Province','Usage',#'LoanTerm',
                                            ]],
                              iTarget,group_d
                              )
        RS.cal_OriginalStat()
        RS_results = RS.iLP_Solver_all()
        
        RS_results['ReverseSelection_Flag'] = RS_results[group_d[0]].astype(str) + RS_results[group_d[1]].astype(str) + RS_results[group_d[2]].astype(str) #+ self.asset_pool[group_d[3]].astype(str)               
        
        RS_results.to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/AssetsSelected_Final.csv',index=False)
        
        logger.info('Selected Outstanding Principal is {0}'.format(sum(RS_results['Amount_Outstanding'])))
        logger.info('Selected Contracts Count is {0}'.format(len(RS_results.index)))
        
        for target_d in iTarget.keys():
             Condition_Satisfied_or_Not(RS_results,target_d,iTarget)
        
        self.asset_pool = self.asset_pool[self.asset_pool['ReverseSelection_Flag'].isin(RS_results['ReverseSelection_Flag'])]

    def run_Stat(self):
        
        S = Statistics(self.name,self.asset_pool)
        S.general_statistics_1()
        S.loop_Ds_ret_province_profession(Distribution_By_Category,Distribution_By_Bins)
        S.cal_income2debt_by_ID()
    
    def get_APCF(self):
        
        APCF = AssetsCashFlow(self.asset_pool[['No_Contract','Interest_Rate','SERVICE_FEE_RATE','Amount_Outstanding_yuan','first_due_date_after_pool_cut','Term_Remain',]],
                             self.date_pool_cut
                             )

        self.apcf_original,self.apcf_structure = APCF.calc_APCF(0)  #BackMonth  

    def get_rearranged_APCF_structure(self):
        
        APCF = AssetsCashFlow(self.asset_pool[['No_Contract','Interest_Rate','SERVICE_FEE_RATE','Amount_Outstanding_yuan','first_due_date_after_pool_cut','Term_Remain',]],
                             self.date_pool_cut
                             )
        return APCF.rearrange_APCF_Structure()
        
    def adjust_APCF(self):
         logger.info('adjust_APCF...')
         for scenario_id in self.scenarios.keys():
            APCFa = APCF_adjuster(self.apcf_original,self.recycle_adjust_factor,self.scenarios,scenario_id)
            self.apcf_original_adjusted[scenario_id] = deepcopy(APCFa.adjust_APCF())
            
    def run_WaterFall(self):
         
         for scenario_id in self.scenarios.keys():
             logger.info('scenario_id is {0}'.format(scenario_id))
             AP_Acc = AssetPoolAccount(self.apcf_adjusted[scenario_id])  # change to apcf_original_adjusted
             WF = Waterfall(AP_Acc.recylce_principal,AP_Acc.recylce_interest,dt_param)
             WF.run_Accounts(Bonds)
             self.waterfall[scenario_id] = deepcopy(WF.waterfall)
             self.wf_BasicInfo[scenario_id] = deepcopy(WF.BasicInfo_calculator(Bonds))
             self.wf_CoverRatio[scenario_id] = deepcopy(WF.CR_calculator())
             self.wf_NPVs[scenario_id] = deepcopy(WF.NPV_calculator())
         
    def cal_RnR(self):
         
        scenarios_weight = [scenarios[scenario_id]['scenario_weight'] for scenario_id in self.scenarios.keys()]
        
        NPV_originator = [self.wf_NPVs[scenario_id]['NPV_originator'][0] for scenario_id in self.scenarios.keys()]
        NPV_asset_pool = [self.wf_NPVs[scenario_id]['NPV_asset_pool'][0] for scenario_id in self.scenarios.keys()]
        
        SD_NPV_originator = SD_with_weight(NPV_originator,scenarios_weight)
        SD_NPV_asset_pool = SD_with_weight(NPV_asset_pool,scenarios_weight)
        
        RnR = SD_NPV_originator / SD_NPV_asset_pool
        
        return RnR