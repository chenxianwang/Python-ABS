# -*- coding: utf-8 -*-
"""
Created on Fri May 18 21:33:52 2018

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
from AssetPool import AssetPool
from AssetsCashFlow import AssetsCashFlow

low_memory=False

logger = get_logger(__name__)

class RevolvingAssetPool():
    
    def __init__(self,PoolCutDate_n_AssetPoolName):
        
        self.date_revolving_pools_cut = PoolCutDate_n_AssetPoolName[0]
        self.list_AssetPoolName = PoolCutDate_n_AssetPoolName[1]
        
        self.asset_pool = pd.DataFrame()
        self.acf_structure_revolving = pd.DataFrame()
        
        self.dates_recycle_list_revolving = [] 

        self.total_purchase_amount = 0

    
    def get_AssetPool(self):
        logger.info('get_RevolvingAssetPool...')
        for Pool_index,Pool_name in enumerate(self.list_AssetPoolName):
            logger.info('Getting part ' + str(Pool_index+1) + '...')
            AssetPoolPath_this = path_project + '/AssetPoolList/' + Pool_name + '.csv'
            try:
                AssetPool_this = pd.read_csv(AssetPoolPath_this,encoding = 'utf-8') 
            except:
                AssetPool_this = pd.read_csv(AssetPoolPath_this,encoding = 'gbk') 
            AssetPool_this = AssetPool_this[list(DWH_header_rename.keys())] 
            logger.info('Renaming header....')
            AssetPool_this = AssetPool_this.rename(columns = DWH_header_rename)
            self.asset_pool = self.asset_pool.append(AssetPool_this,ignore_index=True)
        
        self.asset_pool['Credit_Score'] = self.asset_pool['Credit_Score_4'].round(3)
        self.asset_pool['ReverseSelection_Flag'] = self.asset_pool['Interest_Rate'].astype(str) + self.asset_pool['Credit_Score'].astype(str) #+ self.asset_pool['LoanRemainTerm'].astype(str)
        logger.info('Revolving Asset Pool Gotten.')
        
        return self.asset_pool
        
    def forcast_Revolving_ACF(self,acf_original,acf_structure_revolving,until_which_revolving_pool):
        
        self.acf_structure_revolving = acf_structure_revolving
        self.acf_original = acf_original
        
        for which_revolving_pool in range(1,until_which_revolving_pool + 1):
            purchase_amount = self.prepare_PurchaseAmount(which_revolving_pool)
            self.total_purchase_amount += purchase_amount
            print('purchase_amount for R',which_revolving_pool,' is: ', purchase_amount)
            print('Total purchase_amount is ',self.total_purchase_amount)
            self.acf_structure_revolving['OutstandingPrincipal'] = purchase_amount * self.acf_structure_revolving['OutstandingPrincipal_Proportion']
        
            last_term = int((self.acf_structure_revolving['Term_Remain'] + self.acf_structure_revolving['first_due_period_R']).max())
            self.dates_recycle_list_revolving = [self.date_revolving_pools_cut[which_revolving_pool-1] + relativedelta(months=i) - datetime.timedelta(days=1) for i in range(1,last_term+1)]
            for d_r in self.dates_recycle_list_revolving:
                self.acf_structure_revolving[d_r] = 0
       
            #save_to_excel(self.acf_structure_revolving,'Revolving_ACF_Structure_' + str(which_revolving_pool),self.wb_save_results)
        
            self.acf_revolving_acf[which_revolving_pool] = cash_flow_collection(self.acf_structure_revolving,self.dates_recycle_list_revolving,'first_due_period_R','Revolving'+str(which_revolving_pool),self.wb_save_results)
            #print('acf_revolving_acf',self.acf_revolving_acf)

    def prepare_PurchaseAmount(self,for_which_revolving_pool):
        
        if for_which_revolving_pool == 1:
            
            amount_principal = self.acf_original[pd.to_datetime(self.acf_original['date_recycle']) <= get_next_eom(self.date_trust_effective,0)]['amount_principal'].sum()
            amount_interest = self.acf_original[pd.to_datetime(self.acf_original['date_recycle']) <= get_next_eom(self.date_trust_effective,0)]['amount_interest'].sum()
            return amount_principal + amount_interest
        
        else:
            amount_principal_original = self.acf_original[pd.to_datetime(self.acf_original['date_recycle']) == self.date_revolving_pools_cut[for_which_revolving_pool-1] - datetime.timedelta(days=1) ]['amount_principal'].sum()
            amount_interest_original = self.acf_original[pd.to_datetime(self.acf_original['date_recycle']) == self.date_revolving_pools_cut[for_which_revolving_pool-1] - datetime.timedelta(days=1) ]['amount_interest'].sum()
            
            amount_principal_previous_r = 0
            amount_interest_previous_r = 0
            
            for previous_r in range(1,for_which_revolving_pool):
                amount_principal_previous_r_this = self.acf_revolving_acf[previous_r][pd.to_datetime(self.acf_revolving_acf[previous_r]['date_recycle']) == self.date_revolving_pools_cut[for_which_revolving_pool-1] - datetime.timedelta(days=1) ]['amount_principal'].sum()
                #print('amount_principal_previous_r of ',previous_r,' is ',amount_principal_previous_r_this )
                amount_principal_previous_r += amount_principal_previous_r_this
                amount_interest_previous_r_this = self.acf_revolving_acf[previous_r][pd.to_datetime(self.acf_revolving_acf[previous_r]['date_recycle']) == self.date_revolving_pools_cut[for_which_revolving_pool-1] - datetime.timedelta(days=1) ]['amount_interest'].sum()
                #print('amount_interest_previous_r_this of ',previous_r,' is ',amount_interest_previous_r_this )
                amount_interest_previous_r += amount_interest_previous_r_this
            
            return amount_principal_original + amount_interest_original + \
                   amount_principal_previous_r + amount_interest_previous_r