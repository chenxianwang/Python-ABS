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
