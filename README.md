A US states map polling coronavirus cases reported from John Hopkins refreshing every few hours (when data is available). The cases are divided by population of each state to get a per capita estimate. https://us-covid19-per-capita.net

## Downloading the data

When new data is available, it is updated in [data.csv](https://github.com/silverdrake11/covid_rates_per_capita/blob/master/data.csv). To download all snapshots of the data run `python download.py` (going back to March 21). It will get downloaded in a format for example `2020-03-23-13-04.csv` which corresponds to the date and time in UTC. The last two numbers are hours and minutes.