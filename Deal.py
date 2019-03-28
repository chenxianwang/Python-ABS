# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 21:21:44 2018

@author: Jonah.Chen
"""

from copy import deepcopy
import numpy
from constant import wb_name,path_project,Header_Rename,Header_Rename_REVERSE
from Params import all_asset_status,dates_recycle,dt_param,Bonds,scenarios,amount_ReserveAcount
import pandas as pd
import numpy as np
from abs_util.util_general import get_logger,Condition_Satisfied_or_Not,save_to_excel,SD_with_weight
from abs_util.util_cf import *
from abs_util.util_sr import *
from abs_util.util_waterfall import run_Accounts,BasicInfo_calculator,CR_calculator,NPV_calculator
from dateutil.relativedelta import relativedelta
from ReverseSelection import ReverseSelection
from Statistics import Statistics
from AssetsCashFlow import AssetsCashFlow
from APCF_adjuster import APCF_adjuster
from Accounts.AssetPoolAccount import AssetPoolAccount

low_memory=False

logger = get_logger(__name__)

class Deal():
    
    def __init__(self,name,date_pool_cut,date_trust_effective,scenarios):
        
        self.RevolvingDeal = False
        self.RevolvingPool_PurchaseAmount = None
        
        self.name = name
        self.date_pool_cut = date_pool_cut
        self.date_trust_effective = date_trust_effective
        self.scenarios = scenarios
       
        self.dates_recycle_list = {}
        
        self.asset_pool = pd.DataFrame()  
        
        #for each asset status
        self.apcf_original,self.apcf_original_structure = {},{}
        self.df_ppmt,self.df_ipmt = {},{}
        
        self.df_AP_PAcc_actual_O_DeSimu = pd.DataFrame() 
        
        #for each asset status and each scenario
        self.apcf_original_adjusted,self.APCF_adjusted_save = {},{}
        for asset_status in all_asset_status:
            self.apcf_original_adjusted[asset_status],self.APCF_adjusted_save[asset_status] = {},{}
        
        self.CDR_O = {}
        self.amount_default_O = {}
        
        self.waterfall = {}
        self.wf_BasicInfo = {}
        self.wf_CoverRatio = {}
        self.wf_NPVs = {}
        
        self.RnR = 0.0
        self.reserveAccount_used = {}
     
    def get_AssetPool(self,AssetPoolName):
        for Pool_index,Pool_name in enumerate(AssetPoolName):
            logger.info('Getting part ' + Pool_name + '...')
            AssetPoolPath_this = path_project + '/AssetPoolList/' + Pool_name + '.csv'
            try:AssetPool_this = pd.read_csv(AssetPoolPath_this,encoding = 'utf-8') 
            except:AssetPool_this = pd.read_csv(AssetPoolPath_this,encoding = 'gbk') 
            
            if '贷款状态' not in list(AssetPool_this.columns.values): AssetPool_this['贷款状态'] = '正常贷款'
            if 'SERVICE_FEE_RATE' not in list(AssetPool_this.columns.values):AssetPool_this['SERVICE_FEE_RATE'] = 0
            
            logger.info('Renaming header....')   
            AssetPool_this = AssetPool_this.rename(columns = Header_Rename)
            #AssetPool_this = AssetPool_this[list(Header_Rename_REVERSE.keys())] 
            #print(list(AssetPool_this.columns.values))
            
            self.asset_pool = self.asset_pool.append(AssetPool_this,ignore_index=True)
       
        if isinstance(self.asset_pool['No_Contract'][0],numpy.int64) == False:pass
        else: self.asset_pool['No_Contract'] = '#' + self.asset_pool['No_Contract'].astype(str)
            
        logger.info('Asset Pool Gotten.')
        
        
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
                try:AssetPool_this = pd.read_csv(AssetPoolPath_this,encoding = 'utf-8') 
                except: AssetPool_this = pd.read_csv(AssetPoolPath_this,encoding = 'gbk') 
                AssetPool = AssetPool.append(AssetPool_this,ignore_index=True)
                
            try:
                if isinstance(AssetPool['#合同号'][0],numpy.int64) == False:pass
                else: AssetPool['#合同号'] = '#' + AssetPool['#合同号'].astype(str) 
            except(KeyError):pass
            
            #AssetPool = AssetPool.rename(columns = {'信用评分':'信用评分_new'})
            logger.info('Left Merging Columns...')
            self.asset_pool = self.asset_pool.merge(AssetPool,left_on= left,right_on = right,how='left')
        #self.asset_pool = self.asset_pool[(~self.asset_pool['职业_信托'].isnull()) & (~self.asset_pool['购买商品_信托'].isnull())]
        logger.info('Columns added....')
        
        return self.asset_pool#[~self.asset_pool['职业_信托'].isnull()]
        
        
    def select_by_ContractNO(self,exclude_or_focus,these_assets):
        assets_to_exclude_or_focus = pd.DataFrame()
        logger.info('Reading Assets_to_' + exclude_or_focus + '....')
        for these_asset in these_assets:
            path_assets = path_project + '/AssetPoolList/' + these_asset + '.csv'
            logger.info('Reading ' + these_asset + '....')
            try:  assets_to_exclude_or_focus_this = pd.read_csv(path_assets,encoding = 'utf-8') 
            except: assets_to_exclude_or_focus_this = pd.read_csv(path_assets,encoding = 'gbk') 
            
            try:
                #print(isinstance(assets_to_exclude_or_focus_this['#合同号'][0],numpy.int64))            
                if isinstance(assets_to_exclude_or_focus_this['#合同号'][0],numpy.int64) == False:pass
                else: assets_to_exclude_or_focus_this['#合同号'] = '#' + assets_to_exclude_or_focus_this['#合同号'].astype(str) 
                assets_to_exclude_or_focus = assets_to_exclude_or_focus.append(assets_to_exclude_or_focus_this[['#合同号']],ignore_index=True)
                #print(assets_to_exclude_or_focus[:5])
            except(KeyError):
                #print(isinstance(assets_to_exclude_or_focus_this['订单号'][0],numpy.int64))            
                if isinstance(assets_to_exclude_or_focus_this['订单号'][0],numpy.int64) == False:pass
                else: assets_to_exclude_or_focus_this['订单号'] = '#' + assets_to_exclude_or_focus_this['订单号'].astype(str) 
                assets_to_exclude_or_focus = assets_to_exclude_or_focus.append(assets_to_exclude_or_focus_this[['订单号']],ignore_index=True)
            
        logger.info(exclude_or_focus + 'ing ...') 
        if exclude_or_focus == 'exclude':
            try:self.asset_pool = self.asset_pool[~self.asset_pool['No_Contract'].isin(assets_to_exclude_or_focus['订单号'])]
            except(KeyError):self.asset_pool = self.asset_pool[~self.asset_pool['No_Contract'].isin(assets_to_exclude_or_focus['#合同号'])]
            #finally:self.asset_pool = self.asset_pool[~self.asset_pool['No_Contract'].isin(assets_to_exclude_or_focus['订单号'])]
        else:
            try:self.asset_pool = self.asset_pool[self.asset_pool['No_Contract'].isin(assets_to_exclude_or_focus['订单号'])]
            except(KeyError):self.asset_pool = self.asset_pool[self.asset_pool['No_Contract'].isin(assets_to_exclude_or_focus['#合同号'])]
            #finally:self.asset_pool = self.asset_pool[self.asset_pool['No_Contract'].isin(assets_to_exclude_or_focus['订单号'])]
        logger.info(exclude_or_focus +' assets is done.')
        
        
    def run_ReverseSelection(self,iTarget,group_d):

        self.asset_pool['ReverseSelection_Flag'] = ''
        for d in group_d:
            self.asset_pool['ReverseSelection_Flag'] += self.asset_pool[d].astype(str)
            
        RS = ReverseSelection(self.asset_pool[['No_Contract','Amount_Outstanding_yuan'] + group_d],
                              iTarget,group_d
                              )
        RS.cal_OriginalStat()
        RS_results = RS.iLP_Solver_all()
        
        RS_results['ReverseSelection_Flag'] = ''
        for d in group_d:
            RS_results['ReverseSelection_Flag'] += RS_results[d].astype(str)    
        
        logger.info('Selected Outstanding Principal is {0}'.format(sum(RS_results['Amount_Outstanding'])))
        logger.info('Selected Contracts Count is {0}'.format(len(RS_results.index)))
        
        for target_d in iTarget.keys():
             Condition_Satisfied_or_Not(RS_results,target_d,iTarget)
        
        self.asset_pool = self.asset_pool[self.asset_pool['ReverseSelection_Flag'].isin(RS_results['ReverseSelection_Flag'])]
        
        return RS_results

    def run_Stat(self,Distribution_By_Category,Distribution_By_Bins,CN_EN):
        
        S = Statistics(self.asset_pool,CN_EN)
        S.general_statistics_1()
        S.loop_Ds_ret_province_profession(Distribution_By_Category,Distribution_By_Bins)
        S.cal_income2debt_by_ID()
        
    def get_rearranged_APCF_structure(self):
        
        APCF = AssetsCashFlow(self.asset_pool[['No_Contract','Interest_Rate','SERVICE_FEE_RATE','Amount_Outstanding_yuan','first_due_date_after_pool_cut','Term_Remain','Dt_Start','Province']],
                             self.date_pool_cut
                             )
        return APCF.rearrange_APCF_Structure() 
    
    def get_oAPCF(self,asset_status,BackMonth,dt_pool_cut):
        
        APCF = AssetsCashFlow(self.asset_pool[(self.asset_pool['贷款状态'] == asset_status)][['No_Contract','Interest_Rate','SERVICE_FEE_RATE','Amount_Outstanding_yuan','first_due_date_after_pool_cut','Term_Remain','Dt_Start','Province']],
                             dt_pool_cut
                             )

        self.apcf_original[asset_status],self.apcf_original_structure[asset_status],self.dates_recycle_list[asset_status],self.df_ppmt[asset_status],self.df_ipmt[asset_status] = APCF.calc_APCF(BackMonth)  #BackMonth  

    def adjust_oAPCF(self,scenario_id,asset_status,dt_pool_cut):        
        logger.info('get_adjust_oAPCF_simulation for scenario_id {0}...'.format(scenario_id))
        APCFa = APCF_adjuster(self.apcf_original_structure[asset_status],self.scenarios,scenario_id,self.df_ppmt[asset_status],self.df_ipmt[asset_status],self.dates_recycle_list[asset_status],dt_pool_cut,asset_status) #
        self.apcf_original_adjusted[asset_status][scenario_id],self.APCF_adjusted_save[asset_status][scenario_id] = APCFa.adjust_APCF('O')

    def init_oAP_Acc(self):
        logger.info('init_oAP_Acc....')
        
        self.AP_PAcc_original_O,self.AP_PAcc_actual_O = {},{}
        self.AP_PAcc_pay_O,self.AP_PAcc_buy_O= {},{}
        self.AP_PAcc_overdue_1_30_currentTerm_O,self.AP_PAcc_overdue_1_30_allTerm_O= {},{}
        self.AP_PAcc_overdue_31_60_currentTerm_O,self.AP_PAcc_overdue_31_60_allTerm_O = {},{}
        self.AP_PAcc_overdue_61_90_currentTerm_O,self.AP_PAcc_overdue_61_90_allTerm_O = {},{}
        self.AP_PAcc_loss_currentTerm_O,self.AP_PAcc_loss_allTerm_O = {},{}

        self.AP_IAcc_original_O,self.AP_IAcc_actual_O = {},{}
        self.AP_IAcc_pay_O,self.AP_IAcc_buy_O = {},{}
        self.AP_IAcc_overdue_1_30_currentTerm_O,self.AP_IAcc_overdue_1_30_allTerm_O = {},{}
        self.AP_IAcc_overdue_31_60_currentTerm_O,self.AP_IAcc_overdue_31_60_allTerm_O = {},{}
        self.AP_IAcc_overdue_61_90_currentTerm_O,self.AP_IAcc_overdue_61_90_allTerm_O = {},{}
        self.AP_IAcc_loss_currentTerm_O,self.AP_IAcc_loss_allTerm_O = {},{}
        
        self.AP_PAcc_outstanding_O,self.AP_IAcc_outstanding_O = {},{} 
        self.AP_PAcc_reserve_O = {}
            
        for scenario_id in self.scenarios.keys():
            self.AP_PAcc_original_O[scenario_id],self.AP_PAcc_actual_O[scenario_id] = {},{}
            self.AP_PAcc_pay_O[scenario_id],self.AP_PAcc_buy_O[scenario_id] = {},{}
            self.AP_PAcc_overdue_1_30_currentTerm_O[scenario_id],self.AP_PAcc_overdue_1_30_allTerm_O[scenario_id] = {},{}
            self.AP_PAcc_overdue_31_60_currentTerm_O[scenario_id],self.AP_PAcc_overdue_31_60_allTerm_O[scenario_id] = {},{}
            self.AP_PAcc_overdue_61_90_currentTerm_O[scenario_id],self.AP_PAcc_overdue_61_90_allTerm_O[scenario_id] = {},{}
            self.AP_PAcc_loss_currentTerm_O[scenario_id],self.AP_PAcc_loss_allTerm_O[scenario_id] = {},{}
    
            self.AP_IAcc_original_O[scenario_id],self.AP_IAcc_actual_O[scenario_id] = {},{}
            self.AP_IAcc_pay_O[scenario_id],self.AP_IAcc_buy_O[scenario_id] = {},{}
            self.AP_IAcc_overdue_1_30_currentTerm_O[scenario_id],self.AP_IAcc_overdue_1_30_allTerm_O[scenario_id] = {},{}
            self.AP_IAcc_overdue_31_60_currentTerm_O[scenario_id],self.AP_IAcc_overdue_31_60_allTerm_O[scenario_id] = {},{}
            self.AP_IAcc_overdue_61_90_currentTerm_O[scenario_id],self.AP_IAcc_overdue_61_90_allTerm_O[scenario_id] = {},{}
            self.AP_IAcc_loss_currentTerm_O[scenario_id],self.AP_IAcc_loss_allTerm_O[scenario_id] = {},{}
            
            self.AP_PAcc_outstanding_O[scenario_id],self.AP_IAcc_outstanding_O[scenario_id] = {},{} 
            self.AP_PAcc_reserve_O[scenario_id] = {}
            
        for scenario_id in self.scenarios.keys():
            for k in dates_recycle:
                self.AP_PAcc_original_O[scenario_id][k] = 0
                self.AP_PAcc_actual_O[scenario_id][k] = 0
                self.AP_PAcc_pay_O[scenario_id][k] = 0
                self.AP_PAcc_buy_O[scenario_id][k] = 0
                self.AP_PAcc_overdue_1_30_currentTerm_O[scenario_id][k] = 0
                self.AP_PAcc_overdue_1_30_allTerm_O[scenario_id][k] = 0
                self.AP_PAcc_overdue_31_60_currentTerm_O[scenario_id][k] = 0
                self.AP_PAcc_overdue_31_60_allTerm_O[scenario_id][k] = 0
                self.AP_PAcc_overdue_61_90_currentTerm_O[scenario_id][k] = 0
                self.AP_PAcc_overdue_61_90_allTerm_O[scenario_id][k] = 0
                self.AP_PAcc_loss_currentTerm_O[scenario_id][k] = 0
                self.AP_PAcc_loss_allTerm_O[scenario_id][k] = 0
                self.AP_PAcc_outstanding_O[scenario_id][k] = 0
                
                self.AP_PAcc_reserve_O[scenario_id][k] = amount_ReserveAcount
    
                self.AP_IAcc_original_O[scenario_id][k] = 0                   
                self.AP_IAcc_actual_O[scenario_id][k] = 0
                self.AP_IAcc_pay_O[scenario_id][k] = 0
                self.AP_IAcc_buy_O[scenario_id][k] = 0
                self.AP_IAcc_overdue_1_30_currentTerm_O[scenario_id][k] = 0
                self.AP_IAcc_overdue_1_30_allTerm_O[scenario_id][k] = 0
                self.AP_IAcc_overdue_31_60_currentTerm_O[scenario_id][k] = 0
                self.AP_IAcc_overdue_31_60_allTerm_O[scenario_id][k] = 0
                self.AP_IAcc_overdue_61_90_currentTerm_O[scenario_id][k] = 0
                self.AP_IAcc_overdue_61_90_allTerm_O[scenario_id][k] = 0
                self.AP_IAcc_loss_currentTerm_O[scenario_id][k] = 0
                self.AP_IAcc_loss_allTerm_O[scenario_id][k] = 0
                self.AP_IAcc_outstanding_O[scenario_id][k] = 0
    
    def update_oAP_Acc(self,scenario_id,asset_status):
         logger.info('update_oAP_Acc for scenario_id {0}'.format(scenario_id))
         AP_Acc = AssetPoolAccount(self.apcf_original[asset_status],self.apcf_original_adjusted[asset_status][scenario_id])
         
         principal_available = AP_Acc.available_principal()
         interest_available = AP_Acc.available_interest()
         
         for k in dates_recycle:
             self.AP_PAcc_original_O[scenario_id][k] += principal_available[0][k]
             self.AP_PAcc_actual_O[scenario_id][k] += principal_available[1][k]
             self.AP_PAcc_pay_O[scenario_id][k] += principal_available[2][k]
             self.AP_PAcc_buy_O[scenario_id][k] += principal_available[3][k]
             self.AP_PAcc_overdue_1_30_currentTerm_O[scenario_id][k] += principal_available[4][k]
             self.AP_PAcc_overdue_1_30_allTerm_O[scenario_id][k] += principal_available[5][k]
             self.AP_PAcc_overdue_31_60_currentTerm_O[scenario_id][k] += principal_available[6][k]
             self.AP_PAcc_overdue_31_60_allTerm_O[scenario_id][k] += principal_available[7][k]
             self.AP_PAcc_overdue_61_90_currentTerm_O[scenario_id][k] += principal_available[8][k]
             self.AP_PAcc_overdue_61_90_allTerm_O[scenario_id][k] += principal_available[9][k]
             self.AP_PAcc_loss_currentTerm_O[scenario_id][k] += principal_available[10][k]
             self.AP_PAcc_loss_allTerm_O[scenario_id][k] += principal_available[11][k]  
             self.AP_PAcc_outstanding_O[scenario_id][k] += principal_available[12][k]
             
             self.AP_PAcc_reserve_O[scenario_id][k] += principal_available[13][k]
         
             self.AP_IAcc_original_O[scenario_id][k] += interest_available[0][k]
             self.AP_IAcc_actual_O[scenario_id][k] += interest_available[1][k]
             self.AP_IAcc_pay_O[scenario_id][k] += interest_available[2][k]
             self.AP_IAcc_buy_O[scenario_id][k] += interest_available[3][k]
             self.AP_IAcc_overdue_1_30_currentTerm_O[scenario_id][k] += interest_available[4][k]
             self.AP_IAcc_overdue_1_30_allTerm_O[scenario_id][k] += interest_available[5][k]
             self.AP_IAcc_overdue_31_60_currentTerm_O[scenario_id][k] += interest_available[6][k]
             self.AP_IAcc_overdue_31_60_allTerm_O[scenario_id][k] += interest_available[7][k]
             self.AP_IAcc_overdue_61_90_currentTerm_O[scenario_id][k] += interest_available[8][k]
             self.AP_IAcc_overdue_61_90_allTerm_O[scenario_id][k] += interest_available[9][k]
             self.AP_IAcc_loss_currentTerm_O[scenario_id][k] += interest_available[10][k]
             self.AP_IAcc_loss_allTerm_O[scenario_id][k] += interest_available[11][k]
             self.AP_IAcc_outstanding_O[scenario_id][k] += interest_available[12][k]
             
    def oAP_Acc_DeSimulation(self,scenario_id,simulation_times):
        
        for k in dates_recycle:
             self.AP_PAcc_original_O[scenario_id][k] = self.AP_PAcc_original_O[scenario_id][k] / simulation_times
             self.AP_PAcc_actual_O[scenario_id][k] = self.AP_PAcc_actual_O[scenario_id][k] / simulation_times
             self.AP_PAcc_pay_O[scenario_id][k] = self.AP_PAcc_pay_O[scenario_id][k] / simulation_times
             self.AP_PAcc_buy_O[scenario_id][k] = self.AP_PAcc_buy_O[scenario_id][k] / simulation_times
             self.AP_PAcc_overdue_1_30_currentTerm_O[scenario_id][k] = self.AP_PAcc_overdue_1_30_currentTerm_O[scenario_id][k] / simulation_times
             self.AP_PAcc_overdue_1_30_allTerm_O[scenario_id][k] = self.AP_PAcc_overdue_1_30_allTerm_O[scenario_id][k] / simulation_times
             self.AP_PAcc_overdue_31_60_currentTerm_O[scenario_id][k] = self.AP_PAcc_overdue_31_60_currentTerm_O[scenario_id][k] / simulation_times
             self.AP_PAcc_overdue_31_60_allTerm_O[scenario_id][k] = self.AP_PAcc_overdue_31_60_allTerm_O[scenario_id][k] / simulation_times
             self.AP_PAcc_overdue_61_90_currentTerm_O[scenario_id][k] = self.AP_PAcc_overdue_61_90_currentTerm_O[scenario_id][k] / simulation_times
             self.AP_PAcc_overdue_61_90_allTerm_O[scenario_id][k] = self.AP_PAcc_overdue_61_90_allTerm_O[scenario_id][k] / simulation_times
             self.AP_PAcc_loss_currentTerm_O[scenario_id][k] = self.AP_PAcc_loss_currentTerm_O[scenario_id][k] / simulation_times
             self.AP_PAcc_loss_allTerm_O[scenario_id][k] = self.AP_PAcc_loss_allTerm_O[scenario_id][k] / simulation_times
             self.AP_PAcc_outstanding_O[scenario_id][k] = self.AP_PAcc_outstanding_O[scenario_id][k] / simulation_times
             self.AP_PAcc_reserve_O[scenario_id][k] = self.AP_PAcc_reserve_O[scenario_id][k] / simulation_times
         
             self.AP_IAcc_original_O[scenario_id][k] = self.AP_IAcc_original_O[scenario_id][k] / simulation_times
             self.AP_IAcc_actual_O[scenario_id][k] = self.AP_IAcc_actual_O[scenario_id][k] / simulation_times
             self.AP_IAcc_pay_O[scenario_id][k] = self.AP_IAcc_pay_O[scenario_id][k] / simulation_times
             self.AP_IAcc_buy_O[scenario_id][k] = self.AP_IAcc_buy_O[scenario_id][k] / simulation_times
             self.AP_IAcc_overdue_1_30_currentTerm_O[scenario_id][k] = self.AP_IAcc_overdue_1_30_currentTerm_O[scenario_id][k] / simulation_times
             self.AP_IAcc_overdue_1_30_allTerm_O[scenario_id][k] = self.AP_IAcc_overdue_1_30_allTerm_O[scenario_id][k] / simulation_times
             self.AP_IAcc_overdue_31_60_currentTerm_O[scenario_id][k] = self.AP_IAcc_overdue_31_60_currentTerm_O[scenario_id][k] / simulation_times
             self.AP_IAcc_overdue_31_60_allTerm_O[scenario_id][k] = self.AP_IAcc_overdue_31_60_allTerm_O[scenario_id][k] / simulation_times
             self.AP_IAcc_overdue_61_90_currentTerm_O[scenario_id][k] = self.AP_IAcc_overdue_61_90_currentTerm_O[scenario_id][k] / simulation_times
             self.AP_IAcc_overdue_61_90_allTerm_O[scenario_id][k] = self.AP_IAcc_overdue_61_90_allTerm_O[scenario_id][k] / simulation_times
             self.AP_IAcc_loss_currentTerm_O[scenario_id][k] = self.AP_IAcc_loss_currentTerm_O[scenario_id][k] / simulation_times
             self.AP_IAcc_loss_allTerm_O[scenario_id][k] = self.AP_IAcc_loss_allTerm_O[scenario_id][k] / simulation_times
             self.AP_IAcc_outstanding_O[scenario_id][k] = self.AP_IAcc_outstanding_O[scenario_id][k] / simulation_times
        
        self.df_AP_PAcc_actual_O_DeSimu = pd.DataFrame(list(self.AP_PAcc_actual_O[scenario_id].items()), columns=['date_recycle', 'principal_recycle_total'])
        
    def CDR_calc_O(self,scenario_id):

         self.CDR_O[scenario_id+'_O'] =  [self.AP_PAcc_loss_allTerm_O[scenario_id][dates_recycle[-1]],
                                            sum([self.AP_PAcc_original_O[scenario_id][k] for k in dates_recycle]),
                                            self.AP_PAcc_loss_allTerm_O[scenario_id][dates_recycle[-1]]/sum([self.AP_PAcc_original_O[scenario_id][k] for k in dates_recycle])
                                            ]  
         logger.info('CDR for {0} is: {1:.4%} '.format(scenario_id,self.CDR_O[scenario_id+'_O'][2]))
         self.amount_default_O[scenario_id] = deepcopy(self.AP_PAcc_loss_allTerm_O[scenario_id][dates_recycle[-1]])
             
    def run_WaterFall(self):
         
         for scenario_id in self.scenarios.keys():
             logger.info('scenario_id is {0}'.format(scenario_id))
             self.waterfall[scenario_id],self.reserveAccount_used[scenario_id] = run_Accounts(self.AP_PAcc_original[scenario_id],self.AP_PAcc_outstanding[scenario_id],
                                                       self.AP_PAcc_reserve[scenario_id],#self.AP_PAcc_loss_allTerm[scenario_id],
                                                       self.AP_PAcc_actual[scenario_id],self.AP_PAcc_actual_O[scenario_id],self.AP_PAcc_actual_R[scenario_id],
                                                       self.AP_PAcc_pay[scenario_id],self.AP_PAcc_buy[scenario_id],
                                                       self.AP_IAcc_original[scenario_id],self.AP_IAcc_actual[scenario_id],
                                                       self.AP_IAcc_pay[scenario_id],self.AP_IAcc_buy[scenario_id],
                                                       scenario_id,Bonds,self.RevolvingDeal,self.RevolvingPool_PurchaseAmount
                                                       )
             
             self.wf_BasicInfo[scenario_id] = deepcopy(BasicInfo_calculator(self.waterfall[scenario_id],dt_param,Bonds))
             self.wf_CoverRatio[scenario_id] = deepcopy(CR_calculator(self.waterfall[scenario_id],self.AP_PAcc_pay[scenario_id],self.AP_IAcc_pay[scenario_id]))
             self.wf_NPVs[scenario_id] = deepcopy(NPV_calculator(self.waterfall[scenario_id],self.AP_PAcc_pay[scenario_id],self.AP_IAcc_pay[scenario_id]))
             self.reserveAccount_used[scenario_id] = pd.DataFrame.from_dict(self.reserveAccount_used[scenario_id])
             
    def cal_RnR(self):
         
        scenarios_weight = [scenarios[scenario_id]['scenario_weight'] for scenario_id in self.scenarios.keys()]
        
        NPV_originator = [self.wf_NPVs[scenario_id]['NPV_originator'][0] for scenario_id in self.scenarios.keys()]
        NPV_asset_pool = [self.wf_NPVs[scenario_id]['NPV_asset_pool'][0] for scenario_id in self.scenarios.keys()]
        
        SD_NPV_originator = SD_with_weight(NPV_originator,scenarios_weight)
        SD_NPV_asset_pool = SD_with_weight(NPV_asset_pool,scenarios_weight)
        
        RnR = SD_NPV_originator / SD_NPV_asset_pool
        
        return RnR