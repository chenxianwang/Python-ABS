# -*- coding: utf-8 -*-
'''
Spyder Editor

This is a temporary script file.
'''
import sys
sys.path.append("..")
import os
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np
import datetime
from constant import path_root,wb_name,Header_Rename,Header_Rename_REVERSE,asset_pool_name_list,ProjectName,Flag_Revolving
from Params import dt_param,date_revolving_pools_cut,scenarios,\
                   Targets,RS_Group_d,Distribution_By_Category,Distribution_By_Bins,\
                   simulation_times,BackMonth,dates_recycle,asset_status_calcDate_BackMonth,calcDate,all_asset_status
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
#
    if os.path.isfile(wb_name):
      os.remove(wb_name)

    RD = RevolvingDeal(Flag_Revolving,ProjectName,dt_param['dt_pool_cut'],date_revolving_pools_cut,dt_param['dt_effective'],scenarios)
#    
    RD.get_AssetPool(asset_pool_name_list) #asset_pool_name_list
    #RD.get_AssetPool(['ABS9_R4_selected'])

#    RD.select_by_ContractNO('exclude',['ABS9_R4_selected'])   #ABS10_R1_selected
    #RD.select_by_ContractNO('focus',['all_except_abs9r4'])  

#    RD.add_Columns([
#                  [['ProfessionTypeValueTransform'],'Profession','Profession_HC'],
#                  [['UsageTypeValueTransform'],'Usage','Usage_HC'],
#                  ])
        
    #RD.asset_pool['Credit_Score'] = RD.asset_pool['Credit_Score_15'].round(3)
    #RD.asset_pool.rename(columns = Header_Rename_REVERSE).to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/check_all_except_abs9r4.csv',index=False)    
#    
#    RS_results = RD.run_ReverseSelection(Targets,RS_Group_d)
#    RS_results.to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/AssetsSelected_Final.csv',index=False)
    #RD.asset_pool.rename(columns = Header_Rename_REVERSE).to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/ABS9_R4_selected_20181102.csv',index=False)
    
    #RD.run_Stat(Distribution_By_Category,Distribution_By_Bins)
    #
    RD.asset_pool['first_due_date_after_pool_cut'] = RD.asset_pool['first_due_date_after_pool_cut'].where(RD.asset_pool['first_due_date_after_pool_cut'] != '3000/1/1',RD.date_pool_cut)
    RD.asset_pool = RD.asset_pool[RD.asset_pool['Amount_Outstanding_yuan']>0]
    
    RD.init_oAP_Acc()
    
    for asset_status in all_asset_status:
        if len(RD.asset_pool[(RD.asset_pool['贷款状态'] == asset_status)]) == 0:
            logger.info('No Assets to calc for {0}'.format(asset_status))
            continue
        else:
            #asset_status = all_asset_status[1]
            logger.info('Collecting CF for asset_status {0}'.format(asset_status))   
            #RD.asset_pool[(RD.asset_pool['贷款状态'] == asset_status)].to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/Overdue_1_30.csv',index=False)
            RD.get_oAPCF(asset_status,
                         asset_status_calcDate_BackMonth[asset_status]['BackMonth'],
                         asset_status_calcDate_BackMonth[asset_status]['calcDate']
                         )
            
            save_to_excel(RD.apcf_original[asset_status],'cf_o',wb_name)
            #save_to_excel(RD.df_ppmt[asset_status],'df_ppmt',wb_name)
            #save_to_excel(RD.apcf_original_structure[asset_status],'cf_o_structure',wb_name)
            
            for scenario_id in scenarios.keys():
                logger.info('get_adjust_oAPCF_simulation for {0}...'.format(scenario_id))
                
                for _sim in range(simulation_times):#
                    logger.info('simulator index is {0}'.format(_sim))
                    RD.adjust_oAPCF(scenario_id,asset_status,asset_status_calcDate_BackMonth[asset_status]['calcDate'])
                    save_to_excel(RD.APCF_adjusted_save[asset_status][scenario_id],'cf_O_adjusted_'+scenario_id,wb_name)
                    
                    RD.update_oAP_Acc(scenario_id,asset_status)
                
                
    #            logger.info('CDR_calc_O...for {0}...'.format(scenario_id))
    #            RD.CDR_calc_O(scenario_id,asset_status)
    #            save_to_excel(pd.DataFrame.from_dict(RD.CDR_O),'RnR&CDR',wb_name)
    
    for scenario_id in scenarios.keys():
        
        RD.oAP_Acc_DeSimulation(scenario_id,simulation_times)
        save_to_excel(RD.df_AP_PAcc_DeSimu,'De-Sim_'+scenario_id,wb_name)
        
        logger.info('CDR_calc_O...for {0}...'.format(scenario_id))
        RD.CDR_calc_O(scenario_id)
    save_to_excel(pd.DataFrame.from_dict(RD.CDR_O),'RnR&CDR',wb_name)
#            
########
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

############################################################################################    
#    SR = ServiceReport(ProjectName,datetime.date(2018,11,1),1)
#    SR.get_ServiceReportAssetsList('5thReportDate',
#                                   #['20181001_funding_abs9_asset_916_0','20181001_funding_abs9_asset_916_1','20181001_funding_abs9_asset_916_2'], #pre_AllAssetList
#                                   '',
#                                   ['1_1','1_2','1_3'], #AllAssetList
#                                   '',              #'DefaultAssetList',
#                                   '20181101_funding_abs9_waived',              #'WaivedAssetList',20180901_funding_abs9_waived_845
#                                   ''
#                                   #'RedemptionAssetList' #20180801_funding_abs9_unquali_784 
#                                   ) 
#    
    #SR.service_report_cal() #(trust_effective_date, report_period)
    #SR.service_report_AllAssetList_pre[SR.service_report_AllAssetList_pre['No_Contract'].isin(['#3694454966003'])].to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/pre_3694454966003_.csv',index=False)
    #SR.service_report_AllAssetList[SR.service_report_AllAssetList['No_Contract'].isin(['#3694454966003'])].to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/cur_3694454966003_.csv',index=False)

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
##
#    OP_All,OP_Waived = SR.check_OutstandingPrincipal()
#    OP_PCD = SR.service_report_AllAssetList_pre[['No_Contract','Amount_Outstanding_yuan']]
#    check = OP_PCD.merge(OP_All,left_on='No_Contract',right_on='No_Contract',how='inner')
#    check = check.merge(OP_Waived,left_on='No_Contract',right_on='订单号',how='left')
#
#    try:
#        check['本金减免金额'] = check['本金减免金额'].where(~check['本金减免金额'].isnull(),0)
#        check = check[abs(check['Amount_Outstanding_yuan'] - check['剩余本金_poolcutdate_calc'] - check['本金减免金额']) > 0.04]
#    except(KeyError):
#        check['减免金额'] = check['减免金额'].where(~check['减免金额'].isnull(),0)
#        check = check[abs(check['Amount_Outstanding_yuan'] - check['剩余本金_poolcutdate_calc'] - check['减免金额']) > 0.04]
#    
#    check.to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName + '/compare_OutstandingPrincipal_with_pre.csv')
#
#    Age_SR = SR.check_AgePoolCutDate()
#    Age_PCD = SR.service_report_AllAssetList_pre[['No_Contract','Age_Project_Start']]
#    check = Age_PCD.merge(Age_SR,left_on='No_Contract',right_on='No_Contract',how='left')
#    check_results = check[check['Age_Project_Start'] != check['Age_Project_Start_sr']]
#    check_results.to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName + '/check_AgePoolCutDate.csv')
##
#    for_report = SR.service_report_AllAssetList[(SR.service_report_AllAssetList['No_Contract'].isin(['#3694454966003'])) #&
#                                                       #(SR.service_report_AllAssetList['贷款是否已结清']=='未结清') &
#                                                       #(SR.service_report_AllAssetList['Usage'].isin(['其余种类','其它'])) #&
#                                                       #(SR.service_report_AllAssetList['合格资产'] == '是 ') &
#                                                       #(SR.service_report_AllAssetList['Days_Overdue_Current']>180) #.isnull()) #&
#                                                       #(SR.service_report_AllAssetList['ABS资产性质'] == 'ABS循环测试round3_r5') #&
#                                                       #(SR.service_report_AllAssetList['贷款状态'].isnull() ) #&
#                                                       #(SR.service_report_AllAssetList['Type_Five_Category'] == 'XNA')
#                                                       #(SR.service_report_AllAssetList['Amount_Outstanding_yuan'] < 0) #&
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
