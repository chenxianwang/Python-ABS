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
from Statistics import Statistics
from ReverseSelection import ReverseSelection
from AssetsCashFlow import AssetsCashFlow
from ServiceReport import ServiceReport
from RnR_calculator import *
from Waterfall import *


logger = get_logger(__name__)

def main(): 
    
    start_time = datetime.datetime.now()

    RD = RevolvingDeal(ProjectName,datetime.date(2018,4,16),TrustEffectiveDate,supplement_assets_params,date_revolving_pools_cut)
    RD.Preparation()
##    
    #RD.get_OriginalAssetPool(['part_1','part_2']) 
    #RD.get_RevolvingAssetPool(['2ndRevolvingPool'])
    #print("RD['SERVICE_FEE_RATE'].sum(): ",RD.asset_pool['SERVICE_FEE_RATE'].sum())
    #RD.get_AssetPool(['assets_selected20180608']) 
    #RD.add_Columns_From(['check_p1','check_p2','check_p3'])
    #RD.exclude_or_focus_by_ContractNo('Focus','FinalRevolvingAssets')
    #assets = RD.exclude_or_focus_by_criteria('Focus','Dt_Maturity',datetime.date(2018,4,30))
    #RD.asset_pool = RD.asset_pool[RD.asset_pool['Interest_Rate'] > 0]
#    S = Statistics(RD.name,RD.asset_pool)
#    S.general_statistics_1()
#    S.loop_Ds_ret_province_profession(Distribution_By_Category,Distribution_By_Bins)
#    S.cal_income2debt_by_ID()
    
#    ACF = AssetsCashFlow(RD.name,
#                         RD.asset_pool[['No_Contract','Interest_Rate','SERVICE_FEE_RATE','Amount_Outstanding_yuan','first_due_date_after_pool_cut','Term_Remain',]],
#                         RD.date_pool_cut
#                         )
#
#    acf_original = ACF.calc_OriginalPool_ACF(0)  #BackMonth  
#    cf_original = acf_original

    cf_original_path = path_root  + '/../CheckTheseProjects/' + ProjectName+'/' + 'ACF.csv'
    try:
            cf_original = pd.read_csv(cf_original_path,encoding = 'utf-8') 
    except:
            cf_original = pd.read_csv(cf_original_path,encoding = 'gbk') 
#    
    RR_c = RnR_calculator(cf_original,dt_param,fees,scenarios,Bonds)  #fees;fee_rate_param
    RnR = RR_c.calculator()
    logger.info('RnR is: %s' % RnR)
    save_to_excel(pd.DataFrame({'RnR':[RnR]}),'RnR',wb_name)
    
#    print(acf_original)
#    AmtOverdue = ACF.calc_OverdueRecycle(92654196.57,2)
#    print(AmtOverdue)
#    acf_structure_revolving = ACF.calc_Rearrange_ACF_Structure()
#    RD.forcast_Revolving_ACF(acf_original,acf_structure_revolving,6)

    
#    RS = ReverseSelection(RD.asset_pool[['No_Contract','Interest_Rate','Amount_Outstanding_yuan','LoanRemainTerm','LoanTerm'
#                                         ,'Credit_Score'
#                                         ]],
#                          Targets)
#    RS.cal_OriginalStat()
#    RS_results = RS.iLP_Solver_all()
##    
#    assets = RD.asset_pool[RD.asset_pool['ReverseSelection_Flag'].isin(RS_results['ReverseSelection_Flag'])]
#    S = Statistics(RD.name,assets)
#    S.general_statistics_1()
#    S.loop_Ds_ret_province_profession(Distribution_By_Category,Distribution_By_Bins)
#    S.cal_income2debt_by_ID()
##    
#    assets = assets.rename(columns = DWH_header_REVERSE_rename) 
#    assets = assets.drop('ReverseSelection_Flag',axis=1)
#    assets.to_csv(path_root  + '/../CheckTheseProjects/' +'ABS9_R1/' +'assets_selected.csv')
    
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