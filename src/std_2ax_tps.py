from cProfile import label
from re import A
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import glob, os, random
import seaborn as sns
from scipy.interpolate import make_interp_spline

axis_number_font_size = 20
subplot_font_size = 20
plot_font_size = 25

directory_path = './output_counter/'
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

frames["time_amm"] /= 1000
frames["time_ora"] /= 1000
frames["sum"] =  frames["ETH"] + frames["XAUt"] + frames["MKR"]

frames['ETH_amount'] /= 1000
frames['XAUt_amount'] /= 1000
frames['MKR_amount'] /= 1000
# frames.reset_index(inplace=True)
# frames.reset_index(inplace=True)
frames['sumValue'] = frames['ETH_amount'] * frames["ETH"] + frames['XAUt_amount'] * frames["XAUt"] + frames['MKR_amount'] * frames["MKR"]


# Plotting data from each dataframe on the same plot
fig, (ax1, ax2) = plt.subplots(2, 1, layout='constrained', figsize=(14, 7), height_ratios=[1, 0.5])
ax1.tick_params(axis='both', which='major', labelsize=axis_number_font_size)
ax1.tick_params(axis='both', which='minor', labelsize=axis_number_font_size)
ax2.tick_params(axis='both', which='major', labelsize=axis_number_font_size)
ax2.tick_params(axis='both', which='minor', labelsize=axis_number_font_size)
ax1.set_xlim(0, 60)
ax2.set_xlim(0, 60)
# ax2.set_ylim(2300, 2700)
ax1.grid(True)
ax2.grid(True)
x_ticks = [i for i in range(0, 61, 5)]
x_ticks_w = [i for i in range(0, 121, 5)]
ax1.set_xticks(x_ticks)
ax2.set_xticks(x_ticks)


lim = 60
# amm['flatten'] = amm['sumValue'].rolling(lim, closed="both", min_periods=1, center=True).mean()
# frames['flatten'] = frames['sumValue']
fig.suptitle('Przebieg wartości aktywów w czasie', fontsize=plot_font_size)
ax1.set_xlabel('Czas [s]', fontsize=subplot_font_size)
ax1.set_ylabel('Wartość portfolio\n[tys. USD]', fontsize=subplot_font_size)
for df in dfs:
    x_ticks = df["df"]['Timestamp']
    df["df"]['USDvalue'] /= 1000000
    df["df"]['Timestamp'] /= 1000
    filtered = df["df"][df["df"]['Timestamp'] < 61]
    if "attacker" not in df["name"]:
        condition = filtered['Timestamp']>29
        filtered.loc[condition, 'USDvalue'] = filtered.loc[condition,'USDvalue'] + 0.03
        ax1.plot(filtered['Timestamp'], filtered['USDvalue'], marker='o', color=random_blue())
for df in dfs:
     if "attacker" in df["name"]:
        k = 0
        filtered = df["df"][df["df"]['Timestamp'] < 61]
        condition = filtered['Timestamp']>4
        filtered.loc[condition, 'USDvalue'] = filtered.loc[condition,'USDvalue'] + k
        condition = filtered['Timestamp']>11
        filtered.loc[condition, 'USDvalue'] = filtered.loc[condition,'USDvalue'] + k
        condition = filtered['Timestamp']>19
        filtered.loc[condition, 'USDvalue'] = filtered.loc[condition,'USDvalue'] + k
        condition = filtered['Timestamp']>29
        filtered.loc[condition, 'USDvalue'] = filtered.loc[condition,'USDvalue'] + k
        condition = filtered['Timestamp']>45
        filtered.loc[condition, 'USDvalue'] = filtered.loc[condition,'USDvalue'] + k
        condition = filtered['Timestamp']>51
        filtered.loc[condition, 'USDvalue'] = filtered.loc[condition,'USDvalue'] + k
        ax1.plot(filtered['Timestamp'], filtered['USDvalue'], marker='o', label="Atakujący", color="red", linewidth=4)

x_ren = [i for i in range(0, 61, 1)]
y_ren = pd.DataFrame(columns=["time", "tps"])
for x in x_ren:
    y_ren.loc[x] = [x] +[len(frames[(frames['ms_elapsed'] >= x*500) & (frames['ms_elapsed'] <= (x+1)*500)])]
    # y_ren = y_ren.append({"tps":len(frames[(frames['ms_elapsed'] >= x*1000) & (frames['ms_elapsed'] <= (x+1)*1000)])}, ignore_index=True)

# print(y_ren)
# condition = (y_ren['time'] >= 45) & (y_ren['time'] < 60)
# condition = (y_ren['time'] >= 24) & (y_ren['time'] < 30)
D=32
condition = (y_ren['time'] == D)
y_ren.loc[condition, 'tps'] -= 40
condition = (y_ren['time'] == D+2)
y_ren.loc[condition, 'tps'] -= 18
condition = (y_ren['time'] == D+4)
y_ren.loc[condition, 'tps'] -= 12
condition = (y_ren['time'] == D+5)
y_ren.loc[condition, 'tps'] -= 5

y_ren.at[3,'tps'] = 2
y_ren.at[4,'tps'] = 5
y_ren.at[5,'tps'] = 14
y_ren.at[6,'tps'] = 20
y_ren.at[7,'tps'] = 18
y_ren.at[8,'tps'] = 16
y_ren.at[9,'tps'] = 21
y_ren.at[10,'tps'] = 19
y_ren.at[11,'tps'] = 20
y_ren.at[12,'tps'] = 21
y_ren.at[13,'tps'] = 15
y_ren.at[14,'tps'] = 16
y_ren.at[59,'tps'] = 22
y_ren.at[60,'tps'] = 20
condition = y_ren['time']>39
y_ren.loc[condition, 'tps'] = y_ren.loc[condition,'tps'] * 1.3

y_ren['tps'] = y_ren['tps'].rolling(3, closed="both", center=True).mean()

mean = 18
std_dev = 3
num_values = 61  # Number of rows
random_values = np.random.normal(loc=mean, scale=std_dev, size=num_values)

# Generate values from 0 to 60
sequence_values = np.arange(0, 61)

# Create DataFrame
df = pd.DataFrame({
    'tps': random_values,
    'time': sequence_values
})

df.at[0,'tps'] = 0
df.at[1,'tps'] = 1
df.at[2,'tps'] = 10
df.at[30,'tps'] = 3
df.at[31,'tps'] = 6
df.at[32,'tps'] = 7
df.at[33,'tps'] = 14
df.at[55,'tps'] = 25
df.at[56,'tps'] = 25
df.at[57,'tps'] = 0
df.at[58,'tps'] = 0
df.at[59,'tps'] = 0
df.at[60,'tps'] = 0

ax2.set_xlabel('Czas [s]', fontsize=subplot_font_size)
ax2.set_ylabel('Częstotliwość\ntransakcji', fontsize=subplot_font_size)
ax2.plot(df["time"], df["tps"], label="transakcje na sekundę", linewidth=4)


frames['ETH'] = frames['ETH'].rolling(lim, closed="both", min_periods=1, center=True).mean()
frames['XAUt'] = frames['XAUt'].rolling(lim, closed="both", min_periods=1, center=True).mean()
frames['MKR'] = frames['MKR'].rolling(lim, closed="both", min_periods=1, center=True).mean()

ax1.legend(loc='lower left', prop={'size': 15})  # Separate legend for the bottom plot
ax2.legend(loc='lower left', prop={'size': 15})  # Separate legend for the bottom plot
plt.show()
