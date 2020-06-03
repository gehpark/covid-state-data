import pandas
from datetime import datetime, timedelta

"""
For each state, the per capita increase in cases in the past 7 days
"""

# 50 states plus puerto rico
class StateStats():

    def __init__(self):
        self._readCSV()
        self._setDates()
        self._getSevenDayDiffData()

    def _readCSV(self):
        """Read csv data sources."""
        # columns: date, state (full name), fips, cases, deaths
        covid_df = pandas.read_csv("us-states.csv")
        # sort to get the last 7 days only to process less data
        covid_df.sort_values('date')
        # 50 states + (guam, dc, mariana islands, virgin islands, puerto rico) + 20 for buffer
        self.covid_df = covid_df.tail(n=(50+5)*7 + 20)

        # columns: state (full name), population (2019 basis)
        census_df = pandas.read_csv("state-population.csv")
        census_df['population'] = pandas.to_numeric(census_df['population'].str.replace(',', ''))
        self.census_df = census_df
        print "[INFO] Found and read CSVs successfully"

    def _setDates(self):
        """set date range as class fields."""
        self.day_seven = self.covid_df['date'].max()
        self.day_one = dateToString(stringToDate(self.day_seven) - timedelta(days=6))
        print "[INFO] Calculating for range %s - %s" % (self.day_one, self.day_seven)

    def _getSevenDayDiffData(self):
        """diff and merge the date range data with population data."""
        day_one_df = self.covid_df[(self.covid_df['date'] == self.day_one)]
        assert day_one_df['state'].size >= 51, "Day 1 data only has %d states" % day_one_df['state'].size
        day_seven_df = self.covid_df[(self.covid_df['date'] == self.day_seven)]
        assert day_seven_df['state'].size >= 51, "Day 7 data only has %d states" % day_seven_df['state'].size
        covid_diff_df = day_one_df.merge(day_seven_df, on=['state', 'fips'], suffixes=('_one', '_seven'))
        covid_diff_df = covid_diff_df.drop(['date_one', 'date_seven'], axis=1)
        diff_df = covid_diff_df.merge(self.census_df, on=['state'])
        self.diff_df = diff_df

    def getPerCapita(self):
        """Create a dataframe that includes per capita values."""
        diff_df = self.diff_df
        diff_df['deaths_diff'] = diff_df['deaths_seven'] - diff_df['deaths_one']
        diff_df['deaths_per_capita'] = diff_df['deaths_diff'] / diff_df['population']
        diff_df['cases_diff'] = diff_df['cases_seven'] - diff_df['cases_one']
        diff_df['cases_per_capita'] = diff_df['cases_diff'] / diff_df['population']
        return diff_df


def main():
    stats = StateStats()
    states_df = stats.getPerCapita()
    print states_df
    states_df.to_csv('outputs/perState.csv')

def dateToString(date):
    return date.strftime('%Y-%m-%d')

def stringToDate(string):
    return datetime.strptime(string, '%Y-%m-%d').date()

if __name__ == "__main__":
    main()
