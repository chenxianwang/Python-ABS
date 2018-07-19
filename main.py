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
    #asset_pool_name_list = ['ABS10 contract list_20180719_0','ABS10 contract list_20180719_1','ABS10 contract list_20180719_2']
#    D = Deal(ProjectName,dt_param['dt_pool_cut'],asset_pool_name_list,dt_param['dt_effective'],recycle_adjust_factor,scenarios)
#    D.get_AssetPool()    # D.asset_pool is available
##    
#    #D.select_by_ContractNO('exclude','ABS9_R1_selected')
##    
#    #D.asset_pool = D.asset_pool[D.asset_pool['Credit_Score_15'] == 0]
#    #D.asset_pool = D.asset_pool[pd.to_datetime(D.asset_pool['Dt_Start']).dt.date >= datetime.date(2018,7,1)]
#    #D.asset_pool = D.asset_pool[pd.to_datetime(D.asset_pool['Dt_Maturity']).dt.date >= datetime.datetime.now().date()]
    
#    D.add_Columns([
#                  #[['AssetsFromCFIT'],'No_Contract','#合同号'],
#                  [['ProfessionTypeValueTransform'],'Profession','Profession_HC'],
#                  #[['ABS9 contract list_20180416_0','ABS9 contract list_20180416_1'],'No_Contract','#合同号']
#                  ]
#                  )
## 
#    #D.asset_pool[D.asset_pool['LoanRemainTerm'] <= 230].rename(columns = DWH_header_REVERSE_rename).to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/remain_to_ABS10_1.csv',index=False)
#    #D.asset_pool[D.asset_pool['LoanRemainTerm'] > 230].rename(columns = DWH_header_REVERSE_rename).to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/remain_to_ABS10_2.csv',index=False)    
##    
#    D.asset_pool['Credit_Score'] = D.asset_pool['Credit_Score_15'].round(3)
#    
#    #D.run_ReverseSelection(Targets,RS_Group_d)
#    #D.asset_pool.rename(columns = DWH_header_REVERSE_rename).to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/ABS9_R1_selected.csv',index=False)
#    D.run_Stat()
#    D.get_oAPCF()         # D.apcf is available
#    ##save_to_excel(D.apcf_original,'apcf_original',wb_name)
#    D.adjust_oAPCF()      # D.apcf_adjusted[scenario_id] is available
#    D.init_oAP_Acc()
#    D.run_WaterFall()    # D.waterfall[scenario_id] is available
#    for scenario_id in scenarios.keys():
#        save_to_excel(D.waterfall[scenario_id],scenario_id,wb_name)
#        save_to_excel(D.wf_BasicInfo[scenario_id],scenario_id,wb_name)
#        save_to_excel(D.wf_CoverRatio[scenario_id],scenario_id,wb_name)
#        save_to_excel(D.wf_NPVs[scenario_id],scenario_id,wb_name)
#    
#    RnR = D.cal_RnR()
#    logger.info('RnR is: %s' % RnR)
#    save_to_excel(pd.DataFrame({'RnR':[RnR]}),'RnR',wb_name)


    RD = RevolvingDeal(ProjectName,dt_param['dt_pool_cut'],asset_pool_name_list,date_revolving_pools_cut,dt_param['dt_effective'],recycle_adjust_factor,scenarios)
    RD.get_rAssetPool() 
    RD.asset_pool['Credit_Score'] = RD.asset_pool['Credit_Score_15'].round(3)
    RD.run_Stat()
    RD.get_oAPCF()         # RD.apcf is available
    RD.get_rAPCF_structure()
    
    RD.adjust_oAPCF()
    RD.init_oAP_Acc()
    
    RD.forcast_Revolving_APCF()
    
    RD.run_WaterFall()    # RD.waterfall[scenario_id] is available
    for scenario_id in scenarios.keys():
        save_to_excel(RD.waterfall[scenario_id],scenario_id,wb_name)
        save_to_excel(RD.wf_BasicInfo[scenario_id],scenario_id,wb_name)
        save_to_excel(RD.wf_CoverRatio[scenario_id],scenario_id,wb_name)
        save_to_excel(RD.wf_NPVs[scenario_id],scenario_id,wb_name)
    
    RnR = RD.cal_RnR()
    logger.info('RnR is: %s' % RnR)
    save_to_excel(pd.DataFrame({'RnR':[RnR]}),'RnR',wb_name)
#    
#    SR = ServiceReport(ProjectName,TrustEffectiveDate,-1)
#    SR.get_ServiceReportAssetsList('DateBookBuilding',
#                                   #['OriginalPool_part1','OriginalPool_part2'], #pre_AllAssetList
#                                   '',
#                                   ['20180719_funding_abs9_asset_756_0','20180719_funding_abs9_asset_756_1'], #AllAssetList
#                                   '',              #'DefaultAssetList',
#                                   '',              #'WaivedAssetListq',
#                                   ''
#                                   #'20180630_funding_abs9_unquali_702'
#                                   ) 
#    
#    SR.add_SeviceRate_From(RD.asset_pool[['No_Contract','SERVICE_FEE_RATE']])
    
    #SR.exclude_or_focus_by_ContractNo('exclude','AssetsSelected_Final')
    #SR.service_report_cal() #(trust_effective_date, report_period)
    
    #SR.check_NextPayDate()
    #SR.check_LoanAging()
    #SR.closed_with_outstandingprincipal()
    #SR.check_ContractTerm()
    #SR.check_Redemption_price()

#    S = Statistics(SR.for_report)
#    S.general_statistics_1()
#    S.loop_Ds_ret_province_profession(Distribution_By_Category,Distribution_By_Bins)
#    S.cal_income2debt_by_ID()

#    OP_BB = SR.check_OutstandingPrincipal()
#    OP_PCD = SR.service_report_AllAssetList_pre[['No_Contract','Amount_Outstanding_yuan']]
#    #OP_PCD = D.asset_pool[['No_Contract','Amount_Outstanding_yuan']]
#    check = OP_PCD.merge(OP_BB,left_on='No_Contract',right_on='No_Contract',how='outer')
#    check_results = check[abs(check['Amount_Outstanding_yuan'] - check['剩余本金_poolcutdate_calc']) > 0.01]
#    check_results.to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName + '/check_OutstandingPrincipal_pre.csv')

#    Age_SR = SR.check_AgePoolCutDate()
#    Age_PCD = RD.asset_pool[['No_Contract','Age_Project_Start']]
#    check = Age_PCD.merge(Age_SR,left_on='No_Contract',right_on='#合同号',how='outer')
#    check_results = check[check['Age_Project_Start'] != check['借款人年龄']]
#    check_results.to_csv(path_root  + '/../CheckTheseProjects/' +'ABS9/' + 'check_AgePoolCutDate.csv')

    end_time = datetime.datetime.now()   
    time_elapsed = end_time - start_time
    logger.info('Time: %0.4f' % time_elapsed.total_seconds())


if __name__ == '__main__':
    main()
