import sqlite3
import pandas as pd
import os
import glob
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
import warnings
warnings.filterwarnings('ignore')

# conect to SQLite databse
con = sqlite3.connect("dataverse_db.sqlite")

# load all csv and bz2 files into the databse
folder = "../../Data"
csv_files = glob.glob(os.path.join(folder, "*.csv"))
bz2_files = glob.glob(os.path.join(folder, "*.bz2"))

# import csv files
for file in csv_files:
    table_name = os.path.splitext(os.path.basename(file))[0]
    print(f"Importing CSV: {file}")
    df = pd.read_csv(file)
    df.to_sql(table_name, con, if_exists='replace', index=False)

# import bz2 files
for file in bz2_files:
    table_name = os.path.splitext(os.path.basename(file))[0]
    print(f"Importing BZ2: {file}")
    df = pd.read_csv(file, compression='bz2')
    df.to_sql(table_name, con, if_exists='replace', index=False)

# Question A: best times and days to minimze delays
query_avg_delays = """SELECT
	agg.avg_depDelay,
	agg.avg_arrDelay,
	agg.avg_carrierDelay,
	agg.avg_weatherDelay,
	agg.avg_nasDelay,
	agg.avg_securityDelay,
	agg.avg_lateAircraftDelay,
	(
		agg.avg_depDelay +
		agg.avg_arrDelay +
		agg.avg_carrierDelay +
		agg.avg_weatherDelay +
		agg.avg_nasDelay +
		agg.avg_securityDelay +
		agg.avg_lateAircraftDelay
	) / 7 AS total_avg_delay
FROM (
SELECT
	f.DayOfWeek,
	AVG(f.DepDelay) AS avg_depDelay,
	AVG(f.ArrDelay) AS avg_arrDelay,
	AVG(f.CarrierDelay) AS avg_carrierDelay,
	AVG(f.WeatherDelay) AS avg_weatherDelay,
	AVG(f.NASDelay) AS avg_nasDelay,
	AVG(f.SecurityDelay) AS avg_securityDelay,
	AVG(f.LateAircraftDelay) AS avg_lateAircraftDelay
FROM (
	SELECT
		DayOfWeek,
		DepDelay,
		ArrDelay,
		CarrierDelay,
		WeatherDelay,
		NASDelay,
		SecurityDelay,
		LateAircraftDelay,
		Diverted,
		Cancelled FROM '2004.csv'
	UNION ALL
	SELECT
		DayOfWeek,
		DepDelay,
		ArrDelay,
		CarrierDelay,
		WeatherDelay,
		NASDelay,
		SecurityDelay,
		LateAircraftDelay,
		Diverted,
		Cancelled FROM '2005.csv'
	UNION ALL
	SELECT
		DayOfWeek,
		DepDelay,
		ArrDelay,
		CarrierDelay,
		WeatherDelay,
		NASDelay,
		SecurityDelay,
		LateAircraftDelay,
		Diverted,
		Cancelled FROM '2006.csv'
	UNION ALL
	SELECT
		DayOfWeek,
		DepDelay,
		ArrDelay,
		CarrierDelay,
		WeatherDelay,
		NASDelay,
		SecurityDelay,
		LateAircraftDelay,
		Diverted,
		Cancelled FROM '2007.csv'
	UNION ALL
	SELECT
		DayOfWeek,
		DepDelay,
		ArrDelay,
		CarrierDelay,
		WeatherDelay,
		NASDelay,
		SecurityDelay,
		LateAircraftDelay,
		Diverted,
		Cancelled FROM '2008.csv'
	) AS f
	WHERE f.Cancelled = 0
	AND f.Diverted = 0
Group BY f.DayOfWeek
) AS agg
Order BY agg.DayOfWeek"""

ex = pd.read_sql_query(query_avg_delays, con)
print("Average delays by day of week:")
print(ex)

# positve delays only (excluding early arrivls/departures)
query_positive_delays = """SELECT
	agg.avg_depDelay,
	agg.avg_arrDelay,
	agg.avg_carrierDelay,
	agg.avg_weatherDelay,
	agg.avg_nasDelay,
	agg.avg_securityDelay,
	agg.avg_lateAircraftDelay,
	(
		agg.avg_depDelay +
		agg.avg_arrDelay +
		agg.avg_carrierDelay +
		agg.avg_weatherDelay +
		agg.avg_nasDelay +
		agg.avg_securityDelay +
		agg.avg_lateAircraftDelay
	) / 7 AS total_avg_delay
FROM (
SELECT
	f.DayOfWeek,
	AVG(
		CASE
			WHEN f.DepDelay > 0
			THEN f.DepDelay
			ELSE NULL
		END
		) AS avg_depDelay,
	AVG(
		CASE
			WHEN f.ArrDelay > 0
			THEN f.ArrDelay
			ELSE NULL
		END
		) AS avg_arrDelay,
	AVG(
		CASE
			WHEN f.CarrierDelay > 0
			THEN f.CarrierDelay
			ELSE NULL
		END
		) AS avg_carrierDelay,
	AVG(
		CASE
			WHEN f.WeatherDelay > 0
			THEN f.WeatherDelay
			ELSE NULL
		END
		) AS avg_weatherDelay,
	AVG(
		CASE
			WHEN f.NASDelay > 0
			THEN f.NASDelay
			ELSE NULL
		END
		) AS avg_nasDelay,
	AVG(
		CASE
			WHEN f.SecurityDelay > 0
			THEN f.SecurityDelay
			ELSE NULL
		END
		) AS avg_securityDelay,
	AVG(
		CASE
			WHEN f.LateAircraftDelay > 0
			THEN f.LateAircraftDelay
			ELSE NULL
		END
		) AS avg_lateAircraftDelay
FROM (
	SELECT
		DayOfWeek,
		DepDelay,
		ArrDelay,
		CarrierDelay,
		WeatherDelay,
		NASDelay,
		SecurityDelay,
		LateAircraftDelay,
		Diverted,
		Cancelled FROM '2004.csv'
	UNION ALL
	SELECT
		DayOfWeek,
		DepDelay,
		ArrDelay,
		CarrierDelay,
		WeatherDelay,
		NASDelay,
		SecurityDelay,
		LateAircraftDelay,
		Diverted,
		Cancelled FROM '2005.csv'
	UNION ALL
	SELECT
		DayOfWeek,
		DepDelay,
		ArrDelay,
		CarrierDelay,
		WeatherDelay,
		NASDelay,
		SecurityDelay,
		LateAircraftDelay,
		Diverted,
		Cancelled FROM '2006.csv'
	UNION ALL
	SELECT
		DayOfWeek,
		DepDelay,
		ArrDelay,
		CarrierDelay,
		WeatherDelay,
		NASDelay,
		SecurityDelay,
		LateAircraftDelay,
		Diverted,
		Cancelled FROM '2007.csv'
	UNION ALL
	SELECT
		DayOfWeek,
		DepDelay,
		ArrDelay,
		CarrierDelay,
		WeatherDelay,
		NASDelay,
		SecurityDelay,
		LateAircraftDelay,
		Diverted,
		Cancelled FROM '2008.csv'
	) AS f
	WHERE f.Cancelled = 0
	AND f.Diverted = 0
Group BY f.DayOfWeek
) AS agg
Order BY agg.DayOfWeek"""

positive_delays = pd.read_sql_query(query_positive_delays, con)
print("Positive delays only by day of week:")
print(positive_delays)

# Question B: old vs new planes (20+ years = old)
query_plane_age = """SELECT
	agg.plane_age_group,
	agg.avg_depDelay,
	agg.avg_arrDelay,
	agg.avg_carrierDelay,
	agg.avg_weatherDelay,
	agg.avg_nasDelay,
	agg.avg_securityDelay,
	agg.avg_lateAircraftDelay,
	(
		agg.avg_depDelay +
		agg.avg_arrDelay +
		agg.avg_carrierDelay +
		agg.avg_weatherDelay +
		agg.avg_nasDelay +
		agg.avg_securityDelay +
		agg.avg_lateAircraftDelay
	) / 7 AS total_avg_delay
FROM (
SELECT
	CASE
		WHEN (f.Year - p.Year) < 20
		THEN 'newPlane'
		ELSE 'oldPlane'
	END AS plane_age_group,
	AVG(f.DepDelay) AS avg_depDelay,
	AVG(f.ArrDelay) AS avg_arrDelay,
	AVG(f.CarrierDelay) AS avg_carrierDelay,
	AVG(f.WeatherDelay) AS avg_weatherDelay,
	AVG(f.NASDelay) AS avg_nasDelay,
	AVG(f.SecurityDelay) AS avg_securityDelay,
	AVG(f.LateAircraftDelay) AS avg_lateAircraftDelay
FROM (
	SELECT
		Year,
		TailNum,
		ArrDelay,
		DepDelay,
		CarrierDelay,
		WeatherDelay,
		NASDelay,
		SecurityDelay,
		LateAircraftDelay,
		Diverted,
		Cancelled FROM '2004.csv'
	UNION ALL
	SELECT
		Year,
		TailNum,
		DepDelay,
		ArrDelay,
		CarrierDelay,
		WeatherDelay,
		NASDelay,
		SecurityDelay,
		LateAircraftDelay,
		Diverted,
		Cancelled FROM '2005.csv'
	UNION ALL
	SELECT
		Year,
		TailNum,
		DepDelay,
		ArrDelay,
		CarrierDelay,
		WeatherDelay,
		NASDelay,
		SecurityDelay,
		LateAircraftDelay,
		Diverted,
		Cancelled FROM '2006.csv'
	UNION ALL
	SELECT
		Year,
		TailNum,
		DepDelay,
		ArrDelay,
		CarrierDelay,
		WeatherDelay,
		NASDelay,
		SecurityDelay,
		LateAircraftDelay,
		Diverted,
		Cancelled FROM '2007.csv'
	UNION ALL
	SELECT
		Year,
		TailNum,
		DepDelay,
		ArrDelay,
		CarrierDelay,
		WeatherDelay,
		NASDelay,
		SecurityDelay,
		LateAircraftDelay,
		Diverted,
		Cancelled FROM '2008.csv'
	) AS f
	LEFT JOIN (
		SELECT tailnum, Year
		FROM 'plane-data'
		) AS p
	ON f.TailNum = p.tailnum
	WHERE f.Cancelled = 0
	AND f.Diverted = 0
Group BY plane_age_group
) AS agg
Order BY agg.plane_age_group"""

avg_delays_plane_age = pd.read_sql_query(query_plane_age, con)
print("Average delays by plane age:")
print(avg_delays_plane_age)

# postive delays for plane age
query_positive_plane_age = """SELECT
	agg.plane_age_group,
	agg.avg_depDelay,
	agg.avg_arrDelay,
	agg.avg_carrierDelay,
	agg.avg_weatherDelay,
	agg.avg_nasDelay,
	agg.avg_securityDelay,
	agg.avg_lateAircraftDelay,
	(
		agg.avg_depDelay +
		agg.avg_arrDelay +
		agg.avg_carrierDelay +
		agg.avg_weatherDelay +
		agg.avg_nasDelay +
		agg.avg_securityDelay +
		agg.avg_lateAircraftDelay
	) / 7 AS total_avg_delay
FROM (
SELECT
	CASE
		WHEN (f.Year - p.Year) < 20
		THEN 'newPlane'
		ELSE 'oldPlane'
	END AS plane_age_group,
	AVG(
		CASE
			WHEN f.DepDelay > 0
			THEN f.DepDelay
			ELSE NULL
		END
		) AS avg_depDelay,
	AVG(
		CASE
			WHEN f.ArrDelay > 0
			THEN f.ArrDelay
			ELSE NULL
		END
		) AS avg_arrDelay,
	AVG(
		CASE
			WHEN f.CarrierDelay > 0
			THEN f.CarrierDelay
			ELSE NULL
		END
		) AS avg_carrierDelay,
	AVG(
		CASE
			WHEN f.WeatherDelay > 0
			THEN f.WeatherDelay
			ELSE NULL
		END
		) AS avg_weatherDelay,
	AVG(
		CASE
			WHEN f.NASDelay > 0
			THEN f.NASDelay
			ELSE NULL
		END
		) AS avg_nasDelay,
	AVG(
		CASE
			WHEN f.SecurityDelay > 0
			THEN f.SecurityDelay
			ELSE NULL
		END
		) AS avg_securityDelay,
	AVG(
		CASE
			WHEN f.LateAircraftDelay > 0
			THEN f.LateAircraftDelay
			ELSE NULL
		END
		) AS avg_lateAircraftDelay
FROM (
	SELECT
		Year,
		TailNum,
		ArrDelay,
		DepDelay,
		CarrierDelay,
		WeatherDelay,
		NASDelay,
		SecurityDelay,
		LateAircraftDelay,
		Diverted,
		Cancelled FROM '2004.csv'
	UNION ALL
	SELECT
		Year,
		TailNum,
		DepDelay,
		ArrDelay,
		CarrierDelay,
		WeatherDelay,
		NASDelay,
		SecurityDelay,
		LateAircraftDelay,
		Diverted,
		Cancelled FROM '2005.csv'
	UNION ALL
	SELECT
		Year,
		TailNum,
		DepDelay,
		ArrDelay,
		CarrierDelay,
		WeatherDelay,
		NASDelay,
		SecurityDelay,
		LateAircraftDelay,
		Diverted,
		Cancelled FROM '2006.csv'
	UNION ALL
	SELECT
		Year,
		TailNum,
		DepDelay,
		ArrDelay,
		CarrierDelay,
		WeatherDelay,
		NASDelay,
		SecurityDelay,
		LateAircraftDelay,
		Diverted,
		Cancelled FROM '2007.csv'
	UNION ALL
	SELECT
		Year,
		TailNum,
		DepDelay,
		ArrDelay,
		CarrierDelay,
		WeatherDelay,
		NASDelay,
		SecurityDelay,
		LateAircraftDelay,
		Diverted,
		Cancelled FROM '2008.csv'
	) AS f
	LEFT JOIN (
		SELECT tailnum, Year
		FROM 'plane-data'
		) AS p
	ON f.TailNum = p.tailnum
	WHERE f.Cancelled = 0
	AND f.Diverted = 0
Group BY plane_age_group
) AS agg
Order BY agg.plane_age_group"""

positive_delays_plane_age = pd.read_sql_query(query_positive_plane_age, con)
print("Positive delays by plane age:")
print(positive_delays_plane_age)

# Question C: logistc regression model for diverted flights
carriers = pd.read_sql_query("SELECT Code, Description FROM carriers", con)
airports = pd.read_sql_query("SELECT iata, airport, lat, long FROM airports", con)

# logic regression model for diverted flights
def prepare_year_data(year, con, carriers, airports):
    """prepair data for a given year with sampling and feature enginering"""
    table_name = f"{year}.csv"
    
    query = f"SELECT * FROM '{table_name}' WHERE Cancelled = 0"
    flights_tmp = pd.read_sql_query(query, con)
    
    # sample 10% for speed
    flights_sampled = flights_tmp.sample(frac=0.10, random_state=123)
    
    # join carrier names
    flights_joined = flights_sampled.merge(
        carriers, left_on='UniqueCarrier', right_on='Code', how='left'
    ).rename(columns={'Description': 'CarrierName'})
    
    # join origin airport coords
    flights_joined = flights_joined.merge(
        airports, left_on='Origin', right_on='iata', how='left', suffixes=('', '_origin')
    ).rename(columns={
        'airport': 'OriginAirport',
        'lat': 'OriginLat',
        'long': 'OriginLong'
    })
    
    # join dest airport coords
    flights_joined = flights_joined.merge(
        airports, left_on='Dest', right_on='iata', how='left', suffixes=('', '_dest')
    ).rename(columns={
        'airport': 'DestAirport',
        'lat': 'DestLat',
        'long': 'DestLong'
    })
    
    # convert day of week to names
    day_map = {1: 'Mon', 2: 'Tue', 3: 'Wed', 4: 'Thur', 5: 'Fri', 6: 'Sat', 7: 'Sun'}
    flights_joined['DayOfWeek'] = flights_joined['DayOfWeek'].map(day_map)
    
    # convert month to names
    month_map = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 
                 6: 'June', 7: 'July', 8: 'August', 9: 'September', 
                 10: 'October', 11: 'November', 12: 'December'}
    flights_joined['Month'] = flights_joined['Month'].map(month_map)
    
    # feature enginering - extract hour from time
    flights_joined['CRSDepHour'] = flights_joined['CRSDepTime'].apply(
        lambda x: np.floor(x/100) if pd.notna(x) else np.nan
    )
    flights_joined['CRSArrHour'] = flights_joined['CRSArrTime'].apply(
        lambda x: np.floor(x/100) if pd.notna(x) else np.nan
    )
    
    # select relevent columns
    model_data = flights_joined[[
        'Diverted', 'Month', 'DayOfWeek', 'CRSDepHour', 'CRSArrHour',
        'CarrierName', 'Distance', 'WeatherDelay',
        'OriginLat', 'OriginLong', 'DestLat', 'DestLong'
    ]].copy()
    
    model_data['Year'] = year
    model_data = model_data.dropna()
    
    return model_data

# fit logistc regression for each year
years = [2004, 2005, 2006, 2007, 2008]
all_coefs = []

for year in years:
    print(f"Processing year: {year}")
	
    #call func to get data for each individual year
    model_data = prepare_year_data(year, con, carriers, airports)
    
    # prepare features and target
    X = pd.get_dummies(model_data.drop(['Diverted', 'Year'], axis=1), drop_first=True)
    y = model_data['Diverted']
    
    # check if we have both classes
    if len(y.unique()) < 2:
        print(f"Skipping {year} - insufficent class variaton in sample")
        continue
    
    # fit logistc regression
    model = LogisticRegression(max_iter=1000, random_state=123)
    model.fit(X, y)
    
    # get coeficients
    coef_df = pd.DataFrame({
        'term': X.columns,
        'estimate': model.coef_[0],
        'Year': year
    })
    
    all_coefs.append(coef_df)
    
    print(f"Model fitted for {year} with {len(X.columns)} features")

# combine all coeficients
coef_combined = pd.concat(all_coefs, ignore_index=True)

# clean up term names for better readabilty
coef_combined['term_clean'] = coef_combined['term'].str.replace('Month_', 'Month: ')
coef_combined['term_clean'] = coef_combined['term_clean'].str.replace('DayOfWeek_', 'Day: ')
coef_combined['term_clean'] = coef_combined['term_clean'].str.replace('CarrierName_', 'Carrier: ')

# create seperate plot for each year
for year in years:
    year_data = coef_combined[coef_combined['Year'] == year].copy()
    year_data = year_data.sort_values('estimate', key=abs, ascending=False)
    
    plt.figure(figsize=(10, 12))
    plt.barh(range(len(year_data)), year_data['estimate'], color='steelblue')
    plt.yticks(range(len(year_data)), year_data['term_clean'], fontsize=8)
    plt.xlabel('Coefficient Estimte')
    plt.ylabel('Feature')
    plt.title(f'Logistic Regression Coefficents for Diverted Flights - {year}\n' +
              'Features: Month, Day, Carrier, Times, Distance, Weather, Coordinates (10% sample)')
    plt.tight_layout()
    plt.savefig(f'coef_plot_{year}.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved plot for {year}")

# create comparision plot showing trends accross years
plt.figure(figsize=(14, 8))
for term in coef_combined['term_clean'].unique():
    term_data = coef_combined[coef_combined['term_clean'] == term]
    plt.plot(term_data['Year'], term_data['estimate'], marker='o', alpha=0.6, label=term)

plt.xlabel('Year')
plt.ylabel('Coefficient Estimte')
plt.title('Coefficient Trends Across Years (2004-2008)\nHow each feature\'s impact changes over time')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=6)
plt.xticks(years)
plt.tight_layout()
plt.savefig('coef_trends.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved trends plot")

# disconect from databse
con.close()
print("Database connection closed")

