# -*- coding: utf-8 -*-
'''
Spyder Editor

This is a temporary script file.
'''
import sys
sys.path.append("..")
import os
import pandas as pd
import datetime
from constant import *
from Params import *
from abs_util.util_general import *
from Deal import Deal
from RevolvingDeal import RevolvingDeal
from AssetPool import AssetPool
from RevolvingAssetPool import RevolvingAssetPool
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

    D = Deal(ProjectName,AP,dt_param['dt_effective'],recycle_adjust_factor,scenarios)
    D.get_AssetPool() #D.asset_pool is available
    D.get_APCF() # D.apcf is available
    D.adjust_APCF() #D.apcf_adjusted[scenario_id] is available
    D.run_WaterFall() #D.waterfall[scenario_id] is available
    for scenario_id in scenarios.keys():
        save_to_excel(D.waterfall[scenario_id],scenario_id,wb_name)
        save_to_excel(D.wf_BasicInfo[scenario_id],scenario_id,wb_name)
        save_to_excel(D.wf_CoverRatio[scenario_id],scenario_id,wb_name)
        save_to_excel(D.wf_NPVs[scenario_id],scenario_id,wb_name)
    
    RnR = D.cal_RnR()
    logger.info('RnR is: %s' % RnR)
    save_to_excel(pd.DataFrame({'RnR':[RnR]}),'RnR',wb_name)


    #RAP = RevolvingAssetPool([date_revolving_pools_cut,['2ndRevolvingPool']])
    #RD = RevolvingDeal(ProjectName,AP,RAP,dt_param['dt_effective'],recycle_adjust_factor)
    #RD.get_AssetPool() 
    #RAP.add_Columns_From(['2ndRevolvingPool_CreditScore'])
    #RAP.asset_pool = RD.asset_pool.rename(columns = DWH_header_REVERSE_rename) 
    #RAP.asset_pool.to_csv('2ndRevolvingPool.csv')
    #RAP.exclude_or_focus_by_ContractNo('Focus','FinalRevolvingAssets')
    #assets = RAP.exclude_or_focus_by_criteria('Focus','Dt_Maturity',datetime.date(2018,4,30))
    #RAP.asset_pool = RAP.asset_pool[RD.asset_pool['Interest_Rate'] > 0]
#    S = Statistics(RD.name,RD.asset_pool)
#    S.general_statistics_1()
#    S.loop_Ds_ret_province_profession(Distribution_By_Category,Distribution_By_Bins)
#    S.cal_income2debt_by_ID()
    
#    print(acf_original)
#    AmtOverdue = ACF.calc_OverdueRecycle(92654196.57,2)
#    print(AmtOverdue)
#    acf_structure_revolving = ACF.rearrange_ACF_Structure()
#    RAP.forcast_Revolving_ACF(acf_original,acf_structure_revolving,6)

    
#    RS = ReverseSelection(RAP.asset_pool[['No_Contract','Interest_Rate','Amount_Outstanding_yuan','LoanRemainTerm','LoanTerm','Credit_Score']],
#                          Targets)
#    RS.cal_OriginalStat()
#    RS_results = RS.iLP_Solver_all()
##    
#    assets = RAP.asset_pool[RAP.asset_pool['ReverseSelection_Flag'].isin(RS_results['ReverseSelection_Flag'])]
#    
#    S = Statistics(RAP.name,assets)
#    S.general_statistics_1()
#    S.loop_Ds_ret_province_profession(Distribution_By_Category,Distribution_By_Bins)
#    S.cal_income2debt_by_ID()
#    
#    assets = assets.rename(columns = DWH_header_REVERSE_rename) 
#    assets = assets.drop('ReverseSelection_Flag',axis=1)
#    assets.to_csv(path_root  + '/../CheckTheseProjects/ABS9_R2/' +'assets_selected.csv')
    
#    SR = ServiceReport(RD.name,TrustEffectiveDate,1)
#    SR.get_ServiceReportAssetsList('SpecialReport1',
#                                   ['20180621_funding_abs9_asset_679_0','20180621_funding_abs9_asset_679_1'],
#                                   #['AllAssetList_test'],
#                                   '',              #'DefaultAssetList',
#                                   '',              #'WaivedAssetListq',
#                                   ''
#                                   #'20180613_funding_abs9_unquali_668'
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

#    S = Statistics(RD.name,SR.for_report)
#    S.general_statistics_1()
#    S.loop_Ds_ret_province_profession(Distribution_By_Category,Distribution_By_Bins)
#    S.cal_income2debt_by_ID()


#    OP_BB = SR.check_OutstandingPrincipal()
#    OP_PCD = RD.asset_pool[['No_Contract','Amount_Outstanding_yuan']]
#    check = OP_PCD.merge(OP_BB,left_on='No_Contract',right_on='#合同号',how='outer')
#    check_results = check[check['Amount_Outstanding_yuan'] != check['剩余本金_poolcutdate_calc']]
#    check_results.to_csv(path_root  + '/../CheckTheseProjects/' +'ABS9_DWH/' + 'check_OutstandingPrincipal.csv')

#    Age_SR = SR.check_AgePoolCutDate()
#    Age_PCD = RD.asset_pool[['No_Contract','Age_Project_Start']]
#    check = Age_PCD.merge(Age_SR,left_on='No_Contract',right_on='#合同号',how='outer')
#    check_results = check[check['Age_Project_Start'] != check['借款人年龄']]
#    check_results.to_csv(path_root  + '/../CheckTheseProjects/' +'ABS9_DWH/' + 'check_AgePoolCutDate.csv')

    end_time = datetime.datetime.now()   
    time_elapsed = end_time - start_time
    logger.info('Time: %0.4f' % time_elapsed.total_seconds())


if __name__ == '__main__':
    main()
