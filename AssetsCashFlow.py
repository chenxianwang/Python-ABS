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
    
    def __init__(self,name,asset_pool,date_pool_cut):
        self.asset_pool = asset_pool
        self.date_pool_cut = date_pool_cut
        
        self.max_first_due_date_after_poolcut = datetime.date(3000,1,1)
        self.wb_save_results = path_root  + '/../CheckTheseProjects/' + name + '/'+name+'.xlsx'
        
        self.ideal_ACF = pd.DataFrame()
        self.adjusted_ACF = pd.DataFrame()
        
        self.acf_structure_original = pd.DataFrame()
        self.dates_recycle_list_original = []
        self.acf_original = pd.DataFrame()
        
        self.Have_Rearranged_ACF_Structure = False
    
    def calc_OriginalPool_ACF(self,BackMonth):
        
        logger.info('calc_OriginalPool_ACF_Structure....')
        self.asset_pool['first_due_period_O'] = (pd.to_datetime(self.asset_pool['first_due_date_after_pool_cut']).dt.year - self.date_pool_cut.year) * 12 + \
                                              pd.to_datetime(self.asset_pool['first_due_date_after_pool_cut']).dt.month- self.date_pool_cut.month - BackMonth
        last_term = int((self.asset_pool['Term_Remain'] + self.asset_pool['first_due_period_O']).max())
        self.dates_recycle_list_original= [get_next_eom(self.date_pool_cut,i) for i in range(last_term)]
        logger.info('gen_ACF_Structure for original ACF....')
        
        self.acf_structure_original = self.gen_ACF_Structure('first_due_period_O')
                
        for d_r in self.dates_recycle_list_original:
            self.acf_structure_original[d_r] = 0
        logger.info('Original_ACF_Structure save_to_excel....')                 
        save_to_excel(self.acf_structure_original,'Original_ACF_Structure',self.wb_save_results)
        logger.info('cash_flow_collection....')    
        self.acf_original = cash_flow_collection(self.acf_structure_original,self.dates_recycle_list_original,'first_due_period_O','Original',self.wb_save_results)
        
        return self.acf_original
    
    def calc_OverdueRecycle(self,OutstandingPrincipal,PayTerm):
        acf_structure = self.acf_structure_original
        dates_recycle_list = self.dates_recycle_list_original
        acf_structure['本金余额（元）'] = OutstandingPrincipal * acf_structure['OutstandingPrincipal_Proportion']
        acf_original = cash_flow_collection(acf_structure,dates_recycle_list,'first_due_period_O','Original',self.wb_save_results)
        
        return acf_original['amount_principal'][PayTerm -1]
    
    
    def get_IdealCashFlow(self):
    
        ICFPath = self.path_project + '/IdealCashFlow.csv'
        try:
                ICF = pd.read_csv(ICFPath,encoding = 'utf-8') 
        except:
                ICF = pd.read_csv(ICFPath,encoding = 'gbk') 
        
        self.ideal_ACF = IACF

    def calc_Rearrange_ACF_Structure(self):
    
        logger.info('calc_Rearrange_ACF_Structure')
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
        
        save_to_excel(self.gen_ACF_Structure('first_due_period_R'),'Rearrange_ACF_Structure',self.wb_save_results)
        
        self.acf_structure_original = self.gen_ACF_Structure('first_due_period_R')
        return self.acf_structure_original
        
    def gen_ACF_Structure(self,first_due_period_value):
        self.asset_pool['SERVICE_FEE_RATE'] = self.asset_pool['SERVICE_FEE_RATE'].where(self.asset_pool['SERVICE_FEE_RATE'] > 0,0)        
        #df['Interest_Rate'] = df['Interest_Rate']/100        
        acf_structure = self.asset_pool.groupby([first_due_period_value,'Interest_Rate','SERVICE_FEE_RATE','Term_Remain'])\
                                 .agg({'Amount_Outstanding_yuan':'sum'})\
                                 .reset_index()\
                                 .rename(columns = {'Amount_Outstanding_yuan':'本金余额（元）'}
                                 )
                                 
        acf_structure['Total_Fee_Rate'] = acf_structure['Interest_Rate'] + acf_structure['SERVICE_FEE_RATE']*12
        acf_structure['Interest_Rate_Proportion'] = acf_structure['Interest_Rate'] / acf_structure['Total_Fee_Rate']
        acf_structure['OutstandingPrincipal_Proportion'] = acf_structure['本金余额（元）'] / acf_structure['本金余额（元）'].sum()
    
        return acf_structure
    
    