# -*- coding: utf-8 -*-
'''
Spyder Editor

This is a temporary script file.
'''
import sys
sys.path.append("..")
import os
import pandas as pd
import numpy as np
import datetime
from constant import *
from Params import *
from abs_util.util_general import *
from Deal import Deal
from RevolvingDeal import RevolvingDeal
from Statistics import Statistics
from ReverseSelection import ReverseSelection
from AssetsCashFlow import AssetsCashFlow
from ServiceReport import ServiceReport

logger = get_logger(__name__)

def main(): 
    
    start_time = datetime.datetime.now()

#    if os.path.isfile(wb_name):
#      os.remove(wb_name)

    asset_pool_name_list = ['OriginalPool_part1','OriginalPool_part2']
    #asset_pool_name_list = ['ABS9_R1_selected']
    #asset_pool_name_list = ['1','2','3','4'] 
    D = Deal(ProjectName,dt_param['dt_pool_cut'],asset_pool_name_list,dt_param['dt_effective'],recycle_adjust_factor,scenarios)
    D.get_AssetPool()    # D.asset_pool is available

    #D.select_by_ContractNO('focus','ABS9_R1_selected')
    
    #D.asset_pool = D.asset_pool[D.asset_pool['Credit_Score_15'] > 0]
#  #D.asset_pool = D.asset_pool[(pd.to_datetime(D.asset_pool['Dt_Start']).dt.date < datetime.date(2018,7,1)) &
#                                (D.asset_pool['Credit_Score_15'] == -1)
#                                ]
#    D.asset_pool = D.asset_pool[pd.to_datetime(D.asset_pool['Dt_Maturity']).dt.date >= datetime.datetime.now().date()]
    
#    D.add_Columns([
#                  #[['AssetsFromCFIT'],'No_Contract','#合同号'],
#                  #[['ProfessionTypeValueTransform'],'Profession','Profession_HC'],
#                  [['abs10_contract_list_0','abs10_contract_list_1'],'No_Contract','#合同号']
#                  ]
#                  )
 
    
    ##D.asset_pool[D.asset_pool['LoanRemainTerm'] <= 230].rename(columns = Header_Rename_REVERSE).to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/udpate_cs_ABS10_1.csv',index=False)
    ##D.asset_pool[D.asset_pool['LoanRemainTerm'] > 230].rename(columns = Header_Rename_REVERSE).to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/update_cs_ABS10_2.csv',index=False)    
    
    D.asset_pool['Credit_Score'] = D.asset_pool['Credit_Score_15']#.round(3)

    ##D.run_ReverseSelection(Targets,RS_Group_d)
    ##D.asset_pool.rename(columns = DWH_header_REVERSE_rename).to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/ABS9_R1_selected_final_20180801.csv',index=False)
    
    #D.asset_pool['Amount_Outstanding_yuan'] = D.asset_pool['Amount_Outstanding_yuan'].where(D.asset_pool['Days_Overdue_Current']<=180,0)
    #D.run_Stat()
    
#    D.asset_pool['SERVICE_FEE_RATE'] = 0
    #D.get_oAPCF()         # D.apcf is available
    #D.adjust_oAPCF()      # D.apcf_adjusted[scenario_id] is available
#    
    D.get_adjust_oAPCF()    
#    
    D.init_oAP_Acc()
    D.run_WaterFall()    # D.waterfall[scenario_id] is available
    for scenario_id in scenarios.keys():
        save_to_excel(D.waterfall[scenario_id],scenario_id,wb_name)
        save_to_excel(D.wf_BasicInfo[scenario_id],scenario_id,wb_name)
        save_to_excel(D.wf_CoverRatio[scenario_id],scenario_id,wb_name)
        save_to_excel(D.wf_NPVs[scenario_id],scenario_id,wb_name)
    
    RnR = D.cal_RnR()
    logger.info('RnR is: %s' % RnR)
    save_to_excel(pd.DataFrame({'RnR':[RnR]}),'RnR',wb_name)


#    RD = RevolvingDeal(ProjectName,dt_param['dt_pool_cut'],asset_pool_name_list,date_revolving_pools_cut,dt_param['dt_effective'],recycle_adjust_factor,scenarios)
#    RD.get_rAssetPool() 
#    RD.asset_pool['Credit_Score'] = RD.asset_pool['Credit_Score_15'].round(3)
#    RD.run_Stat()
#    RD.get_oAPCF()         # RD.apcf is available
#    RD.get_rAPCF_structure()
#    
#    RD.adjust_oAPCF()
#    RD.init_oAP_Acc()
#    
#    RD.forcast_Revolving_APCF()
#    
#    RD.run_WaterFall()    # RD.waterfall[scenario_id] is available
#    for scenario_id in scenarios.keys():
#        save_to_excel(RD.waterfall[scenario_id],scenario_id,wb_name)
#        save_to_excel(RD.wf_BasicInfo[scenario_id],scenario_id,wb_name)
#        save_to_excel(RD.wf_CoverRatio[scenario_id],scenario_id,wb_name)
#        save_to_excel(RD.wf_NPVs[scenario_id],scenario_id,wb_name)
#    
#    RnR = RD.cal_RnR()
#    logger.info('RnR is: %s' % RnR)
#    save_to_excel(pd.DataFrame({'RnR':[RnR]}),'RnR',wb_name)
#    
#    SR = ServiceReport(ProjectName,ADate,1)
#    SR.get_ServiceReportAssetsList('13thReportDate',
#                                   ['12_1','12_2','12_3','12_4','12_5','12_6','12_7'], #pre_AllAssetList
#                                   #'',
#                                   ['13_1','13_2','13_3','13_4','13_5','13_6','13_7'], #AllAssetList
#                                   '',              #'DefaultAssetList',
#                                   'WaivedAssetList',              #'WaivedAssetListq',
#                                   ''
#                                   #'RedemptionAssetList' #20180801_funding_abs9_unquali_784 
#                                   ) 
#    
##    SR.add_SeviceRate_From(RD.asset_pool[['No_Contract','SERVICE_FEE_RATE']])
#    #print(SR.service_report_AllAssetList[SR.service_report_AllAssetList['贷款是否已结清'] == '已结清'].count())
#    
#    #SR.select_by_ContractNO('9thReportDate','focus','focusContracts')
    #SR.service_report_cal() #(trust_effective_date, report_period)
    
    #SR.check_NextPayDate()
    #SR.check_LoanAging()
    #SR.closed_with_outstandingprincipal()
    #SR.check_ContractTerm()
    #SR.check_Redemption_price()

#    report_basis = SR.service_report_AllAssetList[(SR.service_report_AllAssetList['贷款是否已结清'] == '未结清') 
#                                                  #&(SR.service_report_AllAssetList['ABS资产性质'] == 'ABS循环测试round3_r5')
#                                                  ]
#    report_basis['Amount_Outstanding_yuan'] = report_basis['Amount_Outstanding_yuan'].where(report_basis['Days_Overdue_Current']<=180,0)
#    report_basis['Type_Five_Category'] = report_basis['Type_Five_Category'].where(~report_basis['Type_Five_Category'].isnull(),'XNA')
#    report_basis['Usage'] = report_basis['Usage'].where(~report_basis['Usage'].isnull(),'XNA')
##    
#    report_basis['Credit_Score'] = report_basis['Credit_Score_15']#.round(3)
#    S = Statistics(report_basis)
#    S.general_statistics_1()
#    S.loop_Ds_ret_province_profession(Distribution_By_Category,Distribution_By_Bins)
#    S.cal_income2debt_by_ID()
##
#    OP_All,OP_Waived = SR.check_OutstandingPrincipal()
#    #print(OP_BB[OP_BB['No_Contract'] == '3878739137002']['剩余本金_poolcutdate_calc'])
#    OP_PCD = SR.service_report_AllAssetList_pre[['No_Contract','Amount_Outstanding_yuan']]
#    check = OP_PCD.merge(OP_All,left_on='No_Contract',right_on='No_Contract',how='inner')
#    check = check.merge(OP_Waived,left_on='No_Contract',right_on='订单号',how='left')
#    check['本金减免金额'] = check['本金减免金额'].where(~check['本金减免金额'].isnull(),0)
#    check = check[abs(check['Amount_Outstanding_yuan'] - check['剩余本金_poolcutdate_calc'] - check['本金减免金额']) == 0]
#    #check = check[(check['Amount_Outstanding_yuan']==check['Amount_Outstanding']) & (check['本金：正常回收'] + check['本金：账务处理'] == 0)]
#    check.to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName + '/check_OutstandingPrincipal_pre.csv')

#    Age_SR = SR.check_AgePoolCutDate()
#    Age_PCD = SR.service_report_AllAssetList_pre[['No_Contract','Age_Project_Start']]
#    check = Age_PCD.merge(Age_SR,left_on='No_Contract',right_on='No_Contract',how='left')
#    check_results = check[check['Age_Project_Start'] != check['Age_Project_Start_sr']]
#    check_results.to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName + '/check_AgePoolCutDate.csv')
#
#    for_report = SR.service_report_AllAssetList_pre[#(~SR.service_report_AllAssetList['No_Contract'].isin(self.service_report_RedemptionAssetList['订单号'])) &
#                                                       #(SR.service_report_AllAssetList['贷款是否已结清'] == 'N') &
#                                                       (SR.service_report_AllAssetList_pre['No_Contract'] == '#3526383292003') #&
#                                                       #(SR.service_report_AllAssetList['合格资产'] == '是 ') &
#                                                       #(SR.service_report_AllAssetList['Days_Overdue_Current']>180) #.isnull()) #&
#                                                       #(SR.service_report_AllAssetList['ABS资产性质'] == 'ABS循环测试round3_r5') #&
#                                                       #(SR.service_report_AllAssetList['贷款状态'] == '正常贷款' ) #&
#                                                       #(SR.service_report_AllAssetList['Type_Five_Category'] == 'XNA')
#                                                       #(SR.service_report_AllAssetList['Usage'] == '278657	') #&
#                                                       #(pd.to_datetime(SR.service_report_AllAssetList['Dt_Maturity']).dt.year == 2020) &
#                                                       #(pd.to_datetime(SR.service_report_AllAssetList['Dt_Maturity']).dt.month == 4) &
#                                                       #(pd.to_datetime(SR.service_report_AllAssetList['Dt_Maturity']).dt.day == 25)
#                                                       ]
#    for_report.to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/' + 'for_report_check.csv')

    end_time = datetime.datetime.now()   
    time_elapsed = end_time - start_time
    logger.info('Time: %0.4f' % time_elapsed.total_seconds())


if __name__ == '__main__':
    main()
