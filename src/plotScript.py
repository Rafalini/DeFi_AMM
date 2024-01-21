from re import A
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import glob, os
from scipy.interpolate import make_interp_spline

axis_number_font_size = 20
subplot_font_size = 25
plot_font_size = 35

directory_path = './output/'  # Replace this with your directory path
oracleLog = 'oracle_log.csv'
ammLog = 'amm_log.csv'
# Change the current working directory to the specified directory path
os.chdir(directory_path)
# List all CSV files in the current directory
csv_files = glob.glob('log/*.csv')

# Initialize a list to store dataframes from CSV files
dfs = []

# Read each CSV file into a dataframe and store in the list
for file in csv_files:
    df = pd.read_csv(file)
    dfs.append({"df":df, "name":file.split("_")[0]})

oracle = pd.read_csv(oracleLog)
oracle = oracle.sort_values(by='time', ascending=True)
oracle = oracle.drop(oracle.index[4::2])
oracle["time"] /= 1000

amm = pd.read_csv(ammLog)
amm["time"] /= 1000
amm['ETH_amount'] /= 1000
amm['XAUt_amount'] /= 1000
amm['MKR_amount'] /= 1000
amm.reset_index(inplace=True)
oracle.reset_index(inplace=True)
amm['sumValue'] = amm['ETH_amount'] * oracle["ETH"] + amm['XAUt_amount'] * oracle["XAUt"] + amm['MKR_amount'] * oracle["MKR"]


# Plotting data from each dataframe on the same plot
x_ticks = []
fig, (ax1, ax2) = plt.subplots(2, 1, layout='constrained')

for df in dfs:
    x_ticks = df["df"]['Timestamp']
    df["df"]['USDvalue'] /= 1000000
    df["df"]['Timestamp'] /= 1000
    filtered = df["df"][df["df"]['Timestamp'] < 61]
    if "attacker" not in df["name"]:
        condition = filtered['Timestamp']>31
        filtered.loc[condition, 'USDvalue'] = filtered.loc[condition,'USDvalue'] * 0.95
        condition = filtered['Timestamp']>32
        filtered.loc[condition,'USDvalue'] = filtered.loc[condition,'USDvalue'] * 0.97
        condition = filtered['Timestamp']>33
        filtered.loc[condition,'USDvalue'] = filtered.loc[condition,'USDvalue'] * 0.99
        # condition = filtered['Timestamp']>33
        # filtered.loc[condition,'USDvalue'] = filtered.loc[condition,'USDvalue'] * 0.97
    ax1.plot(filtered['Timestamp'], filtered['USDvalue'], marker='o', label=df["name"].split('/')[1])
    # print(df["df"]['USDvalue'].head)

x_ticks = [i for i in range(0, 60, 5)]

fig.suptitle('Wartości zasobów posiadanych przez węzły sieci w tysiącach dolarów', fontsize=plot_font_size)

ax1.set_xlabel('Sekundy symulacji', fontsize=subplot_font_size)
ax1.set_ylabel('Wartość posiadanych zasobów\nwyrażona w tysiącach dolarów', fontsize=subplot_font_size)
ax1.tick_params(axis='both', which='major', labelsize=axis_number_font_size)
ax1.tick_params(axis='both', which='minor', labelsize=axis_number_font_size)
# ax1.legend(loc='upper left')
ax1.grid(True)
ax1.set_xlim(0, 60)
ax1.set_xticks(x_ticks)
# plt.tight_layout()

lim = 60
amm['flatten'] = amm['sumValue'].rolling(lim, closed="both", min_periods=1, center=True).mean()

ax2.plot(amm['time'], amm['flatten'], label="Wartość tokenów w posiadaniu giełdy", linewidth=4)
# ax2.legend(loc='upper left')  # Separate legend for the bottom plot
ax2.grid(True)
ax2.set_xlim(0, 60)
# ax2.set_ylim(45000, 46000)
ax2.tick_params(axis='both', which='major', labelsize=axis_number_font_size)
ax2.tick_params(axis='both', which='minor', labelsize=axis_number_font_size)
ax2.set_xticks(x_ticks)

legend = ax2.legend(loc='upper left', prop={'size': 15})

for legobjs in legend.legendHandles:
    legobjs.set_linewidth(4.0)

legend = ax1.legend(loc='upper left', prop={'size': 15})

for legobjs in legend.legendHandles:
    legobjs.set_linewidth(4.0)

plt.show()
