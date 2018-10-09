# -*- coding: utf-8 -*-
"""
Created on Mon Jun 18 19:57:55 2018

@author: Jonah.Chen
"""
import sys
import os
from constant import *
from copy import deepcopy
from Params import *
import pandas as pd
import numpy as np
from abs_util.util_general import *
from abs_util.util_cf import *
from dateutil.relativedelta import relativedelta
import datetime
from scipy.stats import bernoulli

logger = get_logger(__name__)

class APCF_adjuster():
    
    def __init__(self,apcf,scenario,scenario_id,df_ppmt,df_ipmt,dates_recycle_list):
        
        self.apcf = apcf
        self.df_ppmt = df_ppmt
        self.df_ipmt = df_ipmt
        self.scenario_id = scenario_id
        self.main_params = scenarios[scenario_id]   
        self.dates_recycle_list = dates_recycle_list
        
        self.APCF_adjusted_dict = {}
        
        self.principal_normal_currentTerm = {}
        self.interest_normal_currentTerm = {}
        self.principal_overdue_1_30_currentTerm = {}
        self.interest_overdue_1_30_currentTerm = {}        
        self.principal_overdue_31_60_currentTerm = {}
        self.interest_overdue_31_60_currentTerm = {}    
        self.principal_overdue_61_90_currentTerm = {}
        self.interest_overdue_61_90_currentTerm = {}    
        self.principal_loss_currentTerm = {}
        self.interest_loss_currentTerm = {}
        
        #self.principal_normal_allTerm = {}
        #self.interest_normal_allTerm = {}
        self.principal_overdue_1_30_allTerm = {}
        self.interest_overdue_1_30_allTerm = {} 
        self.principal_overdue_31_60_allTerm = {}
        self.interest_overdue_31_60_allTerm = {}    
        self.principal_overdue_61_90_allTerm = {}
        self.interest_overdue_61_90_allTerm = {}  
        self.principal_loss_allTerm = {}
        self.interest_loss_allTerm = {}
        
        self.principal_overdue_1_30_recycle = {}
        self.interest_overdue_1_30_recycle = {}
        self.principal_overdue_31_60_recycle = {}
        self.interest_overdue_31_60_recycle = {}
        self.principal_overdue_61_90_recycle = {}
        self.interest_overdue_61_90_recycle = {}
        
        self.principal_ER_recycle = {}
        self.interest_ER_recycle = {}
        
        self.principal_Redemption_recycle = {}
        self.interest_Redemption_recycle = {}
        self.principal_Redemption_currentTerm_helper = {}
        self.interest_Redemption_currentTerm_helper = {}
        
        self.principal_overdue_31_60_currentTerm_helper = {}
        self.interest_overdue_31_60_currentTerm_helper = {}
        self.principal_overdue_31_60_allTerm_helper = {}
        self.interest_overdue_31_60_allTerm_helper = {}
        
        self.principal_overdue_61_90_currentTerm_helper = {}
        self.interest_overdue_61_90_currentTerm_helper = {}
        self.principal_loss_currentTerm_helper = {}
        self.interest_loss_currentTerm_helper = {}
        
        self.Transition_principal_M1_2_M0 = {}
        self.Transition_interest_M1_2_M0= {}
        self.Transition_principal_M2_2_M0 = {}
        self.Transition_interest_M2_2_M0= {}
        self.Transition_principal_M3_2_M0= {}
        self.Transition_interest_M3_2_M0= {}
    
        for date_r_index,date_r in enumerate(self.dates_recycle_list):
            
            self.principal_overdue_31_60_currentTerm[date_r] = 0
            self.interest_overdue_31_60_currentTerm[date_r] = 0
            self.principal_overdue_61_90_currentTerm[date_r] = 0
            self.interest_overdue_61_90_currentTerm[date_r] = 0
            self.principal_loss_currentTerm[date_r] = 0
            self.interest_loss_currentTerm[date_r] = 0
            
            self.principal_overdue_31_60_allTerm[date_r] = 0
            self.interest_overdue_31_60_allTerm[date_r] = 0
            self.principal_overdue_61_90_allTerm[date_r] = 0
            self.interest_overdue_61_90_allTerm[date_r] = 0
            self.principal_loss_allTerm[date_r] = 0
            self.interest_loss_allTerm[date_r] = 0
            
            self.principal_overdue_61_90_currentTerm_helper[date_r] = 0
            self.interest_overdue_61_90_currentTerm_helper[date_r] = 0
            self.principal_loss_currentTerm_helper[date_r] = 0
            self.interest_loss_currentTerm_helper[date_r] = 0
            
            self.principal_overdue_1_30_recycle[date_r] = 0
            self.interest_overdue_1_30_recycle[date_r] = 0
            self.principal_overdue_31_60_recycle[date_r] = 0
            self.interest_overdue_31_60_recycle[date_r] = 0
            self.principal_overdue_61_90_recycle[date_r] = 0
            self.interest_overdue_61_90_recycle[date_r] = 0
            
            self.principal_ER_recycle[date_r] = 0
            self.interest_ER_recycle[date_r] = 0
            
            self.principal_Redemption_recycle[date_r] = 0
            self.interest_Redemption_recycle[date_r] = 0
            self.principal_Redemption_currentTerm_helper[date_r] = 0
            self.interest_Redemption_currentTerm_helper[date_r] = 0

            self.Transition_principal_M1_2_M0[date_r] = pd.DataFrame()
            self.Transition_interest_M1_2_M0[date_r] = pd.DataFrame()
            self.Transition_principal_M2_2_M0[date_r] = pd.DataFrame()
            self.Transition_interest_M2_2_M0[date_r] = pd.DataFrame()
            self.Transition_principal_M3_2_M0[date_r] = pd.DataFrame()
            self.Transition_interest_M3_2_M0[date_r] = pd.DataFrame()
        
    def adjust_APCF(self,OoR):
        
        df_ppmt,df_ipmt = deepcopy(self.df_ppmt),deepcopy(self.df_ipmt)
        dates_recycle_list = self.dates_recycle_list
        
        ppmt_M0,ipmt_M0 = df_ppmt,df_ipmt
        ppmt_M1,ipmt_M1 = pd.DataFrame(),pd.DataFrame() 
        ppmt_M1_2_M0,ipmt_M1_2_M0 = pd.DataFrame(),pd.DataFrame() 
        ppmt_M1_2_M2,ipmt_M1_2_M2 = pd.DataFrame(),pd.DataFrame()      
        ppmt_M2_2_M0,ipmt_M2_2_M0 = pd.DataFrame(),pd.DataFrame() 
        ppmt_M2_2_M3,ipmt_M2_2_M3 = pd.DataFrame(),pd.DataFrame()    
        ppmt_M3_2_M0,ipmt_M3_2_M0 = pd.DataFrame(),pd.DataFrame() 
        ppmt_M3_2_L,ipmt_M3_2_L = pd.DataFrame(),pd.DataFrame()

        for date_r_index,date_r in enumerate(dates_recycle_list):
            #logger.info('Adjusting for date_r {0}'.format(date_r)) 
#####################################################################################################################
            if date_r_index>0 and date_r_index < len(dates_recycle_list)-1:
                _ppmt_M1_2_M0 = self.Transition_principal_M1_2_M0[dates_recycle_list[date_r_index-1]]
                _ipmt_M1_2_M0 = self.Transition_interest_M1_2_M0[dates_recycle_list[date_r_index-1]]
                self.principal_overdue_1_30_recycle[dates_recycle_list[date_r_index+1]] = _ppmt_M1_2_M0[date_r].sum() + _ppmt_M1_2_M0[dates_recycle_list[date_r_index-1]].sum()
                self.interest_overdue_1_30_recycle[dates_recycle_list[date_r_index+1]] = _ipmt_M1_2_M0[date_r].sum() + _ipmt_M1_2_M0[dates_recycle_list[date_r_index-1]].sum()
                _ppmt_M1_2_M0[date_r],_ppmt_M1_2_M0[dates_recycle_list[date_r_index-1]] = 0,0
                _ipmt_M1_2_M0[date_r],_ipmt_M1_2_M0[dates_recycle_list[date_r_index-1]] = 0,0
            if date_r_index>1 and date_r_index < len(dates_recycle_list)-1:
                _ppmt_M2_2_M0 = self.Transition_principal_M2_2_M0[dates_recycle_list[date_r_index-2]]
                _ipmt_M2_2_M0 = self.Transition_interest_M2_2_M0[dates_recycle_list[date_r_index-2]]
                self.principal_overdue_31_60_recycle[dates_recycle_list[date_r_index+1]] = _ppmt_M2_2_M0[date_r].sum() + _ppmt_M2_2_M0[dates_recycle_list[date_r_index-1]].sum() + _ppmt_M2_2_M0[dates_recycle_list[date_r_index-2]].sum()
                self.interest_overdue_31_60_recycle[dates_recycle_list[date_r_index+1]] = _ipmt_M2_2_M0[date_r].sum() + _ipmt_M2_2_M0[dates_recycle_list[date_r_index-1]].sum() + _ipmt_M2_2_M0[dates_recycle_list[date_r_index-2]].sum()                                                        
                _ppmt_M2_2_M0[date_r],_ppmt_M2_2_M0[dates_recycle_list[date_r_index-1]],_ppmt_M2_2_M0[dates_recycle_list[date_r_index-2]] = 0,0,0
                _ipmt_M2_2_M0[date_r],_ipmt_M2_2_M0[dates_recycle_list[date_r_index-1]],_ipmt_M2_2_M0[dates_recycle_list[date_r_index-2]] = 0,0,0
            if date_r_index>2 and date_r_index < len(dates_recycle_list)-1:       
                _ppmt_M3_2_M0 = self.Transition_principal_M3_2_M0[dates_recycle_list[date_r_index-3]]
                _ipmt_M3_2_M0 = self.Transition_interest_M3_2_M0[dates_recycle_list[date_r_index-3]]
                self.principal_overdue_61_90_recycle[dates_recycle_list[date_r_index+1]] = _ppmt_M3_2_M0[date_r].sum() + _ppmt_M3_2_M0[dates_recycle_list[date_r_index-1]].sum() + _ppmt_M3_2_M0[dates_recycle_list[date_r_index-2]].sum() + _ppmt_M3_2_M0[dates_recycle_list[date_r_index-3]].sum()
                self.interest_overdue_61_90_recycle[dates_recycle_list[date_r_index+1]] = _ipmt_M3_2_M0[date_r].sum() + _ipmt_M3_2_M0[dates_recycle_list[date_r_index-1]].sum() + _ipmt_M3_2_M0[dates_recycle_list[date_r_index-2]].sum() + _ipmt_M3_2_M0[dates_recycle_list[date_r_index-3]].sum()
                _ppmt_M3_2_M0[date_r],_ppmt_M3_2_M0[dates_recycle_list[date_r_index-1]],_ppmt_M3_2_M0[dates_recycle_list[date_r_index-2]],_ppmt_M3_2_M0[dates_recycle_list[date_r_index-3]] = 0,0,0,0
                _ipmt_M3_2_M0[date_r],_ipmt_M3_2_M0[dates_recycle_list[date_r_index-1]],_ipmt_M3_2_M0[dates_recycle_list[date_r_index-2]],_ipmt_M3_2_M0[dates_recycle_list[date_r_index-3]] = 0,0,0,0
            
            ppmt_M0,ipmt_M0,ppmt_M1,ipmt_M1 = self.transit_Status(ppmt_M0,ipmt_M0,OoR,date_r_index,'M0_2_M1','Overdue')
            
            #ppmt_M0.to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/check/ppmt_M0'+str(date_r)+'.csv',index=False)
            
            if date_r_index > 2:
                ppmt_M0 = ppmt_M0.append(_ppmt_M1_2_M0).append(_ppmt_M2_2_M0).append(_ppmt_M3_2_M0,ignore_index=True)
                ipmt_M0 = ipmt_M0.append(_ipmt_M1_2_M0).append(_ipmt_M2_2_M0).append(_ipmt_M3_2_M0,ignore_index=True)
            elif date_r_index > 1:
                ppmt_M0 = ppmt_M0.append(_ppmt_M1_2_M0).append(_ppmt_M2_2_M0,ignore_index=True)
                ipmt_M0 = ipmt_M0.append(_ipmt_M1_2_M0).append(_ipmt_M2_2_M0,ignore_index=True)
            elif date_r_index > 0:
                ppmt_M0 = ppmt_M0.append(_ppmt_M1_2_M0,ignore_index=True)
                ipmt_M0 = ipmt_M0.append(_ipmt_M1_2_M0,ignore_index=True)
            else:pass
            
            #ppmt_M0.to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/check/ppmt_M0'+str(date_r)+'.csv',index=False)
            
            #ER
            ppmt_M0_ER,ipmt_M0_ER,ppmt_M0,ipmt_M0 = self.transit_Status(ppmt_M0,ipmt_M0,OoR,date_r_index,'M0_2_ERM0','ER')
            
            self.principal_ER_recycle[date_r] = sum(ppmt_M0_ER[dates_recycle_list[date_r_index:]].sum())
            self.interest_ER_recycle[date_r] = sum(ipmt_M0_ER[dates_recycle_list[date_r_index:]].sum())
            
            #ppmt_M0.to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/check/ppmt_M0_without_ER'+str(date_r)+'.csv',index=False)           
            
            self.principal_normal_currentTerm[date_r] = ppmt_M0[date_r].sum()
            self.interest_normal_currentTerm[date_r] = ipmt_M0[date_r].sum()   
            
            self.principal_overdue_1_30_currentTerm[date_r] = ppmt_M1[date_r].sum()
            self.interest_overdue_1_30_currentTerm[date_r] = ipmt_M1[date_r].sum()            
            self.principal_overdue_1_30_allTerm[date_r] = sum(ppmt_M1[dates_recycle_list[date_r_index:]].sum())
            self.interest_overdue_1_30_allTerm[date_r] = sum(ipmt_M1[dates_recycle_list[date_r_index:]].sum())
            
            #Transition M1_2_M0M2
            if date_r_index < len(dates_recycle_list)-1:
                #logger.info('Transition M1_2_M0M2...')
                ppmt_M1_2_M0,ipmt_M1_2_M0,ppmt_M1_2_M2,ipmt_M1_2_M2 = self.transit_Status(ppmt_M1,ipmt_M1,OoR,date_r_index,'M1_2_M0M2','Overdue')#self.M1_2_M0M2(ppmt_M1,ipmt_M1)
                #TODO: Adjust by redemption criteria and POOL_CUT_PERIOD for redemption
                if  Redeem_or_Not == True :
                    if date_r_index == 2 and OoR == 'O' :#and POOL_CUT_PERIOD-date_r_index>=0 : CAPTURE M2 on first calculation date
                        self.principal_Redemption_recycle[dates_recycle_list[date_r_index+1]] += sum(ppmt_M1_2_M2[dates_recycle_list[date_r_index:]].sum())
                        self.interest_Redemption_recycle[dates_recycle_list[date_r_index+1]] += sum(ipmt_M1_2_M2[dates_recycle_list[date_r_index:]].sum())          
                        ppmt_M1_2_M2,ipmt_M1_2_M2 = ppmt_M1_2_M2[0:0],ipmt_M1_2_M2[0:0]
                        logger.info('self.principal_Redemption_recycle is {0} :'.format(self.principal_Redemption_recycle[dates_recycle_list[date_r_index+1]]))
                    else: self.cal_overdue_31_60(date_r_index,ppmt_M1_2_M2,ipmt_M1_2_M2)
                else:self.cal_overdue_31_60(date_r_index,ppmt_M1_2_M2,ipmt_M1_2_M2)
                    
            #Transition M2_2_M0M3
            if date_r_index < len(dates_recycle_list)-2:
                #logger.info('Transition M2_2_M0M3...')
                ppmt_M2_2_M0,ipmt_M2_2_M0,ppmt_M2_2_M3,ipmt_M2_2_M3 = self.transit_Status(ppmt_M1_2_M2,ipmt_M1_2_M2,OoR,date_r_index,'M2_2_M0M3','Overdue')
                if  Redeem_or_Not == True :
                    if date_r_index == 1 and OoR == 'O':# and POOL_CUT_PERIOD-date_r_index>=0 :CAPTURE M3 on first calculation date
                        self.principal_Redemption_recycle[dates_recycle_list[date_r_index+2]] += sum(ppmt_M2_2_M3[dates_recycle_list[date_r_index:]].sum())
                        self.interest_Redemption_recycle[dates_recycle_list[date_r_index+2]] += sum(ipmt_M2_2_M3[dates_recycle_list[date_r_index:]].sum())          
                        ppmt_M2_2_M3,ipmt_M2_2_M3 = ppmt_M2_2_M3[0:0],ipmt_M2_2_M3[0:0]
                    else: self.cal_overdue_61_90(date_r_index,ppmt_M2_2_M3,ipmt_M2_2_M3)
                else:self.cal_overdue_61_90(date_r_index,ppmt_M2_2_M3,ipmt_M2_2_M3)
            
            #Transition M3_2_M0L
            if date_r_index < len(dates_recycle_list)-3:
                #logger.info('Transition M3_2_M0L...')
                ppmt_M3_2_M0,ipmt_M3_2_M0,ppmt_M3_2_L,ipmt_M3_2_L = self.transit_Status(ppmt_M2_2_M3,ipmt_M2_2_M3,OoR,date_r_index,'M3_2_M0L','Overdue')     
                if  Redeem_or_Not == True :
                    if date_r_index == 0 and OoR == 'O':# and POOL_CUT_PERIOD-date_r_index>=0  :CAPTURE ML on first calculation date
                        self.principal_Redemption_recycle[dates_recycle_list[date_r_index+3]] = sum(ppmt_M3_2_L[dates_recycle_list[date_r_index:]].sum())
                        self.interest_Redemption_recycle[dates_recycle_list[date_r_index+3]] = sum(ipmt_M3_2_L[dates_recycle_list[date_r_index:]].sum())          
                    else: self.cal_loss(date_r_index,ppmt_M3_2_L,ipmt_M3_2_L)
                else: self.cal_loss(date_r_index,ppmt_M3_2_L,ipmt_M3_2_L)
                
            self.Transition_principal_M1_2_M0[date_r],self.Transition_interest_M1_2_M0[date_r] = deepcopy(ppmt_M1_2_M0),deepcopy(ipmt_M1_2_M0)
            self.Transition_principal_M2_2_M0[date_r],self.Transition_interest_M2_2_M0[date_r] = deepcopy(ppmt_M2_2_M0),deepcopy(ipmt_M2_2_M0)
            self.Transition_principal_M3_2_M0[date_r],self.Transition_interest_M3_2_M0[date_r] = deepcopy(ppmt_M3_2_M0),deepcopy(ipmt_M3_2_M0)
                        
            #ppmt_M1.to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/check/ppmt_M1'+str(date_r)+'.csv',index=False)
            #ppmt_M1_2_M0.to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/check/ppmt_M1_2_M0'+str(date_r)+'.csv',index=False)
            #ppmt_M2_2_M0.to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/check/ppmt_M2_2_M0'+str(date_r)+'.csv',index=False)
            #ppmt_M3_2_M0.to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/check/ppmt_M3_2_M0'+str(date_r)+'.csv',index=False)
            #logger.info('Generating APCF_adjusted_dict for date_r {0} '.format(date_r))
            self.APCF_adjusted_dict[date_r] = [self.principal_normal_currentTerm[date_r],
                                          self.interest_normal_currentTerm[date_r],
                                          
                                          self.principal_overdue_1_30_currentTerm[date_r],
                                          self.interest_overdue_1_30_currentTerm[date_r],  
                                          self.principal_overdue_31_60_currentTerm[date_r],
                                          self.interest_overdue_31_60_currentTerm[date_r],
                                          self.principal_overdue_61_90_currentTerm[date_r],
                                          self.interest_overdue_61_90_currentTerm[date_r],
                                          self.principal_loss_currentTerm[date_r],
                                          self.interest_loss_currentTerm[date_r],
                                          self.principal_overdue_1_30_allTerm[date_r],
                                          self.interest_overdue_1_30_allTerm[date_r],
                                          self.principal_overdue_31_60_allTerm[date_r],
                                          self.interest_overdue_31_60_allTerm[date_r],
                                          self.principal_overdue_61_90_allTerm[date_r],
                                          self.interest_overdue_61_90_allTerm[date_r],
                                          self.principal_loss_allTerm[date_r],
                                          self.interest_loss_allTerm[date_r],
                                          
                                          self.principal_overdue_1_30_recycle[date_r],
                                          self.interest_overdue_1_30_recycle[date_r],
                                          self.principal_overdue_31_60_recycle[date_r],
                                          self.interest_overdue_31_60_recycle[date_r],
                                          self.principal_overdue_61_90_recycle[date_r],
                                          self.interest_overdue_61_90_recycle[date_r],
                                          
                                          self.principal_ER_recycle[date_r],
                                          self.interest_ER_recycle[date_r],     
                                          
                                          self.principal_Redemption_recycle[date_r],
                                          self.interest_Redemption_recycle[date_r],
                                          ]
        
        #logger.info('Saving APCF_adjusted_structure for scenario {0}: '.format(self.scenario_id))
        #save_to_excel(APCF_adjusted_structure,'APCF_adjusted_structure_simulation',wb_name)
        
        return self.gen_APCF_adjusted(OoR)
   
    def transit_Status(self,ppmt_this,ipmt_this,OoR,date_r_index,transition,FLAG):
        
        main_params = self.main_params 
        first_due_period = 'first_due_period_'+OoR
        
        ppmt_this = ppmt_this.reset_index(drop=True)
        ipmt_this = ipmt_this.reset_index(drop=True)
        
        bernollio_list = deepcopy(list(bernoulli.rvs(size=len(ppmt_this),p= (1-main_params[transition]))))
        bernollio_col = pd.DataFrame(bernollio_list,columns=['bernollio_col'])            
        ppmt_this[FLAG + '_'+str(date_r_index)] = bernollio_col['bernollio_col']
        
        if FLAG == 'Overdue':   
            ppmt_this[FLAG + '_'+str(date_r_index)] = ppmt_this[FLAG + '_'+str(date_r_index)].where(ppmt_this[first_due_period] <= date_r_index,1)
        
        ipmt_this[FLAG + '_'+str(date_r_index)] = ppmt_this[FLAG + '_'+str(date_r_index)]
        
        ppmt_pre = ppmt_this[ppmt_this[FLAG + '_'+str(date_r_index)]==1]
        ipmt_pre = ipmt_this[ipmt_this[FLAG + '_'+str(date_r_index)]==1]
        ppmt_next = ppmt_this[ppmt_this[FLAG + '_'+str(date_r_index)]==0]
        ipmt_next = ipmt_this[ipmt_this[FLAG + '_'+str(date_r_index)]==0]
        
        ppmt_pre = ppmt_pre.reset_index(drop=True)
        ipmt_pre = ipmt_pre.reset_index(drop=True)
        ppmt_next = ppmt_next.reset_index(drop=True)
        ipmt_next = ipmt_next.reset_index(drop=True)

        return ppmt_pre,ipmt_pre,ppmt_next,ipmt_next      
    
    def gen_APCF_adjusted(self,OoR):
        #logger.info('Generating APCF_adjusted...' )
        df_total_by_date = pd.DataFrame(self.APCF_adjusted_dict)
        APCF_adjusted = pd.DataFrame({'date_recycle': self.dates_recycle_list,
                                         'Normal_recycle_principal': df_total_by_date.transpose()[0],
                                         'Normal_recycle_interest': df_total_by_date.transpose()[1],
                                         
                                         'principal_overdue_1_30_currentTerm': df_total_by_date.transpose()[2],
                                         'interest_overdue_1_30_currentTerm': df_total_by_date.transpose()[3],
                                         'principal_overdue_31_60_currentTerm': df_total_by_date.transpose()[4],
                                         'interest_overdue_31_60_currentTerm': df_total_by_date.transpose()[5],
                                         'principal_overdue_61_90_currentTerm': df_total_by_date.transpose()[6],
                                         'interest_overdue_61_90_currentTerm': df_total_by_date.transpose()[7],
                                         'principal_loss_currentTerm': df_total_by_date.transpose()[8],
                                         'interest_loss_currentTerm': df_total_by_date.transpose()[9],
                                         'principal_overdue_1_30_allTerm': df_total_by_date.transpose()[10],
                                         'interest_overdue_1_30_allTerm': df_total_by_date.transpose()[11],
                                         'principal_overdue_31_60_allTerm': df_total_by_date.transpose()[12],
                                         'interest_overdue_31_60_allTerm': df_total_by_date.transpose()[13],
                                         'principal_overdue_61_90_allTerm': df_total_by_date.transpose()[14],
                                         'interest_overdue_61_90_allTerm': df_total_by_date.transpose()[15],
                                         'principal_loss_allTerm': df_total_by_date.transpose()[16],
                                         'interest_loss_allTerm': df_total_by_date.transpose()[17],
                                         
                                         'Overdue_1_30_recycle_principal': df_total_by_date.transpose()[18],
                                         'Overdue_1_30_recycle_interest': df_total_by_date.transpose()[19],
                                         'Overdue_31_60_recycle_principal': df_total_by_date.transpose()[20],
                                         'Overdue_31_60_recycle_interest': df_total_by_date.transpose()[21],
                                         'Overdue_61_90_recycle_principal': df_total_by_date.transpose()[22],
                                         'Overdue_61_90_recycle_interest': df_total_by_date.transpose()[23],
                                         
                                         'ER_recycle_principal': df_total_by_date.transpose()[24],
                                         'ER_recycle_interest': df_total_by_date.transpose()[25], 
                                         
                                         'Redemption_recycle_principal': df_total_by_date.transpose()[26],
                                         'Redemption_recycle_interest': df_total_by_date.transpose()[27],  
                                         
                                         'total_recycle_principal': df_total_by_date.transpose()[0] + df_total_by_date.transpose()[18] + df_total_by_date.transpose()[20] + df_total_by_date.transpose()[22] + df_total_by_date.transpose()[24] + df_total_by_date.transpose()[26],
                                         'total_recycle_interest': df_total_by_date.transpose()[1] + df_total_by_date.transpose()[19] + df_total_by_date.transpose()[21] + df_total_by_date.transpose()[23] + df_total_by_date.transpose()[25] + df_total_by_date.transpose()[27],
                                         })
    
        APCF_adjusted_save = pd.DataFrame({'date_recycle': self.dates_recycle_list,
                                 'Normal_recycle_principal': df_total_by_date.transpose()[0],
                                 'principal_overdue_1_30_currentTerm': df_total_by_date.transpose()[2],
                                 'principal_overdue_31_60_currentTerm': df_total_by_date.transpose()[4],
                                 'principal_overdue_61_90_currentTerm': df_total_by_date.transpose()[6],
                                 'principal_loss_currentTerm': df_total_by_date.transpose()[8],
                                 'principal_overdue_1_30_allTerm': df_total_by_date.transpose()[10],
                                 'principal_overdue_31_60_allTerm': df_total_by_date.transpose()[12],
                                 'principal_overdue_61_90_allTerm': df_total_by_date.transpose()[14],
                                 'principal_loss_allTerm': df_total_by_date.transpose()[16],
                                 'Overdue_1_30_recycle_principal': df_total_by_date.transpose()[18],
                                 'Overdue_31_60_recycle_principal': df_total_by_date.transpose()[20],
                                 'Overdue_61_90_recycle_principal': df_total_by_date.transpose()[22],
                                 'ER_recycle_principal': df_total_by_date.transpose()[24],
                                 'Redemption_recycle_principal': df_total_by_date.transpose()[26],
                                 'total_recycle_principal': df_total_by_date.transpose()[0] + df_total_by_date.transpose()[18] + df_total_by_date.transpose()[20] + df_total_by_date.transpose()[22] + df_total_by_date.transpose()[24] + df_total_by_date.transpose()[26],
                                 })
    
        #logger.info('Saving adjusted new APCF for scenario {0}: '.format(self.scenario_id))
        if OoR == 'R':pass
        else:save_to_excel(APCF_adjusted_save,'cf_'+OoR+'_adjusted_simulation'+Batch_ID,wb_name)
        #save_to_excel(APCF_adjusted_save,'cf_'+OoR+'_adjusted_simulation'+Batch_ID,wb_name)
        
        return APCF_adjusted[['date_recycle',
                              'total_recycle_principal','total_recycle_interest',
                              'principal_overdue_1_30_currentTerm','interest_overdue_1_30_currentTerm',
                              'principal_overdue_31_60_currentTerm','interest_overdue_31_60_currentTerm',
                              'principal_overdue_61_90_currentTerm','interest_overdue_61_90_currentTerm',
                              'principal_loss_currentTerm','interest_loss_currentTerm',
                              'principal_overdue_1_30_allTerm','interest_overdue_1_30_allTerm',
                              'principal_overdue_31_60_allTerm','interest_overdue_31_60_allTerm',
                              'principal_overdue_61_90_allTerm','interest_overdue_61_90_allTerm',
                              'principal_loss_allTerm','interest_loss_allTerm'
                              ]]
        
    def cal_overdue_31_60(self,date_r_index,ppmt_MM,ipmt_MM):
        #logger.info('len(ppmt_M1_2_M0) is {0},len(ipmt_M1_2_M0) is {1}'.format(len(ppmt_M1_2_M0),len(ipmt_M1_2_M0)))
        dates_recycle_list = self.dates_recycle_list
        ppmt_M1_2_M2,ipmt_M1_2_M2 = ppmt_MM,ipmt_MM
        
        for k in self.dates_recycle_list:
            self.principal_overdue_31_60_currentTerm_helper[k] = 0
            self.interest_overdue_31_60_currentTerm_helper[k] = 0
        for overdue_date in dates_recycle_list[date_r_index:]:
            self.principal_overdue_31_60_currentTerm_helper[overdue_date] = ppmt_M1_2_M2[overdue_date].sum()
            self.interest_overdue_31_60_currentTerm_helper[overdue_date] = ipmt_M1_2_M2[overdue_date].sum()
        self.principal_overdue_31_60_currentTerm[dates_recycle_list[date_r_index+1]] = self.principal_overdue_31_60_currentTerm_helper[dates_recycle_list[date_r_index]]+self.principal_overdue_31_60_currentTerm_helper[dates_recycle_list[date_r_index+1]]
        self.interest_overdue_31_60_currentTerm[dates_recycle_list[date_r_index+1]] = self.interest_overdue_31_60_currentTerm_helper[dates_recycle_list[date_r_index]]+self.interest_overdue_31_60_currentTerm_helper[dates_recycle_list[date_r_index+1]]
        self.principal_overdue_31_60_allTerm[dates_recycle_list[date_r_index+1]] = sum(ppmt_M1_2_M2[dates_recycle_list[date_r_index:]].sum())
        self.interest_overdue_31_60_allTerm[dates_recycle_list[date_r_index+1]] = sum(ipmt_M1_2_M2[dates_recycle_list[date_r_index:]].sum())

    def cal_overdue_61_90(self,date_r_index,ppmt_MM,ipmt_MM):
        #logger.info('len(ppmt_M2_2_M0) is {0},len(ipmt_M2_2_M0) is {1}'.format(len(ppmt_M2_2_M0),len(ipmt_M2_2_M0)))
        dates_recycle_list = self.dates_recycle_list
        ppmt_M2_2_M3,ipmt_M2_2_M3 = ppmt_MM,ipmt_MM
        
        for k in self.dates_recycle_list:
            self.principal_overdue_61_90_currentTerm_helper[k] = 0
            self.interest_overdue_61_90_currentTerm_helper[k] = 0
        for overdue_date in dates_recycle_list[date_r_index:]:
            self.principal_overdue_61_90_currentTerm_helper[overdue_date] = ppmt_M2_2_M3[overdue_date].sum()
            self.interest_overdue_61_90_currentTerm_helper[overdue_date] = ipmt_M2_2_M3[overdue_date].sum()
        self.principal_overdue_61_90_currentTerm[dates_recycle_list[date_r_index+2]] = sum(self.principal_overdue_61_90_currentTerm_helper[overdue_date] for overdue_date in dates_recycle_list[date_r_index:date_r_index+2])+self.principal_overdue_61_90_currentTerm_helper[dates_recycle_list[date_r_index+2]]
        self.interest_overdue_61_90_currentTerm[dates_recycle_list[date_r_index+2]] = sum(self.interest_overdue_61_90_currentTerm_helper[overdue_date] for overdue_date in dates_recycle_list[date_r_index:date_r_index+2])+self.interest_overdue_61_90_currentTerm_helper[dates_recycle_list[date_r_index+2]]
        self.principal_overdue_61_90_allTerm[dates_recycle_list[date_r_index+2]] = sum(ppmt_M2_2_M3[dates_recycle_list[date_r_index:]].sum())
        self.interest_overdue_61_90_allTerm[dates_recycle_list[date_r_index+2]] = sum(ipmt_M2_2_M3[dates_recycle_list[date_r_index:]].sum())
  
    def cal_loss(self,date_r_index,ppmt_MM,ipmt_MM):
        #logger.info('len(ppmt_M3_2_L) is {0},len(ipmt_M3_2_L) is {1}'.format(len(ppmt_M3_2_L),len(ipmt_M3_2_L)))
        dates_recycle_list = self.dates_recycle_list
        ppmt_M3_2_L,ipmt_M3_2_L = ppmt_MM,ipmt_MM
        
        for overdue_date in dates_recycle_list[date_r_index:]:
            self.principal_loss_currentTerm_helper[overdue_date] += ppmt_M3_2_L[overdue_date].sum()
            self.interest_loss_currentTerm_helper[overdue_date] += ipmt_M3_2_L[overdue_date].sum()
        self.principal_loss_currentTerm[dates_recycle_list[date_r_index+3]] = sum(self.principal_loss_currentTerm_helper[overdue_date] for overdue_date in dates_recycle_list[0:date_r_index+3])+self.principal_loss_currentTerm_helper[dates_recycle_list[date_r_index+3]]
        self.interest_loss_currentTerm[dates_recycle_list[date_r_index+3]] = sum(self.interest_loss_currentTerm_helper[overdue_date] for overdue_date in dates_recycle_list[0:date_r_index+3])+self.interest_loss_currentTerm_helper[dates_recycle_list[date_r_index+3]]
        self.principal_loss_allTerm[dates_recycle_list[date_r_index+3]] = self.principal_loss_allTerm[dates_recycle_list[date_r_index+2]] + sum(ppmt_M3_2_L[dates_recycle_list[date_r_index:]].sum())
        self.interest_loss_allTerm[dates_recycle_list[date_r_index+3]] = self.interest_loss_allTerm[dates_recycle_list[date_r_index+2]] + sum(ipmt_M3_2_L[dates_recycle_list[date_r_index:]].sum())          
                                             