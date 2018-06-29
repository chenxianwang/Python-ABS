# -*- coding: utf-8 -*-
"""
Created on Sat May 26 22:32:19 2018

@author: jonah.chen
"""

import sys
import os
from constant import *
import pandas as pd
import numpy as np
from abs_util.util_general import *
from abs_util.util_cf import *
from dateutil.relativedelta import relativedelta
import datetime

class AssetsCashFlow():
    
    def __init__(self,asset_pool,date_pool_cut):
        self.asset_pool = asset_pool
        self.date_pool_cut = date_pool_cut
        
        self.wb_save_results = wb_name
       
        self.dates_recycle_list = []
        self.apcf = pd.DataFrame()
        self.apcf_p = pd.DataFrame()
        self.apcf_i = pd.DataFrame()
        self.apcf_f = pd.DataFrame()
        
    def calc_APCF(self,BackMonth):
        
        logger.info('calc_AssetPool_Structure....')
        self.asset_pool['first_due_period_O'] = (pd.to_datetime(self.asset_pool['first_due_date_after_pool_cut']).dt.year - self.date_pool_cut.year) * 12 + \
                                              pd.to_datetime(self.asset_pool['first_due_date_after_pool_cut']).dt.month- self.date_pool_cut.month - BackMonth
        last_term = int((self.asset_pool['Term_Remain'] + self.asset_pool['first_due_period_O']).max())
        self.dates_recycle_list= [get_next_eom(self.date_pool_cut,i) for i in range(last_term)]
        logger.info('gen_APCF_Structure for APCF....')
        
        self.apcf_structure = self.gen_APCF_Structure('first_due_period_O')
                
        for d_r in self.dates_recycle_list:
            self.apcf_structure[d_r] = 0
        logger.info('AssetPool_Structure save_to_excel....')                 
        #save_to_excel(self.apcf_structure_original,'Original_APCF_Structure',self.wb_save_results)
        logger.info('cash_flow_collection....')    
        #self.apcf,self.apcf_p,self.apcf_i,self.apcf_f
        self.apcf = cash_flow_collection(self.apcf_structure,self.dates_recycle_list,'first_due_period_O','Original',self.wb_save_results)
        
        return self.apcf,self.apcf_structure
    
    def rearrange_APCF_Structure(self):
    
        logger.info('calc_Rearrange_APCF_Structure')
        self.max_first_due_date_after_poolcut = pd.to_datetime(self.asset_pool['first_due_date_after_pool_cut']).max().date() 
        poolcutdate_next_month = [self.date_pool_cut - datetime.timedelta(days=1)]
        month_increment = 1
        while self.date_pool_cut + relativedelta(months=month_increment) - datetime.timedelta(days=1) <= self.max_first_due_date_after_poolcut + relativedelta(months=1):
            poolcutdate_next_month.append(self.date_pool_cut + relativedelta(months=month_increment) - datetime.timedelta(days=1))
            month_increment += 1
            
        df_poolcutdate_next_month = pd.DataFrame({'poolcutdate_next_month':poolcutdate_next_month})
        labels = [i for i in range(len(poolcutdate_next_month) - 1) ]

        self.asset_pool['first_due_period_R'] = pd.cut(pd.to_datetime(self.asset_pool['first_due_date_after_pool_cut']).astype(np.int64)//10**9, 
                                      bins = pd.to_datetime(df_poolcutdate_next_month['poolcutdate_next_month']).astype(np.int64)//10**9,
                                      labels = labels
                                      )
        self.asset_pool['first_due_period_R'] = self.asset_pool['first_due_period_R'].astype(int)
        
        return self.gen_APCF_Structure('first_due_period_R')
        
    def gen_APCF_Structure(self,first_due_period_value):
        self.asset_pool['SERVICE_FEE_RATE'] = self.asset_pool['SERVICE_FEE_RATE'].where(self.asset_pool['SERVICE_FEE_RATE'] > 0,0)        
        #df['Interest_Rate'] = df['Interest_Rate']/100        
        apcf_structure = self.asset_pool.groupby([first_due_period_value,'Interest_Rate','SERVICE_FEE_RATE','Term_Remain'])\
                                 .agg({'Amount_Outstanding_yuan':'sum'})\
                                 .reset_index()\
                                 .rename(columns = {'Amount_Outstanding_yuan':'OutstandingPrincipal'}
                                 )
                                 
        apcf_structure['Total_Fee_Rate'] = apcf_structure['Interest_Rate'] + apcf_structure['SERVICE_FEE_RATE']*12
        apcf_structure['Interest_Rate_Proportion'] = apcf_structure['Interest_Rate'] / apcf_structure['Total_Fee_Rate']
        apcf_structure['OutstandingPrincipal_Proportion'] = apcf_structure['OutstandingPrincipal'] / apcf_structure['OutstandingPrincipal'].sum()
    
        return apcf_structure
    
    