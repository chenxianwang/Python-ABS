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
from AssetPool import AssetPool
from Statistics import Statistics
from ReverseSelection import ReverseSelection
from AssetsCashFlow import AssetsCashFlow
from ServiceReport import ServiceReport

logger = get_logger(__name__)

def main(): 
    
    start_time = datetime.datetime.now()

    if os.path.isfile(wb_name):
      os.remove(wb_name)

    AP = AssetPool([dt_param['dt_pool_cut'],['OriginalPool_part1','OriginalPool_part2'],['']])
    #AP = AssetPool([dt_param['dt_pool_cut'],['revolving pool r1 asset list_0','revolving pool r1 asset list_1'],['']])
    #AP = AssetPool([dt_param['dt_pool_cut'],['revolving pool r1 asset list_0','revolving pool r1 asset list_1'],['CS_free_contracts_0','CS_free_contracts_1']])
    #AP = AssetPool([dt_param['dt_pool_cut'],['ABS10_1','ABS10_2'],['']])
    #D = Deal(ProjectName,AP,dt_param['dt_effective'],recycle_adjust_factor,scenarios)
    #D.get_AssetPool()    # D.asset_pool is available
    #D.add_Columns()
    #D.asset_pool['Credit_Score'] = D.asset_pool['Credit_Score_15'].round(3)
    #D.run_ReverseSelection(Targets,RS_Group_d)
    #D.asset_pool.rename(columns = DWH_header_REVERSE_rename).to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/ABS9_R1_Selected_add_CS.csv',index=False)
#    D.run_Stat()
#    D.get_APCF()         # D.apcf is available
#    D.get_rearranged_APCF_structure()
#    D.adjust_APCF()      # D.apcf_adjusted[scenario_id] is available
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


    RD = RevolvingDeal(ProjectName,AP,date_revolving_pools_cut,dt_param['dt_effective'],recycle_adjust_factor,scenarios)
    RD.get_rAssetPool() 
    #RD.asset_pool['Credit_Score'] = RD.asset_pool['Credit_Score_15'].round(3)
    #RD.run_Stat()
    RD.get_APCF()         # RD.apcf is available
    RD.get_revolving_APCF_structure()
    RD.forcast_Revolving_APCF()
    RD.adjust_rAPCF()      # RD.apcf_adjusted[scenario_id] is available
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
#    SR = ServiceReport(ProjectName,TrustEffectiveDate,1)
#    SR.get_ServiceReportAssetsList('SpecialReport1',
#                                   ['20180701_funding_abs9_asset_706_0','20180701_funding_abs9_asset_706_1'],
#                                   #['AllAssetList_test'],
#                                   '',              #'DefaultAssetList',
#                                   '',              #'WaivedAssetListq',
#                                   ''
#                                   #'20180630_funding_abs9_unquali_698'
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

#    S = Statistics(ProjectName,SR.for_report)
#    S.general_statistics_1()
#    S.loop_Ds_ret_province_profession(Distribution_By_Category,Distribution_By_Bins)
#    S.cal_income2debt_by_ID()


#    OP_BB = SR.check_OutstandingPrincipal()
#    OP_PCD = RD.asset_pool[['No_Contract','Amount_Outstanding_yuan']]
#    check = OP_PCD.merge(OP_BB,left_on='No_Contract',right_on='#合同号',how='outer')
#    check_results = check[check['Amount_Outstanding_yuan'] != check['剩余本金_poolcutdate_calc']]
#    check_results.to_csv(path_root  + '/../CheckTheseProjects/' +'ABS9/' + 'check_OutstandingPrincipal.csv')

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
