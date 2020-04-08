A US states map polling coronavirus cases reported from Worldometer and the JHU data, refreshing every hour (when new data is available). The cases are divided by population of each state to get a per capita estimate. https://us-covid19-per-capita.net

## Downloading the data

When new data is available, it is updated in [data.csv](https://github.com/silverdrake11/covid_rates_per_capita/blob/master/data.csv). To download all snapshots of the data run `python download.py` (going back to March 21). It will get downloaded in a format for example `2020-03-23-13-04.csv` which corresponds to the date and time in UTC. The last two numbers are hours and minutes.

All of the snapshots are then added to one file `historical.csv`. Which looks like this

| states | confirmed     | deaths | timestamp        | 
| ------ | ------------- | ------ | ---------------- |
| AZ     | 2575          | 73     | 2020-04-07 17:07 |
| AZ     | 2851          | 73     | 2020-04-07 20:22 |
| CA     | 1249          | 24     | 2020-03-21 19:20 |
