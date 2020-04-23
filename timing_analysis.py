#------------------------ Data Decision Science ------------------------#


#----------------------------- Beschreibung ----------------------------#
#Timimng-Analyse der Umsetzung von verschiedenen technischen 
#Anllagestrategien 

#--------------------------------- Code --------------------------------#


#----------- Allgemein -----------#
#Eigene Module
import main_functions as mf

#Allgemeine Module
import pandas as pd
import os
import numpy as np


os.chdir(os.getcwd() + '\\Data')
df_cl1 = pd.read_csv('CL1_index.csv', header=0, index_col='date', parse_dates=['date'])

series = df_cl1['px_last']


    














