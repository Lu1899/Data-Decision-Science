#------------------------ Data Decision Science ------------------------#


#----------------------------- Beschreibung ----------------------------#
#Erste Aufbereitung der Daten:
    #Zusammenführen der Daten
    #Deskriptive Statistiken
    #Erste Visualisierungen

#--------------------------------- Code --------------------------------#


#----------- Allgemein -----------#
#Module
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import copy

#Variablen
data_wd = r'C:\Users\lukas\OneDrive\Dokumente\Bildung und Studium\Universität Augsburg\Semester\SS 20\Data Decision Science\Daten\all_data'
export_wd = r'C:\Users\lukas\OneDrive\Dokumente\Bildung und Studium\Universität Augsburg\Semester\SS 20\Data Decision Science\Daten\concated_data'

#Ändern des wd
os.chdir(data_wd)


#----------- Marktdaten ----------#
#Einlesen der Marktdaten
df_market = pd.read_csv('MarketData.csv', sep=',', header=0, parse_dates=['date'], dayfirst=True)

#Einlesen des AssetInfos
df_assetinfo = pd.read_csv('AssetInfo.csv', sep=',', header=0)
dict_assetnames = {}
for index, row in df_assetinfo.iterrows():
    if row['asset_label'] in list(df_market['asset_label'].value_counts().index):
        dict_assetnames[row['asset_label']] = row['name']
        
#Strukturierung der Marktdaten anhand der Assets
dict_markets = {}
for asset in dict_assetnames.keys():
    data_asset = { 'date': df_market[(df_market['asset_label']==asset)&(df_market['bloomberg_field']=='PX_OPEN')]['date'].values,
                  'px_open': df_market[(df_market['asset_label']==asset)&(df_market['bloomberg_field']=='PX_OPEN')]['price'].values,
                  'px_high': df_market[(df_market['asset_label']==asset)&(df_market['bloomberg_field']=='PX_HIGH')]['price'].values,
                  'px_low': df_market[(df_market['asset_label']==asset)&(df_market['bloomberg_field']=='PX_LOW')]['price'].values,
                  'px_last': df_market[(df_market['asset_label']==asset)&(df_market['bloomberg_field']=='PX_LAST')]['price'].values,
                  'currency': df_market[(df_market['asset_label']==asset)&(df_market['bloomberg_field']=='PX_LAST')]['base_currency'].values}
    df_asset = pd.DataFrame(data=data_asset)
    df_asset = df_asset.set_index('date')
    dict_markets[asset] = df_asset

#Deskriptive Statistiken
for asset in dict_markets.keys():
    print('\n----------------------------------------------------------')
    print('Deskriptive Statistiken - %s - %s\n' % (dict_assetnames[asset], asset))
    print(dict_markets[asset].describe())
    print('\n----------------------------------------------------------')


#------------ Signale ------------#
#Crossover
df_crossover = pd.read_csv('crossover_StrategySignals.csv', header=0, sep=',')
for asset in dict_markets.keys():
    dict_markets[asset]['crossover_signal'] = df_crossover[asset].values
    
#CounterTrend
df_countertrend = pd.read_csv('countertrend_StrategySignals.csv', header=0, sep=',')
for asset in dict_markets.keys():
    dict_markets[asset]['countertrend_signal'] = df_countertrend[asset].values  

#Ändern des wd
os.chdir(export_wd)
for asset in dict_markets.keys():
    dict_markets[asset].to_csv('%s.csv' % asset, header=True, index='date')


#-------- Visualisierung ---------#
#Scatterplot anhand der Strategien
def scatter_strategies(figure, axis, strategy, index, dict_markets, map_assetnames):
    '''Funktion, die einen Scatter-Plot anhand der täglichen Closing-Zahlen und der angegebenen Trading-Strategie erstellt''' 
    data = copy.deepcopy(dict_markets[index].dropna())
    data['Signal'] = pd.Categorical(data[strategy].replace(1, 'Long').replace(0, 'Kein Signal').replace(-1, 'Short'))
    sns.despine(figure, left=True, bottom=True)
    axis = sns.scatterplot(x=data.index, y='px_last', hue='Signal', palette='viridis', data=data)
    axis = plt.legend(loc='upper right', edgecolor='white')
    axis = plt.ylabel('PX_Last', fontweight='bold')
    axis = plt.xlabel('Zeit', fontweight='bold')
    if strategy == 'crossover_signal':
        strategy_name = 'Crossover'
    elif strategy == 'countertrend_signal':
        strategy_name = 'Countertrend'
    axis = plt.title('%s - %s' %(dict_assetnames[index], strategy_name), pad=20, fontweight='bold')
    return axis

#Countertrend
fig = plt.figure(figsize=(60,20))
ax1 = plt.subplot(2,4,1)
ax1= scatter_strategies(fig, ax1, 'countertrend_signal', 'CL1_index', dict_markets, dict_assetnames)
ax2 = plt.subplot(2,4,2)
ax2= scatter_strategies(fig, ax2, 'countertrend_signal', 'EC1_index', dict_markets, dict_assetnames)
ax3 = plt.subplot(2,4,3)
ax3= scatter_strategies(fig, ax3, 'countertrend_signal', 'ES1_index', dict_markets, dict_assetnames)
ax4 = plt.subplot(2,4,4)
ax4= scatter_strategies(fig, ax4, 'countertrend_signal', 'GC1_index', dict_markets, dict_assetnames)
ax5 = plt.subplot(2,4,5)
ax5= scatter_strategies(fig, ax5, 'countertrend_signal', 'JY1_index', dict_markets, dict_assetnames)
ax6 = plt.subplot(2,4,6)
ax6= scatter_strategies(fig, ax6, 'countertrend_signal', 'NQ1_index', dict_markets, dict_assetnames)
ax7 = plt.subplot(2,4,7)
ax7= scatter_strategies(fig, ax7, 'countertrend_signal', 'RX1_index', dict_markets, dict_assetnames)
ax8 = plt.subplot(2,4,8)
ax8= scatter_strategies(fig, ax8, 'countertrend_signal', 'US1_index', dict_markets, dict_assetnames)
plt.show()
plt.close()

#Crossover
fig = plt.figure(figsize=(60,20))
ax1 = plt.subplot(2,4,1)
ax1= scatter_strategies(fig, ax1, 'crossover_signal', 'CL1_index', dict_markets, dict_assetnames)
ax2 = plt.subplot(2,4,2)
ax2= scatter_strategies(fig, ax2, 'crossover_signal', 'EC1_index', dict_markets, dict_assetnames)
ax3 = plt.subplot(2,4,3)
ax3= scatter_strategies(fig, ax3, 'crossover_signal', 'ES1_index', dict_markets, dict_assetnames)
ax4 = plt.subplot(2,4,4)
ax4= scatter_strategies(fig, ax4, 'crossover_signal', 'GC1_index', dict_markets, dict_assetnames)
ax5 = plt.subplot(2,4,5)
ax5= scatter_strategies(fig, ax5, 'crossover_signal', 'JY1_index', dict_markets, dict_assetnames)
ax6 = plt.subplot(2,4,6)
ax6= scatter_strategies(fig, ax6, 'crossover_signal', 'NQ1_index', dict_markets, dict_assetnames)
ax7 = plt.subplot(2,4,7)
ax7= scatter_strategies(fig, ax7, 'crossover_signal', 'RX1_index', dict_markets, dict_assetnames)
ax8 = plt.subplot(2,4,8)
ax8= scatter_strategies(fig, ax8, 'crossover_signal', 'US1_index', dict_markets, dict_assetnames)
plt.show()
plt.close()









