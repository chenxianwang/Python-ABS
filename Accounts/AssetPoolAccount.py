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
        self.recylce_principal = {k:ACFa[pd.to_datetime(ACFa['date_recycle']) == k]['amount_recycle_principal'].sum() for k in dates_recycle}
        self.recylce_principal[dates_recycle[0]] = ACFa['amount_recycle_principal'][pd.to_datetime(ACFa['date_recycle']) <= dates_recycle[0]].sum()
        
        self.recylce_principal_overdue_1_30_currentTerm = {k:ACFa[pd.to_datetime(ACFa['date_recycle']) == k]['amount_principal_overdue_1_30_currentTerm'].sum() for k in dates_recycle}
        self.recylce_principal_overdue_1_30_currentTerm[dates_recycle[0]] = ACFa['amount_principal_overdue_1_30_currentTerm'][pd.to_datetime(ACFa['date_recycle']) <= dates_recycle[0]].sum()
        self.recylce_principal_overdue_1_30_allTerm = {k:ACFa[pd.to_datetime(ACFa['date_recycle']) == k]['amount_principal_overdue_1_30_allTerm'].sum() for k in dates_recycle}
        self.recylce_principal_overdue_1_30_allTerm[dates_recycle[0]] = ACFa['amount_principal_overdue_1_30_allTerm'][pd.to_datetime(ACFa['date_recycle']) <= dates_recycle[0]].sum()
        
        self.recylce_principal_overdue_31_60_currentTerm = {k:ACFa[pd.to_datetime(ACFa['date_recycle']) == k]['amount_principal_overdue_31_60_currentTerm'].sum() for k in dates_recycle}
        self.recylce_principal_overdue_31_60_currentTerm[dates_recycle[0]] = ACFa['amount_principal_overdue_31_60_currentTerm'][pd.to_datetime(ACFa['date_recycle']) <= dates_recycle[0]].sum()
        self.recylce_principal_overdue_31_60_allTerm = {k:ACFa[pd.to_datetime(ACFa['date_recycle']) == k]['amount_principal_overdue_31_60_allTerm'].sum() for k in dates_recycle}
        self.recylce_principal_overdue_31_60_allTerm[dates_recycle[0]] = ACFa['amount_principal_overdue_31_60_allTerm'][pd.to_datetime(ACFa['date_recycle']) <= dates_recycle[0]].sum()
        
        self.recylce_principal_overdue_61_90_currentTerm = {k:ACFa[pd.to_datetime(ACFa['date_recycle']) == k]['amount_principal_overdue_61_90_currentTerm'].sum() for k in dates_recycle}
        self.recylce_principal_overdue_61_90_currentTerm[dates_recycle[0]] = ACFa['amount_principal_overdue_61_90_currentTerm'][pd.to_datetime(ACFa['date_recycle']) <= dates_recycle[0]].sum()
        self.recylce_principal_overdue_61_90_allTerm = {k:ACFa[pd.to_datetime(ACFa['date_recycle']) == k]['amount_principal_overdue_61_90_allTerm'].sum() for k in dates_recycle}
        self.recylce_principal_overdue_61_90_allTerm[dates_recycle[0]] = ACFa['amount_principal_overdue_61_90_allTerm'][pd.to_datetime(ACFa['date_recycle']) <= dates_recycle[0]].sum()
        
        self.recylce_principal_loss_currentTerm = {k:ACFa[pd.to_datetime(ACFa['date_recycle']) == k]['amount_principal_loss_currentTerm'].sum() for k in dates_recycle}
        self.recylce_principal_loss_currentTerm[dates_recycle[0]] = ACFa['amount_principal_loss_currentTerm'][pd.to_datetime(ACFa['date_recycle']) <= dates_recycle[0]].sum()
        self.recylce_principal_loss_allTerm = {k:ACFa[pd.to_datetime(ACFa['date_recycle']) == k]['amount_principal_loss_allTerm'].sum() for k in dates_recycle}
        self.recylce_principal_loss_allTerm[dates_recycle[0]] = ACFa['amount_principal_loss_allTerm'][pd.to_datetime(ACFa['date_recycle']) <= dates_recycle[0]].sum()


        self.original_interest = {k:ACF[pd.to_datetime(ACF['date_recycle']) == k]['amount_interest'].sum() for k in dates_recycle}
        self.original_interest[dates_recycle[0]] = ACF['amount_interest'][pd.to_datetime(ACF['date_recycle']) <= dates_recycle[0]].sum()
        self.recylce_interest = {k:ACFa[pd.to_datetime(ACFa['date_recycle']) == k]['amount_recycle_interest'].sum() for k in dates_recycle}
        self.recylce_interest[dates_recycle[0]] = ACFa['amount_recycle_interest'][pd.to_datetime(ACFa['date_recycle']) <= dates_recycle[0]].sum()
        
        self.recylce_interest_overdue_1_30_currentTerm = {k:ACFa[pd.to_datetime(ACFa['date_recycle']) == k]['amount_interest_overdue_1_30_currentTerm'].sum() for k in dates_recycle}
        self.recylce_interest_overdue_1_30_currentTerm[dates_recycle[0]] = ACFa['amount_interest_overdue_1_30_currentTerm'][pd.to_datetime(ACFa['date_recycle']) <= dates_recycle[0]].sum()
        self.recylce_interest_overdue_1_30_allTerm = {k:ACFa[pd.to_datetime(ACFa['date_recycle']) == k]['amount_interest_overdue_1_30_allTerm'].sum() for k in dates_recycle}
        self.recylce_interest_overdue_1_30_allTerm[dates_recycle[0]] = ACFa['amount_interest_overdue_1_30_allTerm'][pd.to_datetime(ACFa['date_recycle']) <= dates_recycle[0]].sum()
        
        self.recylce_interest_overdue_31_60_currentTerm = {k:ACFa[pd.to_datetime(ACFa['date_recycle']) == k]['amount_interest_overdue_31_60_currentTerm'].sum() for k in dates_recycle}
        self.recylce_interest_overdue_31_60_currentTerm[dates_recycle[0]] = ACFa['amount_interest_overdue_31_60_currentTerm'][pd.to_datetime(ACFa['date_recycle']) <= dates_recycle[0]].sum()
        self.recylce_interest_overdue_31_60_allTerm = {k:ACFa[pd.to_datetime(ACFa['date_recycle']) == k]['amount_interest_overdue_31_60_allTerm'].sum() for k in dates_recycle}
        self.recylce_interest_overdue_31_60_allTerm[dates_recycle[0]] = ACFa['amount_interest_overdue_31_60_allTerm'][pd.to_datetime(ACFa['date_recycle']) <= dates_recycle[0]].sum()
        
        self.recylce_interest_overdue_61_90_currentTerm = {k:ACFa[pd.to_datetime(ACFa['date_recycle']) == k]['amount_interest_overdue_61_90_currentTerm'].sum() for k in dates_recycle}
        self.recylce_interest_overdue_61_90_currentTerm[dates_recycle[0]] = ACFa['amount_interest_overdue_61_90_currentTerm'][pd.to_datetime(ACFa['date_recycle']) <= dates_recycle[0]].sum()
        self.recylce_interest_overdue_61_90_allTerm = {k:ACFa[pd.to_datetime(ACFa['date_recycle']) == k]['amount_interest_overdue_61_90_allTerm'].sum() for k in dates_recycle}
        self.recylce_interest_overdue_61_90_allTerm[dates_recycle[0]] = ACFa['amount_interest_overdue_61_90_allTerm'][pd.to_datetime(ACFa['date_recycle']) <= dates_recycle[0]].sum()
        
        self.recylce_interest_loss_currentTerm = {k:ACFa[pd.to_datetime(ACFa['date_recycle']) == k]['amount_interest_loss_currentTerm'].sum() for k in dates_recycle}
        self.recylce_interest_loss_currentTerm[dates_recycle[0]] = ACFa['amount_interest_loss_currentTerm'][pd.to_datetime(ACFa['date_recycle']) <= dates_recycle[0]].sum()
        self.recylce_interest_loss_allTerm = {k:ACFa[pd.to_datetime(ACFa['date_recycle']) == k]['amount_interest_loss_allTerm'].sum() for k in dates_recycle}
        self.recylce_interest_loss_allTerm[dates_recycle[0]] = ACFa['amount_interest_loss_allTerm'][pd.to_datetime(ACFa['date_recycle']) <= dates_recycle[0]].sum()
                
        self.principal_original = {}
        self.principal_actual = {}
        self.principal_to_pay = {}
        self.principal_to_buy = {}
        self.principal_overdue_1_30_currentTerm = {}
        self.principal_overdue_1_30_allTerm = {}
        self.principal_overdue_31_60_currentTerm = {}
        self.principal_overdue_31_60_allTerm = {}
        self.principal_overdue_61_90_currentTerm = {}
        self.principal_overdue_61_90_allTerm = {}
        self.principal_loss_currentTerm = {}
        self.principal_loss_allTerm = {}
        
        self.interest_original = {}
        self.interest_actual = {}
        self.interest_to_pay = {}
        self.interest_to_buy = {}
        self.interest_overdue_1_30_currentTerm = {}
        self.interest_overdue_1_30_allTerm = {}
        self.interest_overdue_31_60_currentTerm = {}
        self.interest_overdue_31_60_allTerm = {}
        self.interest_overdue_61_90_currentTerm = {}
        self.interest_overdue_61_90_allTerm = {}
        self.interest_loss_currentTerm = {}
        self.interest_loss_allTerm = {}
    
    def available_principal(self):
        
        self.principal_original = self.original_principal
        self.principal_actual = self.recylce_principal
        self.principal_to_pay = deepcopy(self.recylce_principal)
        self.principal_overdue_1_30_currentTerm = deepcopy(self.recylce_principal_overdue_1_30_currentTerm)
        self.principal_overdue_1_30_allTerm = deepcopy(self.recylce_principal_overdue_1_30_allTerm)
        self.principal_overdue_31_60_currentTerm = deepcopy(self.recylce_principal_overdue_31_60_currentTerm)
        self.principal_overdue_31_60_allTerm = deepcopy(self.recylce_principal_overdue_31_60_allTerm)
        self.principal_overdue_61_90_currentTerm = deepcopy(self.recylce_principal_overdue_61_90_currentTerm)
        self.principal_overdue_61_90_allTerm = deepcopy(self.recylce_principal_overdue_61_90_allTerm)
        self.principal_loss_currentTerm = deepcopy(self.recylce_principal_loss_currentTerm)
        self.principal_loss_allTerm = deepcopy(self.recylce_principal_loss_allTerm)
        for k in dates_recycle:
            self.principal_to_buy[k] = 0
        return self.principal_original,self.principal_actual,\
               self.principal_to_pay,self.principal_to_buy,\
               self.principal_overdue_1_30_currentTerm,self.principal_overdue_1_30_allTerm,\
               self.principal_overdue_31_60_currentTerm,self.principal_overdue_31_60_allTerm,\
               self.principal_overdue_61_90_currentTerm,self.principal_overdue_61_90_allTerm,\
               self.principal_loss_currentTerm,self.principal_loss_allTerm
                

    def available_interest(self):
        
        self.interest_original = self.original_interest
        self.interest_actual = self.recylce_interest
        self.interest_to_pay = deepcopy(self.recylce_interest)
        self.interest_overdue_1_30_currentTerm = deepcopy(self.recylce_interest_overdue_1_30_currentTerm)
        self.interest_overdue_1_30_allTerm = deepcopy(self.recylce_interest_overdue_1_30_allTerm)
        self.interest_overdue_31_60_currentTerm = deepcopy(self.recylce_interest_overdue_31_60_currentTerm)
        self.interest_overdue_31_60_allTerm = deepcopy(self.recylce_interest_overdue_31_60_allTerm)
        self.interest_overdue_61_90_currentTerm = deepcopy(self.recylce_interest_overdue_61_90_currentTerm)
        self.interest_overdue_61_90_allTerm = deepcopy(self.recylce_interest_overdue_61_90_allTerm)
        self.interest_loss_currentTerm = deepcopy(self.recylce_interest_loss_currentTerm)
        self.interest_loss_allTerm = deepcopy(self.recylce_interest_loss_allTerm)
        for k in dates_recycle:
            self.interest_to_buy[k] = 0
        return self.interest_original,self.interest_actual,\
               self.interest_to_pay,self.interest_to_buy,\
               self.interest_overdue_1_30_currentTerm,self.interest_overdue_1_30_allTerm,\
               self.interest_overdue_31_60_currentTerm,self.interest_overdue_31_60_allTerm,\
               self.interest_overdue_61_90_currentTerm,self.interest_overdue_61_90_allTerm,\
               self.interest_loss_currentTerm,self.interest_loss_allTerm