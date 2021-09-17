# !/usr/bin/python3
# testJSON.py

import json
from pathlib import Path

if __name__ == '__main__':
    p = Path("C:\\Users\\marki\\Desktop\\Pool Data\\Solar")  # path to where the files are
    keys = ['timestamp']  # just to force the time stamp as first item in the csv
    data = []
    for child in sorted(p.glob('Record-*.json')):  # find all files matching this mask
        jsonSource = ""
        with open(child) as f:
            line = f.readline()
            jsonSource += line
        jsonSource += ']}'  # complete json as it is missing the last two chars to make it valid
        obj = json.loads(jsonSource)  # convert json into an object
        for record in obj['records']:  # records is an array (or list)
            for key in record.keys():  # each record is a set of name / value pairs
                if key not in keys:  # so make sure we add any keys that weren't there in previous records
                    keys.append(key)
            line = ""
            for key in keys:  # use the fixed order of keys to get a csv line that is consistent for each line
                line += ", " + str(record.get(key, ""))
            data.append(line[2:])  # remove first ", "
    outPath = p.joinpath("data.csv")  # create an output file
    with open(outPath, 'w') as f:
        print(", ".join(keys))  # just so we can see some output
        print(", ".join(keys), file=f)  # add header line
        for line in sorted(data):  # sort the rows by date time stamp for convenience
            print(line, file=f)  # add each line to the data file
    print("Done")  # just so we can see we finished

