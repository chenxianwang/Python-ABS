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
from abs_util.util_waterfall import *
from dateutil.relativedelta import relativedelta
import datetime
from ReverseSelection import ReverseSelection
from Statistics import Statistics
from AssetsCashFlow import AssetsCashFlow
from APCF_adjuster import APCF_adjuster
from Accounts.AssetPoolAccount import AssetPoolAccount

low_memory=False

logger = get_logger(__name__)

class Deal():
    
    def __init__(self,name,PoolCutDate,AssetPoolName,date_trust_effective,scenarios):
        
        self.RevolvingDeal = False
        self.RevolvingPool_PurchaseAmount = None
        
        self.name = name
        self.date_pool_cut = PoolCutDate
        self.date_trust_effective = date_trust_effective
        self.scenarios = scenarios
        
        self.list_AssetPoolName = AssetPoolName
        self.dates_recycle_list = []
        
        self.asset_pool = pd.DataFrame()  
        self.apcf_original = pd.DataFrame()
        self.apcf_original_structure = pd.DataFrame()
        self.apcf_original_adjusted = {}
        
        self.AP_PAcc_original = {}
        self.AP_PAcc_actual = {}
        self.AP_PAcc_pay = {}
        self.AP_PAcc_buy = {}
        self.AP_PAcc_overdue_1_30_currentTerm = {}
        self.AP_PAcc_overdue_1_30_allTerm = {}
        self.AP_PAcc_loss_currentTerm = {}
        self.AP_PAcc_loss_allTerm = {}

        self.AP_IAcc_original = {}        
        self.AP_IAcc_actual = {}
        self.AP_IAcc_pay = {}
        self.AP_IAcc_buy = {}
        self.AP_IAcc_overdue_1_30_currentTerm = {}
        self.AP_IAcc_overdue_1_30_allTerm = {}
        self.AP_IAcc_loss_currentTerm = {}
        self.AP_IAcc_loss_allTerm = {}
        
        self.waterfall = {}
        self.wf_BasicInfo = {}
        self.wf_CoverRatio = {}
        self.wf_NPVs = {}
        
        self.RnR = 0.0
     
    def get_AssetPool(self):
        #self.asset_pool = self.AP.get_AP()
        logger.info('get_OriginalAssetPool...')
        for Pool_index,Pool_name in enumerate(self.list_AssetPoolName):
            logger.info('Getting part ' + str(Pool_index+1) + '...')
            AssetPoolPath_this = path_project + '/AssetPoolList/' + Pool_name + '.csv'
            try:
                AssetPool_this = pd.read_csv(AssetPoolPath_this,encoding = 'utf-8') 
            except:
                AssetPool_this = pd.read_csv(AssetPoolPath_this,encoding = 'gbk') 
            self.asset_pool = self.asset_pool.append(AssetPool_this,ignore_index=True)

        #self.asset_pool = self.asset_pool[list(Header_Rename.keys())] 
        #self.asset_pool['#合同号'] = '#' + self.asset_pool['#合同号'].astype(str)
        logger.info('Renaming header....')
        self.asset_pool = self.asset_pool.rename(columns = Header_Rename) 
        logger.info('Original Asset Pool Gotten.')
        
        return self.asset_pool
        
    def add_Columns(self,file_names_left_right):
        logger.info('Adding Columns...')
        for file_name_left_right in file_names_left_right:
            list_NewColumns_Files = file_name_left_right[0]
            left = file_name_left_right[1]
            right = file_name_left_right[2]
            
            AssetPool = pd.DataFrame()
            for Pool_index,Pool_name in enumerate(list_NewColumns_Files):
                logger.info('Getting Adding part ' + str(Pool_index+1) + '...')
                AssetPoolPath_this = path_project + '/AssetPoolList/' + Pool_name + '.csv'
                try:
                    AssetPool_this = pd.read_csv(AssetPoolPath_this,encoding = 'utf-8') 
                except:
                    AssetPool_this = pd.read_csv(AssetPoolPath_this,encoding = 'gbk') 
                AssetPool = AssetPool.append(AssetPool_this,ignore_index=True)
            #AssetPool['#合同号'] = '#' + AssetPool['#合同号'].astype(str)
            #AssetPool = AssetPool.rename(columns = {'信用评分':'信用评分_old'})
            logger.info('outer Merging...')
            self.asset_pool = self.asset_pool.merge(AssetPool,left_on= left,right_on = right,how='left')
        self.asset_pool = self.asset_pool[(~self.asset_pool['职业_信托'].isnull()) & (~self.asset_pool['购买商品_信托'].isnull())]
        logger.info('Columns added....')
        
        return self.asset_pool#[~self.asset_pool['职业_信托'].isnull()]
        
        
    def select_by_ContractNO(self,exclude_or_focus,these_assets):
        
        #self.asset_pool = self.AP.exclude_or_focus_by_ContractNo(exclude_or_focus,these_assets)
        logger.info('Reading Assets_to_' + exclude_or_focus + '....')
        path_assets = path_project + '/AssetPoolList/' + these_assets + '.csv'
        assets_to_exclude_or_focus = pd.read_csv(path_assets,encoding = 'gbk')
        
        logger.info(exclude_or_focus + 'ing ...') 
        if exclude_or_focus == 'exclude':
            try:
                self.asset_pool = self.asset_pool[~self.asset_pool['No_Contract'].isin(assets_to_exclude_or_focus['#合同号'])]
            except(KeyError):
                self.asset_pool = self.asset_pool[~self.asset_pool['No_Contract'].isin(assets_to_exclude_or_focus['No_Contract'])]
        #assets = self.asset_pool[self.asset_pool['ReverseSelection_Flag'].isin(assets_to_exclude_or_focus['ReverseSelection_Flag'])]
        #assets_to_exclude_or_focus['#合同号'] = '#' + assets_to_exclude_or_focus['合同号'].astype(str)       
        else:
            try:self.asset_pool = self.asset_pool[self.asset_pool['No_Contract'].isin(assets_to_exclude_or_focus['#合同号'])]
            except(KeyError):self.asset_pool = self.asset_pool[self.asset_pool['No_Contract'].isin(assets_to_exclude_or_focus['No_Contract'])]
            #assets = self.asset_pool.rename(columns = DWH_header_REVERSE_rename) 
            #assets.to_csv('1stRevolvingPool.csv')
        logger.info(exclude_or_focus +'assets in ' + these_assets +'  is done.')
        
        return self.asset_pool
        
        
    def run_ReverseSelection(self,iTarget,group_d):

        self.asset_pool['ReverseSelection_Flag'] = ''
        for d in group_d:
            self.asset_pool['ReverseSelection_Flag'] += self.asset_pool[d].astype(str)
            
        RS = ReverseSelection(self.asset_pool[['No_Contract','Amount_Outstanding_yuan'#,'Province','Usage'
                                               ] + group_d],
                              iTarget,group_d
                              )
        RS.cal_OriginalStat()
        RS_results = RS.iLP_Solver_all()
        
        RS_results['ReverseSelection_Flag'] = ''
        for d in group_d:
            RS_results['ReverseSelection_Flag'] += RS_results[d].astype(str)    
        
        RS_results.to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/AssetsSelected_Final.csv',index=False)
        
        logger.info('Selected Outstanding Principal is {0}'.format(sum(RS_results['Amount_Outstanding'])))
        logger.info('Selected Contracts Count is {0}'.format(len(RS_results.index)))
        
        for target_d in iTarget.keys():
             Condition_Satisfied_or_Not(RS_results,target_d,iTarget)
        
        self.asset_pool = self.asset_pool[self.asset_pool['ReverseSelection_Flag'].isin(RS_results['ReverseSelection_Flag'])]

    def run_Stat(self):
        
        S = Statistics(self.asset_pool)
        S.general_statistics_1()
        S.loop_Ds_ret_province_profession(Distribution_By_Category,Distribution_By_Bins)
        S.cal_income2debt_by_ID()
        
    def get_rearranged_APCF_structure(self):
        
        APCF = AssetsCashFlow(self.asset_pool[['No_Contract','Interest_Rate','SERVICE_FEE_RATE','Amount_Outstanding_yuan','first_due_date_after_pool_cut','Term_Remain']],
                             self.date_pool_cut
                             )
        return APCF.rearrange_APCF_Structure() 
    
    def get_adjust_oAPCF(self):
        
        APCF = AssetsCashFlow(self.asset_pool[['No_Contract','Interest_Rate','SERVICE_FEE_RATE','Amount_Outstanding_yuan','first_due_date_after_pool_cut','Term_Remain']],
                             self.date_pool_cut
                             )

        self.apcf_original,self.apcf_structure,self.dates_recycle_list,df_ppmt,df_ipmt = APCF.calc_APCF(0)  #BackMonth  
        save_to_excel(self.apcf_original,'cf_o',wb_name)
        #save_to_excel(self.apcf_original_structure,'cf_o_structure',wb_name)
        
        logger.info('get_adjust_oAPCF_simulation...')
        for scenario_id in self.scenarios.keys():
            logger.info('get_adjust_oAPCF_simulation for scenario_id {0}...'.format(scenario_id))
            APCFa = APCF_adjuster(self.apcf_structure,self.scenarios,scenario_id,df_ppmt,df_ipmt)
            #self.apcf_original_adjusted[scenario_id] = deepcopy(APCFa.adjust_APCF('O',self.dates_recycle_list))
            self.apcf_original_adjusted[scenario_id] = deepcopy(APCFa.adjust_APCF('O',self.dates_recycle_list))
            #save_to_excel(self.apcf_original_adjusted[scenario_id],scenario_id+'_o_a',wb_name)
        

    def init_oAP_Acc(self):
        logger.info('init_oAP_Acc...')
        for scenario_id in self.scenarios.keys():
             #logger.info('scenario_id is {0}'.format(scenario_id))
             #AP_Acc = AssetPoolAccount(self.apcf_adjusted[scenario_id] if self.RevolvingDeal == True else self.apcf_original_adjusted[scenario_id])
             AP_Acc = AssetPoolAccount(self.apcf_original,self.apcf_original_adjusted[scenario_id])
             
             principal_available = AP_Acc.available_principal()
             self.AP_PAcc_original[scenario_id] = principal_available[0]
             self.AP_PAcc_actual[scenario_id] = principal_available[1]
             self.AP_PAcc_pay[scenario_id] = principal_available[2]
             self.AP_PAcc_buy[scenario_id] = principal_available[3]
             self.AP_PAcc_overdue_1_30_currentTerm[scenario_id] = principal_available[4]
             self.AP_PAcc_overdue_1_30_allTerm[scenario_id] = principal_available[5]
             self.AP_PAcc_loss_currentTerm[scenario_id] = principal_available[6]
             self.AP_PAcc_loss_allTerm[scenario_id] = principal_available[7]

             
             interest_available = AP_Acc.available_interest()
             self.AP_IAcc_original[scenario_id] = interest_available[0]
             self.AP_IAcc_actual[scenario_id] = interest_available[1]
             self.AP_IAcc_pay[scenario_id] = interest_available[2]
             self.AP_IAcc_buy[scenario_id] = interest_available[3]
             self.AP_IAcc_overdue_1_30_currentTerm[scenario_id] = interest_available[4]
             self.AP_IAcc_overdue_1_30_allTerm[scenario_id] = interest_available[5]
             self.AP_IAcc_loss_currentTerm[scenario_id] = interest_available[6]
             self.AP_IAcc_loss_allTerm[scenario_id] = interest_available[7]
             
             if self.RevolvingDeal is not True:
                self.CDR[scenario_id] =  [sum([self.AP_PAcc_overdue_1_30_allTerm[scenario_id][k] for k in dates_recycle]) / sum([self.AP_PAcc_original[scenario_id][k] for k in dates_recycle])]       
        if self.RevolvingDeal is not True:
            save_to_excel(pd.DataFrame.from_dict(self.CDR),'RnR&CDR',wb_name)
            
    def run_WaterFall(self):
         
         for scenario_id in self.scenarios.keys():
             logger.info('scenario_id is {0}'.format(scenario_id))
             #WF = Waterfall(self.AP_PAcc_pay[scenario_id],self.AP_PAcc_buy[scenario_id],self.AP_IAcc_pay[scenario_id],dt_param)
             waterfall = run_Accounts(self.AP_PAcc_original[scenario_id],self.AP_PAcc_actual[scenario_id],self.AP_PAcc_pay[scenario_id],self.AP_PAcc_buy[scenario_id],
                                      self.AP_IAcc_original[scenario_id],self.AP_IAcc_actual[scenario_id],self.AP_IAcc_pay[scenario_id],self.AP_IAcc_buy[scenario_id],
                                      scenario_id,Bonds,self.RevolvingDeal,self.RevolvingPool_PurchaseAmount)
             
             self.waterfall[scenario_id] = deepcopy(waterfall)
             self.wf_BasicInfo[scenario_id] = deepcopy(BasicInfo_calculator(waterfall,dt_param,Bonds))
             self.wf_CoverRatio[scenario_id] = deepcopy(CR_calculator(waterfall,self.AP_PAcc_pay[scenario_id],self.AP_IAcc_pay[scenario_id]))
             self.wf_NPVs[scenario_id] = deepcopy(NPV_calculator(waterfall,self.AP_PAcc_pay[scenario_id],self.AP_IAcc_pay[scenario_id]))
         
    def cal_RnR(self):
         
        scenarios_weight = [scenarios[scenario_id]['scenario_weight'] for scenario_id in self.scenarios.keys()]
        
        NPV_originator = [self.wf_NPVs[scenario_id]['NPV_originator'][0] for scenario_id in self.scenarios.keys()]
        NPV_asset_pool = [self.wf_NPVs[scenario_id]['NPV_asset_pool'][0] for scenario_id in self.scenarios.keys()]
        
        SD_NPV_originator = SD_with_weight(NPV_originator,scenarios_weight)
        SD_NPV_asset_pool = SD_with_weight(NPV_asset_pool,scenarios_weight)
        
        RnR = SD_NPV_originator / SD_NPV_asset_pool
        
        return RnR