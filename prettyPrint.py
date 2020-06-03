import pandas
from datetime import datetime, timedelta
import sys

"""
Pretty print input data into comma separated arrays
i.e.
dates: [2020-01-01, 2020-01-02]
cases: [1,49]
"""

class PrettyPrinter():

    def __init__(self):
        self._readCSV()
        self._setDates()

    def _readCSV(self):
        """Read csv data sources."""
        # columns: date, state (full name), fips, cases, deaths
        covid_df = pandas.read_csv("us-states.csv", parse_dates=True)
        # data is already sorted ascending order but just in case they change it on us
        self.covid_df = covid_df.sort_values('date')

        # Use for States list
        states_df = pandas.read_csv("state-population.csv")
        self.states = states_df['state'].tolist()
        self.states.sort()
        print "[INFO] Found and read CSVs successfully"

    def _setDates(self):
        """Find the last updated date in data."""
        self.last_date = self.covid_df['date'].max()

    def GetStateStat(self, state, num_dates):
        state_df = self.covid_df[(self.covid_df['state'] == state)]
        if num_dates > 0:
            state_df = state_df.tail(n=num_dates)
        state_df = state_df.drop(['state', 'deaths', 'fips'], axis=1)
        return {"date": state_df['date'].tolist(), "cases": state_df['cases'].tolist()}

    def GetAggregatedStats(self, num_dates):
        usa_df = self.covid_df.drop(['state', 'deaths', 'fips'], axis=1)
        usa_df = usa_df.groupby(['date'], as_index=False).sum()
        if num_dates > 0:
            usa_df = usa_df.tail(n=num_dates)
        return {"date": usa_df['date'].tolist(), "cases": usa_df['cases'].tolist()}

    def GetAllStats(self, num_dates):
        if num_dates > 0:
            first_date = dateToString(stringToDate(self.last_date) - timedelta(days=num_dates))
            all_states_df = self.covid_df[(self.covid_df['date'] > first_date )]
        else:
            all_states_df = self.covid_df
        all_states_df = all_states_df.drop(['deaths', 'fips'], axis=1)
        pretty_map = {}
        for state in self.states:
            state_df = all_states_df[(all_states_df['state'] == state)]
            pretty_map[state] = {"date": state_df['date'].tolist(), "cases": state_df['cases'].tolist()}
        return pretty_map

def main():
    if len(sys.argv) < 2:
        print "Usage: python prettyPrint.py <state> <n> \n \
        -- <state>: state whose data you wish to print or 'usa' for all of america combined or 'all' for all states separately \
        -- <n>: the number of dates you wish to display. omit to unleash all of 2020"
    state = sys.argv[1]
    if len(sys.argv) == 3:
        num_dates = int(sys.argv[2])
    else:
        num_dates = -1

    pp = PrettyPrinter()
    filename = "outputs/prettyPrintOutput%s.txt" % state

    if state == 'all':
        mapOfPrettyLists = pp.GetAllStats(num_dates)
        printMultiSet(filename, mapOfPrettyLists)
    else:
        if state == 'usa':
            prettyLists = pp.GetAggregatedStats(num_dates)
        else:
            prettyLists = pp.GetStateStat(state, num_dates)
        print "Copy & paste away!! Data for %s:" % state
        print prettyLists
        printSingleSet(filename, prettyLists)

def printSingleSet(filename, prettyLists):
    outputFile = open(filename, "w+")
    for key in prettyLists.keys():
        outputFile.write(key + ":\n")
        outputFile.write(str(prettyLists[key]) + "\n")
    outputFile.close()    
    print "(Data is also exported to %s)" % filename    

def printMultiSet(filename, mapOfPrettyLists):
    outputFile = open(filename, "w+")
    state_keys = mapOfPrettyLists.keys()
    state_keys.sort()
    for state in state_keys:
        outputFile.write("=== Data for %s: \n" % state)
        for key in mapOfPrettyLists[state].keys():
            outputFile.write(key + ":\n")
            outputFile.write(str(mapOfPrettyLists[state][key]) + "\n")
    outputFile.close()
    print "Data is exported to %s for your copy&pasting pleasures" % filename


def dateToString(date):
    return date.strftime('%Y-%m-%d')

def stringToDate(string):
    return datetime.strptime(string, '%Y-%m-%d').date()

if __name__ == "__main__":
    main()
