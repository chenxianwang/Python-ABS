# -*- coding: utf-8 -*-
"""
Created on Mon Jun 18 16:11:08 2018

@author: Jonah.Chen
"""

import os
import datetime

TrustEffectiveDate = datetime.date(2018,6,27)

dates_pay = [datetime.date(2018,8,26),datetime.date(2018,9,26),datetime.date(2018,10,26),datetime.date(2018,11,26),datetime.date(2018,12,26),
             datetime.date(2019,1,26),datetime.date(2019,2,26),datetime.date(2019,3,26),datetime.date(2019,4,26),datetime.date(2019,5,26),datetime.date(2019,6,26),
             datetime.date(2019,7,26),datetime.date(2019,8,26),datetime.date(2019,9,26),datetime.date(2019,10,26),datetime.date(2019,11,26),datetime.date(2019,12,26),
             datetime.date(2020,1,26),datetime.date(2020,2,26),datetime.date(2020,3,26),datetime.date(2020,4,26),datetime.date(2020,5,26),datetime.date(2020,6,26),
             ]
dates_recycle = [datetime.date(2018,7,31),datetime.date(2018,8,31),datetime.date(2018,9,30),datetime.date(2018,10,31),datetime.date(2018,11,30),datetime.date(2018,12,31),
        datetime.date(2019,1,31),datetime.date(2019,2,28),datetime.date(2019,3,31),datetime.date(2019,4,30),datetime.date(2019,5,31),datetime.date(2019,6,30),datetime.date(2019,7,31),datetime.date(2019,8,31),datetime.date(2019,9,30),datetime.date(2019,10,31),datetime.date(2019,11,30),datetime.date(2019,12,31),
        datetime.date(2020,1,31),datetime.date(2020,2,29),datetime.date(2020,3,31),datetime.date(2020,4,30),datetime.date(2020,5,31)
        ]

dt_param = {'dt_pool_cut':datetime.date(2018,4,16),'dt_effective':datetime.date(2018,7,20),
            'dt_first_calc':datetime.date(2018,7,31),'dt_first_pay':datetime.date(2018,8,26)
            }

date_revolving_pools_cut = [datetime.date(2018,8,1),datetime.date(2018,9,1),datetime.date(2018,10,1),
                            datetime.date(2018,11,1),datetime.date(2018,12,1),datetime.date(2019,1,1)
                            ]

fees = { 'tax':{'rate':0.0634},
        'trustee':{'rate':0.00006},
        'trust_management':{'rate':0.0005},
        'service':{'rate':0.001},
         'pre_issue':{'amount':643692.18},
         'A':{'rate':0.058},
         'B':{'rate':0.068},
         'C':{'rate':0.0},
         }

recycle_adjust_factor = {'rate_recovery_normal':0.75,'rate_recovery_in_0_month':0.70,'rate_recovery_in_1_month':0.50,
                 'rate_recovery_in_2_month':0.35,'rate_recovery_in_3_month':0.25,'rate_recovery_default':0.2,
                 'rate_early_repaid':0.0125}

days_in_a_year = 365
rate_discount = 0.40

amount_total_issuance = 3015926877.69

Bonds = {}
Bonds['A'] = {'ptg':0.67,'amount':amount_total_issuance * 0.67, 'rate':0.058}
Bonds['B'] = {'ptg':0.12,'amount':amount_total_issuance * 0.12,'rate':0.068}
Bonds['C'] = {'ptg':0.21,'amount':amount_total_issuance * 0.21,'rate':0.0}
Bonds['EE'] = {'ptg':0,'amount':10000000000,'rate':0.0}

scenarios = {}
scenarios['best'] = {'rate_default':0.0,'rate_prepay':0.29,'rate_overdue':0.02,'scenario_weight':0.1}
scenarios['better'] = {'rate_default':0.01,'rate_prepay':0.27,'rate_overdue':0.02,'scenario_weight':0.15}
scenarios['benchmark'] = {'rate_default':0.03,'rate_prepay':0.26,'rate_overdue':0.02,'scenario_weight':0.5}
scenarios['worse'] = {'rate_default':0.05,'rate_prepay':0.24,'rate_overdue':0.03,'scenario_weight':0.15}
scenarios['worst'] = {'rate_default':0.07,'rate_prepay':0.22,'rate_overdue':0.03,'scenario_weight':0.1}
#    

#payment_frequency = {'month':1,'quarter':3,'semi-annual':6,'annual':12}

MaxWAScore = 0.06 
 
MinWARate = 0.18
MaxWARate = 0.18*1.01

MaxWALoanRemainTerm = 390

MaxIssueVolumn = 400000000
MinIssueVolumn = 390000000

MaxSCProp = 0.70
MaxSDProp = 0.3 

Targets_all = { 
           'SCp':{'object':'SC Proportion LessThan','object_value_h':MaxSCProp,'object_sign':-1},
           'Credit_Score':{'object':'Weighted Average LessThan','object_value':MaxWAScore,'object_sign':-1},
           'LoanRemainTerm':{'object':'Weighted Average LessThan','object_value':MaxWALoanRemainTerm,'object_sign':-1},
           'Interest_Rate_min':{'object':'Weighted Average GreaterThan','object_value':MinWARate,'object_sign':1},
           'Interest_Rate_max':{'object':'Weighted Average LessThan','object_value':MaxWARate,'object_sign':-1},
           'Amount_Outstanding_max':{'object':'LessThan','object_value':MaxIssueVolumn},
           'Amount_Outstanding_min':{'object':'GreaterThan','object_value':MinIssueVolumn},
           }

Targets_keys = ['Credit_Score',#'LoanRemainTerm',
                'Interest_Rate_min','Interest_Rate_max',
                #'Amount_Outstanding_max','Amount_Outstanding_min'
               ]

Targets = {k:Targets_all[k] for k in Targets_keys}

RS_Group_d = ['Credit_Score','Interest_Rate','Province',#'Usage'#'LoanRemainTerm',
              ]

Distribution_By_Category = [#'Type_Loans',
                            'Interest_Rate',#'Marriagestate',
                            'Province',
                            'Profession','Type_Five_Category',
                            'Usage'#,'Gender'
                            ]

income_bins = [0,50000,100000,150000,200000,2000000,100000000]
age_bins = [17.9999,20,30,40,50,60]
outstanding_principal_bins = [-0.001,2000,4000,6000,8000,10000,20000]
duration_days_bins = [0,180,360,540,720,1080]
past_days_bins = [-0.01,30,60,90,180,360,720,1080]
future_days_bins = [-0.01,30,60,90,180,360,720,1080]
overdue_times_bins = [-0.001,0,1,2,3,4,5,10,100]
dpd_max_bins = [-0.01,0,5,10,15,20,25,30]
dpd_bins = [-0.01,0,30,60,90,120,150,180,360,1000]
#total_fee_rate_bins = [-0.01,0,0.2,0.24,0.36,0.5,0.6]
credit_score_bins = [-0.01,0.05,0.1,0.15,0.2,0.3,0.4,0.5,0.9]

Distribution_By_Bins = {
                        'Income':income_bins,
                        'Age_Project_Start':age_bins,
                        'OutstandingPrincipal':outstanding_principal_bins,
                        'LoanTerm':duration_days_bins,
                        'LoanAge':past_days_bins,
                        'LoanRemainTerm':future_days_bins,
                        'Days_Overdue_Max':dpd_max_bins,
                        'Days_Overdue_Current':dpd_bins,
                        'Overdue_Times':overdue_times_bins,
                        #'综合费用率':total_fee_rate_bins,
                        #'Credit_Score':credit_score_bins
                        }
