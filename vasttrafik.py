"""A simple data visualization script for Vasttrafik ticket purchase data."""

import math
from calendar import month_abbr as months
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sb

def monthyear_from_number(number, monthslist, start_year, start_month):
    """Convert a Year-Month index number to a string of form 'Month-Year' (%b-%Y format datetime)"""
    year = start_year + math.floor((number+start_month)/12)
    month = monthslist[ (number+start_month) % 12]
    return str(month)+" "+ str(year)

def year_from_monthyear(monthyear, month, start_year, start_month):
    """Convert a Year-Month index number to a year Integer."""
    actual_year = np.floor( (monthyear - (month-start_month) )/12) + start_year
    return actual_year

def month_from_monthyear(monthyear, year, start_year, start_month):
    """Convert a Year-Month index number to a month Integer."""
    actual_month = monthyear - 12*(year -start_year) + start_month
    return actual_month

# Read CSV file
df = pd.read_csv("tickets_automated.csv", header=0)
df['SEK'] = df['SEK'].fillna(0)
# change date column datatype to datetime
df['datetime'] = pd.to_datetime(df['datetime'])
# remove duplicate entries
df.drop_duplicates("datetime", inplace=True)
# set datetime column as index
df.set_index("datetime", inplace=True)
# drop unnecessary old index
df.drop("Unnamed: 0", axis=1, inplace=True)
# show start of the data
df.head()

# extract startYear and startMonth values from data
start_year = min(df["Year"])
start_month = min(df[df["Year"] == start_year]["Month"])
print(f"The data starts in the year {start_year} and month {start_month}.")
# print some info over the data
df.info()
print(df[-50:-1])
# create a new dataFrame that groups tickets by year and month and sums the total ticket purchases
df2 = df.groupby(["Year","Month"], as_index=False)['SEK'].aggregate(['sum'])
# Create Month-Year index which essentially counts the month number from the data's starting month
df2['Month-Year'] = (df2["Year"]-start_year)*12 + df2["Month"]-start_month
print(df2)


# Create first figure: Monthly spending, split by years

df2 = df.groupby(["Year","Month"], as_index=False)['SEK'].aggregate(['sum'])
df2['Month-Year'] = (df2["Year"]-start_year)*12 + df2["Month"]-start_month
df2 = df2.set_index(["Month-Year"])
# adds empty months (no purchases) as well with 0 in spending
df2= df2.reindex(list(range(df2.index.min(),df2.index.max()+1)),fill_value=0)
df2["Year"] = year_from_monthyear(df2.index, df2["Month"], start_year, start_month).astype("int32")
df2["Month"] = month_from_monthyear(df2.index, df2["Year"], start_year, start_month).astype("int32")

months_list = list(months[1:])
plt.figure(figsize=(12,10))
ax = sb.barplot(data=df2, x=df2.index, y='sum', hue="Year", palette=sb.color_palette())
x_labels = [monthyear_from_number(x, months_list, start_year, start_month) for x in df2.index ]
ax.set_ylabel("SEK")
ax.set_xticks(ax.get_xticks(), x_labels, rotation=90)
plt.title("Monthly purchases of Västtrafik tickets in SEK")
plt.show()

# Create second figure: Yearly spending

plt.figure(figsize=(10,8))
df3 = df.groupby(["Year"], as_index=False)['SEK'].aggregate('sum')
ax2 = sb.barplot(data=df3, x='Year', y='SEK', hue="Year", palette=sb.color_palette())
plt.title("Yearly purchases of Västtrafik tickets in SEK")
ax.set_ylabel("SEK")
plt.show()


# Create third figure: Number of monthly tickets bought
plt.figure(figsize=(12,12))
df4 = df.groupby(["Year", "Month"], as_index=False)['Single tickets bought'].aggregate('sum')
df4['Month-Year'] = (df4["Year"]-start_year)*12 + df4["Month"]-start_month
df4 = df4.set_index(["Month-Year"])

df4= df4.reindex(list(range(df4.index.min(),df4.index.max()+1)),fill_value=0)
ax3 = sb.barplot(data=df4, x=df4.index,
                 y='Single tickets bought', hue="Year", palette=sb.color_palette())
x_labels = [monthyear_from_number(x, months_list, start_year, start_month)
            for x in df4.index ]
ax3.set_xticks(ax3.get_xticks(), x_labels, rotation=90)
ax.set_ylabel("number")
plt.title("Monthly purchases of single tickets")
plt.show()

# Create fourth figure: Monthly spending vs average monthly spending
plt.figure()
df5 = df.groupby(["Year", "Month"], as_index=False)['SEK'].aggregate('mean')
df5['Month-Year'] = (df5["Year"]-start_year)*12 + df5["Month"]-start_month
df5 = df5.set_index(["Month-Year"])
df5= df5.reindex(list(range(df5.index.min(),df5.index.max()+1)),fill_value=0)
ax4 = sb.barplot(data=df5, x='Month-Year', y='SEK', hue="Year", palette=sb.color_palette())
x_labels = [monthyear_from_number(x, months_list,start_year, start_month)
            for x in df5['Month-Year'] ]
ax4.set_xticks(ax4.get_xticks(), x_labels, rotation=90)
plt.title("Average daily cost in SEK")
plt.axhline(y=df5.aggregate('mean')['SEK'], label="daily average over entire time period")
plt.legend()
plt.show()

# Create fifth figure: Relative probably of purchase vs hour of the day
df["hour"] = df.index.hour
fig= plt.figure()
ax = plt.subplot(1,1,1)
df_week = df[( df["weekday"] < 5)  ]["Single tickets bought"]
df_weekend = df[( df["weekday"] >= 5) ]["Single tickets bought"]
df_hourly_weekday = df_week.groupby(["hour"]).sum()/df_week.sum()
df_hourly_weekend = df_weekend.groupby(["hour"]).sum()/df_weekend.sum()

plt.plot(df_hourly_weekday.index, df_hourly_weekday.values, marker="o", label="weekdays")
plt.plot(df_hourly_weekend.index, df_hourly_weekend.values, marker="o", label="weekends")
plt.xticks(range(0,24, 2))
plt.title("Relative share of tickets purchases per hour of the day")

ax.set_yticklabels(np.round(100*ax.get_yticks(),2))
ax.set_xlabel("Hour of the day")
ax.set_ylabel("percentage of total ticket purchases")
plt.legend()
plt.show()
