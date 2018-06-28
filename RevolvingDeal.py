# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 21:18:06 2018

@author: Jonah.Chen
"""

import sys
import os
from constant import *
import pandas as pd
import numpy as np
from abs_util.util_general import *
from abs_util.util_cf import *
from abs_util.util_sr import *
from dateutil.relativedelta import relativedelta
import datetime
from Deal import Deal
from AssetPool import AssetPool
from AssetsCashFlow import AssetsCashFlow

low_memory=False

logger = get_logger(__name__)

class RevolvingDeal(Deal):
    
    def __init__(self,name,AP,RAP,date_trust_effective,recycle_adjust_factor):
        super().__init__(name,AP,date_trust_effective,recycle_adjust_factor)
        
        self.RAP = RAP
        self.date_revolving_pools_cut = RAP.date_revolving_pools_cut
        self.acf_structure_revolving = pd.DataFrame()
        self.dates_recycle_list_revolving = [] 
        self.acf_revolving_acf = {}
        self.total_purchase_amount = 0
        
        self.acf_original = pd.DataFrame()
        
    def get_AssetPool(self):
        
        asset_pool_AP = self.AP.get_AssetPool()
        asset_pool_RAP = self.RAP.get_AssetPool()
        self.asset_pool = asset_pool_AP.append(asset_pool_RAP,ignore_index=True)
        

        
        
        
        
        