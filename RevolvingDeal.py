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
from AssetsCashFlow import AssetsCashFlow
from APCF_adjuster import APCF_adjuster
from Accounts.AssetPoolAccount import AssetPoolAccount

low_memory=False

logger = get_logger(__name__)

class RevolvingDeal(Deal):
    
    def __init__(self,name,PoolCutDate,AssetPoolName,date_revolving_pools_cut,date_trust_effective,recycle_adjust_factor,scenarios):
        super().__init__(name,PoolCutDate,AssetPoolName,date_trust_effective,recycle_adjust_factor,scenarios)
        
        self.RevolvingDeal = True
        self.RevolvingPool_PurchaseAmount = {}
        
        self.apcf_adjusted = {}  # Original_adjusted + Revolving_adjusted
        
        self.date_revolving_pools_cut = date_revolving_pools_cut
        
        self.apcf_structure_revolving = pd.DataFrame()
        self.apcf_revolving = {}
        
        self.apcf_revolving_adjusted = {}
        self.apcf_revolving_adjusted_all = {}
        self.RevolvingPool_PurchaseAmount = {}
        
        self.total_purchase_amount = 0
        
        for scenario_id in self.scenarios.keys():
            self.apcf_revolving_adjusted[scenario_id] = {}
            self.apcf_revolving_adjusted_all[scenario_id] = pd.DataFrame()
            self.RevolvingPool_PurchaseAmount[scenario_id] = {}
        
    def get_rAssetPool(self):
        
        self.get_AssetPool()
        
    
    def get_rAPCF_structure(self):
        self.apcf_structure_revolving = self.get_rearranged_APCF_structure()
        #save_to_excel(self.apcf_structure_revolving,'Rearrange_APCF_Structure',wb_name)
    
    def forcast_Revolving_APCF(self):
        for scenario_id in self.scenarios.keys():
            logger.info('forcast_Revolving_APCF for scenario_id {0}...'.format(scenario_id))  
            for which_revolving_pool in range(1,len(self.date_revolving_pools_cut) + 1):
                
                apcf_structure_revolving = deepcopy(self.apcf_structure_revolving)
                
                purchase_amount = self.prepare_PurchaseAmount(which_revolving_pool,scenario_id)
                self.RevolvingPool_PurchaseAmount[scenario_id][which_revolving_pool] = purchase_amount
                self.total_purchase_amount += purchase_amount
                #logger.info('purchase_amount for scenario_id {0} and Revolving pool {1} is :{2}'.format(scenario_id,which_revolving_pool,purchase_amount))
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
                _principal_available = _AP_Acc.available_principal()
                _AP_PAcc_total = {}
                _AP_PAcc_pay = {}
                _AP_PAcc_buy = {}
                _AP_PAcc_total[scenario_id] = _principal_available[0]                
                _AP_PAcc_pay[scenario_id] = _principal_available[1]
                _AP_PAcc_buy[scenario_id] = _principal_available[2]
                
                _interest_available = _AP_Acc.available_interest()
                _AP_IAcc_total = {}
                _AP_IAcc_pay = {}
                _AP_IAcc_buy = {}
                _AP_IAcc_total[scenario_id] = _interest_available[0]                
                _AP_IAcc_pay[scenario_id] = _interest_available[1]
                _AP_IAcc_buy[scenario_id] = _interest_available[2]
                
                #logger.info('_AP_PAcc_total[scenario_id][k] for date {0} is {1}'.format(datetime.date(2018,8,31),_AP_PAcc_total[scenario_id][datetime.date(2018,8,31)]))
                
                #TODO: Check why AP_PAcc_pay has all keys
                for k in dates_recycle:
                    self.AP_PAcc_total[scenario_id][k] += _AP_PAcc_total[scenario_id][k]
                    self.AP_PAcc_pay[scenario_id][k] += _AP_PAcc_pay[scenario_id][k]
                    self.AP_PAcc_buy[scenario_id][k] += _AP_PAcc_buy[scenario_id][k]
                    
                    self.AP_IAcc_total[scenario_id][k] += _AP_IAcc_total[scenario_id][k]
                    self.AP_IAcc_pay[scenario_id][k] += _AP_IAcc_pay[scenario_id][k]
                    self.AP_IAcc_buy[scenario_id][k] += _AP_IAcc_buy[scenario_id][k]

                #logger.info('self.AP_PAcc_total[scenario_id][k] for date {0} is {1}'.format(datetime.date(2018,8,31),self.AP_PAcc_total[scenario_id][datetime.date(2018,8,31)]))
                
                if self.apcf_revolving_adjusted_all[scenario_id].empty :
                    self.apcf_revolving_adjusted_all[scenario_id] = self.apcf_revolving_adjusted[scenario_id][which_revolving_pool]
                else: 
                    self.apcf_revolving_adjusted_all[scenario_id] = self.apcf_revolving_adjusted_all[scenario_id].merge(self.apcf_revolving_adjusted[scenario_id][which_revolving_pool],left_on = 'date_recycle',right_on = 'date_recycle', how = 'outer')
        

    def prepare_PurchaseAmount(self,for_which_revolving_pool,scenario_id):
        amount_principal = self.AP_PAcc_total[scenario_id][dates_recycle[for_which_revolving_pool - 1]]
        amount_interest = self.AP_IAcc_total[scenario_id][dates_recycle[for_which_revolving_pool - 1]]
        #logger.info('amount_interest for Revolving Pool {0} is {1}'.format(for_which_revolving_pool,amount_interest))
        
        amount_principal_reserve = 0
        amount_interest_reserve = 0  
        amount_interest_reserve += amount_interest * fees['tax']['rate']
        #logger.info('amount_interest_reserve for tax of Revolving Pool {0} is {1}'.format(for_which_revolving_pool,amount_interest_reserve))
        #logger.info('calc basis for Revolving Pool {0} is {1}'.format(for_which_revolving_pool,sum([self.AP_PAcc_total[scenario_id][k] for k in dates_recycle if dates_recycle.index(k) >= for_which_revolving_pool - 1])))
        for fee_name in ['trustee','trust_management','service']:
            amount_interest_reserve += self.reserve_for_fee(dates_pay[for_which_revolving_pool - 1],fee_name,
                                                            sum([self.AP_PAcc_total[scenario_id][k] for k in dates_recycle if dates_recycle.index(k) >= for_which_revolving_pool - 1])
                                                            )
        #logger.info('amount_interest_reserve for tax of Revolving Pool {0} is {1}'.format(for_which_revolving_pool,amount_interest_reserve))
        
        for fee_name in ['A','B']:
            amount_interest_reserve += self.reserve_for_fee(dates_pay[for_which_revolving_pool - 1],fee_name,Bonds[fee_name]['amount'])
        
        #logger.info('amount_interest_reserve for tax of Revolving Pool {0} is {1}'.format(for_which_revolving_pool,amount_interest_reserve))
        
        #logger.info('calc basis for Revolving Pool {0} is {1}'.format(for_which_revolving_pool,sum([self.AP_PAcc_total[scenario_id][k] for k in dates_recycle if dates_recycle.index(k) >= for_which_revolving_pool - 1])))
        
        self.AP_PAcc_pay[scenario_id][dates_recycle[for_which_revolving_pool - 1]] = amount_principal_reserve
        self.AP_PAcc_buy[scenario_id][dates_recycle[for_which_revolving_pool - 1]] = amount_principal - amount_principal_reserve
        
        self.AP_IAcc_pay[scenario_id][dates_recycle[for_which_revolving_pool - 1]] = amount_interest_reserve
        self.AP_IAcc_buy[scenario_id][dates_recycle[for_which_revolving_pool - 1]] = amount_interest - amount_interest_reserve
        
        return (amount_principal - amount_principal_reserve) + (amount_interest - amount_interest_reserve)
        
        
    def adjust_rAPCF(self,which_revolving_pool,scenario_id):
        #logger.info('adjust_rAPCF for scenario_id {0} & revolving pool {1}...'.format(scenario_id,which_revolving_pool))  
        APCFa = APCF_adjuster(self.apcf_revolving[which_revolving_pool],self.recycle_adjust_factor,self.scenarios,scenario_id)
        this_adjusted = deepcopy(APCFa.adjust_APCF())
        self.apcf_revolving_adjusted[scenario_id][which_revolving_pool] = deepcopy(this_adjusted)
        #save_to_excel(self.apcf_revolving_adjusted[scenario_id][which_revolving_pool],scenario_id+'_r'+str(which_revolving_pool)+'_a',wb_name)

    def reserve_for_fee(self,date_pay,fee_name,basis):
        
        if (fee_name == 'service') & (date_pay == dates_pay[0]):
            previous_date_pay = dt_param['dt_pool_cut']
        else:
            previous_date_pay = date_pay + relativedelta(months= -1)

        period_range = (date_pay - previous_date_pay).days
        amt_reserve = basis * fees[fee_name]['rate'] * period_range / days_in_a_year
        return  amt_reserve   