import re
import camelot
from bs4 import BeautifulSoup
import pandas

def extract_table_from_pdf(filename):
    #Returns the first grading table
    tables = camelot.read_pdf(filename, pages='all', line_scale = 20)
    for table in tables:
        if '%' in table.df.to_string():
            return table.df
    return None

def extract_table_from_html(filename):
    #Returns the first grading table
    dfs = pandas.read_html(filename)
    for df in dfs:
        if '%' in df.to_string():
            return df
    return None

def process_table(df):
    res = []
    if df.shape == (2,2):
        #str.splitlines() turns a string into an array using \n as delimiters
        keys = df.iloc[1,0].splitlines()
        vals = df.iloc[1,1].splitlines()
        for i, key in enumerate(keys):
            res.append((key, re.findall(r'\d+', vals[i])))
    else:
        for a,b in df.itertuples(index=False):
            matches = re.findall(r'\d+', str(b))
            if len(matches) >= 1:
                res.append((a, matches))
    return res

def extract_grade_pairs(filename):
    if filename.endswith(".pdf"):
        df = extract_table_from_pdf(filename)
    elif filename.endswith(".html"):
        df = extract_table_from_html(filename)
    else:
        df = None
    if df == None:
        return None
    return process_table(df) 

if __name__ == "__main__":

    df = extract_table_from_html("2021syllabus.html")
    print(process_table(df))
    