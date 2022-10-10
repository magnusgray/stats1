import pandas as pd

constructors = pd.read_csv("./data/constructors.csv")

constructorinfo = pd.DataFrame()

constructorinfo["Constructor ID"] = constructors["constructorId"]
constructorinfo["Name"] = constructors["name"]

constructorinfo.to_pickle("./dataframes/constructors")