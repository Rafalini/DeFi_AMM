import pandas as pd
import matplotlib.pyplot as plt
import random

def get_random_color():
    return "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

df1 = pd.read_csv('log.csv')
# df2 = pd.read_csv('log2.csv')

arr = [df1]

# Create three separate subplots
fig, axs = plt.subplots(3, 1, figsize=(8, 12))

maxVal = 0
minVal = 0
maxLen = 0

for df in arr:

# Extract the columns
    BTCamount = df['BTCamount']
    ETHamount = df['ETHamount']
    BTCvETHrate = df['BTCvETHrate']
    con = pd.concat([BTCamount, ETHamount])
    maxVal = max(max(con), maxVal)
    minVal = min(min(con), minVal)
    maxLen = max(len(BTCamount), maxLen)

    # Plot BTCamount
    axs[0].plot(BTCamount, color=get_random_color())
    axs[0].set_title('BTC Amount')
    # axs[0].set_xlabel('Data Point')
    axs[0].set_ylabel('BTC Amount')

    # Plot ETHamount
    axs[1].plot(ETHamount, color=get_random_color())
    axs[1].set_title('ETH Amount')
    # axs[1].set_xlabel('Data Point')
    axs[1].set_ylabel('ETH Amount')

    # Plot BTCvETHrate
    axs[2].plot(BTCvETHrate, color=get_random_color())
    axs[2].set_title('BTC/ETH Rate')
    # axs[2].set_xlabel('Data Point')
    axs[2].set_ylabel('BTC/ETH Rate')

for ax in axs:
    ax.set_facecolor('lightcyan')  # Set the background color of the subplot to light gray
    ax.grid(True, linestyle='--', linewidth=0.5)

    # ax.set_xticks(range(0, maxLen, 25))  # Adjust the range and step size for x-axis
    # ax.set_yticks(range(int(minVal), int(maxVal), 50))  # Adjust the range and step size for y-axis
    ax.xaxis.grid(which='both', linestyle='-', linewidth=0.5, color='gray')  # Use solid lines for thicker gridlines on x-axis
    ax.yaxis.grid(which='both', linestyle='-', linewidth=0.5, color='gray')  # Use solid lines for thicker gridlines on y-axis


fig.patch.set_facecolor('lightgray')
plt.tight_layout()
plt.show()

