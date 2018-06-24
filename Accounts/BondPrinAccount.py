# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 14:55:13 2018

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
from abs_util.util_sr import *
from dateutil.relativedelta import relativedelta
import datetime


class BondPrinAccount():
    
    def __init__(self,name_bond,Bonds):
        self.name_bond = name_bond
        self.bondinfo = Bonds[name_bond]
        self.balance = {}
        self.receive = {}
    
    def pay_then_ToNext(self,date_pay,amount_available):
        
        if amount_available < 0:
            print('!!!!!!!!!    Can not cover payment      !!!!!!!')
        elif self.bondinfo['amount'] == 0:
            self.balance[date_pay] = 0
            self.receive[date_pay] = 0
            return amount_available
        elif self.bondinfo['amount'] >= amount_available:
            self.bondinfo['amount'] -= amount_available
            self.balance[date_pay] = self.bondinfo['amount']
            self.receive[date_pay] = amount_available
            return 0
        else: 
            self.receive[date_pay] = self.bondinfo['amount']
            self.bondinfo['amount'] = 0
            self.balance[date_pay] = self.bondinfo['amount']
            return amount_available - self.receive[date_pay]
           
    def iBalance(self,date_pay):
        return self.bondinfo['amount'] if date_pay==dates_pay[0] else self.balance[date_pay+relativedelta(months= -1)]
