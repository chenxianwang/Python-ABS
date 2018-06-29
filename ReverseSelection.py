# -*- coding: utf-8 -*-
"""
Created on Thu May 24 16:01:23 2018

@author: jonah.chen
"""

import sys
import os
from pulp import *
from constant import *
import pandas as pd
import numpy as np
from abs_util.util_general import *

logger = get_logger(__name__)

class ReverseSelection():
    
    def __init__(self,df,Targets,group_d):
        
        self.asset_pool = df
        self.targets = Targets
        self.group_d = group_d

    def cal_OriginalStat(self):
        
        self.asset_pool['Amount_Outstanding'] = self.asset_pool['Amount_Outstanding_yuan']
        logger.info('Original OutstandingPrincipal: {0}'.format(sum(self.asset_pool['Amount_Outstanding'])))
        logger.info('Original Contracts Count is: {0} '.format(len(self.asset_pool.index)))
        logger.info('Original WACredit_Score is: {0}'.format((self.asset_pool['Credit_Score']*self.asset_pool['Amount_Outstanding']).sum()/self.asset_pool['Amount_Outstanding'].sum()))
        logger.info('Original WARate is: {0}'.format((self.asset_pool['Interest_Rate']*self.asset_pool['Amount_Outstanding']).sum()/self.asset_pool['Amount_Outstanding'].sum()))
        logger.info('Original WALoanRemainTerm is: {0}'.format((self.asset_pool['LoanRemainTerm']*self.asset_pool['Amount_Outstanding']).sum()/self.asset_pool['Amount_Outstanding'].sum()))
        #logger.info('Original WALoanTerm is: {0}'.format((self.asset_pool['LoanTerm']*self.asset_pool['Amount_Outstanding']).sum()/self.asset_pool['Amount_Outstanding'].sum()))
        
        for target in self.targets.keys():
            print('Target for ',target,' is ',self.targets[target]['object'],self.targets[target]['object_value'])

    def iLP_Solver_all(self):

        Assets = self.asset_pool.groupby(self.group_d)\
                               .agg({'Amount_Outstanding':'sum'})\
                               .reset_index()
        
        logger.info('Rows of GroupedBy is {0}'.format(len(Assets['Interest_Rate'])))
        Assets['No_Contract'] = range(1,len(Assets['Interest_Rate'])+1)
        Assets['Interest_Rate_min'] = Assets['Interest_Rate']
        Assets['Interest_Rate_max'] = Assets['Interest_Rate']
        
        for target_d in self.targets.keys() :
            if 'Amount_Outstanding' not in target_d:
                Assets[target_d +'Helper'] = Assets['Amount_Outstanding'] * (Assets[target_d] - self.targets[target_d]['object_value'])
        
        OutstandingPrincipal = Assets['Amount_Outstanding']
                        
        #Data input
        Contracts = Assets['No_Contract']
        Credit_ScoreHelper = Assets['Credit_ScoreHelper']
        Interest_Rate_min_Helper = Assets['Interest_Rate_minHelper']
        Interest_Rate_max_Helper = Assets['Interest_Rate_maxHelper']
        #LoanRemainTermHelper = Assets['LoanRemainTermHelper']
        
        P = range(len(Contracts))
        # Declare problem instance, maximization problem
        prob = LpProblem("AssetsSelection", LpMaximize)
        # Declare decision variable x, which is 1 if certain asset is choosen, otherwise 0
        logger.info('Declaring Variables...')
        x = LpVariable.matrix("x", list(P), 0, 1, LpInteger)
        
        logger.info('Objective function -> Maximize OutstandingPrincipal')
        prob += sum(OutstandingPrincipal[p] * x[p] for p in P)    
        
        logger.info('Constraint definition')
        prob += sum(Credit_ScoreHelper[p] * x[p] for p in P) * self.targets['Credit_Score']['object_sign'] >= 0
        prob += sum(Interest_Rate_min_Helper[p] * x[p] for p in P) * self.targets['Interest_Rate_min']['object_sign'] >= 0 
        prob += sum(Interest_Rate_max_Helper[p] * x[p] for p in P) * self.targets['Interest_Rate_max']['object_sign'] >= 0 
                   
        #prob += sum(OutstandingPrincipal[p] * x[p] for p in P) <= self.targets['Amount_Outstanding_max']['object_value']
        #prob += sum(OutstandingPrincipal[p] * x[p] for p in P) >= self.targets['Amount_Outstanding_min']['object_value']
        
        #prob += sum(LoanRemainTermHelper[p] * x[p] for p in P) * self.targets['LoanRemainTerm']['object_sign'] >= 0
        
        logger.info('Start solving the problem instance')
        #prob.solve()
        logger.info(LpStatus[prob.solve()])
        logger.info('All Selection Done.')
        # Extract solution
        _AssetsSelected = Assets[Assets['No_Contract'].isin(Contracts[p] for p in P if x[p].varValue)]

        return _AssetsSelected