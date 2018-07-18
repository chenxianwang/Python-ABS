# -*- coding: utf-8 -*-
"""
Created on Sun Jun 24 12:56:19 2018

@author: chen
"""

import sys
import os
from constant import *
from Params import *
import pandas as pd
import numpy as np
from abs_util.util_general import *
from abs_util.util_cf import *
from abs_util.util_sr import *
from dateutil.relativedelta import relativedelta
import datetime


class AssetPoolAccount():
    
    def __init__(self,ACFa):
        
        self.recylce_principal = {k:ACFa[pd.to_datetime(ACFa['date_recycle']) == k]['amount_recycle_principal'].sum() for k in dates_recycle}
        self.recylce_principal[dates_recycle[0]] = ACFa['amount_recycle_principal'][pd.to_datetime(ACFa['date_recycle']) <= dates_recycle[0]].sum()

        self.recylce_interest = {k:ACFa[pd.to_datetime(ACFa['date_recycle']) == k]['amount_recycle_interest'].sum() for k in dates_recycle}
        self.recylce_interest[dates_recycle[0]] = ACFa['amount_recycle_interest'][pd.to_datetime(ACFa['date_recycle']) <= dates_recycle[0]].sum()

        
        self.principal_to_pay = {}
        self.principal_to_buy = {}
        
        self.interest_to_pay = {}
    
    def available_principal_to_pay(self):
        
        self.principal_to_pay = self.recylce_principal
        self.principal_to_buy = {}
        return self.principal_to_pay,self.principal_to_buy

    def available_interest_to_pay(self):
        
        self.interest_to_pay = self.recylce_interest
        return self.interest_to_pay
    
    def get_PrincipalBalance(self,date_check):
        return self.recylce_principal[date_check]
    
    def get_InterestBalance(self,date_check):
        return self.recylce_interest[date_check]