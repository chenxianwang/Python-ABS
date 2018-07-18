# -*- coding: utf-8 -*-
"""
Created on Mon Jun 18 16:48:57 2018

@author: Jonah.Chen
"""

import pandas as pd
import numpy as np
from copy import deepcopy
import datetime
from abs_util.util_general import *
from abs_util.util_cf import *
from abs_util.util_sr import *
from dateutil.relativedelta import relativedelta
from Params import *
from Accounts.BondPrinAccount import BondPrinAccount
from Accounts.FeesAccount import FeesAccount
from Accounts.TaxAccount import TaxAccount

logger = get_logger(__name__)

class Waterfall():
    
    def __init__(self,principal_to_pay,principal_to_buy,interest_to_pay,dt_param):

        self.principal_acc_original = deepcopy(principal_to_pay)
        self.interest_acc_original = deepcopy(interest_to_pay)
        
        self.principal_to_pay = principal_to_pay
        self.principal_to_buy = principal_to_buy
        self.interest_to_pay = interest_to_pay
        self.total_to_pay = sum(self.principal_to_pay[k] for k in self.principal_to_pay.keys()) + sum(self.interest_to_pay[k] for k in self.interest_to_pay.keys())
        self.dt_param = dt_param
        self.waterfall = pd.DataFrame()

    def run_Accounts(self,Bonds,RevolvingDeal): # Initalizing BondsCashFlow
        
        logger.info('run_Accounts...')
        
        principal_acc_original = self.principal_acc_original
        interest_acc_original = self.interest_acc_original
        
        principal_to_pay = self.principal_to_pay
        principal_to_buy = self.principal_to_buy
        interest_to_pay = self.interest_to_pay
        #TODO:When to use deepcopy
        tranches_ABC = deepcopy(Bonds)
        
        #preissue_FAcc = FeesAccount('pre_issue',fees)
        tax_Acc = TaxAccount('tax',fees)
        trustee_FAcc = FeesAccount('trustee',fees)
        trust_m_FAcc = FeesAccount('trust_management',fees)
        service_FAcc = FeesAccount('service',fees)
        A_IAcc = FeesAccount('A',fees)
        B_IAcc = FeesAccount('B',fees)
        C_IAcc = FeesAccount('C',fees)
    
        A_PAcc = BondPrinAccount('A',tranches_ABC)
        B_PAcc = BondPrinAccount('B',tranches_ABC)
        C_PAcc = BondPrinAccount('C',tranches_ABC)
        EE_Acc = BondPrinAccount('EE',tranches_ABC)

        #preissue_FAcc
        for date_pay_index,date_pay in enumerate(dates_pay):
            
            #logger.info('B_PAcc.iBalance({0}) is {1}'.format(date_pay,B_PAcc.iBalance(date_pay)))
            pay_for_fee = tax_Acc.pay(date_pay,[interest_to_pay[dates_recycle[date_pay_index]],0][B_PAcc.iBalance(date_pay) == 0])
            pay_for_fee += trustee_FAcc.pay(date_pay,A_PAcc.iBalance(date_pay) + B_PAcc.iBalance(date_pay))
            pay_for_fee += trust_m_FAcc.pay(date_pay,A_PAcc.iBalance(date_pay) + B_PAcc.iBalance(date_pay))
            pay_for_fee += service_FAcc.pay(date_pay,A_PAcc.iBalance(date_pay) + B_PAcc.iBalance(date_pay))
            pay_for_fee += A_IAcc.pay(date_pay,A_PAcc.iBalance(date_pay))
            pay_for_fee += B_IAcc.pay(date_pay,B_PAcc.iBalance(date_pay))
            pay_for_fee += C_IAcc.pay(date_pay,C_PAcc.iBalance(date_pay))
            
            interest_transfer_to_prin = interest_to_pay[dates_recycle[date_pay_index]] - pay_for_fee
            if interest_transfer_to_prin < 0 :
                logger.info('interest_transfer_to_prin on {0} is less than 0: {1}'.format(date_pay,interest_transfer_to_prin))
            
            principal_to_pay[dates_recycle[date_pay_index]] += interest_transfer_to_prin
            
            if RevolvingDeal == True:
                if date_pay >= date_revolving_pools_cut[-1] + relativedelta(months=1):
                    amount_available_for_prin = principal_to_pay[dates_recycle[date_pay_index]]
                else: amount_available_for_prin = 0
                amount_available_for_prin = A_PAcc.pay_then_ToNext(date_pay,amount_available_for_prin)
                amount_available_for_prin = B_PAcc.pay_then_ToNext(date_pay,amount_available_for_prin)
                amount_available_for_prin = C_PAcc.pay_then_ToNext(date_pay,amount_available_for_prin)
                amount_available_for_prin = EE_Acc.pay_then_ToNext(date_pay,amount_available_for_prin)
            else:
                amount_available_for_prin = principal_to_pay[dates_recycle[date_pay_index]]
                amount_available_for_prin = A_PAcc.pay_then_ToNext(date_pay,amount_available_for_prin)
                amount_available_for_prin = B_PAcc.pay_then_ToNext(date_pay,amount_available_for_prin)
                amount_available_for_prin = C_PAcc.pay_then_ToNext(date_pay,amount_available_for_prin)
                amount_available_for_prin = EE_Acc.pay_then_ToNext(date_pay,amount_available_for_prin)
            
#            amount_available_for_prin = principal_to_pay[dates_recycle[date_pay_index]]
#            logger.info('amount_available_for_prin is {0}'.format(amount_available_for_prin))
#            
#            amount_available_for_prin = A_PAcc.pay_then_ToNext(date_pay,amount_available_for_prin)
#            amount_available_for_prin = B_PAcc.pay_then_ToNext(date_pay,amount_available_for_prin)
#            amount_available_for_prin = C_PAcc.pay_then_ToNext(date_pay,amount_available_for_prin)
#            amount_available_for_prin = EE_Acc.pay_then_ToNext(date_pay,amount_available_for_prin)

            #logger.info('Loop Done for {0}'.format(date_pay))        
            
            #interest_acc_original[dates_recycle[date_pay_index]] -= pay_for_fee
            
        
        AP_PAcc_pay_wf = pd.DataFrame(list(principal_acc_original.items()), columns=['date_recycle', 'principal_prepared_to_pay'])
        AP_PAcc_buy_wf = pd.DataFrame(list(principal_to_buy.items()), columns=['date_recycle', 'principal_prepared_to_buy'])
        AP_IAcc_pay_wf = pd.DataFrame(list(interest_acc_original.items()), columns=['date_recycle', 'interest_prepared_to_pay'])
        
        A_Principal_wf = pd.DataFrame(list(A_PAcc.receive.items()), columns=['date_pay', 'amount_pay_A_principal'])
        B_Principal_wf = pd.DataFrame(list(B_PAcc.receive.items()), columns=['date_pay', 'amount_pay_B_principal'])
        C_Principal_wf = pd.DataFrame(list(C_PAcc.receive.items()), columns=['date_pay', 'amount_pay_C_principal'])
        EE_wf = pd.DataFrame(list(EE_Acc.receive.items()), columns=['date_pay', 'amount_pay_EE_principal'])
        
        A_Interest_wf = pd.DataFrame(list(A_IAcc.receive.items()), columns=['date_pay', 'amount_pay_A_interest'])
        B_Interest_wf = pd.DataFrame(list(B_IAcc.receive.items()), columns=['date_pay', 'amount_pay_B_interest'])
        C_Interest_wf = pd.DataFrame(list(C_IAcc.receive.items()), columns=['date_pay', 'amount_pay_C_interest'])
        service_fee_wf = pd.DataFrame(list(service_FAcc.receive.items()), columns=['date_pay', 'fee_service'])
        tax_wf = pd.DataFrame(list(tax_Acc.receive.items()), columns=['date_pay', 'fee_tax'])
        trustee_wf = pd.DataFrame(list(trustee_FAcc.receive.items()), columns=['date_pay', 'fee_trustee'])
        trust_m_wf = pd.DataFrame(list(trust_m_FAcc.receive.items()), columns=['date_pay', 'fee_trust_m'])
        
        A_Balance_wf = pd.DataFrame(list(A_PAcc.balance.items()), columns=['date_pay', 'amount_outstanding_A_principal'])
        B_Balance_wf = pd.DataFrame(list(B_PAcc.balance.items()), columns=['date_pay', 'amount_outstanding_B_principal'])
        C_Balance_wf = pd.DataFrame(list(C_PAcc.balance.items()), columns=['date_pay', 'amount_outstanding_C_principal'])
        EE_Balance_wf = pd.DataFrame(list(EE_Acc.balance.items()), columns=['date_pay', 'amount_outstanding_EE_principal'])
        
        AssetPool_wf = AP_PAcc_pay_wf\
                        .merge(AP_PAcc_buy_wf,left_on='date_recycle',right_on='date_recycle',how='outer')\
                        .merge(AP_IAcc_pay_wf,left_on='date_recycle',right_on='date_recycle',how='outer')
                        
        AssetPool_wf['date_pay'] = dates_pay
        
        Bond_wf = A_Principal_wf\
                  .merge(B_Principal_wf,left_on='date_pay',right_on='date_pay',how='outer')\
                  .merge(C_Principal_wf,left_on='date_pay',right_on='date_pay',how='outer')\
                  .merge(EE_wf,left_on='date_pay',right_on='date_pay',how='outer')\
                  .merge(A_Interest_wf,left_on='date_pay',right_on='date_pay',how='outer')\
                  .merge(B_Interest_wf,left_on='date_pay',right_on='date_pay',how='outer')\
                  .merge(C_Interest_wf,left_on='date_pay',right_on='date_pay',how='outer')\
                  .merge(service_fee_wf,left_on='date_pay',right_on='date_pay',how='outer')\
                  .merge(tax_wf,left_on='date_pay',right_on='date_pay',how='outer')\
                  .merge(trustee_wf,left_on='date_pay',right_on='date_pay',how='outer')\
                  .merge(trust_m_wf,left_on='date_pay',right_on='date_pay',how='outer')\
                  .merge(A_Balance_wf,left_on='date_pay',right_on='date_pay',how='outer')\
                  .merge(B_Balance_wf,left_on='date_pay',right_on='date_pay',how='outer')\
                  .merge(C_Balance_wf,left_on='date_pay',right_on='date_pay',how='outer')\
                  .merge(EE_Balance_wf,left_on='date_pay',right_on='date_pay',how='outer')\
                  .merge(AssetPool_wf,left_on='date_pay',right_on='date_pay',how='outer')\
                        
        
        logger.info('total principal payment is {0}'.format(sum(Bond_wf[['amount_pay_A_principal','amount_pay_B_principal','amount_pay_C_principal']].sum())))
        
        self.waterfall = Bond_wf
    
    def BasicInfo_calculator(self,tranches_ABC):
        
        logger.info('BasicInfo_calculator...')
        tranches_cf = self.waterfall
        dt_param = self.dt_param
    
        tranches_cf['years_interest_calc_this_period'] = (tranches_cf['date_pay'] - (tranches_cf['date_pay']+relativedelta(months= -1))).dt.days/days_in_a_year
        tranches_cf['years_interest_calc_cumulative'] = tranches_cf['years_interest_calc_this_period'].cumsum()
        name_tranche = ['A','B','C']
            
        WA_term = []
        date_maturity_predict = []
        maturity_term = []
        
        for _tranche_index,_tranche_name in enumerate(name_tranche):
            WA_term.append(sum(tranches_cf['amount_pay_' + _tranche_name + '_principal'] * tranches_cf['years_interest_calc_cumulative']) / sum(tranches_cf['amount_pay_' + _tranche_name + '_principal']))
            date_maturity_predict.append(tranches_cf.iloc[tranches_cf['amount_outstanding_' + _tranche_name + '_principal'].idxmin()]['date_pay'])
            maturity_term.append((date_maturity_predict[_tranche_index] - dt_param['dt_effective']).days / days_in_a_year )
        
        tranche_basic_info = pd.DataFrame({'name_tranche':name_tranche,
                                           'WA_term':WA_term,
                                           'date_maturity_predict':date_maturity_predict,
                                           'maturity_term':maturity_term,
                                          })
    
        return tranche_basic_info
    
    def CR_calculator(self):
        tranches_cf = self.waterfall
        Cover_ratio_Senior = self.total_to_pay / sum(tranches_cf[['amount_pay_A_principal','amount_pay_A_interest']].sum())
        Cover_ratio_Mezz = (self.total_to_pay - sum(tranches_cf[['amount_pay_A_principal','amount_pay_A_interest']].sum()) ) / sum(tranches_cf[['amount_pay_B_principal','amount_pay_B_interest']].sum())
        
        CoverRation = pd.DataFrame({'Cover_ratio_Senior':[Cover_ratio_Senior],
                                    'Cover_ratio_Mezz':[Cover_ratio_Mezz]
                                    })
                                   
        return CoverRation                           
    
    def NPV_calculator(self):
        tranches_cf = self.waterfall
        total_recycle = [self.principal_to_pay[k] for k in self.principal_to_pay.keys()] + [self.interest_to_pay[k] for k in self.interest_to_pay.keys()]

        NPV_asset_pool = np.npv(rate_discount / 12,total_recycle) / (1 + rate_discount / 12 )
        
        total_pay_to_Originator = tranches_cf['amount_pay_C_principal'] + tranches_cf['amount_pay_C_interest'] + tranches_cf['amount_pay_EE_principal']+ tranches_cf['fee_service']
        NPV_originator = np.npv(rate_discount / 12,total_pay_to_Originator) / (1 + rate_discount / 12 )  #
        
        NPVs = pd.DataFrame({'NPV_asset_pool':[NPV_asset_pool],
                            'NPV_originator':[NPV_originator]
                            })
    
        return NPVs
