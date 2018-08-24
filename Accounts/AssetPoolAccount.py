# -*- coding: utf-8 -*-
"""
Created on Sun Jun 24 12:56:19 2018

@author: chen
"""

import sys
import os
from copy import deepcopy
from constant import *
from Params import *
import pandas as pd
import numpy as np
from abs_util.util_general import *
from abs_util.util_cf import *
from abs_util.util_sr import *
from dateutil.relativedelta import relativedelta
import datetime

logger = get_logger(__name__)

class AssetPoolAccount():
    
    def __init__(self,ACF,ACFa):
        
        self.original_principal = {k:ACF[pd.to_datetime(ACF['date_recycle']) == k]['amount_principal'].sum() for k in dates_recycle}
        self.original_principal[dates_recycle[0]] = ACF['amount_principal'][pd.to_datetime(ACF['date_recycle']) <= dates_recycle[0]].sum()
        self.original_interest = {k:ACF[pd.to_datetime(ACF['date_recycle']) == k]['amount_interest'].sum() for k in dates_recycle}
        self.original_interest[dates_recycle[0]] = ACF['amount_interest'][pd.to_datetime(ACF['date_recycle']) <= dates_recycle[0]].sum()
        
        self.recylce_principal = {k:ACFa[pd.to_datetime(ACFa['date_recycle']) == k]['amount_recycle_principal'].sum() for k in dates_recycle}
        self.recylce_principal[dates_recycle[0]] = ACFa['amount_recycle_principal'][pd.to_datetime(ACFa['date_recycle']) <= dates_recycle[0]].sum()
        self.recylce_interest = {k:ACFa[pd.to_datetime(ACFa['date_recycle']) == k]['amount_recycle_interest'].sum() for k in dates_recycle}
        self.recylce_interest[dates_recycle[0]] = ACFa['amount_recycle_interest'][pd.to_datetime(ACFa['date_recycle']) <= dates_recycle[0]].sum()

        self.principal_original = {}
        self.principal_actual = {}
        self.principal_to_pay = {}
        self.principal_to_buy = {}
        self.principal_to_loss = {}
        
        self.interest_original = {}
        self.interest_actual = {}
        self.interest_to_pay = {}
        self.interest_to_buy = {}
        self.interest_loss = {}
    
    def available_principal(self):
        
        self.principal_original = self.original_principal
        self.principal_actual = self.recylce_principal
        self.principal_to_pay = deepcopy(self.recylce_principal)
        self.principal_to_buy = {}
        for k in dates_recycle:
            self.principal_to_buy[k] = 0
            self.principal_to_loss[k] = 0
        return self.principal_actual,self.principal_to_pay,self.principal_to_buy,self.principal_to_loss,self.principal_original

    def available_interest(self):
        
        self.interest_original = self.original_interest
        self.interest_actual = self.recylce_interest
        self.interest_to_pay = deepcopy(self.recylce_interest)
        self.interest_to_buy = {}
        for k in dates_recycle:
            self.interest_to_buy[k] = 0
            self.interest_loss[k] = 0
        return self.interest_actual,self.interest_to_pay,self.interest_to_buy,self.interest_loss,self.interest_original