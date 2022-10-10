from statistics import fmean
import pandas as pd
import numpy as np
from statsmodels.stats.weightstats import ztest as ztest
from scipy import stats
import itertools
from tabulate import tabulate

results_df = pd.read_csv("./data/results.csv")
results_df = results_df.sort_values(by=["raceId"])

### Cleaning Data
results_df = results_df[results_df["grid"].notna()] ### Removing records with NaN values for the starting position
results_df = results_df[results_df["grid"] != 0] ### Removing records with 0 values for the starting position
results_df = results_df[results_df["positionOrder"].notna()] ### Removing records with NaN values for the finishing position
results_df = results_df[results_df["positionOrder"] != 0] ### Removing records with 0 values for the finishing position

### Calculating Average Number of Positions Gained/Lost

drivers = results_df["driverId"]
drivers = drivers.sort_values()
drivers = drivers.unique()

drivers = list(drivers) ### List of drivers

change_df = pd.DataFrame() ### Dataframe used to hold results

change_lst = [] ### List used to contain average positions gained/lost for all drivers
gain_loss_list_list = [] ### List used to contain positions gained/lost for all drivers for all races entered
num_races = [] ### List used to store number of races entered for each driver

for i in drivers:
    races = results_df.loc[results_df['driverId'] == i] ### Gets races partipated by driver
    start_list = list(races["grid"]) ### Lists starting positions of driver
    finish_list = list(races["positionOrder"]) ### Lists finishing postitions of driver
    gain_loss_list = np.subtract(start_list, finish_list) ### Subtracts finish position from start position to form list of positions gained/lost
    gain_loss_list_list.append(gain_loss_list) ### Sends list of positions gained/lost to list for all drivers
    avg_change = fmean(gain_loss_list) ### Averages list of positions gained/list to find average change
    change_lst.append(avg_change) ### Sends average change to list for all drivers
    num_races.append(races.shape[0]) ### Sends count of races to list for all drivers


### Using lists to form dataframe
change_df['Driver_ID'] = drivers 
change_df['Races_Counted'] = num_races
change_df['Gains/Losses'] = gain_loss_list_list
change_df['Average_Position_Gain/Loss'] = change_lst

print(change_df)


### Calculating the overall average change by averaging all individual gains/losses
overall_average_change = fmean(list(itertools.chain.from_iterable(change_df['Gains/Losses']))) 

### Filtering out drivers who partipated in less than 10 races
change_df = change_df[change_df['Races_Counted'] >= 10]

### Conducting T Test
change_df["T_Test"] = change_df.apply(lambda row : stats.ttest_1samp(row['Gains/Losses'], popmean=overall_average_change, alternative='greater'), axis=1)
change_df["T_Statistic"] = change_df["T_Test"].str[0] ### The T-Statistic is the first value in "T_Test" tuple
change_df["P_Value"] = change_df["T_Test"].str[1] ### The P-Value is the second value in "T_Test" tuple

### Determining if P-Value is Significant at p<0.001
change_df["Significant_001"] = change_df.apply(lambda row: row["P_Value"] < 0.001, axis=1)

### Fromating Columns - Surpressing Scientific Notation
change_df["T_Statistic"] = change_df.apply(lambda row : '%.10f' % row["T_Statistic"], axis=1)
change_df["P_Value"] = change_df.apply(lambda row : '%.15f' % row["P_Value"], axis=1)

### Organizing Data Frame 
change_df = change_df.sort_values(by=['Average_Position_Gain/Loss', 'P_Value'], ascending=[False,True])

### Replacing Driver ID with Name
driver_info = pd.read_pickle("./dataframes/drivers") ### Data frame with driver IDs and names
driver_lookup = dict(zip(driver_info['Driver ID'], driver_info['Name'])) ### Setting up dictionary with ID and name

key_list = list(change_df["Driver_ID"])
change_df["Name"] = [driver_lookup[item] for item in key_list]
names = change_df.pop("Name")
change_df.insert(0, names.name, names)


### Getting Results
print("Best Average Positions Gained:\n", change_df)
print(change_df[["Name", "Races_Counted", "Gains/Losses", "Average_Position_Gain/Loss", "T_Statistic", "P_Value", "Significant_001"]])

print(pd.value_counts(change_df["Significant_001"]))