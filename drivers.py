import pandas as pd

drivers = pd.read_csv("./data/drivers.csv")

drivers["Name"] = drivers[["forename", "surname"]].agg(' '.join, axis=1)

driverinfo = pd.DataFrame()

driverinfo["Driver ID"] = drivers["driverId"]
driverinfo["Name"] = drivers["Name"]

driverinfo.to_pickle("./dataframes/drivers")