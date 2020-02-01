import re
import camelot
from bs4 import BeautifulSoup
import pandas

class NoTablesFound(Exception):
    pass

def extract_table_from_pdf(filename):
    """Returns the first potential grading table."""
    tables = camelot.read_pdf(filename, pages='all', line_scale = 20)
    for table in tables:
        if '%' in table.df.to_string():
            return table.df
    raise NoTablesFound

def extract_table_from_html(filename):
    """Returns the first potential grading table."""
    dfs = pandas.read_html(filename)
    for df in dfs:
        if '%' in df.to_string():
            return df
    raise NoTablesFound

def process_table(df):
    """Return grade pairs from a dataframe."""
    res = []
    if df.shape == (2,2): # All grade weights clumped in one row
        keys = df.iloc[1,0].splitlines() # Strip new line chars, which likely caused this issue
        vals = df.iloc[1,1].splitlines()
        for i, key in enumerate(keys):
            res.append((key, re.findall(r'\d+', vals[i])))
    else:
        # Assuming only 2 columns, category and weight
        for category,weight in df.itertuples(index=False):
            matches = re.findall(r'\d+', str(weight))
            if len(matches) >= 1:
                res.append((category, matches))
    return res

def extract_grade_pairs(filename):
    """Return grade pairs from table inside a file."""
    try:
        if filename.endswith(".pdf"):
            df = extract_table_from_pdf(filename)
        elif filename.endswith(".html"):
            df = extract_table_from_html(filename)
        else:
            raise NoTablesFound
        return process_table(df)
    except NoTablesFound:
        print("No tables were found in %s." %filename)
        return []

if __name__ == "__main__":
    df = extract_table_from_html("Samples//2021syllabus.html")
    print(process_table(df))