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
from constant import wb_name,Header_Rename,asset_pool_name_list,ProjectName
from Params import dt_param,date_revolving_pools_cut,scenarios,\
                   Targets,RS_Group_d,path_root,Distribution_By_Category,Distribution_By_Bins,\
                   simulation_times
from abs_util.util_general import save_to_excel,get_logger
from Deal import Deal
from RevolvingDeal import RevolvingDeal
from Statistics import Statistics
from ReverseSelection import ReverseSelection
from AssetsCashFlow import AssetsCashFlow
from ServiceReport import ServiceReport

logger = get_logger(__name__)

def main(): 
    
    start_time = datetime.datetime.now()

    if os.path.isfile(wb_name):
      os.remove(wb_name)
#
    RD = RevolvingDeal(True,ProjectName,dt_param['dt_pool_cut'],date_revolving_pools_cut,dt_param['dt_effective'],scenarios)
    #RD = RevolvingDeal(False,ProjectName,dt_param['dt_pool_cut'],date_revolving_pools_cut,dt_param['dt_effective'],scenarios)
    
    RD.get_AssetPool(asset_pool_name_list)    # D.asset_pool is available
    
    #self.asset_pool = self.asset_pool[list(Header_Rename.keys())] 
    logger.info('Renaming header....')
    RD.asset_pool = RD.asset_pool.rename(columns = Header_Rename) 
    
    #RD.asset_pool['Credit_Score'] = RD.asset_pool['Credit_Score_15'].round(3)
        
    #RD.select_by_ContractNO('exclude',[''])  
    #RD.select_by_ContractNO('focus',[''])  
#    
    #RD.asset_pool.rename(columns = Header_Rename_REVERSE).to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/Dt_Maturity.csv',index=False)    
#    
#    RD.add_Columns([
#                  [['R3_selected'],'No_Contract','#合同号'],
#                  #[['ProfessionTypeValueTransform'],'Profession','Profession_HC'],
#                  #[['UsageTypeValueTransform'],'Usage','Usage_HC'],
#                  #[['check_assets'],'No_Contract','合同号'],
#                  ])
# 

    #RS_results = RD.run_ReverseSelection(Targets,RS_Group_d)
    #RS_results.to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/AssetsSelected_Final.csv',index=False)
    #RD.asset_pool.rename(columns = Header_Rename_REVERSE).to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/R3_selected_jonah.csv',index=False)
    
    #RD.run_Stat(Distribution_By_Category,Distribution_By_Bins)
#    
    #for _sim in range(simulation_times):
    #logger.info('simulator index is {0}'.format(_sim))
    RD.get_adjust_oAPCF(0) #BackMonth = 0  
    #save_to_excel(RD.apcf_original,'cf_o',wb_name)
    #save_to_excel(RD.apcf_original_structure,'cf_o_structure',wb_name)
    #save_to_excel(df_ppmt,'df_ppmt',wb_name)

    RD.init_oAP_Acc()
    save_to_excel(pd.DataFrame.from_dict(RD.CDR_O),'RnR&CDR',wb_name)
######
    RD.get_rAPCF_structure()
    RD.forcast_Revolving_APCF()
#   
    RD.run_WaterFall()    # D.waterfall[scenario_id] is available
    for scenario_id in scenarios.keys():
        logger.info('Saving results for scenario {0} '.format(scenario_id))
        save_to_excel(RD.waterfall[scenario_id],scenario_id,wb_name)
        save_to_excel(RD.wf_BasicInfo[scenario_id],scenario_id,wb_name)
        save_to_excel(RD.wf_CoverRatio[scenario_id],scenario_id,wb_name)
        save_to_excel(RD.wf_NPVs[scenario_id],scenario_id,wb_name)
        save_to_excel(RD.reserveAccount_used[scenario_id],scenario_id,wb_name)
    
    RnR = RD.cal_RnR()
    logger.info('RnR is: %s' % RnR)
    save_to_excel(pd.DataFrame({'RnR':[RnR]}),'RnR&CDR',wb_name)

#    
#    SR = ServiceReport(ProjectName,ADate,1)
#    SR.get_ServiceReportAssetsList('1stReportDate',
#                                   #['1_1','1_2'], #pre_AllAssetList
#                                   '',
#                                   ['1_1','1_2','1_3'], #AllAssetList
#                                   '',              #'DefaultAssetList',
#                                   '',              #'WaivedAssetList',20180901_funding_abs9_waived_845
#                                   ''
#                                   #'RedemptionAssetList' #20180801_funding_abs9_unquali_784 
#                                   ) 
##    
#    SR.service_report_cal() #(trust_effective_date, report_period)
    
#    report_basis = SR.service_report_AllAssetList[(SR.service_report_AllAssetList['贷款是否已结清'] == 'N') 
#                                                  &(SR.service_report_AllAssetList['入池时间'] == '2018/8/1')
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

#    OP_All,OP_Waived = SR.check_OutstandingPrincipal()
#    #OP_All = SR.check_OutstandingPrincipal()
#    #print(OP_BB[OP_BB['No_Contract'] == '3878739137002']['剩余本金_poolcutdate_calc'])
#    OP_PCD = SR.service_report_AllAssetList_pre[['No_Contract','Amount_Outstanding_yuan']]
#    check = OP_PCD.merge(OP_All,left_on='No_Contract',right_on='No_Contract',how='inner')
#    check = check.merge(OP_Waived,left_on='No_Contract',right_on='订单号',how='left')
#    check = check[check['No_Contract' == '#3685144445001']]
##    try:
##        check['本金减免金额'] = check['本金减免金额'].where(~check['本金减免金额'].isnull(),0)
##        check = check[abs(check['Amount_Outstanding_yuan'] - check['剩余本金_poolcutdate_calc'] - check['本金减免金额']) > 0.04]
##    except(KeyError):
##        check['减免金额'] = check['减免金额'].where(~check['减免金额'].isnull(),0)
##        check = check[abs(check['Amount_Outstanding_yuan'] - check['剩余本金_poolcutdate_calc'] - check['减免金额']) > 0.04]
#    #check = check[abs(check['Amount_Outstanding_yuan'] - check['剩余本金_poolcutdate_calc']) > 0.04]
#    #check = check[(check['Amount_Outstanding_yuan']==check['Amount_Outstanding']) & (check['本金：正常回收'] + check['本金：账务处理'] == 0)]
#    check.to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName + '/check_OutstandingPrincipal_pre.csv')

#    Age_SR = SR.check_AgePoolCutDate()
#    Age_PCD = SR.service_report_AllAssetList_pre[['No_Contract','Age_Project_Start']]
#    check = Age_PCD.merge(Age_SR,left_on='No_Contract',right_on='No_Contract',how='left')
#    check_results = check[check['Age_Project_Start'] != check['Age_Project_Start_sr']]
#    check_results.to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName + '/check_AgePoolCutDate.csv')
#
#    for_report = SR.service_report_AllAssetList[#(~SR.service_report_AllAssetList['No_Contract'].isin(self.service_report_RedemptionAssetList['订单号'])) &
#                                                       #(SR.service_report_AllAssetList['贷款是否已结清']=='未结清') &
#                                                       #(SR.service_report_AllAssetList['Usage'].isin(['其余种类','其它'])) #&
#                                                       #(SR.service_report_AllAssetList['合格资产'] == '是 ') &
#                                                       #(SR.service_report_AllAssetList['Days_Overdue_Current']>180) #.isnull()) #&
#                                                       #(SR.service_report_AllAssetList['ABS资产性质'] == 'ABS循环测试round3_r5') #&
#                                                       #(SR.service_report_AllAssetList['贷款状态'].isnull() ) #&
#                                                       #(SR.service_report_AllAssetList['Type_Five_Category'] == 'XNA')
#                                                       (SR.service_report_AllAssetList['Amount_Outstanding_yuan'] < 0) #&
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
