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

    #asset_pool_name_list = ['OriginalPool_part1','OriginalPool_part2']
    ##asset_pool_name_list = ['ABS9_R1_selected']
#    asset_pool_name_list = ['ABSround3_initial201808031440380'] #ABS9_R1_selected_20180801 abs9_rvg1_contract_list
#    D = Deal(ProjectName,dt_param['dt_pool_cut'],asset_pool_name_list,dt_param['dt_effective'],recycle_adjust_factor,scenarios)
#    D.get_AssetPool()    # D.asset_pool is available
#
#    #D.select_by_ContractNO('focus','ABS9_R1_selected')
##    
#    #D.asset_pool = D.asset_pool[D.asset_pool['Credit_Score_15'] > 0]
###    D.asset_pool = D.asset_pool[(pd.to_datetime(D.asset_pool['Dt_Start']).dt.date < datetime.date(2018,7,1)) &
###                                (D.asset_pool['Credit_Score_15'] == -1)
###                                ]
###    D.asset_pool = D.asset_pool[pd.to_datetime(D.asset_pool['Dt_Maturity']).dt.date >= datetime.datetime.now().date()]
##    
##    D.add_Columns([
##                  #[['AssetsFromCFIT'],'No_Contract','#合同号'],
##                  #[['ProfessionTypeValueTransform'],'Profession','Profession_HC'],
##                  [['abs10_contract_list_0','abs10_contract_list_1'],'No_Contract','#合同号']
##                  ]
##                  )
## 
#    
#    #D.asset_pool[D.asset_pool['LoanRemainTerm'] <= 230].rename(columns = DWH_header_REVERSE_rename).to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/udpate_cs_ABS10_1.csv',index=False)
#    #D.asset_pool[D.asset_pool['LoanRemainTerm'] > 230].rename(columns = DWH_header_REVERSE_rename).to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/update_cs_ABS10_2.csv',index=False)    
##    
#    D.asset_pool['Credit_Score'] = D.asset_pool['Credit_Score_15'].round(3)
##
#    ##D.run_ReverseSelection(Targets,RS_Group_d)
#    ##D.asset_pool.rename(columns = DWH_header_REVERSE_rename).to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/ABS9_R1_selected_final_20180801.csv',index=False)
#    
#    #D.asset_pool['Amount_Outstanding_yuan'] = D.asset_pool['Amount_Outstanding_yuan'].where(D.asset_pool['Days_Overdue_Current']<=180,0)
#    D.run_Stat()
#    #D.asset_pool['SERVICE_FEE_RATE'] = 0
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
    SR = ServiceReport(ProjectName,ADate,1)
    SR.get_ServiceReportAssetsList('FirstReportDate',
                                   #['OriginalPool_part1','OriginalPool_part2'], #pre_AllAssetList
                                   '',
                                   ['20180801_funding_abs9_asset_786_0','20180801_funding_abs9_asset_786_1'], #AllAssetList
                                   '',              #'DefaultAssetList',
                                   '',              #'WaivedAssetListq',
                                   ''
                                   #'20180801_funding_abs9_unquali_784' #20180801_funding_abs9_unquali_784 
                                   ) 
    
#    SR.add_SeviceRate_From(RD.asset_pool[['No_Contract','SERVICE_FEE_RATE']])
    
    SR.select_by_ContractNO('FirstReportDate','focus','AssetsSelected_Final')
    #SR.service_report_cal() #(trust_effective_date, report_period)
    
    #SR.check_NextPayDate()
    #SR.check_LoanAging()
    #SR.closed_with_outstandingprincipal()
    #SR.check_ContractTerm()
    #SR.check_Redemption_price()

#    SR.for_report['Term_Remain'] = SR.for_report['LoanRemainTerm']/30
#    SR.for_report['Term_Remain'] = (SR.for_report['Term_Remain'].astype(int)).where(SR.for_report['Term_Remain'] > 0,0)

#    SR.for_report['Amount_Outstanding_yuan'] = SR.for_report['Amount_Outstanding_yuan'].where(SR.for_report['Days_Overdue_Current']<=180,0)
#    S = Statistics(SR.for_report)
#    S.general_statistics_1()
#    S.loop_Ds_ret_province_profession(Distribution_By_Category,Distribution_By_Bins)
    ##S.cal_income2debt_by_ID()

#    OP_BB = SR.check_OutstandingPrincipal()
#    OP_PCD = SR.service_report_AllAssetList_pre[['No_Contract','Amount_Outstanding_yuan']]
#    #OP_PCD = D.asset_pool[['No_Contract','Amount_Outstanding_yuan']]
#    check = OP_PCD.merge(OP_BB,left_on='No_Contract',right_on='No_Contract',how='outer')
#    check_results = check[abs(check['Amount_Outstanding_yuan'] - check['剩余本金_poolcutdate_calc']) > 0.01]
#    check_results.to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName + '/check_OutstandingPrincipal_pre.csv')
#
#    Age_SR = SR.check_AgePoolCutDate()
#    Age_PCD = SR.service_report_AllAssetList_pre[['No_Contract','Age_Project_Start']]
#    check = Age_PCD.merge(Age_SR,left_on='No_Contract',right_on='No_Contract',how='left')
#    check_results = check[check['Age_Project_Start'] != check['Age_Project_Start_sr']]
#    check_results.to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName + '/check_AgePoolCutDate.csv')

    end_time = datetime.datetime.now()   
    time_elapsed = end_time - start_time
    logger.info('Time: %0.4f' % time_elapsed.total_seconds())


if __name__ == '__main__':
    main()
