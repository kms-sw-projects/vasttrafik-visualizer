import pandas as pd
from matplotlib import pyplot as plt 
import seaborn as sb
from calendar import month_abbr as months
import math

def monthyear_from_number(number, monthslist):
    year = 2018 + math.floor((number+6)/12)
    month = monthslist[ (number+6) % 12]
    return str(month)+" "+ str(year)

df = pd.read_csv("tickets_automated.csv", header=0)
df['SEK'] = df['SEK'].fillna(0)
startYear = min(df["Year"])
startMonth = 2
print(startYear)

print(df.info())
df2 = df.groupby(["Year","Month"], as_index=False)['SEK'].aggregate(['sum'])
df2['Month-Year'] = (df2["Year"]-startYear)*12 + df2["Month"]-startMonth
print(df2)

months_list = list(months[1:])
plt.figure()
ax = sb.barplot(data=df2, x='Month-Year', y='sum', hue="Year", palette=sb.color_palette())
x_labels = [monthyear_from_number(x, months_list) for x in df2['Month-Year'] ]
ax.set_ylabel("SEK")
ax.set_xticks(ax.get_xticks(), x_labels, rotation=90)
plt.title("Monthly purchases of Västtrafik tickets in SEK")


plt.figure()
df3 = df.groupby(["Year"], as_index=False)['SEK'].aggregate('sum')
print(df3)
ax2 = sb.barplot(data=df3, x='Year', y='SEK', hue="Year", palette=sb.color_palette())
plt.title("Yearly purchases of Västtrafik tickets in SEK")
ax.set_ylabel("SEK")

plt.figure()
df4 = df.groupby(["Year", "Month"], as_index=False)['Single tickets bought'].aggregate('sum')
df4['Month-Year'] = (df4["Year"]-startYear)*12 + df4["Month"]-startMonth
print(df4)
ax3 = sb.barplot(data=df4, x='Month-Year', y='Single tickets bought', hue="Year", palette=sb.color_palette())
x_labels = [monthyear_from_number(x, months_list) for x in df4['Month-Year'] ]
ax3.set_xticks(ax3.get_xticks(), x_labels, rotation=90)
ax.set_ylabel("number")
plt.title("Monthly purchases of single tickets")

plt.figure()
df5 = df.groupby(["Year", "Month"], as_index=False)['SEK'].aggregate('mean')
df5['Month-Year'] = (df5["Year"]-startYear)*12 + df5["Month"]-startMonth
ax4 = sb.barplot(data=df5, x='Month-Year', y='SEK', hue="Year", palette=sb.color_palette())
x_labels = [monthyear_from_number(x, months_list) for x in df5['Month-Year'] ]
ax4.set_xticks(ax4.get_xticks(), x_labels, rotation=90)
plt.title("Average daily cost in SEK")
plt.axhline(y=df5.aggregate('mean')['SEK'], label="daily average over entire time period")
#print(df5)
plt.legend()

plt.figure()

plt.show()
