import re
import nltk
import pandas
import pdfminer.high_level
from bs4 import BeautifulSoup
import textract

grammar = ("""CHUNK1: {<CD>*(<JJ>|<NN>+|<NNP>+)+<:>?<CD><NN><DT>}
              CHUNK2: {(<JJ>|<NN>+|<NNP>+)+<:>?<CD><NN>}
              CHUNK3: {<CD><NN><IN>?<DT><JJ>*<NN>?(<NNP>|<NNS>)?}
              CHUNK4: {<CD><NN><IN><.*>{0,8}(<NN>|<NNP>)+}
              """)
"""Some common grammatical patterns for explaining grade percentages.
    CHUNK1: Covers "4 Midterms: 10% each" phrasing
    CHUNK2: Covers "HW: 5%" phrasing
    CHUNK3: Covers "40% from Midterms" phrasing (<NN>|<NNP>|<NNS>)?
    CHUNK4: Covers cases like 3 but with superfluous wording"""

chunker = nltk.RegexpParser(grammar)

def process_chunk1(subtree_leaves):
    """Parse CHUNK1 to return grade pair."""
    grade_category = ""
    total_weight = int(subtree_leaves[0][0])
    for token, pos in subtree_leaves[1:]:
        if pos == "CD":
            total_weight *= int(token)
            return((grade_category, [str(total_weight), token]))
        grade_category += token + " " 

def process_chunk2(subtree_leaves):
    """Parse CHUNK2 to return grade pair."""
    grade_category = ""
    for token, pos in subtree_leaves:
        if pos == "CD":
            return((grade_category, [token]))
        elif pos != ":":
            grade_category += token + " " 

def process_chunk3or4(subtree_leaves):
    """Parse CHUNK3 and CHUNK4 to return grade pair."""
    grade_category = subtree_leaves[-2][0] + " " + subtree_leaves[-1][0]
    grade_weight = subtree_leaves[0][0]
    return((grade_category, [grade_weight]))

process_chunk_dispatcher = {
    "CHUNK1" : process_chunk1,
    "CHUNK2" : process_chunk2,
    "CHUNK3" : process_chunk3or4,
    "CHUNK4" : process_chunk3or4
}
""""Processed chunks will be tuples of form (category, [weight])
    The weight will either be one number or two numbers.
    First number represents total weight.
    The second number (if any) represents weight per individual instance."""

def extract_grade_pairs(filename):
    """Return a list of grade weight pairs from a file."""
    if filename.endswith(".pdf"):
        text = pdfminer.high_level.extract_text(filename) #pdf2text alternative for Windows compatability
    else:
        text = textract.process(filename).decode('utf-8')
        
    # Move parenthesis phrases to the end of the text to avoid labeling conflicts
    pattern = re.compile(r'(?<=\().*?(?=\))') #Parenthesis phrases without parenthesis using lookaheads/lookbehinds
    parenthesis_phases = pattern.findall(text)
    parenthesis_phases = ". ".join(parenthesis_phases)
    text = pattern.sub('', text) + ". ".join(parenthesis_phases)

    pre_processed = [sentence + '.' for sentence in text.split('.') if '%' in sentence] #Grades usually include % char
    txt = nltk.word_tokenize("".join(pre_processed))
    tagged = nltk.pos_tag(txt)
    chunked = chunker.parse(tagged)

    grade_pairs = []
    for subtree in chunked.subtrees(filter=lambda t: t.label() in process_chunk_dispatcher):
        grade_pairs.append(process_chunk_dispatcher[subtree.label()](subtree))
    return grade_pairs

 
if __name__ == "__main__":
    print(extract_grade_pairs("Samples//2041syllabus.html"))