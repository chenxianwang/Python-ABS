# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 18:00:18 2017

@author: Jonah.Chen
"""
import pandas as pd
from util import get_next_eom,save_to_excel,get_logger

logger = get_logger(__name__)

def adjust_cashflow(cash_flow,data_c,scenario_id,param,scenario,redemption_flag):
    
    if redemption_flag == 1:
        return adjust_with_redemption(cash_flow,data_c,scenario_id,param,scenario)
    
    return adjust_without_redemption(cash_flow,data_c,scenario_id,param,scenario)

def adjust_without_redemption(cash_flow,data_c,scenario_id,param,scenario):
    
    cash_flow = initializing(cash_flow,scenario_id,param,scenario)

    cash_flow['rate_complement_prepay_default'] = 1 - cash_flow['rate_prepay'] - cash_flow['rate_default']
    cash_flow['rate_product_complement_prepay_default_by_period'] = cash_flow['rate_complement_prepay_default']
    for term_count in range(1,len(cash_flow['rate_product_complement_prepay_default_by_period'])):
        cash_flow['rate_product_complement_prepay_default_by_period'][term_count] = cash_flow['rate_product_complement_prepay_default_by_period'][term_count - 1] * cash_flow['rate_complement_prepay_default'][term_count]

    cash_flow = adjuest_principal(cash_flow,param)

    cash_flow = adjust_interest(cash_flow,param)

    logger.info(data_c['amount_recycle_total_principal'].sum() - cash_flow['amount_recycle_total_principal'].sum())
    logger.info(data_c['amount_recycle_total_interest'].sum() - cash_flow['amount_recycle_total_interest'].sum())
    
    save_to_excel(cash_flow,'adjusted_without_redemption')
    
    return cash_flow


def adjust_with_redemption(cash_flow,data_c,scenario_id,param,scenario):
    
    cash_flow = initializing(cash_flow,scenario_id,param,scenario)
#First run to get redemption_division           
    date_f_c = param['dt_first_calc']
    cash_flow['rate_default'] = cash_flow['rate_default'].where(pd.to_datetime(cash_flow['date_recycle'])>date_f_c,0)
    cash_flow['rate_overdue'] = cash_flow['rate_overdue'].where(pd.to_datetime(cash_flow['date_recycle'])>date_f_c,0)

    cash_flow['rate_complement_prepay_default'] = 1 - cash_flow['rate_prepay'] - cash_flow['rate_default']
    cash_flow['rate_product_complement_prepay_default_by_period'] = cash_flow['rate_complement_prepay_default']
    for term_count in range(1,len(cash_flow['rate_product_complement_prepay_default_by_period'])):
        cash_flow['rate_product_complement_prepay_default_by_period'][term_count] = cash_flow['rate_product_complement_prepay_default_by_period'][term_count - 1] * cash_flow['rate_complement_prepay_default'][term_count]

    cash_flow = adjuest_principal(cash_flow,param)

    redemption_division = cash_flow[pd.to_datetime(cash_flow['date_recycle']) == get_next_eom(date_f_c,-1)]['amount_total_outstanding_principal'].iloc[0]
    
    total_princ = cash_flow['amount_principal'].sum()
    cash_flow['rate_prepay'] = cash_flow['rate_prepay'] \
                                   .where(pd.to_datetime(cash_flow['date_recycle']) != date_f_c,
                                   cash_flow['rate_prepay'] + total_princ * param['percentage_redemption'] / redemption_division)

    cash_flow['rate_complement_prepay_default'] = 1 - cash_flow['rate_prepay'] - cash_flow['rate_default']
    cash_flow['rate_product_complement_prepay_default_by_period'] = cash_flow['rate_complement_prepay_default']
    for term_count in range(1,len(cash_flow['rate_product_complement_prepay_default_by_period'])):
        cash_flow['rate_product_complement_prepay_default_by_period'][term_count] = cash_flow['rate_product_complement_prepay_default_by_period'][term_count - 1] * cash_flow['rate_complement_prepay_default'][term_count]

    cash_flow = adjuest_principal(cash_flow,param)

    cash_flow = adjust_interest(cash_flow,param)
    cash_flow['scenario_id'] = scenario_id

    logger.info(data_c['amount_recycle_total_principal'].sum() - cash_flow['amount_recycle_total_principal'].sum())
    logger.info(data_c['amount_recycle_total_interest'].sum() - cash_flow['amount_recycle_total_interest'].sum())
    
    save_to_excel(cash_flow,'adjusted_with_redemption')
    
    return cash_flow[['date_recycle','amount_recycle_total_principal','amount_recycle_total_interest','amount_total_outstanding_principal']]


def adjuest_principal(cash_flow,param):
    
    total_princ = cash_flow['amount_principal'].sum()
    cash_flow['amount_recycle_principal_normal'] = cash_flow['amount_principal'] * cash_flow['rate_product_complement_prepay_default_by_period'] * (1 - cash_flow['rate_overdue'])
    cash_flow['amount_principal_overdue_current'] = cash_flow['amount_principal'] * cash_flow['rate_product_complement_prepay_default_by_period'] * cash_flow['rate_overdue']
    
    cash_flow['amount_recycle_principal_prepay'] = total_princ * cash_flow['rate_prepay'][0]
    cash_flow['amount_recycle_principal_default'] = total_princ * cash_flow['rate_default'][0] * param['rate_recovery']
    cash_flow['amount_principal_default'] = total_princ * cash_flow['rate_default'][0]
    cash_flow['amount_total_outstanding_principal'] = total_princ \
                                                        - cash_flow['amount_recycle_principal_normal'] \
                                                        - cash_flow['amount_principal_overdue_current'] \
                                                        - cash_flow['amount_recycle_principal_prepay'] \
                                                        - cash_flow['amount_principal_default']
    #Refresh
    for term_count in range(1,len(cash_flow['amount_recycle_principal_normal'])):
        cash_flow['amount_recycle_principal_prepay'][term_count] = cash_flow['amount_total_outstanding_principal'][term_count - 1] * cash_flow['rate_prepay'][term_count]
        cash_flow['amount_recycle_principal_default'][term_count] = cash_flow['amount_total_outstanding_principal'][term_count - 1] * cash_flow['rate_default'][term_count] * param['rate_recovery']
        cash_flow['amount_principal_default'][term_count] = cash_flow['amount_total_outstanding_principal'][term_count - 1] * cash_flow['rate_default'][term_count]
        cash_flow['amount_total_outstanding_principal'][term_count] = cash_flow['amount_total_outstanding_principal'][term_count - 1] \
                                                                    - cash_flow['amount_recycle_principal_normal'][term_count] \
                                                                    - cash_flow['amount_principal_overdue_current'][term_count] \
                                                                    - cash_flow['amount_recycle_principal_prepay'][term_count] \
                                                                    - cash_flow['amount_principal_default'][term_count]
    
    cash_flow['amount_recycle_principal_overdue'] = get_recycle_overdue(cash_flow,'principal',param)
    
    cash_flow['amount_total_principal_overdue_begin_period'] = 0
    for term_count in range(1,len(cash_flow['amount_total_principal_overdue_begin_period'])):
        cash_flow['amount_total_principal_overdue_begin_period'][term_count] = sum(cash_flow['amount_principal_overdue_current'][0:term_count]) - sum(cash_flow['amount_recycle_principal_overdue'][0:term_count])
    
    cash_flow['amount_recycle_interest_overdue_principal'] = cash_flow['amount_total_principal_overdue_begin_period'] * cash_flow['rate_interest_if_overdue']

    cash_flow['amount_recycle_total_overdue_principal'] = cash_flow['amount_recycle_principal_overdue'] + cash_flow['amount_recycle_interest_overdue_principal']
    
    cash_flow['amount_recycle_total_principal'] = cash_flow['amount_recycle_principal_normal'] \
                                                    + cash_flow['amount_recycle_principal_prepay'] \
                                                    + cash_flow['amount_recycle_principal_default'] \
                                                    + cash_flow['amount_recycle_total_overdue_principal']
                                                    
    return cash_flow

def adjust_interest(cash_flow,param):
    
    total_interest_fee = cash_flow['total_interest_and_fee'].sum()
    cash_flow['amount_recycle_interest_normal'] = cash_flow['total_interest_and_fee']  * cash_flow['rate_product_complement_prepay_default_by_period'] * (1 - cash_flow['rate_overdue'])
    cash_flow['amount_interest_overdue_current'] = cash_flow['total_interest_and_fee'] * cash_flow['rate_product_complement_prepay_default_by_period'] * cash_flow['rate_overdue']

    cash_flow['amount_recycle_interest_prepay'] = 0
    cash_flow['amount_recycle_interest_overdue'] = get_recycle_overdue(cash_flow,'interest',param)
    cash_flow['amount_recycle_interest_overdue_interest'] = 0
    cash_flow['amount_recycle_total_overdue_interest'] = cash_flow['amount_recycle_interest_overdue'] + cash_flow['amount_recycle_interest_overdue_interest']
    
    cash_flow['amount_interest_default'] = total_interest_fee * cash_flow['rate_default']
    cash_flow['amount_total_outstanding_interest_and_fee'] = total_interest_fee \
                                                                   - cash_flow['amount_recycle_interest_normal'] \
                                                                   - cash_flow['amount_recycle_interest_prepay'] \
                                                                   - cash_flow['amount_interest_overdue_current'] \
                                                                   - cash_flow['amount_interest_default']
    #Refresh
    for term_count in range(1,len(cash_flow['amount_interest_default'])):
        cash_flow['amount_interest_default'][term_count] = cash_flow['amount_total_outstanding_interest_and_fee'][term_count - 1] * cash_flow['rate_default'][term_count]
        cash_flow['amount_total_outstanding_interest_and_fee'][term_count] = cash_flow['amount_total_outstanding_interest_and_fee'][term_count - 1] \
                                                                                - cash_flow['amount_recycle_interest_normal'][term_count] \
                                                                                - cash_flow['amount_recycle_interest_prepay'][term_count] \
                                                                                - cash_flow['amount_interest_overdue_current'][term_count] \
                                                                                - cash_flow['amount_interest_default'][term_count]
    
    cash_flow['amount_recycle_total_interest'] = cash_flow['amount_recycle_interest_normal'] \
                                                   + cash_flow['amount_recycle_interest_prepay'] \
                                                   + cash_flow['amount_recycle_total_overdue_interest']
    
    return cash_flow

def get_recycle_overdue(cash_flow,content_type,param):
    cash_flow['amount_recycle_' + content_type + '_overdue'] = 0
    for month_overdue in range(1,4):
        cash_flow['amount_recycle_' + content_type + '_overdue_' + str(month_overdue)+ '_month'] = 0
        for term_count in range(month_overdue,len(cash_flow['amount_recycle_' + content_type + '_overdue_' + str(month_overdue)+ '_month'])):
            cash_flow['amount_recycle_' + content_type + '_overdue_' + str(month_overdue)+ '_month'][term_count] = cash_flow['amount_' + content_type + '_overdue_current'][term_count - month_overdue] * param['rate_recovery_in_' + str(month_overdue) + '_month']
        cash_flow['amount_recycle_' + content_type + '_overdue'] += cash_flow['amount_recycle_' + content_type + '_overdue_'+ str(month_overdue) + '_month']
    return cash_flow['amount_recycle_' + content_type + '_overdue']


def initializing(cash_flow,scenario_id,param,scenario):
    cash_flow['total_interest_and_fee'] = cash_flow['amount_interest'] + cash_flow['amount_fee'] * param['include_fee']
    date_p_c = param['dt_pool_cut']
   
    cash_flow['days_period'] = pd.to_datetime(cash_flow['date_recycle']).dt.day
    cash_flow['days_period'][0] = pd.to_datetime(cash_flow['date_recycle'][0]).day - date_p_c.day
    cash_flow['years_period'] = cash_flow['days_period'] / param['days_in_a_year']
    cash_flow['rate_default'] = cash_flow['years_period'] * scenario[scenario_id]['rate_default']
    cash_flow['rate_overdue'] = scenario[scenario_id]['rate_overdue']
    cash_flow['rate_prepay'] = cash_flow['years_period'] * scenario[scenario_id]['rate_prepay']
    cash_flow['rate_interest_if_overdue'] = cash_flow['years_period'] * param['rate_interest_if_overdue']
    
    
    return cash_flow