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


class ACF_adjuster():
    
    def __init__(self,name_project,cashflow_original,supplement_assets_params,scenario,scenario_id,dt_param,fee_rate_param):
        
        self.cashflow_original = cashflow_original
        self.supplement_params = supplement_assets_params
        self.main_params = scenario[scenario_id]
        self.name_project = name_project
        self.fee_rate_param = fee_rate_param
        self.dt_param = dt_param
        
        self.wb_save_results = path_root  + '/../CheckTheseProjects/' + self.name_project + '/'+self.name_project+'.xlsx'
        

    def adjust_ACF(self):
        
        aACF = self.cashflow_original
        main_params = self.main_params
        print("main_params['rate_default'] is ",main_params['rate_default'])
        TOTAL_Principal = aACF['amount_principal'].sum()
        aACF['amount_recycle_principal'] = aACF['amount_principal']*(1-main_params['rate_default'])
        aACF['amount_recycle_interest'] = aACF['amount_interest']*(1-main_params['rate_default'])
        
        aACF['amount_total_outstanding_principal'] = TOTAL_Principal - aACF['amount_recycle_principal'].cumsum()
        
        return aACF
