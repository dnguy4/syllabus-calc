import CalculatorGUI
import SyllabusReader
import TableExtractor

def process_grade_pair(grade_pairs):
    """Create a calculator instance for grading categories."""
    calc = CalculatorGUI.Calculator()
    for category, weight_list in grade_pairs:
        if len(weight_list) == 1: # Only 1 instance of category
            calc.addRow(category, weight_list[0])
        else: 
            # (Test, [50, 25]) represents 2 midterms each worth 25%
            total_weight = float(weight_list[0])
            individual_weight = float(weight_list[1])
            end_val = int(total_weight/individual_weight)
            for i in range(1, 1+end_val):
                calc.addRow(category+ str(i), individual_weight) # Label each test
    calc.mainloop()


def create_grade_calulator(filename, tables=False):
    """Return a calculator given a filename.
    
    Args:
        filename (str): filename of the syllabus.
        tables (bool, optional): Indicates if grading stored in table in syllabus. Defaults to False.
    """
    if tables:
        grade_pairs = TableExtractor.extract_grade_pairs(filename)
    else:
        grade_pairs = SyllabusReader.extract_grade_pairs(filename)
    process_grade_pair(grade_pairs)

if __name__ == "__main__":
    #"1302syllabus.pdf", "2041syllabus.html", "4242syllabus.pdf"
    create_grade_calulator("1051syllabus.docx")