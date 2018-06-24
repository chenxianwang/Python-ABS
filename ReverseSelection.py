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

class ReverseSelection():
    
    def __init__(self,df,Targets):
        
        self.asset_pool = df
        self.targets = Targets


    def cal_OriginalStat(self):
        
        self.asset_pool['Amount_Outstanding'] = self.asset_pool['Amount_Outstanding_yuan']
        
        #Assets['SCp'] = (Assets['LoanType']=='SC')
   
        print('Original OutstandingPrincipal:',sum(self.asset_pool['Amount_Outstanding']))
        print('Original Contracts Count is: ', len(self.asset_pool.index))
        #print('Original WACredit_Score is:',(self.asset_pool['Credit_Score']*self.asset_pool['Amount_Outstanding']).sum()/self.asset_pool['Amount_Outstanding'].sum())
        print('Original WARate is:',(self.asset_pool['Interest_Rate']*self.asset_pool['Amount_Outstanding']).sum()/self.asset_pool['Amount_Outstanding'].sum())
        print('Original WALoanRemainTerm is:',(self.asset_pool['LoanRemainTerm']*self.asset_pool['Amount_Outstanding']).sum()/self.asset_pool['Amount_Outstanding'].sum())
        print('Original WALoanTerm is:',(self.asset_pool['LoanTerm']*self.asset_pool['Amount_Outstanding']).sum()/self.asset_pool['Amount_Outstanding'].sum())
        
        #print('Original SC Proportion is: ',sum(Assets[Assets['SCp']==1]['Amount_Outstanding']) / sum(Assets['Amount_Outstanding']))
        
        for target in self.targets.keys():
            print('Target for ',target,' is ',self.targets[target]['object'],self.targets[target]['object_value'])

    def iLP_Solver_all(self):

        Assets = self.asset_pool.groupby(['Interest_Rate'
                                          ,'LoanRemainTerm'
                                          ,'Credit_Score'
                                          ])\
               .agg({'Amount_Outstanding':'sum'})\
               .reset_index() #.rename(columns = {'LoanRemainTerm_original':'LoanRemainTerm'})
        
        Assets['No_Contract'] = range(1,len(Assets['Interest_Rate'])+1)
        Assets['Interest_Rate_min'] = Assets['Interest_Rate']
        Assets['Interest_Rate_max'] = Assets['Interest_Rate']
        #print(Assets[:5])
        #Assets.to_csv('Assets.csv',index=False)
        
        for target_d in self.targets.keys() :
            if 'Amount_Outstanding' not in target_d:
                Assets[target_d +'Helper'] = Assets['Amount_Outstanding'] * (Assets[target_d] - self.targets[target_d]['object_value'])
        
        OutstandingPrincipal = Assets['Amount_Outstanding']
                        
        #Data input
        Contracts = Assets['No_Contract']
        Credit_ScoreHelper = Assets['Credit_ScoreHelper']
        LoanRemainTermHelper = Assets['LoanRemainTermHelper']
        #SCpHelper = Assets['SCpHelper']
        Interest_Rate_min_Helper = Assets['Interest_Rate_minHelper']
        Interest_Rate_max_Helper = Assets['Interest_Rate_maxHelper']
        
        P = range(len(Contracts))
        # Declare problem instance, maximization problem
        prob = LpProblem("AssetsSelection", LpMaximize)
        # Declare decision variable x, which is 1 if certain asset is choosen, otherwise 0
        print('Declaring Variables...')
        x = LpVariable.matrix("x", list(P), 0, 1, LpInteger)
        
        print('Objective function -> Maximize OutstandingPrincipal')
        prob += sum(OutstandingPrincipal[p] * x[p] for p in P)    
        
        print('Constraint definition')
        prob += sum(LoanRemainTermHelper[p] * x[p] for p in P) * self.targets['LoanRemainTerm']['object_sign'] >= 0
        
        prob += sum(Credit_ScoreHelper[p] * x[p] for p in P) * self.targets['Credit_Score']['object_sign'] >= 0
                   
        prob += sum(Interest_Rate_min_Helper[p] * x[p] for p in P) * self.targets['Interest_Rate_min']['object_sign'] >= 0 
        prob += sum(Interest_Rate_max_Helper[p] * x[p] for p in P) * self.targets['Interest_Rate_max']['object_sign'] >= 0 
                   
        prob += sum(OutstandingPrincipal[p] * x[p] for p in P) <= self.targets['Amount_Outstanding_max']['object_value']
        #prob += sum(OutstandingPrincipal[p] * x[p] for p in P) >= self.targets['Amount_Outstanding_min']['object_value']
        
        print('Start solving the problem instance')
        #prob.solve()
        print(LpStatus[prob.solve()])
        print('All Selection Done.')
        # Extract solution
        _AssetsSelected = Assets[Assets['No_Contract'].isin(Contracts[p] for p in P if x[p].varValue)]
        _AssetsSelected['ReverseSelection_Flag'] = _AssetsSelected['Interest_Rate'].astype(str) + \
                                                   _AssetsSelected['LoanRemainTerm'].astype(str) + \
                                                   _AssetsSelected['Credit_Score'].astype(str)               
        
        print()
        print("All Selection Done.")
        print("Selected Outstanding Principal is ",sum(_AssetsSelected['Amount_Outstanding']))
        print("Selected Contracts Count is ",len(_AssetsSelected.index))
        print()
        
        for target_d in self.targets.keys():
             Condition_Satisfied_or_Not(_AssetsSelected,target_d,Targets)
        
        _AssetsSelected.to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/AssetsSelected_Final.csv',index=False)

        return _AssetsSelected