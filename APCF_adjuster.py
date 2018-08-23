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
        self.main_params = scenario[scenario_id]
        
    def adjust_APCF(self):
        
        APCF_adjusted = self.apcf
        main_params = self.main_params
        #logger.info("main_params['rate_default'] is {0}".format(main_params['rate_default']))
        TOTAL_Principal = APCF_adjusted['amount_principal'].sum()
        
        APCF_adjusted['amount_recycle_principal'] = APCF_adjusted['amount_principal']*(1-main_params['rate_default'])
        
        #logger.info("sum(APCF_adjusted['amount_recycle_principal']) is {0}".format(APCF_adjusted['amount_recycle_principal'].sum()))
        
        APCF_adjusted['amount_recycle_interest'] = APCF_adjusted['amount_interest']*(1-main_params['rate_default'])
        
        APCF_adjusted['amount_total_outstanding_principal'] = TOTAL_Principal - APCF_adjusted['amount_principal'].cumsum()
        
        return APCF_adjusted[['date_recycle','amount_recycle_principal','amount_recycle_interest','amount_total_outstanding_principal']]
    
    
    def adjust_APCF_simulation(self):
        
        APCF_adjusted_structure = self.apcf
        main_params = self.main_params  
        
        last_term = int((APCF_adjusted_structure['Term_Remain'] + APCF_adjusted_structure['first_due_period_O']).max())
        dates_recycle_list= [get_next_eom(dt_param['dt_pool_cut'],i) for i in range(last_term)]
        
        APCF_adjusted_structure['Default_Flag'] = pd.DataFrame(list(bernoulli.rvs(size=len(APCF_adjusted_structure['PayDay']),p=main_params['rate_default']))) 
        APCF_adjusted_structure = APCF_adjusted_structure[APCF_adjusted_structure['Default_Flag']==0]        

        APCF_adjusted = cash_flow_collection(APCF_adjusted_structure,dates_recycle_list,'first_due_period_O','Original',wb_name)
        TOTAL_Principal = APCF_adjusted['amount_principal'].sum()
        APCF_adjusted['amount_total_outstanding_principal'] = TOTAL_Principal - APCF_adjusted['amount_principal'].cumsum()        
        APCF_adjusted = APCF_adjusted.rename(columns = {'amount_principal':'amount_recycle_principal','amount_interest':'amount_recycle_interest','':''})
        
        return APCF_adjusted[['date_recycle','amount_recycle_principal','amount_recycle_interest','amount_total_outstanding_principal']]
    
    
    
    
    
    
    
