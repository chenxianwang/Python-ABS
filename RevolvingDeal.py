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
from Accounts.AssetPoolAccount import AssetPoolAccount

low_memory=False

logger = get_logger(__name__)

class RevolvingDeal(Deal):
    
    def __init__(self,name,AP,date_revolving_pools_cut,date_trust_effective,recycle_adjust_factor,scenarios):
        super().__init__(name,AP,date_trust_effective,recycle_adjust_factor,scenarios)
        
        self.RevolvingDeal = True
        self.apcf_adjusted = {}  # Original_adjusted + Revolving_adjusted
        
        self.date_revolving_pools_cut = date_revolving_pools_cut
        
        self.apcf_structure_revolving = pd.DataFrame()
        self.apcf_revolving = {}
        
        self.apcf_revolving_adjusted = {}
        self.apcf_revolving_adjusted_all = {}
        
        self.total_purchase_amount = 0
        
        self.RevolvingPool_PurchaseAmount = {}
        
        for scenario_id in self.scenarios.keys():
            self.apcf_revolving_adjusted[scenario_id] = {}
            self.apcf_revolving_adjusted_all[scenario_id] = pd.DataFrame()
        
    def get_rAssetPool(self):
        
        self.get_AssetPool()
        
    
    def get_rAPCF_structure(self):
        self.apcf_structure_revolving = self.get_rearranged_APCF_structure()
        #save_to_excel(self.apcf_structure_revolving,'Rearrange_APCF_Structure',wb_name)
    
    def forcast_Revolving_APCF(self):
        for scenario_id in self.scenarios.keys():
            #logger.info('forcast_Revolving_APCF for scenario_id {0}...'.format(scenario_id))  
            for which_revolving_pool in range(1,len(self.date_revolving_pools_cut) + 1):
                
                apcf_structure_revolving = deepcopy(self.apcf_structure_revolving)
                
                purchase_amount = self.prepare_PurchaseAmount(which_revolving_pool,scenario_id)
                self.RevolvingPool_PurchaseAmount[which_revolving_pool] = purchase_amount
                self.total_purchase_amount += purchase_amount
                logger.info('purchase_amount for scenario_id {0} and Revolving pool {1} is :{2}'.format(scenario_id,which_revolving_pool,purchase_amount))
                #logger.info('Total purchase_amount is {0}'.format(self.total_purchase_amount))
                apcf_structure_revolving['OutstandingPrincipal'] = purchase_amount * apcf_structure_revolving['OutstandingPrincipal_Proportion']
                last_term = int((apcf_structure_revolving['Term_Remain'] + apcf_structure_revolving['first_due_period_R']).max())
                dates_recycle_list_revolving = [self.date_revolving_pools_cut[which_revolving_pool-1] + relativedelta(months=i) - datetime.timedelta(days=1) for i in range(1,last_term+1)]
                #logger.info('self.dates_recycle_list_revolving[0] is {0}'.format(dates_recycle_list_revolving[0]))
                for d_r in dates_recycle_list_revolving:
                    apcf_structure_revolving[d_r] = 0
                #save_to_excel(apcf_structure_revolving,'Revolving_APCF_Structure_' + str(which_revolving_pool),wb_name)
                self.apcf_revolving[which_revolving_pool] = cash_flow_collection(apcf_structure_revolving,dates_recycle_list_revolving,'first_due_period_R','Revolving'+str(which_revolving_pool),wb_name)
                #save_to_excel(self.apcf_revolving[which_revolving_pool],'rAPCF_' + scenario_id + str(which_revolving_pool),wb_name)
                self.adjust_rAPCF(which_revolving_pool,scenario_id)
                #save_to_excel(self.apcf_revolving_adjusted[scenario_id][which_revolving_pool],'rAPCFa_' + scenario_id + str(which_revolving_pool),wb_name)
                
                _AP_Acc = AssetPoolAccount(self.apcf_revolving_adjusted[scenario_id][which_revolving_pool])
                _principal_available = _AP_Acc.available_principal_to_pay()
                _AP_PAcc_pay = {}
                _AP_PAcc_buy = {}
                _AP_IAcc_pay = {}
                _AP_PAcc_pay[scenario_id] = _principal_available[0]
                _AP_PAcc_buy[scenario_id] = _principal_available[1]
                _AP_IAcc_pay[scenario_id] = _AP_Acc.available_interest_to_pay()
                
                for k in dates_recycle:
                    self.AP_PAcc_pay[scenario_id][k] += _AP_PAcc_pay[scenario_id][k]
                    self.AP_IAcc_pay[scenario_id][k] += _AP_IAcc_pay[scenario_id][k]
                
                if self.apcf_revolving_adjusted_all[scenario_id].empty :
                    self.apcf_revolving_adjusted_all[scenario_id] = self.apcf_revolving_adjusted[scenario_id][which_revolving_pool]
                else: 
                    self.apcf_revolving_adjusted_all[scenario_id] = self.apcf_revolving_adjusted_all[scenario_id].merge(self.apcf_revolving_adjusted[scenario_id][which_revolving_pool],left_on = 'date_recycle',right_on = 'date_recycle', how = 'outer')
        

    def prepare_PurchaseAmount(self,for_which_revolving_pool,scenario_id):
        amount_principal = self.AP_PAcc_pay[scenario_id][dates_recycle[for_which_revolving_pool - 1]]
        amount_interest = self.AP_IAcc_pay[scenario_id][dates_recycle[for_which_revolving_pool - 1]]
        
        self.AP_PAcc_pay[scenario_id][dates_recycle[for_which_revolving_pool - 1]] -= amount_principal
        self.AP_PAcc_buy[scenario_id][dates_recycle[for_which_revolving_pool - 1]] = amount_principal
        
        return amount_principal + amount_interest
        
        
    def adjust_rAPCF(self,which_revolving_pool,scenario_id):
        #logger.info('adjust_rAPCF for scenario_id {0} & revolving pool {1}...'.format(scenario_id,which_revolving_pool))  
        APCFa = APCF_adjuster(self.apcf_revolving[which_revolving_pool],self.recycle_adjust_factor,self.scenarios,scenario_id)
        this_adjusted = deepcopy(APCFa.adjust_APCF())
        self.apcf_revolving_adjusted[scenario_id][which_revolving_pool] = this_adjusted
        #save_to_excel(self.apcf_revolving_adjusted[scenario_id][which_revolving_pool],scenario_id+'_r'+str(which_revolving_pool)+'_a',wb_name)
