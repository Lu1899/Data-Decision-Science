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
def bootstrap(series, return_rates, number_replicates=10, chunksize=0):
    '''Funktion, die die angegebene Anzahl von Bootsraps für die Markt-Series zurückgibt.
    Hierbei wird berücksichtigt, dass es sich um zeitlich abhängige Arrays handelt. Als Input 
    muss die Zeitreihe sowie eine Series der dazugehörigen Renditen, anhand dessen der Bootstrap 
    erstellt wird, angegeben werden. Des Weiteren kann die Anzahl der Straps (Default=10) und die
    Chunksize (Default=0, also keine Chunks) bestimmt werden.'''
    start = time.time()
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
    momentum_df = pd.DataFrame(series.fillna(methond='bfill'))
    momentum_df['avg_short'] = momentum_df[series.name].rolling(avg_short, win_type=None)
    momentum_df['avg_long'] = momentum_df[series.name].rolling(avg_long, win_type=None)
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
    
    
    
    
    
    
    
    
    
    