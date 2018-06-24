# -*- coding: utf-8 -*-
'''
Created on Sun Jun 25 21:20:00 2017

@author: Jonah.Chen
'''
import os
import datetime


path_root = os.path.dirname(os.path.realpath(__file__))
ProjectName = 'ABS9_DWH'
wb_name = path_root  + '/../CheckTheseProjects/' + ProjectName + '/'+ProjectName+'.xlsx'

DWH_header_rename = {'#合同号':'No_Contract','#证件号码':'ID',
                     '职业':'Profession','购买商品':'Usage','信用评分':'Credit_Score',
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
DWH_header_REVERSE_rename['信用评分'] = 'Credit_Score'

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



#合同号	#证件号码	职业	年收入	信用评分	省份	申请日期	起始日	初始还款日	到期日	合同期限	剩余期数	合同本金	截至封包日剩余本金	INTEREST_RATE	利率是否固定	贷款5级分类	提前偿付	最长逾期天数	当期逾期天数	逾期本金金额	购买商品	贷款类型	担保情况	还款方式	首付比例	FLEXIBLE_PACKAGE_FLAG	FLEXIBLE_PACKAGE_NAME	FLEXIBLE_PACKAGE_DATE	每月还款总额	每月管理费	出生日期	贷款发放时借款人年龄	初始起算日借款人年龄	所属公司	NAME_CREDIT_ACQUISITION_CHNL	NAME_CREDIT_ACQUISITION_CHN_EN	消费贷款用途	历史逾期次数	PRODUCT_CATEGORY	是否为线上产品	是否强制付款	商品类型	IS_NEW_MAINTENANCE	月管理费率	总管理费用	印花税	NEW_FIVE_CLASS	五级分类	性别	家庭状况	入池时间	封包后的第一个还款日	合同贷款利息	合同天数	账龄（期数）	账龄（天数）	剩余天数	是否放款成功	综合费用率	SKP_CLIENT	INCOME_DEB_RATIO_CBR	INCOME_DEB_RATIO	RN
#3912510490001	#622301199101219185	公务员、事业单位人员	43200	TBD	甘肃	2017/12/30 18:12	2017/12/30	2018/2/1	2018/7/1	6	3	2698	1384.09	0.21	Yes	正常类	NO	0	0	0	手机	SS	Credit	principal and interest	0.1	Y	灵活还款服务包	2017/12/30	477.61	0	1991/1/21	26	27	CFC	捷信掌中宝	SMARTPOS		0	商品贷	N	N	Cell Phone	N	0	0	0	1	正常类	女	未婚	2018/4/16	2018/5/1	167.66	183	3	107	76	是	0.200118606	75651619	7.80296079	31.21184316	1000001



#        print('PoolList_Profession_D...')
#        AssetPoolList_Profession_1 = AssetPoolList[AssetPoolList['Profession'] == '学生']
#        AssetPoolList_Profession_2 = AssetPoolList[AssetPoolList['Profession'] == '其他-不便分类']
#        AssetPoolList_Profession = AssetPoolList_Profession_1.append(AssetPoolList_Profession_2,ignore_index=True)
#        AssetPoolList_Profession.to_csv('AssetPoolList_Profession_v1.csv')
#        
#        print('AssetPoolList_Usage_D...')
#        AssetPoolList_Usage_1 = AssetPoolList[AssetPoolList['Usage'] == '其余种类'] 
#        AssetPoolList_Usage_2 = AssetPoolList[AssetPoolList['Usage'] == '其它']
#        AssetPoolList_Usage = AssetPoolList_Usage_1.append(AssetPoolList_Usage_2,ignore_index=True)
#        AssetPoolList_Usage.to_csv('AssetPoolList_Usage_v1.csv')
#        
#        print('AssetPoolList_Income_D...')
#        AssetPoolList_Income_1 = AssetPoolList[AssetPoolList['Income'] < 10000]
#        AssetPoolList_Income_2 = AssetPoolList[AssetPoolList['Income'] > 2000000]
#        AssetPoolList_Income = AssetPoolList_Income_1.append(AssetPoolList_Income_2,ignore_index=True)
#        AssetPoolList_Income.to_csv('AssetPoolList_Income_v1.csv')
#
#        print('AssetPoolList_Overdue_Times_D...')
#        AssetPoolList_Overdue_Times = AssetPoolList[(AssetPoolList['Overdue_Times'] > 10)]
#        AssetPoolList_Overdue_Times.to_csv('AssetPoolList_Overdue_Times_v1.csv')
#       
#        print('AssetPoolList_Total_Fee_D...')
#        AssetPoolList_Total_Fee = AssetPoolList[(AssetPoolList['综合费用率'] > 0.24)]
#        AssetPoolList_Total_Fee.to_csv('AssetPoolList_Total_Fee_v1.csv')     
        

#        print('AssetPoolList_Save_1...')
#        AssetPoolList_Save_1 = AssetPoolList[(AssetPoolList['Profession'] != '学生') &
#                                           (AssetPoolList['Profession'] != '其他-不便分类') &
#                                           (AssetPoolList['Usage'] != '其余种类') &
#                                           (AssetPoolList['Usage'] != '其它') &
#                                           (AssetPoolList['Income'] >= 10000) &
#                                           (AssetPoolList['Income'] <= 2000000) &
#                                           (AssetPoolList['Overdue_Times'] <= 10) &
#                                           (AssetPoolList['综合费用率'] <= 0.24) 
#                                           ]
#        AssetPoolList_zero_Interest = AssetPoolList_Save_1[AssetPoolList_Save_1['Interest_Rate'] == 0] 
#        
#        print('AssetPoolList_zero_Interest_Profession_D...')
#        AssetPoolList_zero_Interest_Profession = AssetPoolList_zero_Interest[AssetPoolList_zero_Interest['Profession'] == '其它']
#        AssetPoolList_zero_Interest_Profession.to_csv('AssetPoolList_zero_Interest_Profession_v2.csv')
#    
#        print('AssetPoolList_zero_Interest_Total_Fee_D...')
#        AssetPoolList_zero_Interest_Total_Fee = AssetPoolList_zero_Interest[AssetPoolList_zero_Interest['综合费用率'] > 0]
#        AssetPoolList_zero_Interest_Total_Fee.to_csv('AssetPoolList_zero_Interest_Total_Fee_v2.csv')
#    
#    
#        print('AssetPoolList_Save_2...')
#        AssetPoolList_Save_2_1 = AssetPoolList_Save_1[(AssetPoolList_Save_1['Interest_Rate'] > 0)]
#        AssetPoolList_Save_2_2 = AssetPoolList_Save_1[(AssetPoolList_Save_1['Interest_Rate'] == 0) &
#                                                      (AssetPoolList_Save_1['Profession'] != '其它') &
#                                                      (AssetPoolList_Save_1['综合费用率'] == 0)]
#        
        #AssetPoolList_Save_2 =  AssetPoolList_Save_2_1.append(AssetPoolList_Save_2_2,ignore_index=True) 
##        
#        print('AssetPoolList_Save_3...')
#        AssetPoolList_Save_3_RemainTerm_D = AssetPoolList_Save_2_2[(AssetPoolList_Save_2_2['剩余期限（天）']<= 239)]
#        AssetPoolList_Save_3_RemainTerm_D.to_csv('AssetPoolList_ZR_RemainTerm_D_v3.csv')
#    
#        print('AssetPoolList_Save_4...')
     
#        AssetPoolList_Save_4_1 = AssetPoolList_Save_2_1
#        AssetPoolList_Save_4_2 = AssetPoolList_Save_2_2[AssetPoolList_Save_2_2['剩余期限（天）'] > 239]  
#        print('Append 4...')
#        AssetPoolList_Save_4 =  AssetPoolList_Save_4_1.append(AssetPoolList_Save_4_2,ignore_index=True) 
###        
#        print('AssetPoolList_Save_5...')
#        AssetPoolList_Save_5_LoanAge_D = AssetPoolList_Save_4[AssetPoolList_Save_4['账龄（天）'] > 720]
#        AssetPoolList_Save_5_LoanAge_D.to_csv('LoanAge_gt_720_D_v5.csv')
#        
#        AssetPoolList_Save_5_LoanAge_D = AssetPoolList_Save_4[AssetPoolList_Save_4['账龄（天）'] == 0]
#        AssetPoolList_Save_5_LoanAge_D.to_csv('LoanAge_0_D_v5.csv')
###        
#        AssetPoolList_Save_5 = AssetPoolList_Save_4[(AssetPoolList_Save_4['账龄（天）'] <= 720) &
#                                                    (AssetPoolList_Save_4['账龄（天）'] > 0) & 
#                                                    (AssetPoolList_Save_4['Type_Five_Category'] == 1)
#                                                    ]
        

               
#        AssetPoolList_Save_5_new_five_class = AssetPoolList_Save_5[AssetPoolList_Save_5['Type_Five_Category'] != 1]
#        AssetPoolList_Save_5_new_five_class.to_csv('new_five_class_v6.csv')
        
#        AssetPoolList_Save_6 = AssetPoolList_Save_5[AssetPoolList_Save_5['Type_Five_Category'] == 1]
#        AssetPoolList_Save_6['Type_Five_Category'] = '正常'
        #Due_Date_poolcut = AssetPoolList_Save_6[['No_Contract','封包后的第一个还款日','剩余期限（天）']]
              
#        AssetPoolList_Save = AssetPoolList_Save_1[(AssetPoolList_Save_1['Interest_Rate'] == 0) &
#                                                      (AssetPoolList_Save_1['Profession'] != '其它') &
#                                                      (AssetPoolList_Save_1['综合费用率'] <= 0.24)
#                                                      ]
        
#        #if len(excluded_assets) > 0:
#        print('AssetPoolListPath_to_exclude....')
#        AssetPoolListPath_to_exclude = self.ProjectPath + '/AssetPoolList/' + excluded_assets + '.csv'
#        AssetPoolList_to_exclude = pd.read_csv(AssetPoolListPath_to_exclude,encoding = 'gbk')
#        print('Check isin ...')        
#        AssetPoolList_isin = AssetPoolList[AssetPoolList['#合同号'].isin(AssetPoolList_to_exclude['#合同号'])]
#        AssetPoolList_isin.to_csv('50_sample_contracts_all_cols.csv')
#        print('isin check is done.')
        
        
#        print('Save 50 sample contracts...')
#        AssetPoolList_Save_1 = AssetPoolList_Save[AssetPoolList_Save['剩余期限（天）'] <= 245]
#        AssetPoolList_Save_1.to_csv('AssetPoolList_Save_1.csv')
#        print('Save part 2...')
#        AssetPoolList_Save_2 = AssetPoolList_Save[AssetPoolList_Save['剩余期限（天）'] > 245]
#        AssetPoolList_Save_2.to_csv('AssetPoolList_Save_2.csv')
#        print('Save done.')




