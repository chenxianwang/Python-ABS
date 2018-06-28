# -*- coding: utf-8 -*-
"""
Created on Fri Jun 30 12:05:38 2017

@author: Jonah.Chen
"""
import pandas as pd
from util import get_next_eom,save_to_excel
from dateutil.relativedelta import relativedelta


def run_term_by_term(tranches_cf,param,tranches_ABC):

    for term in range(1,60):
        tranches_cf = run_accounts_by_term(tranches_cf,term,param,tranches_ABC)
    
#Total Pay
    tranches_cf['amount_pay_Senior'] = tranches_cf['amount_pay_Senior_principal'] + tranches_cf['amount_pay_Senior_interest']
    tranches_cf['amount_pay_Mezz'] = tranches_cf['amount_pay_Mezz_principal'] + tranches_cf['amount_pay_Mezz_interest'] 	 
    tranches_cf['amount_pay_Sub'] = 	 tranches_cf['amount_pay_Sub_principal'] + tranches_cf['amount_pay_Sub_interest']
    tranches_cf['amount_pay_all_tranches'] = tranches_cf['amount_pay_Senior'] + tranches_cf['amount_pay_Mezz'] + tranches_cf['amount_pay_Sub']

    waterfall = tranches_cf[['date_interest_calc_end',
                             'amount_pay_Senior_principal',
                             'amount_pay_Mezz_principal',
                             'amount_pay_Sub_principal',
                             'amount_extra_earning'
                            ]]
    
    save_to_excel(waterfall,'tranches_waterfall')
    
    return tranches_cf


def run_accounts_by_term(tranches_cf,term,param,tranches_ABC):

    #Principal outstanding account at begin this term
    tranches_cf['amount_outstanding_A1_principal_begin'][term] = tranches_cf['amount_outstanding_A1_principal_end'][term-1]
    tranches_cf['amount_outstanding_A2_principal_begin'][term] = tranches_cf['amount_outstanding_A2_principal_end'][term-1]
    tranches_cf['amount_outstanding_A3_principal_begin'][term] = tranches_cf['amount_outstanding_A3_principal_end'][term-1]
    tranches_cf['amount_outstanding_A4_principal_begin'][term] = tranches_cf['amount_outstanding_A4_principal_end'][term-1]
    tranches_cf['amount_outstanding_A5_principal_begin'][term] = tranches_cf['amount_outstanding_A5_principal_end'][term-1]
    tranches_cf['amount_outstanding_A6_principal_begin'][term] = tranches_cf['amount_outstanding_A6_principal_end'][term-1]
    
    tranches_cf['amount_outstanding_B_principal_begin'][term] = tranches_cf['amount_outstanding_B_principal_end'][term-1]
    
    tranches_cf['amount_outstanding_C_principal_begin'][term] = tranches_cf['amount_outstanding_C_principal_end'][term-1]
    
    tranches_cf['amount_outstanding_Senior_principal_begin'][term] = tranches_cf['amount_outstanding_Senior_principal_end'][term-1]
    
    tranches_cf['amount_outstanding_Mezz_principal_begin'][term] = tranches_cf['amount_outstanding_Mezz_principal_end'][term-1]
    
    tranches_cf['amount_outstanding_Sub_principal_begin'][term] = tranches_cf['amount_outstanding_Sub_principal_end'][term-1]
    
    tranches_cf['amount_outstanding_principal_all_tranches_begin'][term] = tranches_cf['amount_outstanding_principal_all_tranches_end'][term-1]
 
    #Pay the fees this term
    tranches_cf['fee_tax'][term] = tranches_cf['amount_recycled_interest'][term] * param['rate_tax']
    tranches_cf['fee_trustee'][term] = tranches_cf['amount_outstanding_principal_all_tranches_begin'][term] * param['rate_trustee'] * tranches_cf['years_interest_calc_this_period'][term]
    tranches_cf['fee_trust_management'][term] = tranches_cf['amount_outstanding_principal_all_tranches_begin'][term] * param['rate_trust_management'] * tranches_cf['years_interest_calc_this_period'][term] 	 
    tranches_cf['fee_service'][term] = tranches_cf['amount_outstanding_principal_all_tranches_begin'][term] * param['rate_service'] * tranches_cf['years_interest_calc_this_period'][term] 	 
    tranches_cf['fee_total'][term] = tranches_cf['fee_tax'][term] + tranches_cf['fee_trustee'][term] + tranches_cf['fee_trust_management'][term] + tranches_cf['fee_service'][term]

#Pay interest this term
    tranches_cf['amount_pay_A1_interest'][term] = tranches_cf['amount_outstanding_A1_principal_begin'][term] * tranches_ABC['A1']['rate'] * tranches_cf['years_interest_calc_this_period'][term]
    tranches_cf['amount_pay_A2_interest'][term] = tranches_cf['amount_outstanding_A2_principal_begin'][term] * tranches_ABC['A2']['rate'] * tranches_cf['years_interest_calc_this_period'][term]
    tranches_cf['amount_pay_A3_interest'][term] = tranches_cf['amount_outstanding_A3_principal_begin'][term] * tranches_ABC['A3']['rate'] * tranches_cf['years_interest_calc_this_period'][term]
    tranches_cf['amount_pay_A4_interest'][term] = tranches_cf['amount_outstanding_A4_principal_begin'][term] * tranches_ABC['A4']['rate'] * tranches_cf['years_interest_calc_this_period'][term]
    tranches_cf['amount_pay_A5_interest'][term] = tranches_cf['amount_outstanding_A5_principal_begin'][term] * tranches_ABC['A5']['rate'] * tranches_cf['years_interest_calc_this_period'][term]
    tranches_cf['amount_pay_A6_interest'][term] = tranches_cf['amount_outstanding_A6_principal_begin'][term] * tranches_ABC['A6']['rate'] * tranches_cf['years_interest_calc_this_period'][term]
               
    tranches_cf['amount_pay_B_interest'][term] =  tranches_cf['amount_outstanding_B_principal_begin'][term] * tranches_ABC['B']['rate'] * tranches_cf['years_interest_calc_this_period'][term]
               
    tranches_cf['amount_pay_C_interest'][term] = tranches_cf['amount_outstanding_C_principal_begin'][term] * tranches_ABC['C']['rate'] * tranches_cf['years_interest_calc_this_period'][term]

    tranches_cf['amount_pay_Senior_interest'][term] = tranches_cf['amount_pay_A1_interest'][term] + tranches_cf['amount_pay_A2_interest'][term] + tranches_cf['amount_pay_A3_interest'][term] + tranches_cf['amount_pay_A4_interest'][term] + tranches_cf['amount_pay_A5_interest'][term] + tranches_cf['amount_pay_A6_interest'][term]
    tranches_cf['amount_pay_Mezz_interest'][term] = tranches_cf['amount_pay_B_interest'][term] 	 
    tranches_cf['amount_pay_Sub_interest'][term] = 	 tranches_cf['amount_pay_C_interest'][term]
    tranches_cf['amount_pay_all_tranches_interest'][term] = tranches_cf['amount_pay_Senior_interest'][term] + tranches_cf['amount_pay_Mezz_interest'][term] + tranches_cf['amount_pay_Sub_interest'][term]
#Sum fees and interest    
    tranches_cf['amount_to_pay_interest_and_fee'][term] = tranches_cf['amount_pay_all_tranches_interest'][term] + tranches_cf['fee_total'][term] 

#Account transfer this term
    tranches_cf['amount_remain_after_interest_and_fee_payment'][term] = tranches_cf['amount_available_to_allocate'][term] - tranches_cf['amount_to_pay_interest_and_fee'][term]
    tranches_cf['amount_remain_in_interest_account'][term] = tranches_cf['amount_recycled_interest'][term] + tranches_cf['amount_reserver_last_period'][term] - tranches_cf['amount_to_pay_interest_and_fee'][term]
    tranches_cf['amount_principal_to_interest'][term] = [0,-tranches_cf['amount_remain_in_interest_account'][term]][tranches_cf['amount_remain_in_interest_account'][term]<0]
    tranches_cf['amount_principal_after_transfer_out'][term] = tranches_cf['amount_recycled_principal'][term] - tranches_cf['amount_principal_to_interest'][term]
    tranches_cf['amount_principal_after_transfer_out_and_in'][term] = tranches_cf['amount_principal_after_transfer_out'][term] + tranches_cf['amount_remain_in_interest_account'][term]
    tranches_cf['amount_extra_earning'][term] = tranches_cf['amount_principal_after_transfer_out_and_in'][term]

#Pay principal this term
    tranches_cf['amount_pay_A1_principal'][term] = [tranches_cf['amount_outstanding_A1_principal_begin'][term],tranches_cf['amount_extra_earning'][term]][tranches_cf['amount_extra_earning'][term] < tranches_cf['amount_outstanding_A1_principal_begin'][term]]
    tranches_cf['amount_extra_earning'][term] -= tranches_cf['amount_pay_A1_principal'][term] 
    tranches_cf['amount_pay_A2_principal'][term] = [tranches_cf['amount_outstanding_A2_principal_begin'][term],tranches_cf['amount_extra_earning'][term]][tranches_cf['amount_extra_earning'][term] < tranches_cf['amount_outstanding_A2_principal_begin'][term]]
    tranches_cf['amount_extra_earning'][term] -= tranches_cf['amount_pay_A2_principal'][term]
    tranches_cf['amount_pay_A3_principal'][term] = [tranches_cf['amount_outstanding_A3_principal_begin'][term],tranches_cf['amount_extra_earning'][term]][tranches_cf['amount_extra_earning'][term] < tranches_cf['amount_outstanding_A3_principal_begin'][term]]
    tranches_cf['amount_extra_earning'][term] -= tranches_cf['amount_pay_A3_principal'][term]
    tranches_cf['amount_pay_A4_principal'][term] = [tranches_cf['amount_outstanding_A4_principal_begin'][term],tranches_cf['amount_extra_earning'][term]][tranches_cf['amount_extra_earning'][term] < tranches_cf['amount_outstanding_A4_principal_begin'][term]]
    tranches_cf['amount_extra_earning'][term] -= tranches_cf['amount_pay_A4_principal'][term]
    tranches_cf['amount_pay_A5_principal'][term] = [tranches_cf['amount_outstanding_A5_principal_begin'][term],tranches_cf['amount_extra_earning'][term]][tranches_cf['amount_extra_earning'][term] < tranches_cf['amount_outstanding_A5_principal_begin'][term]]
    tranches_cf['amount_extra_earning'][term] -= tranches_cf['amount_pay_A5_principal'][term]
    tranches_cf['amount_pay_A6_principal'][term] = [tranches_cf['amount_outstanding_A6_principal_begin'][term],tranches_cf['amount_extra_earning'][term]][tranches_cf['amount_extra_earning'][term] < tranches_cf['amount_outstanding_A6_principal_begin'][term]]
    tranches_cf['amount_extra_earning'][term] -= tranches_cf['amount_pay_A6_principal'][term] 
    
    tranches_cf['amount_pay_B_principal'][term] = [tranches_cf['amount_outstanding_B_principal_begin'][term],tranches_cf['amount_extra_earning'][term]][tranches_cf['amount_extra_earning'][term] < tranches_cf['amount_outstanding_B_principal_begin'][term]]
    tranches_cf['amount_extra_earning'][term] -= tranches_cf['amount_pay_B_principal'][term]

    tranches_cf['amount_pay_C_principal'][term] = [tranches_cf['amount_outstanding_C_principal_begin'][term],tranches_cf['amount_extra_earning'][term]][tranches_cf['amount_extra_earning'][term] < tranches_cf['amount_outstanding_C_principal_begin'][term]]
    tranches_cf['amount_extra_earning'][term] -= tranches_cf['amount_pay_C_principal'][term]

    tranches_cf['amount_pay_Senior_principal'][term] = tranches_cf['amount_pay_A1_principal'][term] + tranches_cf['amount_pay_A2_principal'][term] + tranches_cf['amount_pay_A3_principal'][term] + tranches_cf['amount_pay_A4_principal'][term] + tranches_cf['amount_pay_A5_principal'][term] + tranches_cf['amount_pay_A6_principal'][term]
    tranches_cf['amount_pay_Mezz_principal'][term] = tranches_cf['amount_pay_B_principal'][term] 	 
    tranches_cf['amount_pay_Sub_principal'][term] = 	 tranches_cf['amount_pay_C_principal'][term]
    tranches_cf['amount_pay_all_tranches_principal'][term] = tranches_cf['amount_pay_Senior_principal'][term] + tranches_cf['amount_pay_Mezz_principal'][term] + tranches_cf['amount_pay_Sub_principal'][term]

#Principal account at end this term
    tranches_cf['amount_outstanding_A1_principal_end'][term] = tranches_cf['amount_outstanding_A1_principal_begin'][term] - tranches_cf['amount_pay_A1_principal'][term]
    tranches_cf['amount_outstanding_A2_principal_end'][term] = tranches_cf['amount_outstanding_A2_principal_begin'][term] - tranches_cf['amount_pay_A2_principal'][term]
    tranches_cf['amount_outstanding_A3_principal_end'][term] = tranches_cf['amount_outstanding_A3_principal_begin'][term] - tranches_cf['amount_pay_A3_principal'][term]
    tranches_cf['amount_outstanding_A4_principal_end'][term] = tranches_cf['amount_outstanding_A4_principal_begin'][term] - tranches_cf['amount_pay_A4_principal'][term]
    tranches_cf['amount_outstanding_A5_principal_end'][term] = tranches_cf['amount_outstanding_A5_principal_begin'][term] - tranches_cf['amount_pay_A5_principal'][term]
    tranches_cf['amount_outstanding_A6_principal_end'][term] = tranches_cf['amount_outstanding_A6_principal_begin'][term] - tranches_cf['amount_pay_A6_principal'][term]
    
    tranches_cf['amount_outstanding_B_principal_end'][term] = tranches_cf['amount_outstanding_B_principal_begin'][term] - tranches_cf['amount_pay_B_principal'][term]
    
    tranches_cf['amount_outstanding_C_principal_end'][term] = tranches_cf['amount_outstanding_C_principal_begin'][term] - tranches_cf['amount_pay_C_principal'][term]
#    
    tranches_cf['amount_outstanding_Senior_principal_end'][term] = tranches_cf['amount_outstanding_A1_principal_end'][term] \
                                                              +tranches_cf['amount_outstanding_A2_principal_end'][term] \
                                                              +tranches_cf['amount_outstanding_A3_principal_end'][term] \
                                                              +tranches_cf['amount_outstanding_A4_principal_end'][term] \
                                                              +tranches_cf['amount_outstanding_A5_principal_end'][term] \
                                                              +tranches_cf['amount_outstanding_A6_principal_end'][term]
    
    tranches_cf['amount_outstanding_Mezz_principal_end'][term] = tranches_cf['amount_outstanding_B_principal_end'][term]
    
    tranches_cf['amount_outstanding_Sub_principal_end'][term] = tranches_cf['amount_outstanding_C_principal_end'][term]
    
    tranches_cf['amount_outstanding_principal_all_tranches_end'][term] = tranches_cf['amount_outstanding_Senior_principal_end'][term] \
                                                                    +tranches_cf['amount_outstanding_Mezz_principal_end'][term] \
                                                                    +tranches_cf['amount_outstanding_Sub_principal_end'][term]
 
    return tranches_cf

def initializing_accounts(tranches_cf,param,tranches_ABC):
    
#Principal outstanding account at begin
    tranches_cf['amount_outstanding_A1_principal_begin'] = tranches_ABC['A1']['amount']
    tranches_cf['amount_outstanding_A2_principal_begin'] = tranches_ABC['A2']['amount']
    tranches_cf['amount_outstanding_A3_principal_begin'] = tranches_ABC['A3']['amount']
    tranches_cf['amount_outstanding_A4_principal_begin'] = tranches_ABC['A4']['amount']
    tranches_cf['amount_outstanding_A5_principal_begin'] = tranches_ABC['A5']['amount']
    tranches_cf['amount_outstanding_A6_principal_begin'] = tranches_ABC['A6']['amount']
    
    tranches_cf['amount_outstanding_B_principal_begin'] = tranches_ABC['B']['amount']
    
    tranches_cf['amount_outstanding_C_principal_begin'] = tranches_ABC['C']['amount']
    
    tranches_cf['amount_outstanding_Senior_principal_begin'] = tranches_cf['amount_outstanding_A1_principal_begin'] \
                                                              +tranches_cf['amount_outstanding_A2_principal_begin'] \
                                                              +tranches_cf['amount_outstanding_A3_principal_begin'] \
                                                              +tranches_cf['amount_outstanding_A4_principal_begin'] \
                                                              +tranches_cf['amount_outstanding_A5_principal_begin'] \
                                                              +tranches_cf['amount_outstanding_A6_principal_begin']
    
    tranches_cf['amount_outstanding_Mezz_principal_begin'] = tranches_cf['amount_outstanding_B_principal_begin']
    
    tranches_cf['amount_outstanding_Sub_principal_begin'] = tranches_cf['amount_outstanding_C_principal_begin']
    
    tranches_cf['amount_outstanding_principal_all_tranches_begin'] = tranches_cf['amount_outstanding_Senior_principal_begin'] \
                                                                    +tranches_cf['amount_outstanding_Mezz_principal_begin'] \
                                                                    +tranches_cf['amount_outstanding_Sub_principal_begin']
 
    
    #Pay the fees    
    tranches_cf['fee_tax'] = tranches_cf['amount_recycled_interest'] * param['rate_tax']
    tranches_cf['fee_trustee'] = tranches_cf['amount_outstanding_principal_all_tranches_begin'] * param['rate_trustee'] * tranches_cf['years_interest_calc_this_period']
    tranches_cf['fee_trust_management'] = tranches_cf['amount_outstanding_principal_all_tranches_begin'] * param['rate_trust_management'] * tranches_cf['years_interest_calc_this_period'] 	 
    tranches_cf['fee_service'] = tranches_cf['amount_outstanding_principal_all_tranches_begin'] * param['rate_service'] * tranches_cf['years_interest_calc_this_period'] 	 
    tranches_cf['fee_total'] = tranches_cf['fee_tax'] + tranches_cf['fee_trustee'] + tranches_cf['fee_trust_management'] + tranches_cf['fee_service']

#Pay interest    
    tranches_cf['amount_pay_A1_interest'] = tranches_cf['amount_outstanding_A1_principal_begin'] * tranches_ABC['A1']['rate'] * tranches_cf['years_interest_calc_this_period']
    tranches_cf['amount_pay_A2_interest'] = tranches_cf['amount_outstanding_A2_principal_begin'] * tranches_ABC['A2']['rate'] * tranches_cf['years_interest_calc_this_period']
    tranches_cf['amount_pay_A3_interest'] = tranches_cf['amount_outstanding_A3_principal_begin'] * tranches_ABC['A3']['rate'] * tranches_cf['years_interest_calc_this_period']
    tranches_cf['amount_pay_A4_interest'] = tranches_cf['amount_outstanding_A4_principal_begin'] * tranches_ABC['A4']['rate'] * tranches_cf['years_interest_calc_this_period']
    tranches_cf['amount_pay_A5_interest'] = tranches_cf['amount_outstanding_A5_principal_begin'] * tranches_ABC['A5']['rate'] * tranches_cf['years_interest_calc_this_period']
    tranches_cf['amount_pay_A6_interest'] = tranches_cf['amount_outstanding_A6_principal_begin'] * tranches_ABC['A6']['rate'] * tranches_cf['years_interest_calc_this_period']
               
    tranches_cf['amount_pay_B_interest'] =  tranches_cf['amount_outstanding_B_principal_begin'] * tranches_ABC['B']['rate'] * tranches_cf['years_interest_calc_this_period']
               
    tranches_cf['amount_pay_C_interest'] = tranches_cf['amount_outstanding_C_principal_begin'] * tranches_ABC['C']['rate'] * tranches_cf['years_interest_calc_this_period']

    tranches_cf['amount_pay_Senior_interest'] = tranches_cf['amount_pay_A1_interest'] + tranches_cf['amount_pay_A2_interest'] + tranches_cf['amount_pay_A3_interest'] + tranches_cf['amount_pay_A4_interest'] + tranches_cf['amount_pay_A5_interest'] + tranches_cf['amount_pay_A6_interest']
    tranches_cf['amount_pay_Mezz_interest'] = tranches_cf['amount_pay_B_interest'] 	 
    tranches_cf['amount_pay_Sub_interest'] = 	 tranches_cf['amount_pay_C_interest']
    tranches_cf['amount_pay_all_tranches_interest'] = tranches_cf['amount_pay_Senior_interest'] + tranches_cf['amount_pay_Mezz_interest'] + tranches_cf['amount_pay_Sub_interest']
#Sum fees and interest    
    tranches_cf['amount_to_pay_interest_and_fee'] = tranches_cf['amount_pay_all_tranches_interest'] + tranches_cf['fee_total'] 
    tranches_cf['amount_to_pay_interest_and_fee'][0] += param['fee_pay_in_one_time']

#Account transfer
    tranches_cf['amount_remain_after_interest_and_fee_payment'] = tranches_cf['amount_available_to_allocate'] - tranches_cf['amount_to_pay_interest_and_fee']
    tranches_cf['amount_remain_in_interest_account'] = tranches_cf['amount_recycled_interest'] + tranches_cf['amount_reserver_last_period'] - tranches_cf['amount_to_pay_interest_and_fee']
    tranches_cf['amount_principal_to_interest'] = 0
    tranches_cf['amount_principal_to_interest'] = tranches_cf['amount_principal_to_interest'].where(tranches_cf['amount_remain_in_interest_account']>0,-tranches_cf['amount_remain_in_interest_account'])
    tranches_cf['amount_principal_after_transfer_out'] = tranches_cf['amount_recycled_principal'] - tranches_cf['amount_principal_to_interest']
    tranches_cf['amount_principal_after_transfer_out_and_in'] = tranches_cf['amount_principal_after_transfer_out'] + tranches_cf['amount_remain_in_interest_account']
    tranches_cf['amount_extra_earning'] = tranches_cf['amount_principal_after_transfer_out_and_in']
    
#Pay principal
    tranches_cf['amount_pay_A1_principal'] = [tranches_cf['amount_outstanding_A1_principal_begin'][0],tranches_cf['amount_extra_earning'][0]][tranches_cf['amount_extra_earning'][0] < tranches_cf['amount_outstanding_A1_principal_begin'][0]]
    tranches_cf['amount_extra_earning'][0] -= tranches_cf['amount_pay_A1_principal'][0] 
    tranches_cf['amount_pay_A2_principal'] = [tranches_cf['amount_outstanding_A2_principal_begin'][0],tranches_cf['amount_extra_earning'][0]][tranches_cf['amount_extra_earning'][0] < tranches_cf['amount_outstanding_A2_principal_begin'][0]]
    tranches_cf['amount_extra_earning'][0] -= tranches_cf['amount_pay_A2_principal'][0]
    tranches_cf['amount_pay_A3_principal'] = [tranches_cf['amount_outstanding_A3_principal_begin'][0],tranches_cf['amount_extra_earning'][0]][tranches_cf['amount_extra_earning'][0] < tranches_cf['amount_outstanding_A3_principal_begin'][0]]
    tranches_cf['amount_extra_earning'][0] -= tranches_cf['amount_pay_A3_principal'][0]
    tranches_cf['amount_pay_A4_principal'] = [tranches_cf['amount_outstanding_A4_principal_begin'][0],tranches_cf['amount_extra_earning'][0]][tranches_cf['amount_extra_earning'][0] < tranches_cf['amount_outstanding_A4_principal_begin'][0]]
    tranches_cf['amount_extra_earning'][0] -= tranches_cf['amount_pay_A4_principal'][0]
    tranches_cf['amount_pay_A5_principal'] = [tranches_cf['amount_outstanding_A5_principal_begin'][0],tranches_cf['amount_extra_earning'][0]][tranches_cf['amount_extra_earning'][0] < tranches_cf['amount_outstanding_A5_principal_begin'][0]]
    tranches_cf['amount_extra_earning'][0] -= tranches_cf['amount_pay_A5_principal'][0]
    tranches_cf['amount_pay_A6_principal'] = [tranches_cf['amount_outstanding_A6_principal_begin'][0],tranches_cf['amount_extra_earning'][0]][tranches_cf['amount_extra_earning'][0] < tranches_cf['amount_outstanding_A6_principal_begin'][0]]
    tranches_cf['amount_extra_earning'][0] -= tranches_cf['amount_pay_A6_principal'][0] 
    
    tranches_cf['amount_pay_B_principal'] = [tranches_cf['amount_outstanding_B_principal_begin'][0],tranches_cf['amount_extra_earning'][0]][tranches_cf['amount_extra_earning'][0] < tranches_cf['amount_outstanding_B_principal_begin'][0]]
    tranches_cf['amount_extra_earning'][0] -= tranches_cf['amount_pay_B_principal'][0]

    tranches_cf['amount_pay_C_principal'] = [tranches_cf['amount_outstanding_C_principal_begin'][0],tranches_cf['amount_extra_earning'][0]][tranches_cf['amount_extra_earning'][0] < tranches_cf['amount_outstanding_C_principal_begin'][0]]
    tranches_cf['amount_extra_earning'][0] -= tranches_cf['amount_pay_C_principal'][0]

    tranches_cf['amount_pay_Senior_principal'] = tranches_cf['amount_pay_A1_principal'] + tranches_cf['amount_pay_A2_principal'] + tranches_cf['amount_pay_A3_principal'] + tranches_cf['amount_pay_A4_principal'] + tranches_cf['amount_pay_A5_principal'] + tranches_cf['amount_pay_A6_principal']
    tranches_cf['amount_pay_Mezz_principal'] = tranches_cf['amount_pay_B_principal'] 	 
    tranches_cf['amount_pay_Sub_principal'] = 	 tranches_cf['amount_pay_C_principal']
    tranches_cf['amount_pay_all_tranches_principal'] = tranches_cf['amount_pay_Senior_principal'] + tranches_cf['amount_pay_Mezz_principal'] + tranches_cf['amount_pay_Sub_principal']
 
#Principal account at end
    tranches_cf['amount_outstanding_A1_principal_end'] = tranches_cf['amount_outstanding_A1_principal_begin'] - tranches_cf['amount_pay_A1_principal']
    tranches_cf['amount_outstanding_A2_principal_end'] = tranches_cf['amount_outstanding_A2_principal_begin'] - tranches_cf['amount_pay_A2_principal']
    tranches_cf['amount_outstanding_A3_principal_end'] = tranches_cf['amount_outstanding_A3_principal_begin'] - tranches_cf['amount_pay_A3_principal']
    tranches_cf['amount_outstanding_A4_principal_end'] = tranches_cf['amount_outstanding_A4_principal_begin'] - tranches_cf['amount_pay_A4_principal']
    tranches_cf['amount_outstanding_A5_principal_end'] = tranches_cf['amount_outstanding_A5_principal_begin'] - tranches_cf['amount_pay_A5_principal']
    tranches_cf['amount_outstanding_A6_principal_end'] = tranches_cf['amount_outstanding_A6_principal_begin'] - tranches_cf['amount_pay_A6_principal']
    
    tranches_cf['amount_outstanding_B_principal_end'] = tranches_cf['amount_outstanding_B_principal_begin'] - tranches_cf['amount_pay_B_principal']
    
    tranches_cf['amount_outstanding_C_principal_end'] = tranches_cf['amount_outstanding_C_principal_begin'] - tranches_cf['amount_pay_C_principal'] 
#    
    tranches_cf['amount_outstanding_Senior_principal_end'] = tranches_cf['amount_outstanding_A1_principal_end'] \
                                                              +tranches_cf['amount_outstanding_A2_principal_end'] \
                                                              +tranches_cf['amount_outstanding_A3_principal_end'] \
                                                              +tranches_cf['amount_outstanding_A4_principal_end'] \
                                                              +tranches_cf['amount_outstanding_A5_principal_end'] \
                                                              +tranches_cf['amount_outstanding_A6_principal_end']
    
    tranches_cf['amount_outstanding_Mezz_principal_end'] = tranches_cf['amount_outstanding_B_principal_end']
    
    tranches_cf['amount_outstanding_Sub_principal_end'] = tranches_cf['amount_outstanding_C_principal_end']
    
    tranches_cf['amount_outstanding_principal_all_tranches_end'] = tranches_cf['amount_outstanding_Senior_principal_end'] \
                                                                    +tranches_cf['amount_outstanding_Mezz_principal_end'] \
                                                                    +tranches_cf['amount_outstanding_Sub_principal_end']
                                                                    
    return tranches_cf


def prepare_tranches_cf(cash_flow,param):
    
    date_pool_cut = param['dt_pool_cut']
    date_first_calc = param['dt_first_calc']
    date_effective = param['dt_effective']
    date_first_pay = param['dt_first_pay']
    
    last_term = len(cash_flow)
    dates_recycle_begin = [date_pool_cut,date_first_calc]
    date_recycle = date_first_calc
    for i in range(2,last_term - 1):
        dates_recycle_begin.append(get_next_eom(date_recycle,1))
        date_recycle = get_next_eom(date_recycle,1)
    
    dates_recycle_end = [date_first_calc]
    date_recycle = date_first_calc
    for i in range(1,last_term - 1):
        dates_recycle_end.append(get_next_eom(date_recycle,1))
        date_recycle = get_next_eom(date_recycle,1)
    
    dates_interest_calc_begin = [date_effective,date_first_pay]
    date_interest_calc_begin = date_first_pay
    for i in range(2,last_term - 1):
        dates_interest_calc_begin.append(date_interest_calc_begin + relativedelta(months=1))
        date_interest_calc_begin += relativedelta(months=1)
    
    dates_interest_calc_end = [date_first_pay]
    date_interest_calc_end = date_first_pay
    for i in range(1,last_term - 1):
        dates_interest_calc_end.append(date_interest_calc_end + relativedelta(months=1))
        date_interest_calc_end += relativedelta(months=1)
    
    tranches_cf = pd.DataFrame({'date_recycle_begin': dates_recycle_begin,
                                'date_recycle_end': dates_recycle_end,
                                'date_interest_calc_begin':dates_interest_calc_begin,
                                'date_interest_calc_end':dates_interest_calc_end
                                })
    
    tranches_cf['years_interest_calc_this_period'] = (tranches_cf['date_interest_calc_end'] - tranches_cf['date_interest_calc_begin']).dt.days/param['days_in_a_year']
    tranches_cf['years_interest_calc_cumulative'] = tranches_cf['years_interest_calc_this_period'][0]
    for i in range(1,last_term - 1):
        tranches_cf['years_interest_calc_cumulative'][i] = tranches_cf['years_interest_calc_cumulative'][i-1] + tranches_cf['years_interest_calc_this_period'][i]
    
    amount_total_outstanding_principal = []
    for _dt in tranches_cf['date_recycle_end']:
        try:
            amount_total_outstanding_principal.append(cash_flow['amount_total_outstanding_principal'][pd.to_datetime(cash_flow['date_recycle']) == _dt].iloc[0])
        except(IndexError):
            amount_total_outstanding_principal.append(0)
    tranches_cf['amount_total_outstanding_principal'] = pd.DataFrame(amount_total_outstanding_principal)
    
    amount_recycled_principal = []
    for i in range(last_term-1):
        try:
            amount_recycled_principal.append(cash_flow['amount_recycle_total_principal']\
                                             [(pd.to_datetime(cash_flow['date_recycle']) > tranches_cf['date_recycle_begin'][i]) \
                                              & (pd.to_datetime(cash_flow['date_recycle']) <= tranches_cf['date_recycle_end'][i])].sum()\
                                              )
        except(IndexError):
            amount_recycled_principal.append(0)
    tranches_cf['amount_recycled_principal'] = pd.DataFrame(amount_recycled_principal)
    
    amount_recycled_interest = []
    for i in range(last_term-1):
        try:
            amount_recycled_interest.append(cash_flow['amount_recycle_total_interest']\
                                             [(pd.to_datetime(cash_flow['date_recycle']) > tranches_cf['date_recycle_begin'][i]) \
                                              & (pd.to_datetime(cash_flow['date_recycle']) <= tranches_cf['date_recycle_end'][i])].sum()\
                                              )
        except(IndexError):
            amount_recycled_interest.append(0)
    tranches_cf['amount_recycled_interest'] = pd.DataFrame(amount_recycled_interest)
    
    tranches_cf['amount_recycled_total'] = tranches_cf['amount_recycled_principal'] + tranches_cf['amount_recycled_interest']
    
    tranches_cf['amount_reserver_last_period'] = 0
    tranches_cf['amount_available_to_allocate'] = tranches_cf['amount_recycled_total'] \
                                                  + tranches_cf['amount_reserver_last_period'] * tranches_cf['years_interest_calc_this_period'] * param['rate_interest_reserve']

    return tranches_cf