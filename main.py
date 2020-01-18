import CalculatorGUI
import SyllabusReader

def process_grade_pair(grade_pair):
    calc = CalculatorGUI.Calculator()
    for category, weight_list in grade_pair:
        total_weight = float(weight_list[0])
        individual_weight = float(weight_list[1])
        end_val = int(total_weight/individual_weight)
        if (end_val == 1):
            calc.addRow(category, individual_weight)
        else:
            for i in range(1, 1+end_val):
                calc.addRow(category+ str(i), individual_weight)
    calc.mainloop()


def create_grade_calulator(files):
    for filename in files:
        grade_pairs = SyllabusReader.extract_grade_pairs(filename)
        process_grade_pair(grade_pairs)

#"1302syllabus.pdf", "2041syllabus.html", "4242syllabus.pdf"
create_grade_calulator(["1302syllabus.pdf", "2011syllabus.html"])