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
#
#    if os.path.isfile(wb_name):
#      os.remove(wb_name)
#
    RD = RevolvingDeal(ProjectName,dt_param['dt_pool_cut'],dt_param['dt_trust_effective'],Flag_RevolvingDeal,date_revolving_pools_cut,scenarios)
#    
    RD.get_AssetPool(['ABS13_InitialPool_20190311']) #ABS11R3_selected_to_HCCFC_20190306
    #RD.get_AssetPool(['ABS11_r3201903011641050','ABS11_r3201903011641051','ABS11_r3201903011641052'])
    #RD.get_AssetPool(['all_exclude_ABS11R3_selected_without_cs','all_exclude_ABS10R5_selected_with_cs'])
    #RD.get_AssetPool(['ABS13_InitialPool201903012000130','ABS13_InitialPool201903012000131','ABS13_InitialPool201903012000132'])
    #RD.get_AssetPool(['ABS11_r3201903041407300','ABS13_InitialPool201903012000130','ABS13_InitialPool201903012000131','ABS13_InitialPool201903012000132'])
    #RD.get_AssetPool(['abs13_contracts_list_0(add score)','abs13_contracts_list_1(add score)']) # ABS11_r3201903051104050 ABS11R3_selected_to_Trust_20190304_1.2times ABS11R3_selected_to_Trust_20190304_1time(fyr)
#
    #RD.select_by_ContractNO('focus',['ABS13_InitialPool_20190311']) 
    
    #RD.select_by_ContractNO('exclude',['ABS11R3_selected_to_HCCFC_20190306'])     
    
#    RD.select_by_ContractNO('exclude',['DWH-ABSSystem']) 
#    RD.select_by_ContractNO('exclude',['ABS10_R5_selected_20190306_toHCCFC'])  #'ABS13_InitialPool_selected_20190304_IR_21','ABS13_InitialPool_selected_20190304_RT_298'
#    RD.select_by_ContractNO('exclude',['ABS11R3_selected_to_Trust_20190301']) 
#    RD.asset_pool = RD.asset_pool[~RD.asset_pool['No_Contract'].isin(['#4030632760001','#4019566684001','#4042877223001'])]
    
    #RD.select_by_ContractNO('focus',['ABS13_InitialPool201903012000130','ABS13_InitialPool201903012000131','ABS13_InitialPool201903012000132']) #['ABS11_r2201902011521110','ABS11_r2201902011521111','ABS11_r2201902011521112']
    #RD.select_by_ContractNO('exclude',['abs13_contracts_list_0','abs13_contracts_list_1']) 
    #RD.select_by_ContractNO('focus',['ABS11R3_selected_to_Trust_20190304_1time(fyr)_Jonah'])  
##
#    RD.add_Columns([
#                  [['ProfessionTypeValueTransform'],'Profession','Profession_HC'],
#                  [['UsageTypeValueTransform'],'Usage','Usage_HC'],
#                 #[['ABS13_InitialPool201903012000130','ABS13_InitialPool201903012000131','ABS13_InitialPool201903012000132'],'No_Contract','#合同号']
#                  ])
#        
    RD.asset_pool['Credit_Score'] = RD.asset_pool['Credit_Score_15'].round(3)
#    RD.asset_pool = RD.asset_pool[RD.asset_pool['Credit_Score']>0]
#    RD.asset_pool = RD.asset_pool[(RD.asset_pool['Interest_Rate'] < 0.21)|((RD.asset_pool['Interest_Rate'] == 0.21)&(RD.asset_pool['LoanRemainTerm'] <= 360))]

    #RD.asset_pool = RD.asset_pool[abs(RD.asset_pool['Amount_Outstanding_yuan'] - RD.asset_pool['截至封包日剩余本金(元)']) > 0]

######################### V1 WA_IR_21 #################################
#    RD.asset_pool = RD.asset_pool[RD.asset_pool['Interest_Rate'] == 0.21]
#    RD.asset_pool = RD.asset_pool[RD.asset_pool['Overdue_Times'] <= 2]
#    RD.asset_pool = RD.asset_pool[RD.asset_pool['LoanTerm'] <= 743]
#    RD.asset_pool = RD.asset_pool[RD.asset_pool['LoanRemainTerm'] <= 624]
#

##################### V2 WA_RemainTerm ######################
#    RD.asset_pool = RD.asset_pool[RD.asset_pool['Interest_Rate'] > 0]
#    RD.asset_pool = RD.asset_pool[~((RD.asset_pool['Interest_Rate'] == 0.16)&((RD.asset_pool['LoanAge'] > 25)|(RD.asset_pool['LoanAge'] <= 10)))]
#    RD.asset_pool = RD.asset_pool[RD.asset_pool['Overdue_Times'] <= 2]
#    RD.asset_pool = RD.asset_pool[RD.asset_pool['LoanRemainTerm'] <= 570]
#    RD.asset_pool = RD.asset_pool[~RD.asset_pool['Usage'].isin(['其余种类','其它'])]
#    
#    RD.asset_pool = RD.asset_pool[RD.asset_pool['LoanAge'] <= 720]
#    RD.asset_pool = RD.asset_pool[~RD.asset_pool['Profession'].isin(['其他-不便分类','其它'])]
#    RD.asset_pool = RD.asset_pool[RD.asset_pool['LoanTerm'] <= 720]
#    RD.asset_pool = RD.asset_pool[RD.asset_pool['LoanTerm'] > 90]

##################################################

###    #RD.asset_pool = RD.asset_pool[['No_Contract','Days_Overdue_Current','当期逾期天数']]
#    #print(RD.asset_pool.rename(columns = Header_Rename_REVERSE)[:5])
    #RD.asset_pool[pd.to_datetime(RD.asset_pool['first_due_date_after_pool_cut']) < pd.Timestamp(datetime.date(2019,3,1))].rename(columns = Header_Rename_REVERSE).to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/Check_first_due_date_after_pool_cut.csv',index=False,encoding="utf_8_sig")    
###    
    #RS_results = RD.run_ReverseSelection(Targets,RS_Group_d)
    #RS_results.to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/AssetsSelected_Final.csv',index=False)
    #RD.asset_pool.rename(columns = Header_Rename_REVERSE).to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/to_exclude_fromABS11r3.csv',index=False,encoding="utf_8_sig")
    #RD.asset_pool[RD.asset_pool['LoanRemainTerm'] < 280].rename(columns = Header_Rename_REVERSE).to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/to_exclude_in_ABSSystem_2.csv',index=False,encoding="utf_8_sig")
    
#    RD.asset_pool[RD.asset_pool['No_Contract'] <= '#3506414827004'].rename(columns = Header_Rename_REVERSE).to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/Missing Assets.csv',index=False,encoding="utf_8_sig")
#    RD.asset_pool[RD.asset_pool['LoanRemainTerm'] <= 240].rename(columns = Header_Rename_REVERSE).to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/Exclude part 1.csv',index=False,encoding="utf_8_sig")
#    RD.asset_pool[RD.asset_pool['LoanRemainTerm'] > 240].rename(columns = Header_Rename_REVERSE).to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/Exclude part 2.csv',index=False,encoding="utf_8_sig")

    RD.run_Stat(Distribution_By_Category,Distribution_By_Bins,'CN')
#        
#    RD.asset_pool['first_due_date_after_pool_cut'] = RD.asset_pool['first_due_date_after_pool_cut'].where(RD.asset_pool['first_due_date_after_pool_cut'] != '3000/01/01','2019/01/01')
#    RD.asset_pool = RD.asset_pool[RD.asset_pool['Amount_Outstanding_yuan']>0]
#    
    RD.init_oAP_Acc()
    
    for asset_status in all_asset_status:
        if len(RD.asset_pool[(RD.asset_pool['贷款状态'] == asset_status)]) == 0:
            logger.info('No Assets to calc for {0}'.format(asset_status))
            continue
        else:
            logger.info('Collecting CF for asset_status {0}'.format(asset_status))   
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
#                ####logger.info('CDR_calc_O...for {0}...'.format(scenario_id))
#                ####RD.CDR_calc_O(scenario_id,asset_status)
#                ####save_to_excel(pd.DataFrame.from_dict(RD.CDR_O),'RnR&CDR',wb_name)
    
    for scenario_id in scenarios.keys():
        
        RD.oAP_Acc_DeSimulation(scenario_id,simulation_times)
        save_to_excel(RD.df_AP_PAcc_actual_O_DeSimu,'De-Sim_'+scenario_id,wb_name)
        
        logger.info('CDR_calc_O...for {0}...'.format(scenario_id))
        RD.CDR_calc_O(scenario_id)
    save_to_excel(pd.DataFrame.from_dict(RD.CDR_O),'RnR&CDR',wb_name)
##            
#########
    RD.get_rAPCF_structure()
    RD.forcast_Revolving_APCF()
#   
    RD.run_WaterFall()    # RD.waterfall[scenario_id] is available
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
    end_time = datetime.datetime.now()   
    time_elapsed = end_time - start_time
    logger.info('Time: %0.4f' % time_elapsed.total_seconds())


if __name__ == '__main__':
    main()
