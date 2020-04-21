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


os.chdir(os.getcwd() + '\\Data')
df_cl1 = pd.read_csv('CL1_index.csv', header=0, index_col='date', parse_dates=['date'])

series = df_cl1['px_last']
return_rates = mf.rate_of_return(series)

bootstraps = mf.bootstrap(series, return_rates, chunksize=180)

for bootstrap in bootstraps:
    bootstrap = pd.Series(bootstrap)
    print(mf.sharpe_ratio(bootstrap, mf.rate_of_return(bootstrap)))
    
mf.plot_bootstraps(series, bootstraps, 'Crude Oil Future', 'CL1')

print(mf.sharpe_ratio(series, return_rates))

signale = df_cl1['crossover_signal']

signal_change = mf.detect_signal_change(signale)

umsetzungen = {'days': [1, 5],
               'portions': [0.5, 1]}

from datetime import timedelta

gewichtungen = mf.umsetzung_gewichtung(signale, umsetzungen)
    




