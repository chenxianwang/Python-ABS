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
    
    def __init__(self,apcf,scenario,scenario_id,df_ppmt,df_ipmt,dates_recycle_list):
        
        self.apcf = apcf
        self.df_ppmt = df_ppmt
        self.df_ipmt = df_ipmt
        self.scenario_id = scenario_id
        self.main_params = scenarios[scenario_id]   
        self.dates_recycle_list = dates_recycle_list
        
        self.APCF_adjusted_dict = {}
        
        self.amount_principal_overdue_1_30_currentTerm = {}
        self.amount_interest_overdue_1_30_currentTerm = {}        
        self.amount_principal_overdue_31_60_currentTerm = {}
        self.amount_interest_overdue_31_60_currentTerm = {}    
        self.amount_principal_overdue_61_90_currentTerm = {}
        self.amount_interest_overdue_61_90_currentTerm = {}    
        self.amount_principal_loss_currentTerm = {}
        self.amount_interest_loss_currentTerm = {}
        
        self.amount_principal_overdue_1_30_allTerm = {}
        self.amount_interest_overdue_1_30_allTerm = {} 
        self.amount_principal_overdue_31_60_allTerm = {}
        self.amount_interest_overdue_31_60_allTerm = {}    
        self.amount_principal_overdue_61_90_allTerm = {}
        self.amount_interest_overdue_61_90_allTerm = {}  
        self.amount_principal_loss_allTerm = {}
        self.amount_interest_loss_allTerm = {}
        
        self.amount_principal_overdue_31_60_currentTerm_helper = {}
        self.amount_interest_overdue_31_60_currentTerm_helper = {}
        self.amount_principal_overdue_31_60_allTerm_helper = {}
        self.amount_interest_overdue_31_60_allTerm_helper = {}
        
        self.amount_principal_overdue_61_90_currentTerm_helper = {}
        self.amount_interest_overdue_61_90_currentTerm_helper = {}
        self.amount_principal_loss_currentTerm_helper = {}
        self.amount_interest_loss_currentTerm_helper = {}
    
        for date_r_index,date_r in enumerate(self.dates_recycle_list):
            self.amount_principal_overdue_31_60_currentTerm_helper[date_r] = 0
            self.amount_interest_overdue_31_60_currentTerm_helper[date_r] = 0
            self.amount_principal_overdue_61_90_currentTerm_helper[date_r] = 0
            self.amount_interest_overdue_61_90_currentTerm_helper[date_r] = 0
            self.amount_principal_loss_currentTerm_helper[date_r] = 0
            self.amount_interest_loss_currentTerm_helper[date_r] = 0

    def adjust_APCF(self,OoR):
        
        df_ppmt = deepcopy(self.df_ppmt)
        df_ipmt = deepcopy(self.df_ipmt)
        dates_recycle_list = self.dates_recycle_list
        
        ppmt_M0,ipmt_M0 = df_ppmt,df_ipmt 
        
        ppmt_M1,ipmt_M1 = pd.DataFrame(),pd.DataFrame() 
        ppmt_M1_2_M0,ipmt_M1_2_M0 = pd.DataFrame(),pd.DataFrame() 
        ppmt_M1_2_M2,ipmt_M1_2_M2 = pd.DataFrame(),pd.DataFrame()                

        for date_r_index,date_r in enumerate(dates_recycle_list):
            #logger.info('Adjusting for date_r {0}'.format(date_r)) 
            if len(ppmt_M1_2_M0) > 0 :
                ppmt_M0 = ppmt_M0.append(ppmt_M1_2_M0,ignore_index=True)
                ipmt_M0 = ipmt_M0.append(ipmt_M1_2_M0,ignore_index=True)
            
            ppmt_M0,ipmt_M0,ppmt_M1,ipmt_M1 = self.transit_Status(ppmt_M0,ipmt_M0,OoR,date_r_index,'M0_2_M1')
            
            self.amount_principal_overdue_1_30_currentTerm[date_r] = ppmt_M1[date_r].sum()
            self.amount_interest_overdue_1_30_currentTerm[date_r] = ipmt_M1[date_r].sum()            
            self.amount_principal_overdue_1_30_allTerm[date_r] = sum(ppmt_M1[dates_recycle_list[date_r_index:]].sum())
            self.amount_interest_overdue_1_30_allTerm[date_r] = sum(ipmt_M1[dates_recycle_list[date_r_index:]].sum())
            
            self.amount_principal_overdue_31_60_currentTerm[date_r] = sum(self.amount_principal_overdue_31_60_currentTerm_helper[k] for k in dates_recycle_list[date_r_index-1:date_r_index+1])
            self.amount_interest_overdue_31_60_currentTerm[date_r] = sum(self.amount_interest_overdue_31_60_currentTerm_helper[k] for k in dates_recycle_list[date_r_index-1:date_r_index+1])
            self.amount_principal_overdue_61_90_currentTerm[date_r] = self.amount_principal_overdue_61_90_currentTerm_helper[date_r]
            self.amount_interest_overdue_61_90_currentTerm[date_r] = self.amount_interest_overdue_61_90_currentTerm_helper[date_r]
            self.amount_principal_loss_currentTerm[date_r] =  sum(self.amount_principal_loss_currentTerm_helper[k] for k in dates_recycle_list[0:date_r_index+1]) \
                                                        -self.amount_principal_overdue_31_60_currentTerm[date_r]\
                                                        -self.amount_principal_overdue_61_90_currentTerm[date_r]
            self.amount_interest_loss_currentTerm[date_r] = sum(self.amount_interest_loss_currentTerm_helper[k] for k in dates_recycle_list[0:date_r_index+1]) \
                                                        -self.amount_interest_overdue_31_60_currentTerm[date_r]\
                                                        -self.amount_interest_overdue_61_90_currentTerm[date_r]

            #Transition
            ppmt_M1_2_M0,ipmt_M1_2_M0,ppmt_M1_2_M2,ipmt_M1_2_M2 = self.transit_Status(ppmt_M1,ipmt_M1,OoR,date_r_index,'M1_2_M0M2')#self.M1_2_M0M2(ppmt_M1,ipmt_M1)
            #logger.info('len(ppmt_M1_2_M0) is {0} for {1}'.format(len(ppmt_M1_2_M0),date_r))
            if date_r_index < len(dates_recycle_list)-1:
                ppmt_M1_2_M0[dates_recycle_list[date_r_index+1]] += ppmt_M1_2_M0[dates_recycle_list[date_r_index]]
                ipmt_M1_2_M0[dates_recycle_list[date_r_index+1]] += ipmt_M1_2_M0[dates_recycle_list[date_r_index]]
#            
            #Without Transition
            #ppmt_M1_2_M0,ipmt_M1_2_M0,ppmt_M1_2_M2,ipmt_M1_2_M2 = self.M1_2_M0M2(ppmt_M1,ipmt_M1)
            
            if date_r_index < len(dates_recycle_list)-1:
                self.amount_principal_overdue_61_90_currentTerm_helper[dates_recycle_list[date_r_index+1]] = 0 if date_r_index==0 else sum(self.amount_principal_overdue_31_60_currentTerm_helper[k] for k in dates_recycle_list[date_r_index-1:date_r_index+2])
                self.amount_interest_overdue_61_90_currentTerm_helper[dates_recycle_list[date_r_index+1]] = 0 if date_r_index==0 else sum(self.amount_interest_overdue_31_60_currentTerm_helper[k] for k in dates_recycle_list[date_r_index-1:date_r_index+2])
            
            for overdue_date in dates_recycle_list[date_r_index:]:
                self.amount_principal_overdue_31_60_currentTerm_helper[overdue_date] = ppmt_M1_2_M2[overdue_date].sum()
                self.amount_interest_overdue_31_60_currentTerm_helper[overdue_date] = ipmt_M1_2_M2[overdue_date].sum()
                self.amount_principal_loss_currentTerm_helper[overdue_date] += ppmt_M1_2_M2[overdue_date].sum()
                self.amount_interest_loss_currentTerm_helper[overdue_date] += ipmt_M1_2_M2[overdue_date].sum()
                
            self.amount_principal_overdue_31_60_allTerm_helper[date_r] = sum(ppmt_M1_2_M2[dates_recycle_list[date_r_index:]].sum())
            self.amount_interest_overdue_31_60_allTerm_helper[date_r] = sum(ipmt_M1_2_M2[dates_recycle_list[date_r_index:]].sum())            
            self.amount_principal_overdue_31_60_allTerm[date_r] = 0 if date_r_index == 0 else self.amount_principal_overdue_31_60_allTerm_helper[dates_recycle_list[date_r_index-1]]
            self.amount_interest_overdue_31_60_allTerm[date_r] = 0 if date_r_index == 0 else self.amount_interest_overdue_31_60_allTerm_helper[dates_recycle_list[date_r_index-1]]
            self.amount_principal_overdue_61_90_allTerm[date_r] = 0 if date_r_index <= 1 else self.amount_principal_overdue_31_60_allTerm[dates_recycle_list[date_r_index-1]]
            self.amount_interest_overdue_61_90_allTerm[date_r] = 0 if date_r_index <= 1 else self.amount_interest_overdue_31_60_allTerm[dates_recycle_list[date_r_index-1]]
            self.amount_principal_loss_allTerm[date_r] = sum([self.amount_principal_overdue_61_90_allTerm[k] for k in dates_recycle_list[0:date_r_index]])
            self.amount_interest_loss_allTerm[date_r] = sum([self.amount_interest_overdue_61_90_allTerm[k] for k in dates_recycle_list[0:date_r_index]])
            
            #logger.info('Generating APCF_adjusted_dict for date_r {0} '.format(date_r))
            self.APCF_adjusted_dict[date_r] = [ppmt_M0[date_r].sum(),
                                          ipmt_M0[date_r].sum(),
                                          self.amount_principal_overdue_1_30_currentTerm[date_r],
                                          self.amount_interest_overdue_1_30_currentTerm[date_r],  
                                          self.amount_principal_overdue_31_60_currentTerm[date_r],
                                          self.amount_interest_overdue_31_60_currentTerm[date_r],
                                          self.amount_principal_overdue_61_90_currentTerm[date_r],
                                          self.amount_interest_overdue_61_90_currentTerm[date_r],
                                          self.amount_principal_loss_currentTerm[date_r],
                                          self.amount_interest_loss_currentTerm[date_r],
                                          self.amount_principal_overdue_1_30_allTerm[date_r],
                                          self.amount_interest_overdue_1_30_allTerm[date_r],
                                          self.amount_principal_overdue_31_60_allTerm[date_r],
                                          self.amount_interest_overdue_31_60_allTerm[date_r],
                                          self.amount_principal_overdue_61_90_allTerm[date_r],
                                          self.amount_interest_overdue_61_90_allTerm[date_r],
                                          self.amount_principal_loss_allTerm[date_r],
                                          self.amount_interest_loss_allTerm[date_r]
                                          ]
        
        #logger.info('Saving APCF_adjusted_structure for scenario {0}: '.format(self.scenario_id))
        #save_to_excel(APCF_adjusted_structure,'APCF_adjusted_structure_simulation',wb_name)
        
        return self.gen_APCF_adjusted(OoR)
   
    def transit_Status(self,ppmt_this,ipmt_this,OoR,date_r_index,transition):
        
        main_params = self.main_params 
        first_due_period = 'first_due_period_'+OoR
        
        ppmt_this = ppmt_this.reset_index(drop=True)
        ipmt_this = ipmt_this.reset_index(drop=True)
        
        bernollio_list = deepcopy(list(bernoulli.rvs(size=len(ppmt_this),p= (1-main_params[transition]))))
        #logger.info('bernollio_list.count(0) is {0}, bernollio_list.count(1) is {1}, Equal_or Not: {2},{3}'.format(bernollio_list.count(0),bernollio_list.count(1),len(bernollio_list)==bernollio_list.count(0)+bernollio_list.count(1),len(bernollio_list)==len(ppmt_this)))
        
        bernollio_col = pd.DataFrame(bernollio_list,columns=['bernollio_col'])            
        ppmt_this['Overdue_Flag_'+str(date_r_index)] = bernollio_col['bernollio_col']
           
        ppmt_this['Overdue_Flag_'+str(date_r_index)] = ppmt_this['Overdue_Flag_'+str(date_r_index)].where(ppmt_this[first_due_period] <= date_r_index,1)
        ipmt_this['Overdue_Flag_'+str(date_r_index)] = ppmt_this['Overdue_Flag_'+str(date_r_index)]
        
        ppmt_pre = ppmt_this[ppmt_this['Overdue_Flag_'+str(date_r_index)]==1]
        ipmt_pre = ipmt_this[ipmt_this['Overdue_Flag_'+str(date_r_index)]==1]
        ppmt_next = ppmt_this[ppmt_this['Overdue_Flag_'+str(date_r_index)]==0]
        ipmt_next = ipmt_this[ipmt_this['Overdue_Flag_'+str(date_r_index)]==0]
        
        ppmt_pre = ppmt_pre.reset_index(drop=True)
        ipmt_pre = ipmt_pre.reset_index(drop=True)
        ppmt_next = ppmt_next.reset_index(drop=True)
        ipmt_next = ipmt_next.reset_index(drop=True)

        return ppmt_pre,ipmt_pre,ppmt_next,ipmt_next      

    def M1_2_M0M2(self,ppmt,ipmt):
        
        return pd.DataFrame(),pd.DataFrame(),ppmt,ipmt


    
    def gen_APCF_adjusted(self,OoR):
        #logger.info('Generating APCF_adjusted...' )
        df_total_by_date = pd.DataFrame(self.APCF_adjusted_dict)
        APCF_adjusted = pd.DataFrame({'date_recycle': self.dates_recycle_list,
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
        
        logger.info('Saving adjusted new APCF for scenario {0}: '.format(self.scenario_id))
        if OoR == 'R':pass
        else:save_to_excel(APCF_adjusted,'cf_'+OoR+'_adjusted_simulation'+Batch_ID,wb_name)
        #save_to_excel(APCF_adjusted,'cf_'+OoR+'_adjusted_simulation'+Batch_ID,wb_name)
        
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
        
    
    
