#------------------------ Data Decision Science ------------------------#


#----------------------------- Beschreibung ----------------------------#
#Implementierung verschiedener Funktionen, um das Timing der Umsetzung 
#von technischen Anlagestrategien untersuchen zu können. 

#--------------------------------- Code --------------------------------#


#----------- Allgemein -----------#
#Module
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import copy
import random 
import time
from datetime import timedelta

#------------ Funktionen ---------#

#Performance
#% Rendite
def rate_of_return(series, kind='normal'):
    '''Funktion, die die Renditen einer Series berechnet und 
    ebenfalls als Pandas Series zurückgibt. Falls kind='normal' (default) wird die 
    normale, falls kind='log' die logarithmierte Rendite ausgegeben.'''
    return_rates = series.pct_change()
    if kind == 'log':
        return_rates = np.log(1 + return_rates)
    return_rates = return_rates.fillna(0)
    return return_rates

#% Jensen Alpha
def jensen_alpha(series, kind='normal'):
    '''Funktion, anhand dessen das Jensen Alpha einer Series berechnet werden kann.'''
    pass
    print('Diese Funktion ist noch nicht fertig!')

#% Sharpe Ratio
def sharpe_ratio(series, return_rates):
    '''Funktion, die die Sharpe Ratio einer Series zurückgibt.'''
    sharpe_ratio = np.mean(return_rates) / (np.std(return_rates)**(0.5)) 
    return sharpe_ratio

#Bootstraps
#% Erstellen der Bootstraps
def bootstrap(series, return_rates, number_replicates=10, chunksize=0, seed=None):
    '''Funktion, die die angegebene Anzahl von Bootsraps für die Markt-Series zurückgibt.
    Hierbei wird berücksichtigt, dass es sich um zeitlich abhängige Arrays handelt. Als Input 
    muss die Zeitreihe sowie eine Series der dazugehörigen Renditen, anhand dessen der Bootstrap 
    erstellt wird, angegeben werden. Des Weiteren kann die Anzahl der Straps (Default=10), die
    Chunksize (Default=0, also keine Chunks) und die Seed-Zahl bestimmt werden.'''
    start = time.time()
    if seed != None:
        random.seed(seed)
    bootstraps = []
    for iteration in range(number_replicates):
        bootstrap = [series.fillna(method='bfill')[0]]
        chunk = return_rates
        for observation in range(len(series) - 1):
            if chunksize != 0:
                chunk = return_rates[max(0, (observation - chunksize)): 
                                       min((observation + chunksize), 
                                           (len(series) - 1))]
            random_index = random.randint(0, (len(chunk) - 1))
            random_return_rate = chunk[random_index]
            new_observation = bootstrap[-1] * (1 + random_return_rate)
            bootstrap.append(new_observation)
        bootstraps.append(bootstrap)
    print('Der Bootsrap benötigte %.2f Sekunden.' % (time.time() - start))
    return bootstraps

#% Graph der Bootstraps
def plot_bootstraps(series, bootstraps, title, market_label, currency='USD'):
    '''Funktion, die die erstellten Bootstraps visualisiert und den originalen 
    Marktdaten gegenüber stellt. Hierzu muss die origniale Zeitreihe, der 
    Bootstrap-Array, der Titel und das Marktlabel angegeben werden. Weiterhin kann 
    die Währung bestimmt werden (Default='USD')'''
    fig = plt.figure()
    plt.plot(series, label=market_label)
    sns.despine(fig, left=True, bottom=True)
    counter = 1
    series_df = pd.DataFrame(series)
    for item in bootstraps:
        series_df['strap'] = item
        if counter == 1: 
               plt.plot(series_df['strap'], color='grey', label='Bootstraps', alpha=0.4)
               counter += 1
        else:
            plt.plot(series_df['strap'], color='grey', alpha=0.4)
    plt.legend(loc='upper right', edgecolor='white')
    plt.ylabel(currency, fontweight='bold')
    plt.xlabel('Zeit', fontweight='bold')
    plt.title(title, pad=22, fontweight='bold')
    plt.show()
    plt.close()

#Umsetzungen      
#% Signalwechsel
def detect_signal_change(signals):
    '''Funktion, die ausliest, wann das Signal umschlägt.'''
    signal_change = signals.pct_change().fillna(0)
    def convert_signal_change(x):
        if x == 0:
            return x
        else:
            return 1
    signal_change = pd.Series([convert_signal_change(x) for x in signal_change])
    signal_change.index = signals.index
    return signal_change
    
    
    
#% Renditen gemäß Umsetzung    
def umsetzung_gewichtung(signals, umsetzungen):
    '''Funktion, die ausliest, zu welchen Anteilen jeweils gemäß der Umsetzung in die Strategie
    investiert werden soll.'''
    signal_change = detect_signal_change(signals)
    weights = signal_change.copy()
    changes = list(weights[weights == 1].index)
    for index in changes:
        if 0 not in umsetzungen['days']:
            weights[index] = 0
        else:
            weights[index] = umsetzungen['portions'][0]
        for i in range(len(umsetzungen['days'])):
            try:
                day_range = umsetzungen['days'][i + 1] - umsetzungen['days'][i]
            except:
                day_range = 1
            if i == 0:
                day_start = index + timedelta(umsetzungen['days'][i]) 
                while day_start not in weights.index:
                    day_start = day_start + timedelta(1)
            for day in range(day_range):
                if (i == 0) and (day == 0):
                    current_date = day_start
                else:
                    current_date = current_date + timedelta(1)
                while current_date not in weights.index:
                    current_date = current_date + timedelta(1)
                weights[current_date] = umsetzungen['portions'][i]  
    normal_weights = pd.Series(weights[~weights.isin([0.5,0.75,1])].index)
    normal_weights = list(normal_weights[~normal_weights.isin(changes)])
    weights[normal_weights] = (signals ** 2)[normal_weights]
    return weights
    
#Signale 
#% 38/200 Momentum
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
    
#% Clenow Counter Plunger
    #% Average True Range
def average_true_range(high_series, low_series, close_series, true_range=20):
    '''Funktion, die anhand der Low-, High- und Closing-Prices die Avereage True Range berechnet und als 
    Series zurückgibt.'''
    dataframe_atr = pd.DataFrame()
    dataframe_atr['ATR1'] = abs (high_series - low_series)
    dataframe_atr['ATR2'] = abs (high_series - close_series.shift())
    dataframe_atr['ATR3'] = abs (low_series - close_series.shift())
    dataframe_atr['TrueRange'] = dataframe_atr[['ATR1', 'ATR2', 'ATR3']].max(axis=1).fillna(method='bfill')
    dataframe_atr['AverageTrueRange'] = dataframe_atr['TrueRange'].rolling(true_range, win_type=None).mean()
    return dataframe_atr['AverageTrueRange']

    #% Auswählen des jeweigen besten Readings
def pick_reading(row):
    '''Funktion, die anhand eines Trend-Wertes jeweils den Maximal- oder den Minimalwert einer Observation zurückgibt.
    Diese Funktion geht Hand in Hand mit der Funktion "best_reading".'''
    if row['trend'] == 1:
        return row['high']
    elif row['trend'] == -1:
        return row['low']
    else:
        return np.nan

    #% Ermitteln der besten Readings
def best_reading(high_series, low_series, trend, window=20):
    '''Funktion, die anhand der High- und der Low-Prices sowie der Trend-Zeitreihe die jeweils besten Readings 
    ermittelt.'''
    dataframe_br = pd.DataFrame()
    dataframe_br['high'] = high_series.fillna(method='bfill').rolling(window, win_type=None).max()
    dataframe_br['low'] = low_series.fillna(method='bfill').rolling(window, win_type=None).min()
    dataframe_br['trend'] = trend
    dataframe_br['best_reading'] = dataframe_br.apply(pick_reading, axis=1)
    return dataframe_br['best_reading']

    #% Erkennen des Signals
def clewno_counter_plunger_signals(df):
    '''Funktion, ...'''
    
    #------------------------#
    #----- IN PROGRESS! -----#
    #------------------------#
    
    status = np.nan
    stop = np.nan
    target = np.nan
    df['signal'] = np.nan
    for index, row in df.iterrows():
        if ((status != 1) & (row['atr'] >= 3)):
            status = 1
            stop = row['px_last'] - (row['atr'] * 2)
            target = row['px_last'] + (row['atr'] * 4)
            df.loc[index, 'signal'] = 1
        elif status == 1: 
            if row['px_last'] <= stop:
                status = 0
                stop = np.nan
                target = np.nan
                df.loc[index, 'signal'] = 0
            elif row['px_last'] >= target:
                status = 0
                stop = np.nan
                target = np.nan
                df.loc[index, 'signal'] = 0
            elif row['trend'] <= 0:
                status = 0
                stop = np.nan
                target = np.nan
                df.loc[index, 'signal'] = 0
            else:
                df.loc[index, 'signal'] = 1
        else:
            pass
        return df
                
    #% Ermitteln der relevanten Kennzahlen 
def clenow_counter_plunger(high_series, low_series, close_series, ewm_lower=50, ewm_higher=100, window_reading=20):
    '''Funktion,...'''
    
    #------------------------#
    #----- IN PROGRESS! -----#
    #------------------------#
    
    dataframe_ccp = pd.DataFrame(close_series, columns=['px_last'])
    dataframe_ccp['trend'] = dataframe_ccp['px_last'].ewm(span=ewm_lower).mean() - dataframe_ccp['px_last'].ewm(span=ewm_higher).mean()
    def calc_trend(x):
        if x > 0:
            return 1
        elif x < 0: 
            return -1
        else:
            return 0
    dataframe_ccp['trend'] = dataframe_ccp['trend'].apply(calc_trend)
    dataframe_ccp['atr'] = average_true_range(high_series, low_series, close_series)
    dataframe_ccp['best_reading'] = best_reading(high_series, low_series, dataframe_ccp['trend'], window=window_reading)
    dataframe_ccp['atr_difference'] = (dataframe_ccp['px_last'] - dataframe_ccp['best_reading']) / dataframe_ccp['atr']
    return dataframe_ccp
    
    
    
    
    
    