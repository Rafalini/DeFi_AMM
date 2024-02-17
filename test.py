import pandas as pd
import numpy as np

# Sample DataFrame
df = pd.DataFrame({'A': [1.1, 2.4, 3.6],
                   'B': [4.5, 5.7, 6.9]})

# Round all values in the DataFrame up to the nearest integer
df_rounded = df.apply(np.ceil)

print("Original DataFrame:")
print(df)
print("\nDataFrame with rounded values:")
print(df_rounded)
