# -*- coding: utf-8 -*-
"""
Created on Tue Mar 13 09:50:23 2018

@author: Jonah.Chen
"""

import sys
import os
from constant import *
import pandas as pd
import numpy as np
from abs_util.util_general import *
from abs_util.util_cf import *
from abs_util.util_sr import *
from dateutil.relativedelta import relativedelta
import datetime


low_memory=False

logger = get_logger(__name__)

class Deal():
    def __init__(self,name,date_pool_cut,params,date_trust_effective):

        self.name = name
        self.date_pool_cut = date_pool_cut        
        self.date_trust_effective = date_trust_effective
        self.params = params
        
        self.path_project = path_root  + '/../CheckTheseProjects/' + self.name
        self.wb_save_results = self.path_project + '/' + self.name +'.xlsx'
               
        self.asset_pool = pd.DataFrame()
        self.volumm_pool_cut = 0.0
        self.cnt_assets = 0
        self.max_maturity_date = datetime.date(3000,1,1)
    
    def Preparation(self):
        if os.path.isfile(self.wb_save_results):
          os.remove(self.wb_save_results)
    
    def get_OriginalAssetPool(self,list_AssetPoolName):
        logger.info('get_OriginalAssetPool...')
        for Pool_index,Pool_name in enumerate(list_AssetPoolName):
            logger.info('Getting part ' + str(Pool_index+1) + '...')
            AssetPoolPath_this = self.path_project + '/AssetPoolList/' + Pool_name + '.csv'
            try:
                AssetPool_this = pd.read_csv(AssetPoolPath_this,encoding = 'utf-8') 
            except:
                AssetPool_this = pd.read_csv(AssetPoolPath_this,encoding = 'gbk') 
            #AssetPool_this = AssetPool_this[AssetPool_this['综合费用率'] <= 0.24]
            self.asset_pool = self.asset_pool.append(AssetPool_this,ignore_index=True)

        self.asset_pool = self.asset_pool[list(DWH_header_rename.keys())] 
        logger.info('Renaming header....')
        self.asset_pool = self.asset_pool.rename(columns = DWH_header_rename) 
#        logger.info('Calculating Pool Cut Volumn...')
#        self.volumm_pool_cut = self.asset_pool['Amount_Outstanding_yuan'].sum()
#        self.max_maturity_date = pd.to_datetime(self.asset_pool['Dt_Maturity']).max().date() #type is pandas.tslib.Timestamp
#        #self.cnt_assets = self.asset_pool['No_Contract'].count()
#        
#        self.asset_pool['ReverseSelection_Flag'] = self.asset_pool['Interest_Rate'].astype(str) + \
#                                                   self.asset_pool['LoanRemainTerm'].astype(str)+ \
#                                                   self.asset_pool['Credit_Score'].astype(str) 
        logger.info('Original Asset Pool Gotten.')
    
    def add_Columns_From(self,list_NewColumns_Files):
        AssetPool = pd.DataFrame()
        for Pool_index,Pool_name in enumerate(list_NewColumns_Files):
            logger.info('Getting Adding part ' + str(Pool_index+1) + '...')
            AssetPoolPath_this = self.path_project + '/AssetPoolList/' + Pool_name + '.csv'
            try:
                AssetPool_this = pd.read_csv(AssetPoolPath_this,encoding = 'utf-8') 
            except:
                AssetPool_this = pd.read_csv(AssetPoolPath_this,encoding = 'gbk') 
            AssetPool = AssetPool.append(AssetPool_this,ignore_index=True)
        
        AssetPool['#合同号'] = '#' + AssetPool['TEXT_CONTRACT_NUMBER'].astype(str)
        logger.info('Inner Merging...')
        self.asset_pool = self.asset_pool[['No_Contract','Age_Project_Start','Income']].merge(AssetPool,left_on='No_Contract',right_on='#合同号',how='inner')

#        logger.info('rename added header....')
#        self.asset_pool = self.asset_pool.rename(columns = DWH_header_rename_AddColumns)     
        
#        self.asset_pool['ReverseSelection_Flag'] = self.asset_pool['Interest_Rate'].astype(str) + \
#                                                   self.asset_pool['LoanRemainTerm'].astype(str) + \
#                                                   self.asset_pool['Credit_Score'].astype(str)     
        
        #self.asset_pool = self.asset_pool.rename(columns = DWH_header_REVERSE_rename) 
#        print('Saving...')
        part_1 = self.asset_pool[self.asset_pool['Age_Project_Start'] != self.asset_pool['NUM_LOAN_AGE']]
        part_1.to_csv('part_1.csv')
#        part_2 = self.asset_pool[self.asset_pool['剩余天数'] > 240]
#        part_2.to_csv('part_2.csv')        
#        
        #Assets_Not_Matched = self.asset_pool[self.asset_pool['No_Contract','Age_Project_Start','#合同号','封包日年龄_Noodles']]
        #Assets_Not_Matched.to_csv('Assets_Not_Matched.csv') 
#        
        print('Saving done.')
        
        
    def exclude_or_focus_by_ContractNo(self,exclude_or_focus,these_assets):
        logger.info('Reading Assets_to_' + exclude_or_focus + '....')
        path_assets = self.path_project + '/AssetPoolList/' + these_assets + '.csv'
        assets_to_exclude_or_focus = pd.read_csv(path_assets,encoding = 'gbk')
        
        #print(assets_to_exclude_or_focus['ReverseSelection_Flag'][:5])
        #print(self.asset_pool['ReverseSelection_Flag'][:5])
        
        logger.info(exclude_or_focus + 'ing ...') 
        if exclude_or_focus == 'exclude':
            self.asset_pool = self.asset_pool[~self.asset_pool['#合同号'].isin(assets_to_exclude_or_focus['#合同号'])]
        #assets = self.asset_pool[self.asset_pool['ReverseSelection_Flag'].isin(assets_to_exclude_or_focus['ReverseSelection_Flag'])]
        #assets_to_exclude_or_focus['#合同号'] = '#' + assets_to_exclude_or_focus['合同号'].astype(str)
       
        self.asset_pool = self.asset_pool[self.asset_pool['No_Contract'].isin(assets_to_exclude_or_focus['#合同号'])]
        
        #assets = self.asset_pool.rename(columns = DWH_header_REVERSE_rename) 
        #assets.to_csv('1stRevolvingPool.csv')
        
        logger.info(exclude_or_focus + 'is done.')
        
        #return assets

    def exclude_or_focus_by_criteria(self,exclude_or_focus,criteria,criteria_value):
        
        logger.info(exclude_or_focus + 'ing ...') 
        if exclude_or_focus == 'exclude':
            self.asset_pool = self.asset_pool[~self.asset_pool['#合同号'].isin(assets_to_exclude_or_focus['#合同号'])]
        assets = self.asset_pool[pd.to_datetime(self.asset_pool['Dt_Maturity']) <= criteria_value]
        print(assets['Amount_Outstanding_yuan'].sum())
        logger.info(exclude_or_focus + ' is done.')