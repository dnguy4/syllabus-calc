import re

import camelot
import nltk
import pandas
import pdfminer.high_level
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
            return((grade_category, [token]))
        elif pos != ":":
            grade_category += token + " " 

def process_chunk3or4(subtree_leaves):
    grade_category = subtree_leaves[-2][0] + " " + subtree_leaves[-1][0]
    grade_weight = subtree_leaves[0][0]
    return((grade_category, [grade_weight]))

dispatcher = {
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
    text = re.sub(r'\([^)]*\)', '', text) #will replace parenthesis in txt with nothing

    pre_processed = [sentence + '.' for sentence in text.split('.') if '%' in sentence]
    #tokens = [sentence for sentence in tokens if any(k in sentence for k in keywords)]
    txt = nltk.word_tokenize("".join(pre_processed))
    tagged = nltk.pos_tag(txt)
    chunked = chunker.parse(tagged)

    res = []
    for subtree in chunked.subtrees(filter=lambda t: t.label() in dispatcher):
        res.append(dispatcher[subtree.label()](subtree))
    return(res)

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

class NotEnoughGrades(Exception):
    pass

def grade_calc(lst):
    res = []
    for grade_pair in lst:
        try:
            if len(grade_pair[1]) == 1:
                print("Please enter your overall grade for " + grade_pair[0])
                grade = float(input())
                weight = float(grade_pair[1][0]) / 100
                res.append(grade*weight)
            else:
                num_of_grades =  float(grade_pair[1][0]) // float(grade_pair[1][1])
                print("Please enter each of your " + str(num_of_grades) + " grades for " + grade_pair[0] + ", seperated by commas")
                input_list = input()
                input_list = input_list.split(',')
                grades = [float(num) for num in input_list]
                if len(grades) != num_of_grades:
                    raise NotEnoughGrades
                weight = float(grade_pair[1][0]) / 100
                grade = sum(grades) * weight / num_of_grades
                res.append(grade)
        except ValueError:
            print("A number(s) was not detected. Exiting.")
            return
        except NotEnoughGrades:
            print("Not enough grades were entered. Exiting.")
            return

    print("Your final grade is " + str(sum(res)) + "%.")

# process_table(extract_table_from_pdf("4242syllabus.pdf"))
#grade_calc([('HW/Quizzes', ['15']), ('Midterms', ['50', '25']), ('Final exam', ['35'])])
#"1302syllabus.pdf", "2041syllabus.html", "4242syllabus.pdf"
if __name__ == "__main__":
    print(extract_grade_pairs("4242syllabus.pdf"))