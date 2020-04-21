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
import np


os.chdir(os.getcwd() + '\\Data')
df_cl1 = pd.read_csv('CL1_index.csv', header=0, index_col='date', parse_dates=['date'])

series = df_cl1['px_last']
return_rates = mf.rate_of_return(series)

def crossover_signal(series, avg_short=38, avg_long=200):
    '''Funktion, die das Momentum-Modell einer Series anhand einer Crossover-Strategie zurück gibt. Hierbei
    kann die untere  (Default=38) und die obere Durchschnittsgrenze (Default=200) bei Bedarf variiert werden.'''
    momentum_df = pd.DataFrame(series.fillna(method='bfill'))
    momentum_df['avg_short'] = momentum_df[series.name].rolling(avg_short, win_type=None).mean()
    momentum_df['avg_long'] = momentum_df[series.name].rolling(avg_long, win_type=None).mean()
    momentum_df['difference'] = momentum_df['avg_short'] - momentum_df['avg_long']
    def momentum(x):
        if x > 0:
            return 1
        elif x == 0:
            return 0
        elif x < 0:
            return -1
        else:
            return np.nan
    momentum_df['signal'] = momentum_df['difference'].apply(momentum)
    return momentum_df['signal']
    


signal_momentum = crossover_signal(series)

