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
        
        self.recylce_principal = {k:ACFa[pd.to_datetime(ACFa['date_recycle']) == k]['amount_principal'].sum() for k in dates_recycle}
        self.recylce_principal[dates_recycle[0]] = ACFa['amount_principal'][pd.to_datetime(ACFa['date_recycle']) <= dates_recycle[0]].sum()
        
        self.recylce_interest = {k:ACFa[pd.to_datetime(ACFa['date_recycle']) == k]['amount_interest'].sum() for k in dates_recycle}
        self.recylce_interest[dates_recycle[0]] = ACFa['amount_interest'][pd.to_datetime(ACFa['date_recycle']) <= dates_recycle[0]].sum()
    
    def available_to_pay_p(self,date_pay):
        
        return self.recylce_principal[dates_pay.index(date_pay)]
    
    
    def get_PrincipalBalance(self,date_check):
        return self.recylce_principal[date_check]
    
    def get_InterestBalance(self,date_check):
        return self.recylce_interest[date_check]