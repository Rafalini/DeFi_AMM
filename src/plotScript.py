import pandas as pd
import matplotlib.pyplot as plt
import glob, os

directory_path = './node/log'  # Replace this with your directory path
# Change the current working directory to the specified directory path
os.chdir(directory_path)
# List all CSV files in the current directory
csv_files = glob.glob('*.csv')

# Initialize a list to store dataframes from CSV files
dfs = []

# Read each CSV file into a dataframe and store in the list
for file in csv_files:
    df = pd.read_csv(file)
    dfs.append(df)

# Plotting data from each dataframe on the same plot
plt.figure(figsize=(10, 6))
for df in dfs:
    plt.plot(df['Timestamp'], df['USDvalue'], marker='o', label=df.columns[-1])

plt.xlabel('Timestamp')
plt.ylabel('Price')
plt.title('Price Data from CSV Files')
plt.legend()
plt.grid(True)
plt.tight_layout()

# Show the plot
plt.show()
