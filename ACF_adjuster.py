# -*- coding: utf-8 -*-
"""
Created on Mon Jun 18 19:57:55 2018

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
from dateutil.relativedelta import relativedelta
import datetime


class ACF_adjuster():
    
    def __init__(self,name_project,cashflow_original,supplement_assets_params,scenario,scenario_id,dt_param,fee_rate_param):
        
        self.cashflow_original = cashflow_original
        self.supplement_params = supplement_assets_params
        self.main_params = scenario[scenario_id]
        self.name_project = name_project
        self.fee_rate_param = fee_rate_param
        self.dt_param = dt_param
        
        self.wb_save_results = path_root  + '/../CheckTheseProjects/' + self.name_project + '/'+self.name_project+'.xlsx'
        

    def adjust_ACF(self):
        
        aACF = self.cashflow_original
        
        TOTAL_Principal = aACF['amount_principal'].sum()
        aACF['amount_recycle_total_principal'] = aACF['amount_principal']
        aACF['amount_recycle_total_interest'] = aACF['amount_interest']
        
        aACF['amount_total_outstanding_principal'] = TOTAL_Principal - aACF['amount_recycle_total_principal'].cumsum()
        
        return aACF
    
    def prepare_for_waterfall(self,aACF):
        #ACF['EarlyRepaid'] = ACF['amount_principal'] * self.params['rate_early_repaid']
        logger.info('prepare_tranches_cf...')
        date_pool_cut = self.dt_param['dt_pool_cut']
        date_first_calc = self.dt_param['dt_first_calc']
        date_effective = self.dt_param['dt_effective']
        date_first_pay = self.dt_param['dt_first_pay']
        fee_rate_param = self.fee_rate_param
        
        #cash_flow = self.cash_flow_in
        
        last_term = len(aACF[pd.to_datetime(aACF['date_recycle']) >= date_effective ]) + 1
        
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
        
        tranches_cf['years_interest_calc_this_period'] = (tranches_cf['date_interest_calc_end'] - tranches_cf['date_interest_calc_begin']).dt.days/days_in_a_year
        tranches_cf['years_interest_calc_cumulative'] = tranches_cf['years_interest_calc_this_period'][0]
        for i in range(1,last_term - 1):
            tranches_cf['years_interest_calc_cumulative'][i] = tranches_cf['years_interest_calc_cumulative'][i-1] + tranches_cf['years_interest_calc_this_period'][i]
        
        amount_total_outstanding_principal = []
        for _dt in tranches_cf['date_recycle_end']:
            try:
                amount_total_outstanding_principal.append(aACF['amount_total_outstanding_principal'][pd.to_datetime(aACF['date_recycle']) == _dt].iloc[0])
            except(IndexError):
                amount_total_outstanding_principal.append(0)
        tranches_cf['amount_total_outstanding_principal'] = pd.DataFrame(amount_total_outstanding_principal)
        
        amount_recycled_principal = []
        for i in range(last_term-1):
            try:
                amount_recycled_principal.append(aACF['amount_recycle_total_principal']\
                                                 [(pd.to_datetime(aACF['date_recycle']) > tranches_cf['date_recycle_begin'][i]) \
                                                  & (pd.to_datetime(aACF['date_recycle']) <= tranches_cf['date_recycle_end'][i])].sum()\
                                                  )
            except(IndexError):
                amount_recycled_principal.append(0)
        tranches_cf['amount_recycled_principal'] = pd.DataFrame(amount_recycled_principal)
        
        amount_recycled_interest = []
        for i in range(last_term-1):
            try:
                amount_recycled_interest.append(aACF['amount_recycle_total_interest']\
                                                 [(pd.to_datetime(aACF['date_recycle']) > tranches_cf['date_recycle_begin'][i]) \
                                                  & (pd.to_datetime(aACF['date_recycle']) <= tranches_cf['date_recycle_end'][i])].sum()\
                                                  )
            except(IndexError):
                amount_recycled_interest.append(0)
        tranches_cf['amount_recycled_interest'] = pd.DataFrame(amount_recycled_interest) 
        
        tranches_cf['amount_recycled_total'] = tranches_cf['amount_recycled_principal'] + tranches_cf['amount_recycled_interest']
        
        #TODO: Add interest_from_reserve
        tranches_cf['amount_reserver_last_period'] = 0
        tranches_cf['amount_available_to_allocate'] = tranches_cf['amount_recycled_total'] #+ tranches_cf['amount_reserver_last_period'] * tranches_cf['years_interest_calc_this_period'] * fee_rate_param['rate_interest_reserve']
    
        #save_to_excel(tranches_cf,'prepare_tranches_cf',wb_name)
        
        save_to_excel(tranches_cf,'tranches_cf',self.wb_save_results)       
        
        return tranches_cf
        #self.adjusted_ACF = ACF