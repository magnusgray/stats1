from statistics import fmean
import pandas as pd
import numpy as np
from statsmodels.stats.weightstats import ztest as ztest
from scipy import stats
import itertools

results_df = pd.read_csv("./data/results.csv")
results_df = results_df.sort_values(by=["raceId"])

### Cleaning Data
results_df = results_df[results_df["grid"].notna()] ### Removing records with NaN values for the starting position
results_df = results_df[results_df["grid"] != 0] ### Removing records with 0 values for the starting position
results_df = results_df[results_df["positionOrder"].notna()] ### Removing records with NaN values for the finishing position
results_df = results_df[results_df["positionOrder"] != 0] ### Removing records with 0 values for the finishing position

races_df = pd.read_csv("./data/races.csv") ### Contains data regarding each race

driver_info = pd.read_pickle("./dataframes/drivers") ### Data frame with driver IDs and names
driver_lookup = dict(zip(driver_info['Driver ID'], driver_info['Name'])) ### Setting up dictionary with ID and name

constructor_info = pd.read_pickle("./dataframes/constructors") ### Data frame with constructor (team) IDs and names
constructor_lookup = dict(zip(constructor_info['Constructor ID'], constructor_info['Name'])) ### Setting up dictionary with ID and name

year_races = list(races_df.loc[races_df["year"].isin([2021]), "raceId"]) ### Getting list of races in 2021
results_df = results_df[results_df["raceId"].isin(year_races)] ### Selecting data only the races from above

### Calculating Average Number of Positions Gained/Lost

constructors = results_df["constructorId"]
constructors = constructors.sort_values()
constructors = constructors.unique()

constructors = list(constructors) ### List of constructors

df = pd.DataFrame() ### Dataframe to contain final results

for x in constructors:
    drivers = results_df.loc[results_df["constructorId"] == x, 'driverId']
    drivers = drivers.sort_values()
    drivers = drivers.unique()

    drivers = list(drivers) ### List of driver for specific constructor

    change_df = pd.DataFrame() ### Dataframe to contain results for one constructor

    change_lst = [] ### List used to contain average positions gained/lost for drivers
    gain_loss_list_list = [] ### List used to contain positions gained/lost for drivers for all races entered
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
    change_df["Constructor_ID"] = x 
    change_df['Races_Counted'] = num_races
    change_df['Gains/Losses'] = gain_loss_list_list
    change_df['Average_Position_Gain/Loss'] = change_lst

    change_df = change_df.sort_values(by=["Races_Counted","Average_Position_Gain/Loss"], ascending=[False,False])
    change_df = change_df[change_df['Races_Counted'] > 1] ### Test does not work for drivers with one race

    change_df = change_df.head(2) ### Only two drivers can be tested
    change_df = change_df.sort_values(by=["Average_Position_Gain/Loss", "Races_Counted"], ascending=[False,False])

    change1 = change_df.iloc[0]["Gains/Losses"] ### Sample 1
    change2 = change_df.iloc[1]["Gains/Losses"] ### Sample 2

    var1, var2 = np.var(change1), np.var(change2) ### Getting variance of samples

    ### Determining variance ratio between samples
    if var1 > var2:
        var_ratio = var1/var2
    elif var2 > var1:
        var_ratio = var2/var1
    else:
        var_ratio = 1

    ### If variance ratio is less than four, the samples can be considered to have equal variance
    ### Else, the variance is considered unequal
    ### Thus, two different versions of T-Test
    if var_ratio < 4:
        t_test = stats.ttest_ind(change1, change2, equal_var=True)
    elif var_ratio > 4:
        t_test = stats.ttest_ind(change1, change2, equal_var=False)

    change_df["T_Statistic"] = t_test[0] ### The T-Statistic is the first value in "T_Test" tuple
    change_df["P_Value"] = t_test[1] ### The P-Value is the second value in "T_Test" tuple

    ### Determining if P-Value is Significant at p<0.001
    change_df["Significant_001"] = change_df.apply(lambda row: row["P_Value"] < 0.001, axis=1)
    change_df["Better_Than_Teammate?"] = ""
    
    change_df = change_df.reset_index(drop=True)

    ### Determining if one teammate is better than other
    ### If P-Value is significant, first driver (i.e., the one with better stat) is better
    ### Else, no driver is better
    if True in change_df["Significant_001"].values:
        change_df["Better_Than_Teammate?"].loc[0] = True
        change_df["Better_Than_Teammate?"].loc[1] = False
    else:
        change_df["Better_Than_Teammate?"].loc[0] = False
        change_df["Better_Than_Teammate?"].loc[1] = False


    ### Organizing datafrane
    change_df = change_df.sort_values(by=['Average_Position_Gain/Loss', 'P_Value'], ascending=[False,True])


    ### Replacing Driver & Consturctor ID with Name
    key_list = list(change_df["Driver_ID"])
    change_df["Driver"] = [driver_lookup[item] for item in key_list]
    key_list = list(change_df["Constructor_ID"])
    change_df["Constructor"] = [constructor_lookup[item] for item in key_list]

    names = change_df.pop("Driver")
    change_df.insert(0, names.name, names)
    names = change_df.pop("Constructor")
    change_df.insert(0, names.name, names)


    ### Getting Results
    print("Best Average Positions Gained:\n", change_df)
    print(change_df[["Driver", "Constructor", "Races_Counted", "Gains/Losses", "Average_Position_Gain/Loss", "T_Statistic", "P_Value", "Significant_001"]])

    change_df = change_df[["Constructor", "Driver", "Races_Counted", "Gains/Losses", "Average_Position_Gain/Loss", "T_Statistic", "P_Value", "Better_Than_Teammate?"]]

    df = pd.concat([df, change_df])


print(df)