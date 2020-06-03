import pandas
from datetime import datetime, timedelta
import sys 
import os

"""
For each state, list up to 10 counties with the greatest per capita
increase in cases in the past 7 days, ordered from greatest to least,
and list their per capita increase
"""

# 50 states plus puerto rico
class CountyStats():

    def __init__(self):
        self._readCSV()
        self._setDates()
        self._getSevenDayDiffData()

    def _readCSV(self):
        """Read csv data sources."""
        # columns: date, county, state, fips, cases, deaths
        covid_df = pandas.read_csv("us-counties.csv")
        covid_df = covid_df.sort_values('date', ascending=False)
        self.covid_df = covid_df

        # columns: county (full name), population (2019 basis)
        # columns: state (full name), population (2019 basis)
        census_df = pandas.read_csv("county-population.csv")
        census_df = census_df[['State', 'County', 'Total Population']]
        census_df = census_df.rename(columns={"State": "state", "County": "county", "Total Population": "population"})
        self.census_df = census_df

        # Use for States list
        states_df = pandas.read_csv("state-population.csv")
        self.states = states_df['state'].tolist()
        print "[INFO] Found and read CSVs successfully"

    def _setDates(self):
        """set date range as class fields."""
        self.day_seven = self.covid_df['date'].iloc[0]
        self.day_one = dateToString(stringToDate(self.day_seven) - timedelta(days=6))
        print "[INFO] Calculating for range %s - %s" % (self.day_one, self.day_seven)

    def _getSevenDayDiffData(self):
        """diff and merge the date range data with population data."""
        day_one_df = self.covid_df[(self.covid_df['date'] == self.day_one)]
        day_seven_df = self.covid_df[(self.covid_df['date'] == self.day_seven)]
        covid_diff_df = day_one_df.merge(day_seven_df, on=['county', 'state'], suffixes=('_one', '_seven'))
        covid_diff_df = covid_diff_df[["county", "state", "cases_one", "cases_seven", "deaths_one", "deaths_seven"]]
        diff_df = covid_diff_df.merge(self.census_df, on=["state", "county"])
        self.diff_df = diff_df

    def getPerCapita(self):
        """Create a dataframe that includes per capita values."""

        # Calculate deaths and cases per capita per county
        diff_df = self.diff_df
        diff_df['deaths_diff'] = diff_df['deaths_seven'] - diff_df['deaths_one']
        diff_df['deaths_per_capita'] = diff_df['deaths_diff'] / diff_df['population']
        diff_df['cases_diff'] = diff_df['cases_seven'] - diff_df['cases_one']
        diff_df['cases_per_capita'] = diff_df['cases_diff'] / diff_df['population']

        states_dfs = {}
        # Categorize by State
        for state in self.states:
            state_df = diff_df[diff_df['state'] == state]
            state_df = state_df.sort_values('cases_per_capita', ascending=False)
            state_df = state_df.head(n=10)
            states_dfs[state] = state_df

        self.states_dfs = states_dfs
        return states_dfs

    def printGivenState(self, state):
        print "[OUTPUT] Printing for state %s" % state
        print self.states_dfs[state]

    def outputAllStates(self, filepath):
        for state in self.states:
            self.states_dfs[state].to_csv(filepath, mode='a', header=False)


def main():
    if len(sys.argv) == 2:
        state = sys.argv[1]
    else:
        state = None

    stats = CountyStats()
    states_df = stats.getPerCapita()

    if state:
        stats.printGivenState(state)
        states_df[state].to_csv('outputs/perCounty%sStats.csv' % state)

    else:
        filepath = 'outputs/perCountyPerState.csv'
        if os.path.exists(filepath):
            os.remove(filepath)
        stats.outputAllStates(filepath)

def dateToString(date):
    return date.strftime('%Y-%m-%d')

def stringToDate(string):
    return datetime.strptime(string, '%Y-%m-%d').date()

if __name__ == "__main__":
    main()
