# -*- coding: utf-8 -*-
"""
Created on Mon Jun 18 19:57:55 2018

@author: Jonah.Chen
"""
import sys
import os
from constant import *
from copy import deepcopy
from Params import *
import pandas as pd
import numpy as np
from abs_util.util_general import *
from abs_util.util_cf import *
from dateutil.relativedelta import relativedelta
import datetime
from scipy.stats import bernoulli

logger = get_logger(__name__)

class APCF_adjuster():
    
    def __init__(self,apcf,scenario,scenario_id,df_ppmt,df_ipmt):
        
        self.apcf = apcf
        self.df_ppmt = df_ppmt
        self.df_ipmt = df_ipmt
        self.scenario_id = scenario_id
        self.main_params = scenarios[scenario_id]      
    
    def adjust_APCF(self,OoR,dates_recycle_list):
        
        df_ppmt = deepcopy(self.df_ppmt)
        df_ipmt = deepcopy(self.df_ipmt)
        
        APCF_adjusted_dict = {}
        
        amount_principal_overdue_1_30_currentTerm = {}
        amount_interest_overdue_1_30_currentTerm = {}        
        amount_principal_overdue_31_60_currentTerm = {}
        amount_interest_overdue_31_60_currentTerm = {}    
        amount_principal_overdue_61_90_currentTerm = {}
        amount_interest_overdue_61_90_currentTerm = {}    
        amount_principal_loss_currentTerm = {}
        amount_interest_loss_currentTerm = {}
        
        amount_principal_overdue_1_30_allTerm = {}
        amount_interest_overdue_1_30_allTerm = {} 
        amount_principal_overdue_31_60_allTerm = {}
        amount_interest_overdue_31_60_allTerm = {}    
        amount_principal_overdue_61_90_allTerm = {}
        amount_interest_overdue_61_90_allTerm = {}  
        amount_principal_loss_allTerm = {}
        amount_interest_loss_allTerm = {}
        
        amount_principal_overdue_31_60_currentTerm_helper = {}
        amount_interest_overdue_31_60_currentTerm_helper = {}
        amount_principal_overdue_61_90_currentTerm_helper = {}
        amount_interest_overdue_61_90_currentTerm_helper = {}
        amount_principal_loss_currentTerm_helper = {}
        amount_interest_loss_currentTerm_helper = {}

        for date_r_index,date_r in enumerate(dates_recycle_list):
            amount_principal_overdue_31_60_currentTerm_helper[date_r] = 0
            amount_interest_overdue_31_60_currentTerm_helper[date_r] = 0
            amount_principal_overdue_61_90_currentTerm_helper[date_r] = 0
            amount_interest_overdue_61_90_currentTerm_helper[date_r] = 0
            amount_principal_loss_currentTerm_helper[date_r] = 0
            amount_interest_loss_currentTerm_helper[date_r] = 0
        
        APCF_ppmt_1,APCF_ipmt_1 = df_ppmt,df_ipmt                
        
        for date_r_index,date_r in enumerate(dates_recycle_list):
            #logger.info('Adjusting for date_r {0}'.format(date_r))
            
            APCF_ppmt_1,APCF_ipmt_1,APCF_ppmt_0,APCF_ipmt_0 = self.prepare_APCF_Account(APCF_ppmt_1,APCF_ipmt_1,OoR,dates_recycle_list,date_r_index)
            
#            try:APCF_ppmt_1,APCF_ipmt_1,APCF_ppmt_0,APCF_ipmt_0 = self.prepare_APCF_Account(APCF_ppmt_1,APCF_ipmt_1,OoR,dates_recycle_list,date_r_index)
#            except(ValueError): 
#                logger.info('Adjusting for date_r {0}'.format(date_r))
#                sys.exit("!!!!!!!!!    Wrong number of items passed 0, placement implies 1     !!!!!!!")
                
                
            amount_principal_overdue_1_30_currentTerm[date_r] = APCF_ppmt_0[date_r].sum()
            amount_interest_overdue_1_30_currentTerm[date_r] = APCF_ipmt_0[date_r].sum()
            
#            amount_principal_overdue_31_60_currentTerm[date_r] =  amount_principal_loss_currentTerm_helper[dates_recycle_list[date_r_index]]
#            amount_interest_overdue_31_60_currentTerm[date_r] = amount_interest_loss_currentTerm_helper[dates_recycle_list[date_r_index]]
#            amount_principal_overdue_61_90_currentTerm[date_r] = 0 if date_r_index <= 1 else amount_principal_loss_currentTerm_helper[dates_recycle_list[date_r_index-1]]
#            amount_interest_overdue_61_90_currentTerm[date_r] = 0 if date_r_index <= 1 else amount_interest_loss_currentTerm_helper[dates_recycle_list[date_r_index-1]]
#            amount_principal_loss_currentTerm[date_r] = 0 if date_r_index <= 2 else sum(amount_principal_loss_currentTerm_helper[k] for k in dates_recycle_list[0:date_r_index-1])
#            amount_interest_loss_currentTerm[date_r] = 0 if date_r_index <= 2 else sum(amount_interest_loss_currentTerm_helper[k] for k in dates_recycle_list[0:date_r_index-1])
#            
            amount_principal_overdue_31_60_currentTerm[date_r] = sum(amount_principal_overdue_31_60_currentTerm_helper[k] for k in dates_recycle_list[date_r_index-1:date_r_index+1])
            amount_interest_overdue_31_60_currentTerm[date_r] = sum(amount_interest_overdue_31_60_currentTerm_helper[k] for k in dates_recycle_list[date_r_index-1:date_r_index+1])
            amount_principal_overdue_61_90_currentTerm[date_r] = amount_principal_overdue_61_90_currentTerm_helper[date_r]
            amount_interest_overdue_61_90_currentTerm[date_r] = amount_interest_overdue_61_90_currentTerm_helper[date_r]
            amount_principal_loss_currentTerm[date_r] =  sum(amount_principal_loss_currentTerm_helper[k] for k in dates_recycle_list[0:date_r_index+1]) \
                                                        -amount_principal_overdue_31_60_currentTerm[date_r]\
                                                        -amount_principal_overdue_61_90_currentTerm[date_r]
            amount_interest_loss_currentTerm[date_r] = sum(amount_interest_loss_currentTerm_helper[k] for k in dates_recycle_list[0:date_r_index+1]) \
                                                        -amount_interest_overdue_31_60_currentTerm[date_r]\
                                                        -amount_interest_overdue_61_90_currentTerm[date_r]

            if date_r_index < len(dates_recycle_list)-1:
                amount_principal_overdue_61_90_currentTerm_helper[dates_recycle_list[date_r_index+1]] = 0 if date_r_index==0 else sum(amount_principal_overdue_31_60_currentTerm_helper[k] for k in dates_recycle_list[date_r_index-1:date_r_index+2])
                amount_interest_overdue_61_90_currentTerm_helper[dates_recycle_list[date_r_index+1]] = 0 if date_r_index==0 else sum(amount_interest_overdue_31_60_currentTerm_helper[k] for k in dates_recycle_list[date_r_index-1:date_r_index+2])
            
            for overdue_date in dates_recycle_list[date_r_index:]:
                amount_principal_overdue_31_60_currentTerm_helper[overdue_date] = APCF_ppmt_0[overdue_date].sum()
                amount_interest_overdue_31_60_currentTerm_helper[overdue_date] = APCF_ipmt_0[overdue_date].sum()
                amount_principal_loss_currentTerm_helper[overdue_date] += APCF_ppmt_0[overdue_date].sum()
                amount_interest_loss_currentTerm_helper[overdue_date] += APCF_ipmt_0[overdue_date].sum()
                
            amount_principal_overdue_1_30_allTerm[date_r] = sum(APCF_ppmt_0[dates_recycle_list[date_r_index:]].sum())
            amount_interest_overdue_1_30_allTerm[date_r] = sum(APCF_ipmt_0[dates_recycle_list[date_r_index:]].sum())
            
            amount_principal_overdue_31_60_allTerm[date_r] = 0 if date_r_index == 0 else amount_principal_overdue_1_30_allTerm[dates_recycle_list[date_r_index-1]]
            amount_interest_overdue_31_60_allTerm[date_r] = 0 if date_r_index == 0 else amount_interest_overdue_1_30_allTerm[dates_recycle_list[date_r_index-1]]
            amount_principal_overdue_61_90_allTerm[date_r] = 0 if date_r_index <= 1 else amount_principal_overdue_31_60_allTerm[dates_recycle_list[date_r_index-1]]
            amount_interest_overdue_61_90_allTerm[date_r] = 0 if date_r_index <= 1 else amount_interest_overdue_31_60_allTerm[dates_recycle_list[date_r_index-1]]
            amount_principal_loss_allTerm[date_r] = sum([amount_principal_overdue_61_90_allTerm[k] for k in dates_recycle_list[0:date_r_index]])
            amount_interest_loss_allTerm[date_r] = sum([amount_interest_overdue_61_90_allTerm[k] for k in dates_recycle_list[0:date_r_index]])
            
#            amount_principal_overdue_31_60_allTerm[date_r] = 0
#            amount_interest_overdue_31_60_allTerm[date_r] = 0
#            amount_principal_overdue_61_90_allTerm[date_r] = 0
#            amount_interest_overdue_61_90_allTerm[date_r] = 0
#            amount_principal_loss_allTerm[date_r] = 0 if date_r_index==0 else sum([amount_principal_overdue_1_30_allTerm[k] for k in dates_recycle_list[0:date_r_index]])
#            amount_interest_loss_allTerm[date_r] = 0 if date_r_index==0 else sum([amount_interest_overdue_1_30_allTerm[k] for k in dates_recycle_list[0:date_r_index]])

            #logger.info('Generating APCF_adjusted_dict for date_r {0} '.format(date_r))
            APCF_adjusted_dict[date_r] = [APCF_ppmt_1[date_r].sum(),
                                          APCF_ipmt_1[date_r].sum(),
                                          amount_principal_overdue_1_30_currentTerm[date_r],
                                          amount_interest_overdue_1_30_currentTerm[date_r],  
                                          amount_principal_overdue_31_60_currentTerm[date_r],
                                          amount_interest_overdue_31_60_currentTerm[date_r],
                                          amount_principal_overdue_61_90_currentTerm[date_r],
                                          amount_interest_overdue_61_90_currentTerm[date_r],
                                          amount_principal_loss_currentTerm[date_r],
                                          amount_interest_loss_currentTerm[date_r],
                                          amount_principal_overdue_1_30_allTerm[date_r],
                                          amount_interest_overdue_1_30_allTerm[date_r],
                                          amount_principal_overdue_31_60_allTerm[date_r],
                                          amount_interest_overdue_31_60_allTerm[date_r],
                                          amount_principal_overdue_61_90_allTerm[date_r],
                                          amount_interest_overdue_61_90_allTerm[date_r],
                                          amount_principal_loss_allTerm[date_r],
                                          amount_interest_loss_allTerm[date_r]
                                          ]
        
        #logger.info('Saving APCF_adjusted_structure for scenario {0}: '.format(self.scenario_id))
        #save_to_excel(APCF_adjusted_structure,'APCF_adjusted_structure_simulation',wb_name)
        
        #logger.info('Generating APCF_adjusted...' )
        df_total_by_date = pd.DataFrame(APCF_adjusted_dict)
        APCF_adjusted = pd.DataFrame({'date_recycle': dates_recycle_list,
                                         'amount_principal': df_total_by_date.transpose()[0],
                                         'amount_interest': df_total_by_date.transpose()[1],
                                         'amount_principal_overdue_1_30_currentTerm': df_total_by_date.transpose()[2],
                                         'amount_interest_overdue_1_30_currentTerm': df_total_by_date.transpose()[3],
                                         'amount_principal_overdue_31_60_currentTerm': df_total_by_date.transpose()[4],
                                         'amount_interest_overdue_31_60_currentTerm': df_total_by_date.transpose()[5],
                                         'amount_principal_overdue_61_90_currentTerm': df_total_by_date.transpose()[6],
                                         'amount_interest_overdue_61_90_currentTerm': df_total_by_date.transpose()[7],
                                         'amount_principal_loss_currentTerm': df_total_by_date.transpose()[8],
                                         'amount_interest_loss_currentTerm': df_total_by_date.transpose()[9],
                                         'amount_principal_overdue_1_30_allTerm': df_total_by_date.transpose()[10],
                                         'amount_interest_overdue_1_30_allTerm': df_total_by_date.transpose()[11],
                                         'amount_principal_overdue_31_60_allTerm': df_total_by_date.transpose()[12],
                                         'amount_interest_overdue_31_60_allTerm': df_total_by_date.transpose()[13],
                                         'amount_principal_overdue_61_90_allTerm': df_total_by_date.transpose()[14],
                                         'amount_interest_overdue_61_90_allTerm': df_total_by_date.transpose()[15],
                                         'amount_principal_loss_allTerm': df_total_by_date.transpose()[16],
                                         'amount_interest_loss_allTerm': df_total_by_date.transpose()[17],
                                         'amount_total': df_total_by_date.transpose()[0] + df_total_by_date.transpose()[1]
                                         })
        
        #logger.info('Saving adjusted new APCF for scenario {0}: '.format(self.scenario_id))
        if OoR == 'R':pass
        else:save_to_excel(APCF_adjusted,'cf_'+OoR+'_adjusted_simulation'+Batch_ID,wb_name)
        
        TOTAL_Principal = APCF_adjusted['amount_principal'].sum()
        APCF_adjusted['amount_total_outstanding_principal'] = TOTAL_Principal - APCF_adjusted['amount_principal'].cumsum()        
        APCF_adjusted = APCF_adjusted.rename(columns = {'amount_principal':'amount_recycle_principal','amount_interest':'amount_recycle_interest',
                                                        'amount_principal_loss':'amount_recycle_principal_loss','amount_interest_loss':'amount_recycle_interest_loss'
                                                        })
        
        return APCF_adjusted[['date_recycle',
                              'amount_recycle_principal','amount_recycle_interest','amount_total_outstanding_principal',
                              'amount_principal_overdue_1_30_currentTerm','amount_interest_overdue_1_30_currentTerm',
                              'amount_principal_overdue_31_60_currentTerm','amount_interest_overdue_31_60_currentTerm',
                              'amount_principal_overdue_61_90_currentTerm','amount_interest_overdue_61_90_currentTerm',
                              'amount_principal_loss_currentTerm','amount_interest_loss_currentTerm',
                              'amount_principal_overdue_1_30_allTerm','amount_interest_overdue_1_30_allTerm',
                              'amount_principal_overdue_31_60_allTerm','amount_interest_overdue_31_60_allTerm',
                              'amount_principal_overdue_61_90_allTerm','amount_interest_overdue_61_90_allTerm',
                              'amount_principal_loss_allTerm','amount_interest_loss_allTerm'
                              ]]
        
    def prepare_APCF_Account(self,ppmt,ipmt,OoR,dates_recycle_list,date_r_index):
        
        main_params = self.main_params 
        first_due_period = 'first_due_period_'+OoR
        
        ppmt['Overdue_Flag_'+str(date_r_index)] = pd.DataFrame(list(bernoulli.rvs(size=len(ppmt.index),p= (1-main_params['rate_overdue']) ))) 
        ######TODO: Find out WHY  Null happens ########
        ppmt['Overdue_Flag_'+str(date_r_index)] = ppmt['Overdue_Flag_'+str(date_r_index)].where(~ppmt['Overdue_Flag_'+str(date_r_index)].isnull(),0)
        ppmt['Overdue_Flag_'+str(date_r_index)] = ppmt['Overdue_Flag_'+str(date_r_index)].where(ppmt[first_due_period] <= date_r_index,1)
        ipmt['Overdue_Flag_'+str(date_r_index)] = ppmt['Overdue_Flag_'+str(date_r_index)]
        
        ppmt_1 = deepcopy(ppmt[ppmt['Overdue_Flag_'+str(date_r_index)]==1])
        ipmt_1 = deepcopy(ipmt[ipmt['Overdue_Flag_'+str(date_r_index)]==1])
        
        ppmt_0 = deepcopy(ppmt[ppmt['Overdue_Flag_'+str(date_r_index)]==0])
        ipmt_0 = deepcopy(ipmt[ipmt['Overdue_Flag_'+str(date_r_index)]==0])
        
        return ppmt_1,ipmt_1,ppmt_0,ipmt_0