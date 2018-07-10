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

class AssetPool():
    def __init__(self,PoolCutDate_n_AssetPoolName):

        self.date_pool_cut = PoolCutDate_n_AssetPoolName[0]
        self.list_AssetPoolName = PoolCutDate_n_AssetPoolName[1]
        
        self.asset_pool = pd.DataFrame()    
   
    def get_AP(self):
        logger.info('get_OriginalAssetPool...')
        for Pool_index,Pool_name in enumerate(self.list_AssetPoolName):
            logger.info('Getting part ' + str(Pool_index+1) + '...')
            AssetPoolPath_this = path_project + '/AssetPoolList/' + Pool_name + '.csv'
            try:
                AssetPool_this = pd.read_csv(AssetPoolPath_this,encoding = 'utf-8') 
            except:
                AssetPool_this = pd.read_csv(AssetPoolPath_this,encoding = 'gbk') 
            self.asset_pool = self.asset_pool.append(AssetPool_this,ignore_index=True)

        self.asset_pool = self.asset_pool[list(DWH_header_rename.keys())] 
        logger.info('Renaming header....')
        self.asset_pool = self.asset_pool.rename(columns = DWH_header_rename) 
#        self.asset_pool['LoanRemainTerm'] = pd.to_datetime(self.asset_pool['Dt_Maturity']).dt.date - datetime.date(2018,6,29)
#        self.asset_pool['LoanRemainTerm'] = (self.asset_pool['LoanRemainTerm'] / np.timedelta64(1, 'D')).astype(int)
        logger.info('Original Asset Pool Gotten.')
        
        return self.asset_pool
    
    def add_Columns_From(self,file_names_left_right):
        
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
    
            try:
                AssetPool['#合同号'] = '#' + AssetPool['合同号'].astype(str)
            except(KeyError):
                pass
           
            logger.info('left Merging...')
            self.asset_pool = self.asset_pool.merge(AssetPool,left_on= left,right_on = right,how='left')
            logger.info('Columns added....')
        
        return self.asset_pool
        
    def exclude_or_focus_by_ContractNo(self,exclude_or_focus,these_assets):
        logger.info('Reading Assets_to_' + exclude_or_focus + '....')
        path_assets = self.path_project + '/AssetPoolList/' + these_assets + '.csv'
        assets_to_exclude_or_focus = pd.read_csv(path_assets,encoding = 'gbk')
        
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