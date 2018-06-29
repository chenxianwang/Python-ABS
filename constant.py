# -*- coding: utf-8 -*-
'''
Created on Sun Jun 25 21:20:00 2017

@author: Jonah.Chen
'''
import os
import datetime


path_root = os.path.dirname(os.path.realpath(__file__))

ProjectName = 'ABS9'
path_project = path_root  + '/../CheckTheseProjects/' + ProjectName
wb_name = path_root  + '/../CheckTheseProjects/' + ProjectName + '/'+ProjectName+'.xlsx'

#DWH_header_rename = {'#合同号':'No_Contract','信用评分':'Credit_Score_15',
#                     '截至封包日剩余本金':'Amount_Outstanding_yuan',
#                     '起始日':'Dt_Start','到期日':'Dt_Maturity','INTEREST_RATE':'Interest_Rate'
#                     }


DWH_header_rename = {'#合同号':'No_Contract','#证件号码':'ID',
                     '职业':'Profession','购买商品':'Usage','信用评分':'Credit_Score_15',
                     '年收入':'Income','省份':'Province','起始日':'Dt_Start','初始还款日':'Dt_First_Pay','到期日':'Dt_Maturity','合同期限':'Term_Contract',
                      '剩余期数':'Term_Remain','合同本金':'Amount_Contract_yuan','截至封包日剩余本金':'Amount_Outstanding_yuan',
                          'INTEREST_RATE':'Interest_Rate','五级分类':'Type_Five_Category',
                          '最长逾期天数':'Days_Overdue_Max','当期逾期天数':'Days_Overdue_Current',
                          '出生日期':'Dt_Birthday','贷款发放时借款人年龄':'Age_Loan_Start',
                          '初始起算日借款人年龄':'Age_Project_Start','封包后的第一个还款日':'first_due_date_after_pool_cut',
                          '合同天数':'LoanTerm','账龄（天数）':'LoanAge','剩余天数':'LoanRemainTerm',
                          '性别':'Gender','家庭状况':'Marriagestate','历史逾期次数':'Overdue_Times',#'综合费用率':'综合费用率',
                          'SERVICE_FEE_RATE':'SERVICE_FEE_RATE','IS_NEW_SERVICE_FEE_CALCULATION':'SERVICE_FEE_CALCULATION',
                          'FLEXIBLE_PACKAGE_FLAG':'FLEXIBLE_PACKAGE_FLAG','FLEXIBLE_PACKAGE_NAME':'FLEXIBLE_PACKAGE_NAME'
                          }

DWH_header_REVERSE_rename  = {v:k for k,v in DWH_header_rename.items()}
DWH_header_REVERSE_rename['Credit_Score_15'] = '信用评分'

ABSSystem_header_rename = {'合同编号':'No_Contract','证件号码':'ID','职业类别':'Profession','年收入(万元)':'Income',
                          #'省份':'Province','初始还款日':'Dt_First_Pay','合同期限':'Term_Contract','历史逾期次数':'Overdue_Times',
                          '起息日':'Dt_Start','到期日':'Dt_Maturity','剩余期数':'Term_Remain','合同金额(元)':'Amount_Contract','封包时点余额(元)':'Amount_Outstanding',
                          '利率(%)':'Interest_Rate','最长逾期天数':'Days_Overdue_Max','当前逾期天数':'Days_Overdue_Current',
                          '购买商品':'Usage','贷款发放时借款人年龄':'Age_Loan_Start','封包日年龄':'Age_Project_Start',
                          '期限(天)':'合同期限（天）','账龄(天)':'账龄（天）','剩余期限(天)':'剩余期限（天）',
                          '性别':'Gender','婚姻状况':'Marriagestate'
                          }

DWH_header_rename_AddColumns = {'SCORE_FINAL_NEW':'Credit_Score'}

sr_recycle_rename = {'E1:正常回收':'E1：正常回收','E2：提前还款':'E2：提前还款','E3:拖欠回收':'E3；拖欠回收','E4:违约回收':'E4：违约回收','E5:账务处理':'E5：账务处理',
             'F1:正常回收':'F1：正常回收','F2：提前还款':'F2：提前还款','F3:拖欠回收':'F3：拖欠回收','F4:违约回收':'F4：违约回收','F5:账务处理':'F5：账务处理'
             }

sr_distribution_rename = {'订单号':'No_Contract','账户号':'ID','借款人职业':'Profession','贷款用途':'Usage',
                     #'信用评分':'Credit_Score','初始还款日':'Dt_First_Pay','出生日期':'Dt_Birthday',
                     '借款人年龄':'Age_Project_Start',
                     '借款人年收入':'Income','G3：省份':'Province','贷款发放日':'Dt_Start','贷款到期日':'Dt_Maturity','合同期数':'Term_Contract',
                      '剩余期数':'Term_Remain','合同金额':'Amount_Contract_yuan','剩余本金':'Amount_Outstanding_yuan',
                          '合同贷款利率':'Interest_Rate','五级分类':'Type_Five_Category',
                          '历史最大逾期天数':'Days_Overdue_Max','当前逾期天数':'Days_Overdue_Current',
                          '下一个交易日':'first_due_date_after_pool_cut',
                          '合同天数':'LoanTerm',
                          '账龄':'LoanAge','剩余天数':'LoanRemainTerm',
                          #'性别':'Gender','家庭状况':'Marriagestate','历史逾期次数':'Overdue_Times',#'综合费用率':'综合费用率',
                          #'SERVICE_FEE_RATE':'SERVICE_FEE_RATE','IS_NEW_SERVICE_FEE_CALCULATION':'SERVICE_FEE_CALCULATION',
                          #'FLEXIBLE_PACKAGE_FLAG':'FLEXIBLE_PACKAGE_FLAG','FLEXIBLE_PACKAGE_NAME':'FLEXIBLE_PACKAGE_NAME'
                          }
