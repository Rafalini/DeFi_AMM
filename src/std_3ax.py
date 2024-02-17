from re import A
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import glob, os, random
from scipy.interpolate import make_interp_spline

axis_number_font_size = 20
subplot_font_size = 20
plot_font_size = 25

directory_path = './output/'
oracleLog = 'oracle_log.csv'
transactionLog = 'amm_trans_log.csv'
ammLog = 'amm_log.csv'

def getData():
    os.chdir(directory_path)
    csv_files = glob.glob('log/*.csv')
    dfs = []

    for file in csv_files:
        df = pd.read_csv(file)
        dfs.append({"df":df, "name":file.split("_")[0]})

    oracle = pd.read_csv(oracleLog)
    amm = pd.read_csv(ammLog)
    trans = pd.read_csv(transactionLog)

    
    return dfs, pd.concat([oracle, amm, trans], axis=1)

def random_blue():
    return (random.uniform(0, 0.3), random.uniform(0.3, 0.8), random.uniform(0.7, 1))

dfs, frames = getData()

# print(frames.head)

frames["time_amm"] /= 1000
frames["time_ora"] /= 1000
frames["sum"] =  frames["ETH"] + frames["XAUt"] + frames["MKR"]

frames['ETH_amount'] /= 1000
frames['XAUt_amount'] /= 1000
frames['MKR_amount'] /= 1000
# frames.reset_index(inplace=True)
# frames.reset_index(inplace=True)
frames['sumValue'] = (frames['ETH_amount'] * frames["ETH"] + frames['XAUt_amount'] * frames["XAUt"] + frames['MKR_amount'] * frames["MKR"])


# Plotting data from each dataframe on the same plot
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, layout='constrained', figsize=(14, 14))
ax1.tick_params(axis='both', which='major', labelsize=axis_number_font_size)
ax1.tick_params(axis='both', which='minor', labelsize=axis_number_font_size)
ax2.tick_params(axis='both', which='major', labelsize=axis_number_font_size)
ax2.tick_params(axis='both', which='minor', labelsize=axis_number_font_size)
ax3.tick_params(axis='both', which='major', labelsize=axis_number_font_size)
ax3.tick_params(axis='both', which='minor', labelsize=axis_number_font_size)
ax1.set_xlim(0, 60)
ax2.set_xlim(0, 60)
ax3.set_xlim(0, 60)
# ax3.set_ylim(550, 1100)
# ax2.set_ylim(2300, 2700)
ax1.grid(True)
ax2.grid(True)
ax3.grid(True)
x_ticks = [i for i in range(0, 61, 5)]
ax1.set_xticks(x_ticks)
ax2.set_xticks(x_ticks)
# ax3.set_xticks(x_ticks)


lim = 60
# amm['flatten'] = amm['sumValue'].rolling(lim, closed="both", min_periods=1, center=True).mean()
# frames['flatten'] = frames['sumValue']
fig.suptitle('Przebieg wartości aktywów w czasie', fontsize=plot_font_size)
ax1.set_xlabel('Czas [s]', fontsize=subplot_font_size)
ax1.set_ylabel('Wartość portfolio\nagentów [tys. USD]', fontsize=subplot_font_size)
for df in dfs:
    x_ticks = df["df"]['Timestamp']
    df["df"]['USDvalue'] /= 100000
    df["df"]['Timestamp'] /= 1000
    filtered = df["df"][df["df"]['Timestamp'] < 61]
    if "attacker" not in df["name"]:
        # condition = filtered['Timestamp']>30
        # filtered.loc[condition, 'USDvalue'] = filtered.loc[condition,'USDvalue'] * 0.98
        # condition = filtered['Timestamp']>17
        # filtered.loc[condition, 'USDvalue'] = filtered.loc[condition,'USDvalue'] * 0.98
        # condition = filtered['Timestamp']>23
        # filtered.loc[condition, 'USDvalue'] = filtered.loc[condition,'USDvalue'] * 0.99
        ax1.plot(filtered['Timestamp'], filtered['USDvalue'], marker='o', color=random_blue())
        # ax1.plot(filtered['Timestamp'], filtered['USDvalue'], marker='o', label=df["name"].split('/')[1])
for df in dfs:
    if "attacker" in df["name"]:
        filtered = df["df"][df["df"]['Timestamp'] < 61]
        ax1.plot(filtered['Timestamp'], filtered['USDvalue'], marker='o', label=df["name"].split('/')[1], color="red", linewidth=4)

frames['sum'] = frames['sum'].rolling(lim, closed="both", min_periods=1, center=True).mean()/10
ax2.set_xlabel('Czas [s]', fontsize=subplot_font_size)
ax2.set_ylabel('Sumaryczna wartość\naktywów [USD]', fontsize=subplot_font_size)
ax2.plot(frames['time_ora'], frames["sum"], label="Wartość sumaryczna aktywów", linewidth=4)

frames['ETH'] = frames['ETH'].rolling(lim, closed="both", min_periods=1, center=True).mean()
frames['XAUt'] = frames['XAUt'].rolling(lim, closed="both", min_periods=1, center=True).mean()
frames['MKR'] = frames['MKR'].rolling(lim, closed="both", min_periods=1, center=True).mean()

ax3.set_xlabel('Czas [s]', fontsize=subplot_font_size)
ax3.set_ylabel('Wartość poszczególnych\naktywów [USD]', fontsize=subplot_font_size)
ax3.plot(frames['time_amm'], frames['ETH_amount'], label="ETH", linewidth=4)
ax3.plot(frames['time_amm'], frames['XAUt_amount'], label="XAUt", linewidth=4)
ax3.plot(frames['time_amm'], frames['MKR_amount'], label="MKR", linewidth=4)

# ax1.legend(loc='lower left', prop={'size': 10})  # Separate legend for the bottom plot
ax2.legend(loc='lower left', prop={'size': 15})  # Separate legend for the bottom plot
ax3.legend(loc='lower left', prop={'size': 15})  # Separate legend for the bottom plot

# legend = ax2.legend(loc='upper left', prop={'size': 15})

# for legobjs in legend.legendHandles:
#     legobjs.set_linewidth(4.0)

# legend = ax1.legend(loc='upper left', prop={'size': 15})

# for legobjs in legend.legendHandles:
#     legobjs.set_linewidth(4.0)

plt.show()
