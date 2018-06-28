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
        self.list_NewColumns_Files = PoolCutDate_n_AssetPoolName[2]
        
        self.asset_pool = pd.DataFrame()
        self.acf_structure = pd.DataFrame()
        
        self.rearranged_acf_structure = pd.DataFrame()
    
   
    def get_AssetPool(self):
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
        self.asset_pool['Credit_Score'] = self.asset_pool['Credit_Score_4'].round(3)
#        self.asset_pool['ReverseSelection_Flag'] = self.asset_pool['Interest_Rate'].astype(str) + self.asset_pool['Credit_Score'].astype(str) + self.asset_pool['LoanRemainTerm'].astype(str)
#        
        logger.info('Original Asset Pool Gotten.')
        
        return self.asset_pool
    
    def add_Columns_From(self):
        AssetPool = pd.DataFrame()
        for Pool_index,Pool_name in enumerate(self.list_NewColumns_Files):
            logger.info('Getting Adding part ' + str(Pool_index+1) + '...')
            AssetPoolPath_this = self.path_project + '/AssetPoolList/' + Pool_name + '.csv'
            try:
                AssetPool_this = pd.read_csv(AssetPoolPath_this,encoding = 'utf-8') 
            except:
                AssetPool_this = pd.read_csv(AssetPoolPath_this,encoding = 'gbk') 
            AssetPool = AssetPool.append(AssetPool_this,ignore_index=True)
        
        logger.info('Rename added header....')
        AssetPool = AssetPool.rename(columns = DWH_header_rename_AddColumns)    
        logger.info('Inner Merging...')
        self.asset_pool = self.asset_pool.merge(AssetPool,left_on='No_Contract',right_on='TEXT_CONTRACT_NUMBER',how='inner')

        logger.info('Columns added....')
        
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