from statistics import fmean
import pandas as pd
import numpy as np
from statsmodels.stats.weightstats import ztest as ztest
from scipy import stats
import itertools
import dash
from dash import dcc, html, dash_table, Dash
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go

#pd.options.display.float_format = '{:.20f}'.format


results_df = pd.read_csv("./data/results.csv")
results_df = results_df.sort_values(by=["raceId"])


races_df = pd.read_csv("./data/races.csv")
years = races_df["year"]
years = years.sort_values()
years = years.unique()
years = list(years)
years.pop()

app = dash.Dash(__name__)

server = app.server

app.layout = html.Div([
    html.H1("Who is #1 in Formula 1?: Analyzing Formula 1 World Championship Statisics", style={'textAlign': 'center'}),
    html.H1(""),
    dcc.Tabs([
        dcc.Tab(label="Solo Drivers (One-Sample T-Test)", selected_style={"borderTop": "3px solid #FF1801"}, children=[
            dcc.Tabs([
                dcc.Tab(label="Best Of All Time", selected_style={"borderTop": "3px solid #FF1801"}, children=[
                    html.H2("Top 10 Drivers of All Time based on:"),
                    dcc.Dropdown(
                        id='d_all_stat',
                        options=[
                            {'label': 'Best Average Positions Gained/Lost', 'value': 0},
                            {'label': 'Best Average Finishing Position', 'value': 1},
                            {'label': 'Best Average Starting Position', 'value': 2},
                        ],
                        value = 0
                    ),
                    html.H2("with a minimum race count of:"),
                    dcc.Input(
                        id='d_all_filter',
                        type='number',
                        min=1,
                        max=350,
                        step=1,
                        value = 10,
                    ),
                    html.H2("with a minimum statistical significance of:"),
                    dcc.Input(
                        id='d_all_sig',
                        type='number',
                        min=0.001,
                        max=1.0,
                        step=0.001,
                        value = 0.010,
                    ),
                    html.H1(""),
                    html.H4("***Note: If a table does not appear, no significant results were found for the selected filters. Try adjusting the minimum statistical signifcance level or race count.***"),
                    html.H1(""),
                    dash_table.DataTable(id="d_all"),
                    html.H1(""),
                ]),
                dcc.Tab(label="Best By Era", selected_style={"borderTop": "3px solid #FF1801"}, children=[
                    html.H2("Top 10 Drivers in:"),
                    dcc.Dropdown(
                        id="d_era_years",
                        options=[
                            {'label': "Era 1: 1950-1957 (The era of factory Italian and Mercedes front-engine cars)", 'value': 1},
                            {'label': "Era 2: 1958-1961 (British independent specialist teams and the rear-mid engine revolution)", 'value': 2},
                            {'label': "Era 3: 1962-1967 (Anglophone drivers and 1.5-litre engines)", 'value': 3},
                            {'label': "Era 4: 1968-1976 (The DFV engine, 12-cylinder engines and the arrival of sponsorship, safety and aerodynamics)", 'value': 4},
                            {'label': "Era 5: 1977-1982 (Ground-effect era)", 'value': 5},
                            {'label': "Era 6: 1983-1988 (1.5-litre turbo-charged engines)", 'value': 6},
                            {'label': "Era 7: 1989-1993 (3.5-litre naturally-aspirated engines, active suspension and electronic driver aids)", 'value': 7},
                            {'label': "Era 8: 1994 (Safety, rules and regulations)", 'value': 8},
                            {'label': "Era 9: 1995-1999 (3-litre engines)", 'value': 9},
                            {'label': "Era 10: 2000-2005 (V10 engines and rise of road car manufacturer participation)", 'value': 10},
                            {'label': "Era 11: 2006-2008 (2.4-litre V8 engines)", 'value': 11},
                            {'label': "Era 12: 2009-2013 (Cost-cutting measures and departure of car manufacturers)", 'value': 12},
                            {'label': "Era 13: 2014-2021 (1.6-litre turbocharged V6 hybrid power units)", 'value': 13},
                        ],
                        value = 13,
                        multi=False
                    ),
                    html.H2("based on:"),
                    dcc.Dropdown(
                        id='d_eras_stat',
                        options=[
                            {'label': 'Best Average Positions Gained/Lost', 'value': 0},
                            {'label': 'Best Average Finishing Position', 'value': 1},
                            {'label': 'Best Average Starting Position', 'value': 2},
                        ],
                        value = 0
                    ),
                    html.H2("with a minimum race count of:"),
                    dcc.Input(
                        id='d_eras_filter',
                        type='number',
                        min=1,
                        max=350,
                        step=1,
                        value = 5,
                    ),
                    html.H2("with a minimum statistical significance of:"),
                    dcc.Input(
                        id='d_eras_sig',
                        type='number',
                        min=0.001,
                        max=1.0,
                        step=0.001,
                        value = 0.010,
                    ),
                    html.H1(""),
                    html.H4("***Note: If a table does not appear, no significant results were found for the selected filters. Try adjusting the minimum statistical signifcance level or race count.***"),
                    html.H1(""),
                    dash_table.DataTable(id="d_eras"),
                    html.H1(""),
                ]),
                dcc.Tab(label="Best By Season", selected_style={"borderTop": "3px solid #FF1801"}, children=[
                    html.H2("Top 10 Drivers in:"),
                    dcc.Dropdown(
                        id="d_years",
                        options=[{'label': x, 'value': x} for x in years],
                        value = [2021],
                        multi=True
                    ),
                    html.H2("based on:"),
                    dcc.Dropdown(
                        id='d_seasons_stat',
                        options=[
                            {'label': 'Best Average Positions Gained/Lost', 'value': 0},
                            {'label': 'Best Average Finishing Position', 'value': 1},
                            {'label': 'Best Average Starting Position', 'value': 2},
                        ],
                        value = 0
                    ),
                    html.H2("with a minimum race count of:"),
                    dcc.Input(
                        id='d_seasons_filter',
                        type='number',
                        min=1,
                        max=350,
                        step=1,
                        value = 5,
                    ),
                    html.H2("with a minimum statistical significance of:"),
                    dcc.Input(
                        id='d_seasons_sig',
                        type='number',
                        min=0.001,
                        max=1.0,
                        step=0.001,
                        value = 0.010,
                    ),
                    html.H1(""),
                    html.H4("***Note: If a table does not appear, no significant results were found for the selected filters. Try adjusting the minimum statistical signifcance level or race count.***"),
                    html.H1(""),
                    dash_table.DataTable(id="d_seasons"),
                    html.H1(""),
                ]),
            ])
        ]),
        dcc.Tab(label="Teammates (Two-Sample T-Test)", selected_style={"borderTop": "3px solid #FF1801"}, children=[
            html.H2("Teammate comparison for the year of:"),
            dcc.Dropdown(
                id="t_years",
                options=[{'label': x, 'value': x} for x in years],
                value = 2021,
                multi=False
            ),
            html.H2("based on:"),
            dcc.Dropdown(
                id='t_stat',
                options=[
                    {'label': 'Best Average Positions Gained/Lost', 'value': 0},
                    {'label': 'Best Average Finishing Position', 'value': 1},
                    {'label': 'Best Average Starting Position', 'value': 2},
                ],
                value = 0
            ),
            html.H2("with a minimum statistical significance of:"),
            dcc.Input(
                id='t_sig',
                type='number',
                min=0.001,
                max=1.0,
                step=0.001,
                value = 0.10,
            ),
            html.H1(""),
            html.H4("***Note: For mathematical purposes, teams with only one member and drivers with less than two races were excluded***"),
            html.H1(""),
            dash_table.DataTable(id="t"),
            html.H1(""),
        ]),     
    ])

])


@app.callback(
    Output("d_all", "data"),
    Output('d_all', 'columns'),
    Input("d_all_stat", "value"),
    Input('d_all_filter', 'value'),
    Input('d_all_sig', 'value'),
)
def update_d_all(var, race_count, sig_level):
    results_df = pd.read_csv("./data/results.csv")
    results_df = results_df[results_df["grid"].notna()]
    results_df = results_df[results_df["grid"] != 0]
    results_df = results_df[results_df["positionOrder"].notna()]
    results_df = results_df[results_df["positionOrder"] != 0]

    driver_info = pd.read_pickle("./dataframes/drivers")
    driver_lookup = dict(zip(driver_info['Driver ID'], driver_info['Name']))

    if var == 0:
        drivers = results_df["driverId"]
        drivers = drivers.sort_values()
        drivers = drivers.unique()

        drivers = list(drivers)

        change_df = pd.DataFrame()

        change_lst = []
        gain_loss_list_list = []
        num_races = []

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
        change_df['Gains/Losses'] = gain_loss_list_list
        change_df['Average_Position_Gain/Loss'] = change_lst
        change_df['Races_Counted'] = num_races

        overall_average_change2 = fmean(list(itertools.chain.from_iterable(change_df['Gains/Losses']))) ### Calculating the overall average change by averaging all individual gains/losses
        change_df = change_df[change_df['Races_Counted'] >= race_count] ### Filters out drivers who partipated in less than 5 races

        ### Conducting T Test and Determining if P-Value is Significant
        change_df["T_Test"] = change_df.apply(lambda row : stats.ttest_1samp(row['Gains/Losses'], popmean=overall_average_change2, alternative='greater'), axis=1)
        change_df["T_Statistic"] = change_df["T_Test"].str[0]
        change_df["P_Value"] = change_df["T_Test"].str[1]
        change_df["Significant"] = change_df.apply(lambda row: row["P_Value"] < sig_level, axis=1)

        ### Organizing datafrane
        change_df = change_df.sort_values(by=['Average_Position_Gain/Loss', 'P_Value'], ascending=[False,True])
        if True in change_df["Significant"].values:
            change_df = change_df[change_df["Significant"] == True]

            key_list = list(change_df["Driver_ID"])
            change_df["Name"] = [driver_lookup[item] for item in key_list]
            names = change_df.pop("Name")
            change_df.insert(0, names.name, names)

            change_df = change_df.drop(columns=["Driver_ID", "Gains/Losses", "T_Test", "Significant"])
            change_df = change_df.head(10)

            change_df["T_Statistic"] = change_df.apply(lambda row : '%.10f' % row["T_Statistic"], axis=1)
            change_df["P_Value"] = change_df.apply(lambda row : '%.15f' % row["P_Value"], axis=1)
            print(change_df)
            
            return change_df.to_dict('records'), [{"name": i, "id": i} for i in change_df.columns]
        else:
            change_df = pd.DataFrame()
            return change_df.to_dict('records'), [{"name": i, "id": i} for i in change_df.columns]
    if var == 1:
        drivers = results_df["driverId"]
        drivers = drivers.sort_values()
        drivers = drivers.unique()

        drivers = list(drivers)

        change_df = pd.DataFrame()

        change_lst = []
        finish_list_list = []
        num_races = []

        for i in drivers:
            races = results_df.loc[results_df['driverId'] == i] ### Gets races partipated by driver
            finish_list = list(races["positionOrder"]) ### Lists finishing postitions of driver
            finish_list_list.append(finish_list) ### Sends list of positions gained/lost to list for all drivers
            avg_change = fmean(finish_list) ### Averages list of positions gained/list to find average change
            change_lst.append(avg_change) ### Sends average change to list for all drivers
            num_races.append(races.shape[0]) ### Sends count of races to list for all drivers

        ### Using lists to form dataframe
        change_df['Driver_ID'] = drivers 
        change_df['Finishes'] = finish_list_list
        change_df['Average_Finish_Position'] = change_lst
        change_df['Races_Counted'] = num_races

        overall_average_change2 = fmean(list(itertools.chain.from_iterable(change_df['Finishes']))) ### Calculating the overall average change by averaging all individual gains/losses
        change_df = change_df[change_df['Races_Counted'] >= race_count] ### Filters out drivers who partipated in less than 5 races

        ### Conducting T Test and Determining if P-Value is Significant
        change_df["T_Test"] = change_df.apply(lambda row : stats.ttest_1samp(row['Finishes'], popmean=overall_average_change2, alternative='less'), axis=1)
        change_df["T_Statistic"] = change_df["T_Test"].str[0]
        change_df["P_Value"] = change_df["T_Test"].str[1]
        change_df["Significant"] = change_df.apply(lambda row: row["P_Value"] < sig_level, axis=1)

        ### Organizing datafrane
        change_df = change_df.sort_values(by=['Average_Finish_Position', 'P_Value'], ascending=[True,True])
        if True in change_df["Significant"].values:
            change_df = change_df[change_df["Significant"] == True]

            key_list = list(change_df["Driver_ID"])
            change_df["Name"] = [driver_lookup[item] for item in key_list]
            names = change_df.pop("Name")
            change_df.insert(0, names.name, names)

            change_df = change_df.drop(columns=["Driver_ID", "Finishes", "T_Test", "Significant"])
            change_df = change_df.head(10)

            change_df["T_Statistic"] = change_df.apply(lambda row : '%.10f' % row["T_Statistic"], axis=1)
            change_df["P_Value"] = change_df.apply(lambda row : '%.15f' % row["P_Value"], axis=1)
            print(change_df)
            
            return change_df.to_dict('records'), [{"name": i, "id": i} for i in change_df.columns]
        else:
            change_df = pd.DataFrame()
            return change_df.to_dict('records'), [{"name": i, "id": i} for i in change_df.columns]
    if var == 2:
        drivers = results_df["driverId"]
        drivers = drivers.sort_values()
        drivers = drivers.unique()

        drivers = list(drivers)

        change_df = pd.DataFrame()

        change_lst = []
        start_list_list = []
        num_races = []

        for i in drivers:
            races = results_df.loc[results_df['driverId'] == i] ### Gets races partipated by driver
            start_list = list(races["grid"]) ### Lists finishing postitions of driver
            start_list_list.append(start_list) ### Sends list of positions gained/lost to list for all drivers
            avg_change = fmean(start_list) ### Averages list of positions gained/list to find average change
            change_lst.append(avg_change) ### Sends average change to list for all drivers
            num_races.append(races.shape[0]) ### Sends count of races to list for all drivers

        ### Using lists to form dataframe
        change_df['Driver_ID'] = drivers 
        change_df['Starts'] = start_list_list
        change_df['Average_Start_Position'] = change_lst
        change_df['Races_Counted'] = num_races

        overall_average_change2 = fmean(list(itertools.chain.from_iterable(change_df['Starts']))) ### Calculating the overall average change by averaging all individual gains/losses
        change_df = change_df[change_df['Races_Counted'] >= race_count] ### Filters out drivers who partipated in less than 5 races

        ### Conducting T Test and Determining if P-Value is Significant
        change_df["T_Test"] = change_df.apply(lambda row : stats.ttest_1samp(row['Starts'], popmean=overall_average_change2, alternative='less'), axis=1)
        change_df["T_Statistic"] = change_df["T_Test"].str[0]
        change_df["P_Value"] = change_df["T_Test"].str[1]
        change_df["Significant"] = change_df.apply(lambda row: row["P_Value"] < sig_level, axis=1)

        ### Organizing datafrane
        change_df = change_df.sort_values(by=['Average_Start_Position', 'P_Value'], ascending=[True,True])
        if True in change_df["Significant"].values:
            change_df = change_df[change_df["Significant"] == True]

            key_list = list(change_df["Driver_ID"])
            change_df["Name"] = [driver_lookup[item] for item in key_list]
            names = change_df.pop("Name")
            change_df.insert(0, names.name, names)

            change_df = change_df.drop(columns=["Driver_ID", "Starts", "T_Test", "Significant"])
            change_df = change_df.head(10)

            change_df["T_Statistic"] = change_df.apply(lambda row : '%.10f' % row["T_Statistic"], axis=1)
            change_df["P_Value"] = change_df.apply(lambda row : '%.15f' % row["P_Value"], axis=1)
            print(change_df)
            
            return change_df.to_dict('records'), [{"name": i, "id": i} for i in change_df.columns]
        else:
            change_df = pd.DataFrame()
            return change_df.to_dict('records'), [{"name": i, "id": i} for i in change_df.columns]
    


@app.callback(
    Output("d_eras", "data"),
    Output('d_eras', 'columns'),
    Input('d_era_years', 'value'),
    Input("d_eras_stat", "value"),
    Input('d_eras_filter', 'value'),
    Input('d_eras_sig', 'value'),
)
def update_d_eras(eras, var, race_count, sig_level):
    results_df = pd.read_csv("./data/results.csv")
    results_df = results_df[results_df["grid"].notna()]
    results_df = results_df[results_df["grid"] != 0]
    results_df = results_df[results_df["positionOrder"].notna()]
    results_df = results_df[results_df["positionOrder"] != 0]

    races_df = pd.read_csv("./data/races.csv")

    driver_info = pd.read_pickle("./dataframes/drivers")
    driver_lookup = dict(zip(driver_info['Driver ID'], driver_info['Name']))

    ## Eras:
    # The era of factory Italian and Mercedes front-engine cars (1950–1957)
    era1 = [1950, 1951, 1952, 1953, 1954, 1955, 1956, 1957]
    # British independent specialist teams and the rear-mid engine revolution (1958–1961)
    era2 = [1958, 1959, 1960, 1961]
    # Anglophone drivers and 1.5-litre engines (1962–1967)
    era3 = [1962, 1963, 1964, 1965, 1966, 1967]
    # The DFV engine, 12-cylinder engines and the arrival of sponsorship, safety and aerodynamics (1968–1976)
    era4 = [1968, 1969, 1970, 1971, 1972, 1973, 1974, 1975, 1976]
    # Ground-effect era (1977–1982)
    era5 = [1977, 1978, 1979, 1980, 1981, 1982]
    # 1.5-litre turbo-charged engines (1983–1988)
    era6 = [1983, 1984, 1985, 1986, 1987, 1988]
    # 3.5-litre naturally-aspirated engines, active suspension and electronic driver aids (1989–1993)
    era7 = [1989, 1990, 1991, 1992, 1993]
    # Safety, rules and regulations (1994)
    era8 = [1994]
    # 3-litre engines (1995–1999)
    era9 = [1995, 1996, 1997, 1998, 1999]
    # V10 engines and rise of road car manufacturer participation (2000–2005)
    era10 = [2000, 2001, 2002, 2003, 2004, 2005]
    # 2.4-litre V8 engines (2006–2008)
    era11 = [2006, 2007, 2008]
    # Cost-cutting measures and departure of car manufacturers (2009–2013)
    era12 = [2009, 2010, 2011, 2012, 2013]
    # 1.6-litre turbocharged V6 hybrid power units (2014–2021)
    era13 = [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021]

    if eras == 1:
        year_races = list(races_df.loc[races_df["year"].isin(era1), "raceId"])
    elif eras == 2:
        year_races = list(races_df.loc[races_df["year"].isin(era2), "raceId"])
    elif eras == 3:
        year_races = list(races_df.loc[races_df["year"].isin(era3), "raceId"])
    elif eras == 4:
        year_races = list(races_df.loc[races_df["year"].isin(era4), "raceId"])
    elif eras == 5:
        year_races = list(races_df.loc[races_df["year"].isin(era5), "raceId"])
    elif eras == 6:
        year_races = list(races_df.loc[races_df["year"].isin(era6), "raceId"])
    elif eras == 7:
        year_races = list(races_df.loc[races_df["year"].isin(era7), "raceId"])
    elif eras == 8:
        year_races = list(races_df.loc[races_df["year"].isin(era8), "raceId"])
    elif eras == 9:
        year_races = list(races_df.loc[races_df["year"].isin(era9), "raceId"])
    elif eras == 10:
        year_races = list(races_df.loc[races_df["year"].isin(era10), "raceId"])
    elif eras == 11:
        year_races = list(races_df.loc[races_df["year"].isin(era11), "raceId"])
    elif eras == 12:
        year_races = list(races_df.loc[races_df["year"].isin(era12), "raceId"])
    elif eras == 13:
        year_races = list(races_df.loc[races_df["year"].isin(era13), "raceId"])

    results_df = results_df[results_df["raceId"].isin(year_races)]

    if var == 0:
        drivers = results_df["driverId"]
        drivers = drivers.sort_values()
        drivers = drivers.unique()

        drivers = list(drivers)

        change_df = pd.DataFrame()

        change_lst = []
        gain_loss_list_list = []
        num_races = []

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
        change_df['Gains/Losses'] = gain_loss_list_list
        change_df['Average_Position_Gain/Loss'] = change_lst
        change_df['Races_Counted'] = num_races

        overall_average_change2 = fmean(list(itertools.chain.from_iterable(change_df['Gains/Losses']))) ### Calculating the overall average change by averaging all individual gains/losses
        change_df = change_df[change_df['Races_Counted'] >= race_count] ### Filters out drivers who partipated in less than 5 races

        ### Conducting T Test and Determining if P-Value is Significant
        change_df["T_Test"] = change_df.apply(lambda row : stats.ttest_1samp(row['Gains/Losses'], popmean=overall_average_change2, alternative='greater'), axis=1)
        change_df["T_Statistic"] = change_df["T_Test"].str[0]
        change_df["P_Value"] = change_df["T_Test"].str[1]
        change_df["Significant"] = change_df.apply(lambda row: row["P_Value"] < sig_level, axis=1)

        ### Organizing datafrane
        change_df = change_df.sort_values(by=['Average_Position_Gain/Loss', 'P_Value'], ascending=[False,True])
        if True in change_df["Significant"].values:
            change_df = change_df[change_df["Significant"] == True]

            key_list = list(change_df["Driver_ID"])
            change_df["Name"] = [driver_lookup[item] for item in key_list]
            names = change_df.pop("Name")
            change_df.insert(0, names.name, names)

            change_df = change_df.drop(columns=["Driver_ID", "Gains/Losses", "T_Test", "Significant"])
            change_df = change_df.head(10)

            change_df["T_Statistic"] = change_df.apply(lambda row : '%.10f' % row["T_Statistic"], axis=1)
            change_df["P_Value"] = change_df.apply(lambda row : '%.15f' % row["P_Value"], axis=1)
            print(change_df)
            
            return change_df.to_dict('records'), [{"name": i, "id": i} for i in change_df.columns]
        else:
            change_df = pd.DataFrame()
            return change_df.to_dict('records'), [{"name": i, "id": i} for i in change_df.columns]
    if var == 1:
        drivers = results_df["driverId"]
        drivers = drivers.sort_values()
        drivers = drivers.unique()

        drivers = list(drivers)

        change_df = pd.DataFrame()

        change_lst = []
        finish_list_list = []
        num_races = []

        for i in drivers:
            races = results_df.loc[results_df['driverId'] == i] ### Gets races partipated by driver
            finish_list = list(races["positionOrder"]) ### Lists finishing postitions of driver
            finish_list_list.append(finish_list) ### Sends list of positions gained/lost to list for all drivers
            avg_change = fmean(finish_list) ### Averages list of positions gained/list to find average change
            change_lst.append(avg_change) ### Sends average change to list for all drivers
            num_races.append(races.shape[0]) ### Sends count of races to list for all drivers

        ### Using lists to form dataframe
        change_df['Driver_ID'] = drivers 
        change_df['Finishes'] = finish_list_list
        change_df['Average_Finish_Position'] = change_lst
        change_df['Races_Counted'] = num_races

        overall_average_change2 = fmean(list(itertools.chain.from_iterable(change_df['Finishes']))) ### Calculating the overall average change by averaging all individual gains/losses
        change_df = change_df[change_df['Races_Counted'] >= race_count] ### Filters out drivers who partipated in less than 5 races

        ### Conducting T Test and Determining if P-Value is Significant
        change_df["T_Test"] = change_df.apply(lambda row : stats.ttest_1samp(row['Finishes'], popmean=overall_average_change2, alternative='less'), axis=1)
        change_df["T_Statistic"] = change_df["T_Test"].str[0]
        change_df["P_Value"] = change_df["T_Test"].str[1]
        change_df["Significant"] = change_df.apply(lambda row: row["P_Value"] < sig_level, axis=1)

        ### Organizing datafrane
        change_df = change_df.sort_values(by=['Average_Finish_Position', 'P_Value'], ascending=[True,True])
        if True in change_df["Significant"].values:
            change_df = change_df[change_df["Significant"] == True]

            key_list = list(change_df["Driver_ID"])
            change_df["Name"] = [driver_lookup[item] for item in key_list]
            names = change_df.pop("Name")
            change_df.insert(0, names.name, names)

            change_df = change_df.drop(columns=["Driver_ID", "Finishes", "T_Test", "Significant"])
            change_df = change_df.head(10)

            change_df["T_Statistic"] = change_df.apply(lambda row : '%.10f' % row["T_Statistic"], axis=1)
            change_df["P_Value"] = change_df.apply(lambda row : '%.15f' % row["P_Value"], axis=1)
            print(change_df)
            
            return change_df.to_dict('records'), [{"name": i, "id": i} for i in change_df.columns]
        else:
            change_df = pd.DataFrame()
            return change_df.to_dict('records'), [{"name": i, "id": i} for i in change_df.columns]
    if var == 2:
        drivers = results_df["driverId"]
        drivers = drivers.sort_values()
        drivers = drivers.unique()

        drivers = list(drivers)

        change_df = pd.DataFrame()

        change_lst = []
        start_list_list = []
        num_races = []

        for i in drivers:
            races = results_df.loc[results_df['driverId'] == i] ### Gets races partipated by driver
            start_list = list(races["grid"]) ### Lists finishing postitions of driver
            start_list_list.append(start_list) ### Sends list of positions gained/lost to list for all drivers
            avg_change = fmean(start_list) ### Averages list of positions gained/list to find average change
            change_lst.append(avg_change) ### Sends average change to list for all drivers
            num_races.append(races.shape[0]) ### Sends count of races to list for all drivers

        ### Using lists to form dataframe
        change_df['Driver_ID'] = drivers 
        change_df['Starts'] = start_list_list
        change_df['Average_Start_Position'] = change_lst
        change_df['Races_Counted'] = num_races

        overall_average_change2 = fmean(list(itertools.chain.from_iterable(change_df['Starts']))) ### Calculating the overall average change by averaging all individual gains/losses
        change_df = change_df[change_df['Races_Counted'] >= race_count] ### Filters out drivers who partipated in less than 5 races

        ### Conducting T Test and Determining if P-Value is Significant
        change_df["T_Test"] = change_df.apply(lambda row : stats.ttest_1samp(row['Starts'], popmean=overall_average_change2, alternative='less'), axis=1)
        change_df["T_Statistic"] = change_df["T_Test"].str[0]
        change_df["P_Value"] = change_df["T_Test"].str[1]
        change_df["Significant"] = change_df.apply(lambda row: row["P_Value"] < sig_level, axis=1)

        ### Organizing datafrane
        change_df = change_df.sort_values(by=['Average_Start_Position', 'P_Value'], ascending=[True,True])
        if True in change_df["Significant"].values:
            change_df = change_df[change_df["Significant"] == True]

            key_list = list(change_df["Driver_ID"])
            change_df["Name"] = [driver_lookup[item] for item in key_list]
            names = change_df.pop("Name")
            change_df.insert(0, names.name, names)

            change_df = change_df.drop(columns=["Driver_ID", "Starts", "T_Test", "Significant"])
            change_df = change_df.head(10)

            change_df["T_Statistic"] = change_df.apply(lambda row : '%.10f' % row["T_Statistic"], axis=1)
            change_df["P_Value"] = change_df.apply(lambda row : '%.15f' % row["P_Value"], axis=1)
            print(change_df)
            
            return change_df.to_dict('records'), [{"name": i, "id": i} for i in change_df.columns]
        else:
            change_df = pd.DataFrame()
            return change_df.to_dict('records'), [{"name": i, "id": i} for i in change_df.columns]



@app.callback(
    Output("d_seasons", "data"),
    Output('d_seasons', 'columns'),
    Input('d_years', 'value'),
    Input("d_seasons_stat", "value"),
    Input('d_seasons_filter', 'value'),
    Input('d_seasons_sig', 'value'),
)
def update_d_seasons(seasons, var, race_count, sig_level):
    results_df = pd.read_csv("./data/results.csv")
    results_df = results_df[results_df["grid"].notna()]
    results_df = results_df[results_df["grid"] != 0]
    results_df = results_df[results_df["positionOrder"].notna()]
    results_df = results_df[results_df["positionOrder"] != 0]
    
    races_df = pd.read_csv("./data/races.csv")

    driver_info = pd.read_pickle("./dataframes/drivers")
    driver_lookup = dict(zip(driver_info['Driver ID'], driver_info['Name']))

    year_races = list(races_df.loc[races_df["year"].isin(seasons), "raceId"])
    results_df = results_df[results_df["raceId"].isin(year_races)]

    if var == 0:
        drivers = results_df["driverId"]
        drivers = drivers.sort_values()
        drivers = drivers.unique()

        drivers = list(drivers)

        change_df = pd.DataFrame()

        change_lst = []
        gain_loss_list_list = []
        num_races = []

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
        change_df['Gains/Losses'] = gain_loss_list_list
        change_df['Average_Position_Gain/Loss'] = change_lst
        change_df['Races_Counted'] = num_races

        overall_average_change2 = fmean(list(itertools.chain.from_iterable(change_df['Gains/Losses']))) ### Calculating the overall average change by averaging all individual gains/losses
        change_df = change_df[change_df['Races_Counted'] >= race_count] ### Filters out drivers who partipated in less than 5 races

        ### Conducting T Test and Determining if P-Value is Significant
        change_df["T_Test"] = change_df.apply(lambda row : stats.ttest_1samp(row['Gains/Losses'], popmean=overall_average_change2, alternative='greater'), axis=1)
        change_df["T_Statistic"] = change_df["T_Test"].str[0]
        change_df["P_Value"] = change_df["T_Test"].str[1]
        change_df["Significant"] = change_df.apply(lambda row: row["P_Value"] < sig_level, axis=1)

        ### Organizing datafrane
        change_df = change_df.sort_values(by=['Average_Position_Gain/Loss', 'P_Value'], ascending=[False,True])
        if True in change_df["Significant"].values:
            change_df = change_df[change_df["Significant"] == True]

            key_list = list(change_df["Driver_ID"])
            change_df["Name"] = [driver_lookup[item] for item in key_list]
            names = change_df.pop("Name")
            change_df.insert(0, names.name, names)

            change_df = change_df.drop(columns=["Driver_ID", "Gains/Losses", "T_Test", "Significant"])
            change_df = change_df.head(10)

            change_df["T_Statistic"] = change_df.apply(lambda row : '%.10f' % row["T_Statistic"], axis=1)
            change_df["P_Value"] = change_df.apply(lambda row : '%.15f' % row["P_Value"], axis=1)
            print(change_df)
            
            return change_df.to_dict('records'), [{"name": i, "id": i} for i in change_df.columns]
        else:
            change_df = pd.DataFrame()
            return change_df.to_dict('records'), [{"name": i, "id": i} for i in change_df.columns]
    if var == 1:
        drivers = results_df["driverId"]
        drivers = drivers.sort_values()
        drivers = drivers.unique()

        drivers = list(drivers)

        change_df = pd.DataFrame()

        change_lst = []
        finish_list_list = []
        num_races = []

        for i in drivers:
            races = results_df.loc[results_df['driverId'] == i] ### Gets races partipated by driver
            finish_list = list(races["positionOrder"]) ### Lists finishing postitions of driver
            finish_list_list.append(finish_list) ### Sends list of positions gained/lost to list for all drivers
            avg_change = fmean(finish_list) ### Averages list of positions gained/list to find average change
            change_lst.append(avg_change) ### Sends average change to list for all drivers
            num_races.append(races.shape[0]) ### Sends count of races to list for all drivers

        ### Using lists to form dataframe
        change_df['Driver_ID'] = drivers 
        change_df['Finishes'] = finish_list_list
        change_df['Average_Finish_Position'] = change_lst
        change_df['Races_Counted'] = num_races

        overall_average_change2 = fmean(list(itertools.chain.from_iterable(change_df['Finishes']))) ### Calculating the overall average change by averaging all individual gains/losses
        change_df = change_df[change_df['Races_Counted'] >= race_count] ### Filters out drivers who partipated in less than 5 races

        ### Conducting T Test and Determining if P-Value is Significant
        change_df["T_Test"] = change_df.apply(lambda row : stats.ttest_1samp(row['Finishes'], popmean=overall_average_change2, alternative='less'), axis=1)
        change_df["T_Statistic"] = change_df["T_Test"].str[0]
        change_df["P_Value"] = change_df["T_Test"].str[1]
        change_df["Significant"] = change_df.apply(lambda row: row["P_Value"] < sig_level, axis=1)

        ### Organizing datafrane
        change_df = change_df.sort_values(by=['Average_Finish_Position', 'P_Value'], ascending=[True,True])
        if True in change_df["Significant"].values:
            change_df = change_df[change_df["Significant"] == True]

            key_list = list(change_df["Driver_ID"])
            change_df["Name"] = [driver_lookup[item] for item in key_list]
            names = change_df.pop("Name")
            change_df.insert(0, names.name, names)

            change_df = change_df.drop(columns=["Driver_ID", "Finishes", "T_Test", "Significant"])
            change_df = change_df.head(10)

            change_df["T_Statistic"] = change_df.apply(lambda row : '%.10f' % row["T_Statistic"], axis=1)
            change_df["P_Value"] = change_df.apply(lambda row : '%.15f' % row["P_Value"], axis=1)
            print(change_df)
            
            return change_df.to_dict('records'), [{"name": i, "id": i} for i in change_df.columns]
        else:
            change_df = pd.DataFrame()
            return change_df.to_dict('records'), [{"name": i, "id": i} for i in change_df.columns]
    if var == 2:
        drivers = results_df["driverId"]
        drivers = drivers.sort_values()
        drivers = drivers.unique()

        drivers = list(drivers)

        change_df = pd.DataFrame()

        change_lst = []
        start_list_list = []
        num_races = []

        for i in drivers:
            races = results_df.loc[results_df['driverId'] == i] ### Gets races partipated by driver
            start_list = list(races["grid"]) ### Lists finishing postitions of driver
            start_list_list.append(start_list) ### Sends list of positions gained/lost to list for all drivers
            avg_change = fmean(start_list) ### Averages list of positions gained/list to find average change
            change_lst.append(avg_change) ### Sends average change to list for all drivers
            num_races.append(races.shape[0]) ### Sends count of races to list for all drivers

        ### Using lists to form dataframe
        change_df['Driver_ID'] = drivers 
        change_df['Starts'] = start_list_list
        change_df['Average_Start_Position'] = change_lst
        change_df['Races_Counted'] = num_races

        overall_average_change2 = fmean(list(itertools.chain.from_iterable(change_df['Starts']))) ### Calculating the overall average change by averaging all individual gains/losses
        change_df = change_df[change_df['Races_Counted'] >= race_count] ### Filters out drivers who partipated in less than 5 races

        ### Conducting T Test and Determining if P-Value is Significant
        change_df["T_Test"] = change_df.apply(lambda row : stats.ttest_1samp(row['Starts'], popmean=overall_average_change2, alternative='less'), axis=1)
        change_df["T_Statistic"] = change_df["T_Test"].str[0]
        change_df["P_Value"] = change_df["T_Test"].str[1]
        change_df["Significant"] = change_df.apply(lambda row: row["P_Value"] < sig_level, axis=1)

        ### Organizing datafrane
        change_df = change_df.sort_values(by=['Average_Start_Position', 'P_Value'], ascending=[True,True])
        if True in change_df["Significant"].values:
            change_df = change_df[change_df["Significant"] == True]

            key_list = list(change_df["Driver_ID"])
            change_df["Name"] = [driver_lookup[item] for item in key_list]
            names = change_df.pop("Name")
            change_df.insert(0, names.name, names)

            change_df = change_df.drop(columns=["Driver_ID", "Starts", "T_Test", "Significant"])
            change_df = change_df.head(10)

            change_df["T_Statistic"] = change_df.apply(lambda row : '%.10f' % row["T_Statistic"], axis=1)
            change_df["P_Value"] = change_df.apply(lambda row : '%.15f' % row["P_Value"], axis=1)
            print(change_df)
            
            return change_df.to_dict('records'), [{"name": i, "id": i} for i in change_df.columns]
        else:
            change_df = pd.DataFrame()
            return change_df.to_dict('records'), [{"name": i, "id": i} for i in change_df.columns]


@app.callback(
    Output("t", "data"),
    Output('t', 'columns'),
    Input('t_years', 'value'),
    Input("t_stat", "value"),
    Input('t_sig', 'value'),
)
def update_t(seasons, var, sig_level):
    results_df = pd.read_csv("./data/results.csv")
    results_df = results_df[results_df["grid"].notna()]
    results_df = results_df[results_df["grid"] != 0]
    results_df = results_df[results_df["positionOrder"].notna()]
    results_df = results_df[results_df["positionOrder"] != 0]
    
    races_df = pd.read_csv("./data/races.csv")

    driver_info = pd.read_pickle("./dataframes/drivers")
    driver_lookup = dict(zip(driver_info['Driver ID'], driver_info['Name']))

    constructor_info = pd.read_pickle("./dataframes/constructors")
    constructor_lookup = dict(zip(constructor_info['Constructor ID'], constructor_info['Name']))

    year_races = list(races_df.loc[races_df["year"] == seasons, "raceId"])
    results_df = results_df[results_df["raceId"].isin(year_races)]

    if var == 0:
        constructors = results_df["constructorId"]
        constructors = constructors.sort_values()
        constructors = constructors.unique()

        constructors = list(constructors)

        drivers = results_df["driverId"]
        drivers = drivers.sort_values()
        drivers = drivers.unique()

        drivers = list(drivers)

        df = pd.DataFrame()


        for x in constructors:
            drivers = results_df.loc[results_df["constructorId"] == x, 'driverId']
            drivers = drivers.sort_values()
            drivers = drivers.unique()

            drivers = list(drivers)

            change_df = pd.DataFrame()

            change_lst = []
            gain_loss_list_list = []
            num_races = []

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
            change_df['Gains/Losses'] = gain_loss_list_list
            change_df['Average_Position_Gain/Loss'] = change_lst
            change_df['Races_Counted'] = num_races

            change_df = change_df.sort_values(by=["Races_Counted","Average_Position_Gain/Loss"], ascending=[False,False])
            change_df = change_df[change_df['Races_Counted'] > 1]
            change_df = change_df.head(2)
            change_df = change_df.sort_values(by=["Average_Position_Gain/Loss", "Races_Counted"], ascending=[False,False])

            if change_df.shape[0] < 2:
                pass
            else:
                change1 = change_df.iloc[0]["Gains/Losses"]
                change2 = change_df.iloc[1]["Gains/Losses"]

                var1, var2 = np.var(change1), np.var(change2)

                if var1 > var2:
                    var_ratio = var1/var2
                elif var2 > var1:
                    var_ratio = var2/var1
                else:
                    var_ratio = 1

                if var_ratio < 4:
                    t_test = stats.ttest_ind(change1, change2, equal_var=True)
                elif var_ratio > 4:
                    t_test = stats.ttest_ind(change1, change2, equal_var=False)

                change_df["T_Statistic"] = t_test[0]
                change_df["P_Value"] = t_test[1]

                change_df["Significant"] = change_df.apply(lambda row: row["P_Value"] < sig_level, axis=1)
                change_df["Better_Than_Teammate?"] = ""
                
                change_df = change_df.reset_index(drop=True)

                if True in change_df["Significant"].values:
                    change_df["Better_Than_Teammate?"].loc[0] = True
                    change_df["Better_Than_Teammate?"].loc[1] = False
                else:
                    change_df["Better_Than_Teammate?"].loc[0] = False
                    change_df["Better_Than_Teammate?"].loc[1] = False


                ### Organizing datafrane
                change_df = change_df.sort_values(by=['Average_Position_Gain/Loss', 'P_Value'], ascending=[False,True])

                key_list = list(change_df["Driver_ID"])
                change_df["Driver"] = [driver_lookup[item] for item in key_list]
                key_list = list(change_df["Constructor_ID"])
                change_df["Constructor"] = [constructor_lookup[item] for item in key_list]

                names = change_df.pop("Driver")
                change_df.insert(0, names.name, names)
                names = change_df.pop("Constructor")
                change_df.insert(0, names.name, names)

                change_df = change_df.drop(columns=["Driver_ID", "Constructor_ID", "Gains/Losses", "Significant"])

                df = pd.concat([df, change_df])
        
        print(df)
        return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns]
    if var == 1:
        constructors = results_df["constructorId"]
        constructors = constructors.sort_values()
        constructors = constructors.unique()

        constructors = list(constructors)

        drivers = results_df["driverId"]
        drivers = drivers.sort_values()
        drivers = drivers.unique()

        drivers = list(drivers)

        df = pd.DataFrame()


        for x in constructors:
            drivers = results_df.loc[results_df["constructorId"] == x, 'driverId']
            drivers = drivers.sort_values()
            drivers = drivers.unique()

            drivers = list(drivers)

            change_df = pd.DataFrame()

            change_lst = []
            gain_loss_list_list = []
            num_races = []

            for i in drivers:
                races = results_df.loc[results_df['driverId'] == i] ### Gets races partipated by driver
                finish_list = list(races["positionOrder"]) ### Lists finishing postitions of driver
                gain_loss_list_list.append(finish_list) ### Sends list of positions gained/lost to list for all drivers
                avg_change = fmean(finish_list) ### Averages list of positions gained/list to find average change
                change_lst.append(avg_change) ### Sends average change to list for all drivers
                num_races.append(races.shape[0]) ### Sends count of races to list for all drivers


            ### Using lists to form dataframe
            change_df['Driver_ID'] = drivers
            change_df["Constructor_ID"] = x 
            change_df['Finishes'] = gain_loss_list_list
            change_df['Average_Finish_Position'] = change_lst
            change_df['Races_Counted'] = num_races

            change_df = change_df.sort_values(by=["Races_Counted","Average_Finish_Position"], ascending=[False,True])
            change_df = change_df[change_df['Races_Counted'] > 1]
            change_df = change_df.head(2)
            change_df = change_df.sort_values(by=["Average_Finish_Position", "Races_Counted"], ascending=[True,False])

            if change_df.shape[0] < 2:
                pass
            else:
                change1 = change_df.iloc[0]["Finishes"]
                change2 = change_df.iloc[1]["Finishes"]

                var1, var2 = np.var(change1), np.var(change2)

                if var1 > var2:
                    var_ratio = var1/var2
                elif var2 > var1:
                    var_ratio = var2/var1
                else:
                    var_ratio = 1

                if var_ratio < 4:
                    t_test = stats.ttest_ind(change1, change2, equal_var=True)
                elif var_ratio > 4:
                    t_test = stats.ttest_ind(change1, change2, equal_var=False)

                change_df["T_Statistic"] = t_test[0]
                change_df["P_Value"] = t_test[1]

                change_df["Significant"] = change_df.apply(lambda row: row["P_Value"] < sig_level, axis=1)
                change_df["Better_Than_Teammate?"] = ""
                
                change_df = change_df.reset_index(drop=True)

                if True in change_df["Significant"].values:
                    change_df["Better_Than_Teammate?"].loc[0] = True
                    change_df["Better_Than_Teammate?"].loc[1] = False
                else:
                    change_df["Better_Than_Teammate?"].loc[0] = False
                    change_df["Better_Than_Teammate?"].loc[1] = False


                ### Organizing datafrane
                change_df = change_df.sort_values(by=['Average_Finish_Position', 'P_Value'], ascending=[True,True])

                key_list = list(change_df["Driver_ID"])
                change_df["Driver"] = [driver_lookup[item] for item in key_list]
                key_list = list(change_df["Constructor_ID"])
                change_df["Constructor"] = [constructor_lookup[item] for item in key_list]

                names = change_df.pop("Driver")
                change_df.insert(0, names.name, names)
                names = change_df.pop("Constructor")
                change_df.insert(0, names.name, names)

                change_df = change_df.drop(columns=["Driver_ID", "Constructor_ID", "Finishes", "Significant"])

                df = pd.concat([df, change_df])
        
        print(df)
        return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns]
    if var == 2:
        constructors = results_df["constructorId"]
        constructors = constructors.sort_values()
        constructors = constructors.unique()

        constructors = list(constructors)

        drivers = results_df["driverId"]
        drivers = drivers.sort_values()
        drivers = drivers.unique()

        drivers = list(drivers)

        df = pd.DataFrame()


        for x in constructors:
            drivers = results_df.loc[results_df["constructorId"] == x, 'driverId']
            drivers = drivers.sort_values()
            drivers = drivers.unique()

            drivers = list(drivers)

            change_df = pd.DataFrame()

            change_lst = []
            gain_loss_list_list = []
            num_races = []

            for i in drivers:
                races = results_df.loc[results_df['driverId'] == i] ### Gets races partipated by driver
                finish_list = list(races["grid"]) ### Lists finishing postitions of driver
                gain_loss_list_list.append(finish_list) ### Sends list of positions gained/lost to list for all drivers
                avg_change = fmean(finish_list) ### Averages list of positions gained/list to find average change
                change_lst.append(avg_change) ### Sends average change to list for all drivers
                num_races.append(races.shape[0]) ### Sends count of races to list for all drivers


            ### Using lists to form dataframe
            change_df['Driver_ID'] = drivers
            change_df["Constructor_ID"] = x 
            change_df['Starts'] = gain_loss_list_list
            change_df['Average_Start_Position'] = change_lst
            change_df['Races_Counted'] = num_races

            change_df = change_df.sort_values(by=["Races_Counted","Average_Start_Position"], ascending=[False,True])
            change_df = change_df[change_df['Races_Counted'] > 1]
            change_df = change_df.head(2)
            change_df = change_df.sort_values(by=["Average_Start_Position", "Races_Counted"], ascending=[True,False])

            if change_df.shape[0] < 2:
                pass
            else:
                change1 = change_df.iloc[0]["Starts"]
                change2 = change_df.iloc[1]["Starts"]

                var1, var2 = np.var(change1), np.var(change2)

                if var1 > var2:
                    var_ratio = var1/var2
                elif var2 > var1:
                    var_ratio = var2/var1
                else:
                    var_ratio = 1

                if var_ratio < 4:
                    t_test = stats.ttest_ind(change1, change2, equal_var=True)
                elif var_ratio > 4:
                    t_test = stats.ttest_ind(change1, change2, equal_var=False)

                change_df["T_Statistic"] = t_test[0]
                change_df["P_Value"] = t_test[1]

                change_df["Significant"] = change_df.apply(lambda row: row["P_Value"] < sig_level, axis=1)
                change_df["Better_Than_Teammate?"] = ""
                
                change_df = change_df.reset_index(drop=True)

                if True in change_df["Significant"].values:
                    change_df["Better_Than_Teammate?"].loc[0] = True
                    change_df["Better_Than_Teammate?"].loc[1] = False
                else:
                    change_df["Better_Than_Teammate?"].loc[0] = False
                    change_df["Better_Than_Teammate?"].loc[1] = False


                ### Organizing datafrane
                change_df = change_df.sort_values(by=['Average_Start_Position', 'P_Value'], ascending=[True,True])

                key_list = list(change_df["Driver_ID"])
                change_df["Driver"] = [driver_lookup[item] for item in key_list]
                key_list = list(change_df["Constructor_ID"])
                change_df["Constructor"] = [constructor_lookup[item] for item in key_list]

                names = change_df.pop("Driver")
                change_df.insert(0, names.name, names)
                names = change_df.pop("Constructor")
                change_df.insert(0, names.name, names)

                change_df = change_df.drop(columns=["Driver_ID", "Constructor_ID", "Starts", "Significant"])

                df = pd.concat([df, change_df])
        
        print(df)
        return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns]




if __name__ == '__main__':
    app.run_server(debug=True)