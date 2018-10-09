# -*- coding: utf-8 -*-
"""
Created on Mon Jun 18 16:11:08 2018

@author: Jonah.Chen
"""

import os
import datetime
from dateutil.relativedelta import relativedelta
from abs_util.util_general import *
from constant import *

Batch_ID = str(datetime.datetime.now().hour) + str(datetime.datetime.now().minute)+str(datetime.datetime.now().second)

days_in_a_year = 365
rate_discount = 0.40
ADate = datetime.date(2018,8,1)


if ProjectName == 'ABS9':
    amount_total_issuance = 3015926877.69
    Bonds = {}
    Bonds['A'] = {'ptg':0.6714,'amount':2025000000, 'rate':0.0575}
    Bonds['B'] = {'ptg':0.1107,'amount':334000000,'rate':0.0719}
    Bonds['C'] = {'ptg':0.2178,'amount':656926877.69,'rate':0.0}
    Bonds['EE'] = {'ptg':0,'amount':100000000000,'rate':0.0}
    dt_param = {'dt_pool_cut':datetime.date(2018,4,16),'dt_effective':datetime.date(2018,7,20)}

elif ProjectName == 'ABS10':
    amount_total_issuance = 3014292721.30
    Bonds = {}
    Bonds['A'] = {'ptg':0.6502,'amount':1960000000, 'rate':0.055}
    Bonds['B'] = {'ptg':0.1287,'amount':388000000,'rate':0.072}
    Bonds['C'] = {'ptg':0.2211,'amount':666292721.30,'rate':0.0}
    Bonds['EE'] = {'ptg':0,'amount':100000000000,'rate':0.0}
    dt_param = {'dt_pool_cut':datetime.date(2018,7,23),'dt_effective':datetime.date(2018,10,16)}

elif ProjectName == 'ABS11':
    amount_total_issuance = 2501010000.7
    Bonds = {}
    Bonds['A'] = {'ptg':0.6502,'amount':1626000000 , 'rate':0.0575}
    Bonds['B'] = {'ptg':0.1287,'amount':322000000,'rate':0.0719}
    Bonds['C'] = {'ptg':0.2211,'amount':553010000.7,'rate':0.0}
    Bonds['EE'] = {'ptg':0,'amount':100000000000,'rate':0.0}
    dt_param = {'dt_pool_cut':datetime.date(2018,8,31),'dt_effective':datetime.date(2018,11,30)}
    
else: dt_param = {'dt_pool_cut':datetime.date(2018,8,1),'dt_effective':datetime.date(2018,8,8)}

try:
    POOL_CUT_PERIOD = dt_param['dt_effective'].month - dt_param['dt_pool_cut'].month
    dt_param['dt_first_calc'] = get_next_eom(dt_param['dt_effective'],0)
    dt_param['dt_first_pay'] = dt_param['dt_first_calc']+ relativedelta(days = 26)
    dates_pay = [dt_param['dt_first_pay'] + relativedelta(months= i) for i in range(36)]
    dates_recycle = [get_next_eom(dt_param['dt_first_calc'],month_increment) for month_increment in range(36)]
########## Hom many revolving pools ###############
    nbr_revolving_pools = 6
    date_revolving_pools_cut = [dt_param['dt_first_calc'] + relativedelta(days = 1) + relativedelta(months= i) for i in range(nbr_revolving_pools)]
    Redeem_or_Not = True
    #Redeem_or_Not = False
except(NameError):
    pass

fees = { 'tax':{'rate':0.032621359223},
        'trustee':{'rate':0.0005},
        'custodian':{'rate':0.000055},
        'servicer':{'rate':0.001},
        'pay_interest_service':{'rate':0.00005},
         'pre_issue':{'amount':245797.32215745+500000},
         'A':{'rate':0.058},
         'B':{'rate':0.068},
         'C':{'rate':0.0},
         }

scenarios = {}
scenarios['best'] = {'M0_2_ERM0':0.99,'M0_2_M1':0.03,'M1_2_M0M2':0.5,'M2_2_M0M3':0.8,'M3_2_M0L':0.85,'scenario_weight':0.1}
#scenarios['better'] = {'M0_2_ERM0':0.991,'M0_2_M1':0.033,'M1_2_M0M2':0.53,'M2_2_M0M3':0.83,'M3_2_M0L':0.87,'scenario_weight':0.15}
#scenarios['benchmark'] = {'M0_2_ERM0':0.992,'M0_2_M1':0.035,'M1_2_M0M2':0.55,'M2_2_M0M3':0.85,'M3_2_M0L':0.89,'scenario_weight':0.5}
#scenarios['worse'] = {'M0_2_ERM0':0.993,'M0_2_M1':0.037,'M1_2_M0M2':0.57,'M2_2_M0M3':0.87,'M3_2_M0L':0.91,'scenario_weight':0.15}
#scenarios['worst'] = {'M0_2_ERM0':0.995,'M0_2_M1':0.04,'M1_2_M0M2':0.6,'M2_2_M0M3':0.9,'M3_2_M0L':0.93,'scenario_weight':0.1}
#    
#payment_frequency = {'month':1,'quarter':3,'semi-annual':6,'annual':12}

MaxWAScore = 0.065
MinWAScore = 0.0645

MinWARate = 0.18
MaxWARate = 0.18004

MaxWALoanRemainTerm = 390

MaxIssueVolumn = 767962857.70
MinIssueVolumn = 767960857.70

MaxSCProp = 0.70
MaxSDProp = 0.3 

Targets_all = { 
           'SCp':{'object':'SC Proportion LessThan','object_value_h':MaxSCProp,'object_sign':-1},
           'Credit_Score_max':{'object':'Weighted Average LessThan','object_value':MaxWAScore,'object_sign':-1},
           'Credit_Score_min':{'object':'Weighted Average GreaterThan','object_value':MinWAScore,'object_sign':1},
           'LoanRemainTerm':{'object':'Weighted Average LessThan','object_value':MaxWALoanRemainTerm,'object_sign':-1},
           'Interest_Rate_min':{'object':'Weighted Average GreaterThan','object_value':MinWARate,'object_sign':1},
           'Interest_Rate_max':{'object':'Weighted Average LessThan','object_value':MaxWARate,'object_sign':-1},
           'Amount_Outstanding_max':{'object':'LessThan','object_value':MaxIssueVolumn},
           'Amount_Outstanding_min':{'object':'GreaterThan','object_value':MinIssueVolumn},
           }

Targets_keys = ['Credit_Score_max','Credit_Score_min',
                'Interest_Rate_min','Interest_Rate_max',
                'Amount_Outstanding_max','Amount_Outstanding_min',
               ]

RS_Group_d = ['Credit_Score',
              'Interest_Rate',#'Usage','LoanRemainTerm'#,'Province',#'Usage'
              #'LoanRemainTerm',
              ]

Targets = {k:Targets_all[k] for k in Targets_keys}


Distribution_By_Category = ['Type_Loans',
                            'Interest_Rate','Marriagestate',
                            'Province',
                            'Profession','职业_信托',
                            'Type_Five_Category',
                            'Usage','购买商品_信托',
                            'Gender'
                            ]

income_bins = [0,50000,100000,150000,200000,2000000,100000000]
age_bins = [17.9999,20,30,40,50,55,60]
outstanding_principal_bins = [-0.001,1000,2000,3000,4000,5000,6000,7000,8000,9000,10000,20000,1000000]

duration_days_bins = [0,90,180,360,540,720,1080,3000]
past_days_bins = [-0.01,90,180,360,540,720,1080,3000]
future_days_bins = [-0.01,90,180,360,540,720,1080,3000]

duration_months_bins = [0,5.999,9.999,12,18,24,31]

overdue_times_bins = [-0.001,0,1,2,5,10,15,20,25,30]
dpd_max_bins = [-0.01,0,5,30,60,90,120,150,180,360]
dpd_bins = [-0.01,0,30,60,90,120,150,180,360,1000]
#total_fee_rate_bins = [-0.01,0,0.2,0.24,0.36,0.5,0.6]
credit_score_bins = [-0.01,0.01,0.02,0.03,0.04,0.05,0.06,0.07,0.08,0.09,0.1,
                     0.11,0.12,0.13,0.14,0.15,0.2,0.25,1]

Distribution_By_Bins = {
                        'Income':income_bins,
                        'Age_Project_Start':age_bins,
                        'OutstandingPrincipal':outstanding_principal_bins,
                        'LoanTerm':duration_days_bins,
                        'LoanAge':past_days_bins,
                        'LoanRemainTerm':future_days_bins,
                        'Term_Contract':duration_months_bins,
                        'Days_Overdue_Max':dpd_max_bins,
                        'Days_Overdue_Current':dpd_bins,
                        'Overdue_Times':overdue_times_bins,
                        #'综合费用率':total_fee_rate_bins,
                        'Credit_Score':credit_score_bins
                        }