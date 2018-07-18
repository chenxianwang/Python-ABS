# -*- coding: utf-8 -*-
"""
Created on Mon May 28 13:42:18 2018

@author: jonah.chen
"""

import sys
import os
from constant import *
import pandas as pd
import numpy as np
from abs_util.util_general import *
from abs_util.util_cf import *
from abs_util.util_sr import *
from dateutil.relativedelta import relativedelta
import datetime
logger = get_logger(__name__)

class ServiceReport():
    
    def __init__(self,name,trust_effective_date,report_period):
        self.name = name
        self.trust_effective_date = trust_effective_date
        
        self.service_report_AllAssetList_pre = pd.DataFrame()
        
        self.service_report_AllAssetList = pd.DataFrame()
        self.service_report_DefaultAssetList = pd.DataFrame()
        self.service_report_WaivedAssetList = pd.DataFrame()
        self.service_report_RedemptionAssetList = pd.DataFrame()
        
        self.for_report = pd.DataFrame()
        
        self.report_period = report_period
        
        
    def get_ServiceReportAssetsList(self,FilePath,AllAssetList_previous,AllAssetList,DefaultAssetList,WaivedAssetList,RedemptionAssetList):
        
        if AllAssetList_previous != '':
            for Pool_index,Pool_name in enumerate(AllAssetList_previous):
                logger.info('Getting AllAssetList_pre part ' + str(Pool_index+1) + '...')
                AssetPoolPath_all_pre = path_root +'/../CheckTheseProjects/'+self.name+'/ServiceReportList/'+ '/' + FilePath + '/' + Pool_name + '.csv'
                try:
                    AssetPool_all_pre = pd.read_csv(AssetPoolPath_all_pre,encoding = 'utf-8') 
                except:
                    AssetPool_all_pre = pd.read_csv(AssetPoolPath_all_pre,encoding = 'gbk') 
                AssetPool_all_pre['订单号'] = '#' + AssetPool_all_pre['订单号'].astype(str)
                self.service_report_AllAssetList_pre = self.service_report_AllAssetList_pre.append(AssetPool_all_pre,ignore_index=True)
            self.service_report_AllAssetList_pre = self.service_report_AllAssetList_pre.rename(columns = sr_distribution_rename)
            
        for Pool_index,Pool_name in enumerate(AllAssetList):
            logger.info('Getting AllAssetList part ' + str(Pool_index+1) + '...')
            AssetPoolPath_all = path_root +'/../CheckTheseProjects/'+self.name+'/ServiceReportList/'+ '/' + FilePath + '/' + Pool_name + '.csv'
            try:
                AssetPool_all = pd.read_csv(AssetPoolPath_all,encoding = 'utf-8') 
            except:
                AssetPool_all = pd.read_csv(AssetPoolPath_all,encoding = 'gbk') 
            AssetPool_all['订单号'] = '#' + AssetPool_all['订单号'].astype(str)
            self.service_report_AllAssetList = self.service_report_AllAssetList.append(AssetPool_all,ignore_index=True)
            
        if DefaultAssetList != '':
            logger.info('Getting DefaultAssetList...')
            AssetPoolPath_this = path_root +'/../CheckTheseProjects/'+self.name+'/ServiceReportList/'+ FilePath + '/' + DefaultAssetList + '.csv'
            try:
                AssetPoolPath_this = pd.read_csv(AssetPoolPath_this,encoding = 'utf-8') 
            except:
                AssetPoolPath_this = pd.read_csv(AssetPoolPath_this,encoding = 'gbk')
            self.service_report_DefaultAssetList = self.service_report_DefaultAssetList.append(AssetPool_this,ignore_index=True)

        if WaivedAssetList != '':
            logger.info('Getting WaivedAssetList...')
            AssetPoolPath_this = path_root +'/../CheckTheseProjects/'+self.name+'/ServiceReportList/' + FilePath + '/' + WaivedAssetList + '.csv'
            try:
                AssetPoolPath_this = pd.read_csv(AssetPoolPath_this,encoding = 'utf-8') 
            except:
                AssetPoolPath_this = pd.read_csv(AssetPoolPath_this,encoding = 'gbk') 
            self.service_report_WaivedAssetList = self.service_report_WaivedAssetList.append(AssetPool_this,ignore_index=True)
        
        if RedemptionAssetList != '':
            logger.info('Getting RedemptionAssetList...')
            AssetPoolPath_redemp = path_root +'/../CheckTheseProjects/'+self.name+'/ServiceReportList/'+ FilePath + '/' + RedemptionAssetList + '.csv'
            #print(AssetPoolPath_redemp[:5])
            try:
                AssetPool_redemp = pd.read_csv(AssetPoolPath_redemp,encoding = 'utf-8') 
            except:
                AssetPool_redemp = pd.read_csv(AssetPoolPath_redemp,encoding = 'gbk') 
            AssetPool_redemp['订单号'] = '#' + AssetPool_redemp['订单号'].astype(str)
            self.service_report_RedemptionAssetList = self.service_report_RedemptionAssetList.append(AssetPool_redemp,ignore_index=True)

            #self.service_report_RedemptionAssetList = self.service_report_RedemptionAssetList.rename(columns = sr_distribution_rename)
        
        self.service_report_AllAssetList = self.service_report_AllAssetList.rename(columns = sr_distribution_rename)

        self.for_report = self.service_report_AllAssetList[#(~self.service_report_AllAssetList['No_Contract'].isin(self.service_report_RedemptionAssetList['订单号'])) &
                                                           (self.service_report_AllAssetList['贷款是否已结清'] == 'N') &
                                                           (self.service_report_AllAssetList['贷款状态'] == '拖欠1-30天贷款' ) &
                                                           #(self.service_report_AllAssetList['Type_Five_Category'] == 'XNA')
                                                           (self.service_report_AllAssetList['入池时间'] == '2018/4/16') &
                                                           (pd.to_datetime(self.service_report_AllAssetList['Dt_Maturity']).dt.year == 2020) &
                                                           (pd.to_datetime(self.service_report_AllAssetList['Dt_Maturity']).dt.month == 4) &
                                                           (pd.to_datetime(self.service_report_AllAssetList['Dt_Maturity']).dt.day == 25)
                                                           ]
        self.for_report.to_csv(path_root  + '/../CheckTheseProjects/' +self.name+'/' + 'for_report_cf_check_o.csv')
        
    def add_SeviceRate_From(self,df):
        
        logger.info('Adding Service Fee Rate...')
        #self.for_report['No_Contract'] = '#' + self.for_report['No_Contract'].astype(str)
        self.for_report = self.for_report.merge(df,left_on='No_Contract',right_on='No_Contract',how='left')
        #self.for_report.to_csv('for_report_cf_check.csv')
        print("for_report['SERVICE_FEE_RATE'].sum(): ",self.for_report['SERVICE_FEE_RATE'].sum())

    def check_NextPayDate(self):
        logger.info('check_NextPayDate...')
        DetailList = self.service_report_AllAssetList
        NextPayDate = DetailList[#(~self.service_report_AllAssetList['订单号'].isin(self.service_report_RedemptionAssetList['订单号'])) &
                                (DetailList['Amount_Outstanding_yuan'] > 0) &
                                (DetailList['first_due_date_after_pool_cut'] == '3000/1/1') &
                                (pd.to_datetime(DetailList['Dt_Maturity']).dt.date <= TrustEffectiveDate )
                               ]
        NextPayDate.to_csv(path_root  + '/../CheckTheseProjects/' +self.name+'/' + 'check_NextPayDate.csv')
        
    
    def check_Redemption_price(self):
       logger.info('check_Redemption_price......')
       AllDetailList = self.service_report_AllAssetList[['No_Contract','剩余本金']]
       RedemptionDetailList = self.service_report_RedemptionAssetList[['No_Contract','赎回贷款债权的未偿本金余额']]
       
       AllDetailList['#合同号'] = "#" + AllDetailList['No_Contract'].astype(str)
       RedemptionDetailList['#合同号'] = "#" + RedemptionDetailList['订单号'].astype(str)
       
       logger.info('Inner Merging...')
       R_A = RedemptionDetailList.merge(AllDetailList,left_on='#合同号',right_on='#合同号',how='inner')
       R_A_D = R_A[R_A['剩余本金'] != R_A['赎回贷款债权的未偿本金余额']]
       R_A_D.to_csv(path_root  + '/../CheckTheseProjects/' +self.name+'/' + 'R_A_D.csv')
    
    
    def check_OutstandingPrincipal(self):
        logger.info('check_OutstandingPrincipal......')
        DetailList = self.service_report_AllAssetList
        DetailList = DetailList[['No_Contract','Amount_Outstanding_yuan','B1：正常回收','B2：提前还款','B3：拖欠回收','B4：违约回收','B5：账务处理']]
        DetailList[['Amount_Outstanding_yuan','B1：正常回收','B2：提前还款','B3：拖欠回收','B4：违约回收','B5：账务处理']] = DetailList[['Amount_Outstanding_yuan','B1：正常回收','B2：提前还款','B3：拖欠回收','B4：违约回收','B5：账务处理']].where(DetailList[['Amount_Outstanding_yuan','B1：正常回收','B2：提前还款','B3：拖欠回收','B4：违约回收','B5：账务处理']]!=0,0)
        DetailList = DetailList.rename(columns = {'Amount_Outstanding_yuan':'Amount_Outstanding'})
        DetailList['剩余本金_poolcutdate_calc'] = DetailList['Amount_Outstanding']+DetailList['B1：正常回收']+DetailList['B2：提前还款']+DetailList['B3：拖欠回收']+DetailList['B4：违约回收']+DetailList['B5：账务处理']
        return DetailList
     
    def check_AgePoolCutDate(self):
        logger.info('check_AgePoolCutDate......')
        DetailList = self.service_report_AllAssetList
        DetailList = DetailList[['订单号','借款人年龄']]
        return DetailList
        
    
    def check_LoanAging(self):
        logger.info('check_LoanAging...')
        DetailList = self.service_report_AllAssetList[self.service_report_AllAssetList['贷款是否已结清']=='N'][['No_Contract','Dt_Start','Dt_Maturity','Days_Overdue_Current','LoanAge','LoanTerm','LoanRemainTerm']]
        DetailList['TrustEffectiveDate'] = TrustEffectiveDate
        DetailList['账龄_Jonah'] = (DetailList['TrustEffectiveDate']+ relativedelta(days=-1)).where(DetailList['TrustEffectiveDate'] <= pd.to_datetime(DetailList['Dt_Maturity']).dt.date + relativedelta(days=1),pd.to_datetime(DetailList['Dt_Maturity']).dt.date)  \
                                    - pd.to_datetime(DetailList['Dt_Start']).dt.date 
        DetailList['账龄_Jonah'] = (DetailList['账龄_Jonah'] / np.timedelta64(1, 'D')).astype(int)
        DetailList = DetailList[DetailList['账龄_Jonah'] != DetailList['LoanAge']]
        DetailList.to_csv(path_root  + '/../CheckTheseProjects/' +self.name+'/' + 'check_账龄_Jonah.csv')

    def check_ContractTerm(self):
        logger.info('check_ContractTerm...')
        DetailList = self.service_report_AllAssetList[self.service_report_AllAssetList['贷款是否已结清']=='N'][['No_Contract','Dt_Start','Dt_Maturity','Days_Overdue_Current','LoanAge','LoanTerm','LoanRemainTerm']]
        DetailList['合同天数_Jonah'] = pd.to_datetime(DetailList['Dt_Maturity']).dt.date - pd.to_datetime(DetailList['Dt_Start']).dt.date 
        DetailList['合同天数_Jonah'] = (DetailList['合同天数_Jonah'] / np.timedelta64(1, 'D')).astype(int)
        
        #DetailList['合同天数_Jonah'] = DetailList['LoanAge'] + DetailList['LoanRemainTerm']
        
        DetailList = DetailList[DetailList['合同天数_Jonah'] != DetailList['LoanTerm']]
        
        DetailList.to_csv(path_root  + '/../CheckTheseProjects/' +self.name+'/' + 'check_合同天数_Jonah.csv')
    
    def closed_with_outstandingprincipal(self):
        logger.info('closed_with_outstandingprincipal...')
        DetailList = self.service_report_AllAssetList[(self.service_report_AllAssetList['贷款是否已结清']=='N') & 
                                                       (self.service_report_AllAssetList['Type_Five_Category']=='XNA')
                                                        ]
        DetailList.to_csv(path_root  + '/../CheckTheseProjects/' +self.name+'/' + 'check_五级分类_Jonah.csv')
        save_to_excel(group_by_d(self.service_report_AllAssetList,['贷款是否已结清','Type_Five_Category'],'Amount_Outstanding_yuan'),'service_report',self.wb_save_results)
    
    
    def service_report_cal(self):
        logger.info('service_report_cal...')
        #cal_table_4_1(self.for_report,wb_name_sr)
        #cal_table_4_2(self.service_report_DefaultAssetList,self.wb_save_results)
        #cal_table_4_3(ServiceReportListPath_D,self.pool_cut_volumn,self.report_period,self.wb_to_save_results)
        
        #cal_table_5(ServiceReportListPath_D,self.wb_to_save_results)
        
#        _calcDate = self.trust_effective_date + relativedelta(months=self.report_period-1)
#        calcDate = date(_calcDate.year,_calcDate.month,1)
        
        cal_table_6(self.for_report,self.trust_effective_date,wb_name_sr)
        
        #cal_table_7(self.service_report_AllAssetList,wb_name_sr)
        #cal_table_10(self.for_report,self.wb_save_results)    
        
        
        