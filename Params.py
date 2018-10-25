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
amount_ReserveAcount = 1000000
ADate = datetime.date(2018,8,1)


if ProjectName == 'ABS9':
    amount_total_issuance = 3015926877.69
    Bonds = {}
    Bonds['A'] = {'ptg':0.6714,'amount':2025000000, 'rate':0.05750}
    Bonds['B'] = {'ptg':0.1107,'amount':334000000,'rate':0.07190}
    Bonds['C'] = {'ptg':0.2178,'amount':656926877.69,'rate':0.0}
    Bonds['EE'] = {'ptg':0,'amount':100000000000,'rate':0.0}
    rate_discount = 0.2
    dt_param = {'dt_pool_cut':datetime.date(2018,4,16),'dt_effective':datetime.date(2018,7,24)}

elif ProjectName == 'ABS10':
    amount_total_issuance = 3014292721.30
    Bonds = {}
    Bonds['A'] = {'ptg':0.6502,'amount':1960000000, 'rate':0.0550}
    Bonds['B'] = {'ptg':0.1287,'amount':388000000,'rate':0.0720}
    Bonds['C'] = {'ptg':0.2211,'amount':666292721.30,'rate':0.0}
    Bonds['EE'] = {'ptg':0,'amount':100000000000,'rate':0.0}
    rate_discount = 0.18
    dt_param = {'dt_pool_cut':datetime.date(2018,7,23),'dt_effective':datetime.date(2018,10,16)}

elif ProjectName == 'ABS11':
    amount_total_issuance = 2501010000.7
    Bonds = {}
    Bonds['A'] = {'ptg':0.6697,'amount':1675000000 , 'rate':0.05750}
    Bonds['B'] = {'ptg':0.12,'amount':300000000,'rate':0.07190}
    Bonds['C'] = {'ptg':0.2103,'amount':526010000.7,'rate':0.0}
    Bonds['EE'] = {'ptg':0,'amount':100000000000,'rate':0.0}
    rate_discount = 0.185
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
    #Redeem_or_Not = True
    Redeem_or_Not = False
except(NameError):
    pass
############################################################
fees = { 'tax':{'rate':0.032621359223},
        'pay_interest_service':{'rate':0.00005},
        'pre_issue':{'amount':245797.32215745+500000},
        'trustee':{'dates_to_calc':[dt_param['dt_effective']]+dates_recycle,'rate':0.0005},
        'custodian':{'dates_to_calc':[dt_param['dt_effective']]+dates_recycle,'rate':0.0000539},
        'servicer':{'dates_to_calc':[dt_param['dt_pool_cut']]+dates_recycle,'rate':0.001},
         'A':{'dates_to_calc':[dt_param['dt_effective']]+dates_pay},
         'B':{'dates_to_calc':[dt_param['dt_effective']]+dates_pay},
         'C':{'dates_to_calc':[dt_param['dt_effective']]+dates_pay},
         }
for name_Tranche in ['A','B','C']:
    fees[name_Tranche]['rate'] = Bonds[name_Tranche]['rate']
################################################################


scenarios = {}
#scenarios['benchmark'] = {'M0_2_ERM0':0.9805,'M0_2_M1':0.0858,'M1_2_M0M2':0.3896,'M2_2_M0M3':0.7133,'M3_2_M0D':0.7310,'D_2_RL':0.7799,'scenario_weight':0.1} #ER 0.01%, PD = 1.455% ,PDL = 99%

scenarios['stress_A'] = {'M0_2_ERM0':0.9805,'M0_2_M1':0.429,'M1_2_M0M2':0.3896,'M2_2_M0M3':0.7133,'M3_2_M0D':0.7310,'D_2_RL':1,'scenario_weight':0.1} #ER 0.01%, PD = 1.455% ,PDL = 99%
scenarios['stress_B'] = {'M0_2_ERM0':0.9805,'M0_2_M1':0.3689,'M1_2_M0M2':0.3896,'M2_2_M0M3':0.7133,'M3_2_M0D':0.7310,'D_2_RL':0.8,'scenario_weight':0.1} #ER 0.01%, PD = 1.455% ,PDL = 99%

#payment_frequency = {'month':1,'quarter':3,'semi-annual':6,'annual':12}

MaxWAScore = 0.065
MinWAScore = 0.0645

MinWARate = 0.18
MaxWARate = 0.185

MaxWALoanTerm = 450

MaxIssueVolumn = 3000000000
MinIssueVolumn = 0

MaxSCProp = 0.70
MaxSDProp = 0.3 

Targets_all = { 
           'SCp':{'object':'SC Proportion LessThan','object_value_h':MaxSCProp,'object_sign':-1},
           'Credit_Score_max':{'object':'Weighted Average LessThan','object_value':MaxWAScore,'object_sign':-1},
           'Credit_Score_min':{'object':'Weighted Average GreaterThan','object_value':MinWAScore,'object_sign':1},
           'LoanTerm':{'object':'Weighted Average LessThan','object_value':MaxWALoanTerm,'object_sign':-1},
           'Interest_Rate_min':{'object':'Weighted Average GreaterThan','object_value':MinWARate,'object_sign':1},
           'Interest_Rate_max':{'object':'Weighted Average LessThan','object_value':MaxWARate,'object_sign':-1},
           'Amount_Outstanding_max':{'object':'LessThan','object_value':MaxIssueVolumn},
           'Amount_Outstanding_min':{'object':'GreaterThan','object_value':MinIssueVolumn},
           }

Targets_keys = ['Credit_Score_max',#'Credit_Score_min',
                'Interest_Rate_min',#'Interest_Rate_max',
                #'LoanTerm',#'',
                #'Amount_Outstanding_max',
                'Amount_Outstanding_min',
               ]

RS_Group_d = ['Credit_Score',
              'Interest_Rate',#'Usage','LoanRemainTerm'#,'Province',#'Usage'
              #'LoanTerm',
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
outstanding_principal_bins = [-0.001,2000,4000,6000,8000,10000,20000,1000000]
credit_bins = [-0.001,2000,4000,6000,8000,10000,20000,1000000]

duration_days_bins = [0,90,180,360,540,720,1080,3000]
past_days_bins = [-0.01,90,180,360,540,720,1080,3000]
future_days_bins = [-0.01,90,180,360,540,720,1080,3000]

duration_months_bins = [0,5.999,9.999,12,18,24,31]

overdue_times_bins = [-0.001,0,1,2,5,10,15,20,25,30]
dpd_max_bins = [-0.01,0,5,10,15,20,25,30]
dpd_bins = [-0.01,0,30,60,90,120,150,180,360,1000]
#total_fee_rate_bins = [-0.01,0,0.2,0.24,0.36,0.5,0.6]
credit_score_bins = [-0.01,0.01,0.02,0.03,0.04,0.05,0.06,0.07,0.08,0.09,0.1,
                     0.11,0.12,0.13,0.14,0.15,0.2,0.25,1]

Distribution_By_Bins = {
                        'Income':income_bins,
                        'Age_Project_Start':age_bins,
                        'OutstandingPrincipal':outstanding_principal_bins,
                        'Credit':credit_bins,
                        'LoanTerm':duration_days_bins,
                        'LoanAge':past_days_bins,
                        'LoanRemainTerm':future_days_bins,
                        'Term_Contract':duration_months_bins,
                        'Days_Overdue_Max':dpd_max_bins,
                        'Days_Overdue_Current':dpd_bins,
                        'Overdue_Times':overdue_times_bins,
                        'Credit_Score':credit_score_bins
                        }