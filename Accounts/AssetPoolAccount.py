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
    
    def __init__(self,ACFa):
        
        self.recylce_principal = {k:ACFa[pd.to_datetime(ACFa['date_recycle']) == k]['amount_recycle_principal'].sum() for k in dates_recycle}
        self.recylce_principal[dates_recycle[0]] = ACFa['amount_recycle_principal'][pd.to_datetime(ACFa['date_recycle']) <= dates_recycle[0]].sum()
        
        self.recylce_interest = {k:ACFa[pd.to_datetime(ACFa['date_recycle']) == k]['amount_recycle_interest'].sum() for k in dates_recycle}
        self.recylce_interest[dates_recycle[0]] = ACFa['amount_recycle_interest'][pd.to_datetime(ACFa['date_recycle']) <= dates_recycle[0]].sum()

        self.principal_total = {}
        self.principal_to_pay = {}
        self.principal_to_buy = {}
        
        self.interest_total = {}
        self.interest_to_pay = {}
        self.interest_to_buy = {}
    
    def available_principal(self):
        
        self.principal_total = self.recylce_principal
        self.principal_to_pay = deepcopy(self.recylce_principal)
        self.principal_to_buy = {}
        for k in dates_recycle:
            self.principal_to_buy[k] = 0
        return self.principal_total,self.principal_to_pay,self.principal_to_buy

    def available_interest(self):
        
        self.interest_total = self.recylce_interest
        self.interest_to_pay = deepcopy(self.recylce_interest)
        self.interest_to_buy = {}
        for k in dates_recycle:
            self.interest_to_buy[k] = 0
        return self.interest_total,self.interest_to_pay,self.interest_to_buy
    
    def get_PrincipalBalance(self,date_check):
        return self.recylce_principal[date_check]
    
    def get_InterestBalance(self,date_check):
        return self.recylce_interest[date_check]