import pandas as pd


X = pd.read_csv('ordered_serp_full_core_2.mvol', header=None, skiprows=7, engine='python', delim_whitespace=True)

vol_fuel = 0
vol_graphite = 0
for i in range(54):
    if 'fuel' in X[0][i]:
        vol_fuel += X[2][i]
    elif 'Graphite' in X[0][i]:
        vol_graphite += X[2][i]

print(vol_fuel, vol_graphite)
