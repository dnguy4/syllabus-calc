import re

import camelot
import nltk
import pandas
import pdfminer.high_level
from bs4 import BeautifulSoup
import textract

keywords = ["test", "midterm", "homework", "quiz", "project", "lab", 
            "attendance", "participation", "labs", "each", "worth"]
grammar = ("""CHUNK1: {<CD>*(<JJ>|<NN>+|<NNP>+)+<:>?<CD><NN><DT>}
              CHUNK2: {(<JJ>|<NN>+|<NNP>+)+<:>?<CD><NN>}
              CHUNK3: {<CD><NN><IN>?<DT><JJ>*<NN>?(<NNP>|<NNS>)?}
              CHUNK4: {<CD><NN><IN><.*>{0,8}(<NN>|<NNP>)+}
              """)
#CHUNK1: Covers "4 Midterms: 10% each" phrasing
#CHUNK2: Covers "HW: 5%" phrasing
#CHUNK3: Covers "40% from Midterms" phrasing (<NN>|<NNP>|<NNS>)?
#CHUNK4: Covers cases like 3 but with superfluous wording

def process_chunk1(subtree_leaves):
    grade_category = ""
    total_weight = int(subtree_leaves[0][0])
    for token, pos in subtree_leaves[1:]:
        if pos == "CD":
            total_weight *= int(token)
            return((grade_category, [str(total_weight), token]))
        grade_category += token + " " 

def process_chunk2(subtree_leaves):
    grade_category = ""
    for token, pos in subtree_leaves:
        if pos == "CD":
            return((grade_category, [token, token]))
        elif pos != ":":
            grade_category += token + " " 

def process_chunk3or4(subtree_leaves):
    grade_category = subtree_leaves[-2][0] + " " + subtree_leaves[-1][0]
    grade_weight = subtree_leaves[0][0]
    return((grade_category, [grade_weight, grade_weight]))

process_chunk_dispatcher = {
    "CHUNK1" : process_chunk1,
    "CHUNK2" : process_chunk2,
    "CHUNK3" : process_chunk3or4,
    "CHUNK4" : process_chunk3or4
}
chunker = nltk.RegexpParser(grammar)
 

def extract_grade_pairs(filename):
    if filename.endswith(".pdf"):
        text = pdfminer.high_level.extract_text(filename)
    else:
        text = textract.process(filename).decode('utf-8')
    pattern = re.compile(r'(?<=\().*?(?=\))') #Parenthesis phases without parenthesis using lookaheads/lookbehinds
    #pattern = re.compile(r'\([^)]*\)') #Parenthesis phases including parenthesis
    parenthesis_phases = pattern.findall(text)
    parenthesis_phases = ". ".join(parenthesis_phases)
    text = pattern.sub('', text) + ". ".join(parenthesis_phases)
    pre_processed = [sentence + '.' for sentence in text.split('.') if '%' in sentence]

    txt = nltk.word_tokenize("".join(pre_processed))
    tagged = nltk.pos_tag(txt)
    chunked = chunker.parse(tagged)

    grade_pairs = []
    for subtree in chunked.subtrees(filter=lambda t: t.label() in process_chunk_dispatcher):
        grade_pairs.append(process_chunk_dispatcher[subtree.label()](subtree))
    return(grade_pairs)

def extract_table_from_pdf(filename):
    #Returns the first grading table
    tables = camelot.read_pdf(filename, pages='all', line_scale = 20)
    for table in tables:
        if '%' in table.df.to_string():
            return table.df
    return None

def process_table(df):
    res = []
    if df.to_string().count("\n") != 0:
        #TODO: weave through new lines, creating assignment weight pairs
        #str.splitlines() turns a string into an array using \n as delimiters
        keys = df.iloc[1,0].splitlines()
        vals = df.iloc[1,1].splitlines()
        for i, key in enumerate(keys):
            res.append((key, re.findall(r'\d+', vals[i])))
    return res
 

if __name__ == "__main__":
    #print(extract_grade_pairs("4242syllabus.pdf"))
    #process_table(extract_table_from_pdf("4242syllabus.pdf")) -> [('HW/Quizzes', ['15']), ('Midterms', ['50', '25']), ('Final exam', ['35'])]
    html = """<table border="1"><tbody><tr><td></td></tr>
<tr><td>Item </td><td align="right">Fraction of Grade </td></tr>
<tr><td></td></tr>
<tr><td>Lab attendance (12/15)</td><td align="right">5%</td></tr>
<tr><td>Written exercises</td><td align="right">15%</td></tr>
<tr><td>Hands-on assignments</td><td align="right">20%</td></tr>
<tr><td>Midterm 1</td><td align="right">15%</td></tr>
<tr><td>Midterm 2</td><td align="right">15%</td></tr>
<tr><td>Final Exam</td><td align="right">30%</td></tr>
<tr><td></td></tr></tbody></table>"""

    soup = BeautifulSoup(html)
    table = soup.find("table")