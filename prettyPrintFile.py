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

    def __init__(self, filepath):
        self._readCSV(filepath)

    def _readCSV(self, filepath):
        """Read csv data sources."""
        # columns: date, state (full name), fips, cases, deaths
        self.input_df = pandas.read_csv(filepath, parse_dates=True)
        print "[INFO] Found and read CSVs successfully"

    def GetData(self, output_filepath):
        outputFile = open(output_filepath, "w+")

        for c in self.input_df.columns:
            print c
            outputFile.write(c + ":\n")
            listed_column = self.input_df[c].tolist()
            print listed_column
            outputFile.write(str(listed_column) + "\n")

        outputFile.close()  


def main():
    if len(sys.argv) < 2:
        print "Usage: python prettyPrintFile.py <filepath> <output file name> \n \
        -- filepath: path of the file you want to prettyprint. should be a csv \
        -- output file name: optional; name of the file you want to output (file type will automatically be .txt) "
    filepath = sys.argv[1]
    if len(sys.argv) == 3:
        output_filename = sys.argv[2]
        output_filepath += "outputs/%s.txt" % output_filename
    else:
        output_filepath = "outputs/prettyPrintFileOutput.txt"

    if not FileReadCheck(filepath):
        print "Your filepath seems to be invalid"
        return

    pp = PrettyPrinter(filepath)
    pp.GetData(output_filepath)

    print "(Data is also exported to %s)" % output_filepath 

def FileReadCheck(filepath):
    try:
      file = open(filepath, "r")
      file.close()
      return 1
    except IOError:
      print "Error: File does not appear to exist."
      return 0

if __name__ == "__main__":
    main()
