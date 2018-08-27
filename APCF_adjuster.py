# -*- coding: utf-8 -*-
"""
Created on Mon Jun 18 19:57:55 2018

@author: Jonah.Chen
"""
import sys
import os
from constant import *
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
    
    def __init__(self,apcf,recycle_adjust_factor,scenario,scenario_id):
        
        self.apcf = apcf
        self.recycle_adjust_factor = recycle_adjust_factor
        self.scenario_id = scenario_id      

    
    def adjust_APCF(self,OoR,dates_recycle_list):
        
        APCF_adjusted_structure = self.apcf
        main_params = scenarios[self.scenario_id]  
        
        first_due_period = 'first_due_period_'+OoR
        APCF_adjusted_structure['Overdue_Flag'] = pd.DataFrame(list(bernoulli.rvs(size=len(APCF_adjusted_structure['OutstandingPrincipal_Proportion']),p= (1-main_params['rate_overdue'])))) 
        APCF_adjusted_structure = APCF_adjusted_structure[APCF_adjusted_structure['Overdue_Flag']==1]        

        APCF_adjusted = cash_flow_collection(APCF_adjusted_structure,dates_recycle_list,first_due_period,'Original',wb_name)
        TOTAL_Principal = APCF_adjusted['amount_principal'].sum()
        APCF_adjusted['amount_total_outstanding_principal'] = TOTAL_Principal - APCF_adjusted['amount_principal'].cumsum()        
        APCF_adjusted = APCF_adjusted.rename(columns = {'amount_principal':'amount_recycle_principal','amount_interest':'amount_recycle_interest','':''})
        
        return APCF_adjusted[['date_recycle','amount_recycle_principal','amount_recycle_interest','amount_total_outstanding_principal']]
    
    
    def adjust_APCF_term_by_term(self,OoR,dates_recycle_list):
        
        APCF_adjusted_structure = self.apcf
        main_params = scenarios[self.scenario_id]  
        
        APCF_adjusted_structure['Overdue_Flag_0'] = pd.DataFrame(list(bernoulli.rvs(size=len(APCF_adjusted_structure['OutstandingPrincipal_Proportion']),p= (1-main_params['rate_overdue']) ))) 
        APCF_adjusted_structure.sort_values(by = 'Overdue_Flag_0',axis = 0,ascending = False)
        
        for date_r_index in range(len(dates_recycle_list)):
            flag_name = 'Overdue_Flag_'+str(date_r_index+1)
            APCF_adjusted_structure[flag_name] = 0
            APCF_adjusted_structure[flag_name] = pd.DataFrame(list(bernoulli.rvs(size=len(APCF_adjusted_structure[APCF_adjusted_structure['Overdue_Flag_'+str(date_r_index)]==1]),p= (1-main_params['rate_overdue']) )) + [0 for i in range(len(APCF_adjusted_structure[APCF_adjusted_structure['Overdue_Flag_'+str(date_r_index)]==0]))]) 
            APCF_adjusted_structure.sort_values(by = flag_name,axis = 0,ascending = False)
        #logger.info('Saving APCF_adjusted_structure for scenario {0}: '.format(self.scenario_id))
        #save_to_excel(APCF_adjusted_structure,'APCF_adjusted_structure_simulation',wb_name)

        first_due_period = 'first_due_period_'+OoR
        APCF_ppmt = calc_PPMT(APCF_adjusted_structure,dates_recycle_list,first_due_period)
        APCF_ipmt = calc_IPMT(APCF_adjusted_structure,dates_recycle_list,first_due_period)
        
        for date_r_index,date_r in enumerate(dates_recycle_list):
            
            APCF_ppmt[date_r] = APCF_ppmt[date_r].where(APCF_ppmt['Overdue_Flag_'+str(date_r_index)]==1,0)
            APCF_ipmt[date_r] = APCF_ipmt[date_r].where(APCF_ipmt['Overdue_Flag_'+str(date_r_index)]==1,0)
        
        
        df_ppmt_total_by_date = pd.DataFrame([APCF_ppmt[dates_recycle_list].sum()])
        df_ipmt_total_by_date = pd.DataFrame([APCF_ipmt[dates_recycle_list].sum()])
   
        APCF_adjusted = pd.DataFrame({'date_recycle': dates_recycle_list,
                                         'amount_principal': df_ppmt_total_by_date.transpose()[0],
                                         'amount_interest': df_ipmt_total_by_date.transpose()[0],
                                         'amount_total': (df_ppmt_total_by_date
                                                          + df_ipmt_total_by_date
                                                          ).transpose()[0]
                                         })
        
        #logger.info('Saving adjusted new APCF for scenario {0}: '.format(self.scenario_id))
        #save_to_excel(APCF_adjusted,'cf_'+OoR+'_adjusted_simulation',wb_name)
        
        TOTAL_Principal = APCF_adjusted['amount_principal'].sum()
        APCF_adjusted['amount_total_outstanding_principal'] = TOTAL_Principal - APCF_adjusted['amount_principal'].cumsum()        
        APCF_adjusted = APCF_adjusted.rename(columns = {'amount_principal':'amount_recycle_principal','amount_interest':'amount_recycle_interest','':''})
        
        return APCF_adjusted[['date_recycle','amount_recycle_principal','amount_recycle_interest','amount_total_outstanding_principal']]