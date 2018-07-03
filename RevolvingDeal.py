# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 21:18:06 2018

@author: Jonah.Chen
"""

import sys
import os
from copy import deepcopy
from constant import *
import pandas as pd
import numpy as np
from abs_util.util_general import *
from abs_util.util_cf import *
from abs_util.util_sr import *
from dateutil.relativedelta import relativedelta
import datetime
from Deal import Deal
from AssetPool import AssetPool
from AssetsCashFlow import AssetsCashFlow
from APCF_adjuster import APCF_adjuster

low_memory=False

logger = get_logger(__name__)

class RevolvingDeal(Deal):
    
    def __init__(self,name,AP,date_revolving_pools_cut,date_trust_effective,recycle_adjust_factor,scenarios):
        super().__init__(name,AP,date_trust_effective,recycle_adjust_factor,scenarios)
        
        self.RevolvingDeal = True
        self.apcf_adjusted = {}
        
        self.date_revolving_pools_cut = date_revolving_pools_cut
        
        self.apcf_structure_revolving = pd.DataFrame()
        self.apcf_revolving = {}
        
        self.apcf_revolving_adjusted = {}
        self.apcf_revolving_adjusted_all = {}
        
        self.total_purchase_amount = 0
        
        self.RevolvingPool_PurchaseAmount = {}
        
    def get_rAssetPool(self):
        
        self.get_AssetPool()
        
    
    def get_revolving_APCF_structure(self):
        self.apcf_structure_revolving = self.get_rearranged_APCF_structure()
        #save_to_excel(self.apcf_structure_revolving,'Rearrange_APCF_Structure',wb_name)
    
    def forcast_Revolving_APCF(self):
        
        for which_revolving_pool in range(1,len(self.date_revolving_pools_cut) + 1):
            
            apcf_structure_revolving = deepcopy(self.apcf_structure_revolving)
            
            purchase_amount = self.prepare_PurchaseAmount(which_revolving_pool)
            self.RevolvingPool_PurchaseAmount[which_revolving_pool] = purchase_amount
            self.total_purchase_amount += purchase_amount
            
            #logger.info('purchase_amount for {0} is :{1}'.format(purchase_amount,which_revolving_pool))
            #logger.info('Total purchase_amount is {0}'.format(self.total_purchase_amount))

            apcf_structure_revolving['OutstandingPrincipal'] = purchase_amount * apcf_structure_revolving['OutstandingPrincipal_Proportion']
        
            last_term = int((apcf_structure_revolving['Term_Remain'] + apcf_structure_revolving['first_due_period_R']).max())
            dates_recycle_list_revolving = [self.date_revolving_pools_cut[which_revolving_pool-1] + relativedelta(months=i) - datetime.timedelta(days=1) for i in range(1,last_term+1)]
            
            #logger.info('self.dates_recycle_list_revolving[0] is {0}'.format(dates_recycle_list_revolving[0]))
            
            for d_r in dates_recycle_list_revolving:
                apcf_structure_revolving[d_r] = 0
       
            #save_to_excel(apcf_structure_revolving,'Revolving_APCF_Structure_' + str(which_revolving_pool),wb_name)
        
            self.apcf_revolving[which_revolving_pool] = cash_flow_collection(apcf_structure_revolving,dates_recycle_list_revolving,'first_due_period_R','Revolving'+str(which_revolving_pool),wb_name)
            
            #save_to_excel(self.apcf_revolving[which_revolving_pool],'Revolving_APCF_' + str(which_revolving_pool),wb_name)
            
            

    def prepare_PurchaseAmount(self,for_which_revolving_pool):
        
        if for_which_revolving_pool == 1:
            amount_principal = self.apcf_original[pd.to_datetime(self.apcf_original['date_recycle']) <= get_next_eom(self.date_trust_effective,0)]['amount_principal'].sum()
            amount_interest = self.apcf_original[pd.to_datetime(self.apcf_original['date_recycle']) <= get_next_eom(self.date_trust_effective,0)]['amount_interest'].sum()
            return amount_principal + amount_interest
        
        else:
            amount_principal_original = self.apcf_original[pd.to_datetime(self.apcf_original['date_recycle']) == self.date_revolving_pools_cut[for_which_revolving_pool-1] - datetime.timedelta(days=1) ]['amount_principal'].sum()
            amount_interest_original = self.apcf_original[pd.to_datetime(self.apcf_original['date_recycle']) == self.date_revolving_pools_cut[for_which_revolving_pool-1] - datetime.timedelta(days=1) ]['amount_interest'].sum()
            
            amount_principal_previous_r = 0
            amount_interest_previous_r = 0
            for previous_r in range(1,for_which_revolving_pool):
                amount_principal_previous_r_this = self.apcf_revolving[previous_r][pd.to_datetime(self.apcf_revolving[previous_r]['date_recycle']) == self.date_revolving_pools_cut[for_which_revolving_pool-1] - datetime.timedelta(days=1) ]['amount_principal'].sum()
                
                #logger.info('amount_principal_previous_r of {0} is {1}'.format(previous_r,amount_principal_previous_r_this ))
                amount_principal_previous_r += amount_principal_previous_r_this
                amount_interest_previous_r_this = self.apcf_revolving[previous_r][pd.to_datetime(self.apcf_revolving[previous_r]['date_recycle']) == self.date_revolving_pools_cut[for_which_revolving_pool-1] - datetime.timedelta(days=1) ]['amount_interest'].sum()
                
                #logger.info('amount_interest_previous_r_this of {0} is {1}'.format(previous_r,amount_interest_previous_r_this ))
                amount_interest_previous_r += amount_interest_previous_r_this
            
            return amount_principal_original + amount_interest_original + \
                   amount_principal_previous_r + amount_interest_previous_r
        
        
    def adjust_rAPCF(self):
        logger.info('adjust_rAPCF...')  
        
        self.adjust_APCF()
        
        for scenario_id in self.scenarios.keys():
            logger.info('scenario_id is {0}'.format(scenario_id))
            
            self.apcf_revolving_adjusted[scenario_id] = {}
            self.apcf_revolving_adjusted_all[scenario_id] = pd.DataFrame()
            
            for which_revolving_pool in range(1,len(self.date_revolving_pools_cut) + 1):
                APCFa = APCF_adjuster(self.apcf_revolving[which_revolving_pool],self.recycle_adjust_factor,self.scenarios,scenario_id)
                this_adjusted = deepcopy(APCFa.adjust_APCF())
                this_adjusted = this_adjusted.rename(columns = {'amount_recycle_principal':'amount_recycle_principal'+'_R' + str(which_revolving_pool),
                                                                'amount_recycle_interest':'amount_recycle_interest'+'_R' + str(which_revolving_pool),
                                                                'amount_total_outstanding_principal':'amount_total_outstanding_principal'+'_R' + str(which_revolving_pool)
                                                                })
                self.apcf_revolving_adjusted[scenario_id][which_revolving_pool] = this_adjusted
                #save_to_excel(self.apcf_revolving_adjusted[scenario_id][which_revolving_pool],scenario_id+'_'+str(which_revolving_pool),wb_name)
                
                if self.apcf_revolving_adjusted_all[scenario_id].empty :
                    self.apcf_revolving_adjusted_all[scenario_id] = self.apcf_revolving_adjusted[scenario_id][which_revolving_pool]
                else: 
                    self.apcf_revolving_adjusted_all[scenario_id] = self.apcf_revolving_adjusted_all[scenario_id].merge(self.apcf_revolving_adjusted[scenario_id][which_revolving_pool],left_on = 'date_recycle',right_on = 'date_recycle', how = 'outer')
            
            self.apcf_revolving_adjusted_all[scenario_id]['amount_recycle_principal_R'] = 0
            self.apcf_revolving_adjusted_all[scenario_id]['amount_recycle_interest_R'] = 0
            self.apcf_revolving_adjusted_all[scenario_id]['amount_total_outstanding_principal_R'] = 0
            
            for fee_name in list(self.apcf_revolving_adjusted_all[scenario_id]):
                if 'amount_recycle_principal_R' in fee_name :
                    self.apcf_revolving_adjusted_all[scenario_id][fee_name] = self.apcf_revolving_adjusted_all[scenario_id][fee_name].where(self.apcf_revolving_adjusted_all[scenario_id][fee_name]>0,0)
                    self.apcf_revolving_adjusted_all[scenario_id]['amount_recycle_principal_R'] += self.apcf_revolving_adjusted_all[scenario_id][fee_name]
                elif 'amount_recycle_interest_R' in fee_name :
                    self.apcf_revolving_adjusted_all[scenario_id][fee_name] = self.apcf_revolving_adjusted_all[scenario_id][fee_name].where(self.apcf_revolving_adjusted_all[scenario_id][fee_name]>0,0)
                    self.apcf_revolving_adjusted_all[scenario_id]['amount_recycle_interest_R'] += self.apcf_revolving_adjusted_all[scenario_id][fee_name]
                elif 'amount_total_outstanding_principal_R' in fee_name:
                    self.apcf_revolving_adjusted_all[scenario_id][fee_name] = self.apcf_revolving_adjusted_all[scenario_id][fee_name].where(self.apcf_revolving_adjusted_all[scenario_id][fee_name]>0,0)
                    self.apcf_revolving_adjusted_all[scenario_id]['amount_total_outstanding_principal_R'] +=  self.apcf_revolving_adjusted_all[scenario_id][fee_name]
            
            self.apcf_revolving_adjusted_all[scenario_id] = self.apcf_revolving_adjusted_all[scenario_id][['date_recycle','amount_recycle_principal_R','amount_recycle_interest_R','amount_total_outstanding_principal_R']]
            
            self.apcf_original_adjusted[scenario_id] = self.apcf_original_adjusted[scenario_id].rename(columns = {'amount_recycle_principal':'amount_recycle_principal'+'_O',
                                                                                                                   'amount_recycle_interest':'amount_recycle_interest'+'_O',
                                                                                                                   'amount_total_outstanding_principal':'amount_total_outstanding_principal'+'_O'
                                                                                                                   })
            
            self.apcf_adjusted[scenario_id] = self.apcf_original_adjusted[scenario_id].merge(self.apcf_revolving_adjusted_all[scenario_id],left_on = 'date_recycle',right_on = 'date_recycle', how = 'outer')
            
            self.apcf_adjusted[scenario_id]['amount_recycle_principal'] = 0
            self.apcf_adjusted[scenario_id]['amount_recycle_interest'] = 0
            self.apcf_adjusted[scenario_id]['amount_total_outstanding_principal'] = 0
            for fee_name in list(self.apcf_adjusted[scenario_id]):
                if 'amount_recycle_principal_' in fee_name :
                    self.apcf_adjusted[scenario_id][fee_name] = self.apcf_adjusted[scenario_id][fee_name].where(self.apcf_adjusted[scenario_id][fee_name]>0,0)
                    self.apcf_adjusted[scenario_id]['amount_recycle_principal'] += self.apcf_adjusted[scenario_id][fee_name]
                elif 'amount_recycle_interest_' in fee_name :
                    self.apcf_adjusted[scenario_id][fee_name] = self.apcf_adjusted[scenario_id][fee_name].where(self.apcf_adjusted[scenario_id][fee_name]>0,0)
                    self.apcf_adjusted[scenario_id]['amount_recycle_interest'] += self.apcf_adjusted[scenario_id][fee_name]
                elif 'amount_total_outstanding_principal_' in fee_name:
                    self.apcf_adjusted[scenario_id][fee_name] = self.apcf_adjusted[scenario_id][fee_name].where(self.apcf_adjusted[scenario_id][fee_name]>0,0)
                    self.apcf_adjusted[scenario_id]['amount_total_outstanding_principal'] +=  self.apcf_adjusted[scenario_id][fee_name]
            
            
            save_to_excel(self.apcf_revolving_adjusted_all[scenario_id],'r_adjusted' + scenario_id,wb_name)      
            save_to_excel(self.apcf_original_adjusted[scenario_id],'o_adjusted' + scenario_id,wb_name) 
            save_to_excel(self.apcf_adjusted[scenario_id],'cf_adjusted' + scenario_id,wb_name)
                 
            
            
            