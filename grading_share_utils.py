# for functions needed by both grading_module.py and rdf_utils.py

import xml.etree.ElementTree as ET
import os

from student_module import *
from subject_module import *
from rdf_utils import *

# This function is used to clear the screen
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

STUDENT_FILE = "data/students.xml"
SUBJECT_FILE = "data/subjects.xml"
GRADE_FILE = "data/grades.xml"

def calculate_grade(mark, grading_type):
    mark = int(mark)

    if grading_type == 'G':
        if 90 <= mark <= 100:
            return 'A+', 4.00
        elif 80 <= mark < 90:
            return 'A', 4.00
        elif 79 <= mark < 80:
            return 'A-', 3.93
        elif 78 <= mark < 79:
            return 'A-', 3.87
        elif 77 <= mark < 78:
            return 'A-', 3.80
        elif 76 <= mark < 77:
            return 'A-', 3.73
        elif 75 <= mark < 76:
            return 'A-', 3.67
        elif 74 <= mark < 75:
            return 'B+', 3.60
        elif 73 <= mark < 74:
            return 'B+', 3.53
        elif 72 <= mark < 73:
            return 'B+', 3.47
        elif 71 <= mark < 72:
            return 'B+', 3.40
        elif 70 <= mark < 71:
            return 'B+', 3.33
        elif 69 <= mark < 70:
            return 'B', 3.27
        elif 68 <= mark < 69:
            return 'B', 3.20
        elif 67 <= mark < 68:
            return 'B', 3.13
        elif 66 <= mark < 67:
            return 'B', 3.07
        elif 65 <= mark < 66:
            return 'B', 3.00
        elif 64 <= mark < 65:
            return 'B-', 2.93
        elif 63 <= mark < 64:
            return 'B-', 2.87
        elif 62 <= mark < 63:
            return 'B-', 2.80
        elif 61 <= mark < 62:
            return 'B-', 2.73
        elif 60 <= mark < 61:
            return 'B-', 2.67
        elif 59 <= mark < 60:
            return 'C+', 2.59
        elif 58 <= mark < 59:
            return 'C+', 2.53
        elif 57 <= mark < 58:
            return 'C+', 2.46
        elif 56 <= mark < 57:
            return 'C+', 2.40
        elif 55 <= mark < 56:
            return 'C+', 2.33
        elif 54 <= mark < 55:
            return 'C', 2.26
        elif 53 <= mark < 54:
            return 'C', 2.20
        elif 52 <= mark < 53:
            return 'C', 2.13
        elif 51 <= mark < 52:
            return 'C', 2.07
        elif 50 <= mark < 51:
            return 'C', 2.00
        elif 47 <= mark < 50:
            return 'C-', 1.67
        elif 44 <= mark < 47:
            return 'D+', 1.33
        elif 40 <= mark < 44:
            return 'D', 1.00
        elif 0 <= mark < 40:
            return 'F', 0.00
        else:
            return 'Invalid', 0.00
    else:
        if mark >= 40:
            return 'PASS', 4.00
        else:
            return 'FAIL', 0.00

def update_cgpa(student_id):
    grade_tree = ET.parse(GRADE_FILE)
    subject_tree = ET.parse(SUBJECT_FILE)
    student_tree = ET.parse(STUDENT_FILE)

    # find grade of the student
    grades = [
        g for g in grade_tree.getroot().findall("grade")
        if g.get("student_id") == student_id
    ]

    total_points = 0.0
    total_credits = 0 # for CGPA calculation (only grading type = 'G')
    all_credits = 0 # total taken credit hours (includes P and G)

    for grade in grades:
        #find gpa for each subject
        subject_code = grade.get("subject_code")
        gpa = float(grade.find("gpa").text)

        # Get subject's credit hour and grading type
        subject = next((s for s in subject_tree.getroot().findall("subject") if s.get("code") == subject_code), None)
        if subject is None:
            continue

        #find credit hour and grading type
        credit_hour = int(subject.find("credit").text)
        grading_type = subject.find("grading").text

        all_credits += credit_hour  # count for both G and P -> this is to store in students.xml

        if grading_type == 'G':
            total_points += gpa * credit_hour
            total_credits += credit_hour #-> this is for cgpa calculation only

    new_cgpa = total_points / total_credits if total_credits > 0 else 0.0

    # Update student info in xml
    for stu in student_tree.getroot().findall("student"):
        if stu.get("id") == student_id:
            stu.find("cgpa").text = f"{new_cgpa:.2f}"
            stu.find("taken_CH").text = str(all_credits)
            
            # Update cgpa_CH element
            cgpa_ch_elem = stu.find("cgpa_CH")
            if cgpa_ch_elem is None:
                cgpa_ch_elem = ET.SubElement(stu, "cgpa_CH")
            cgpa_ch_elem.text = str(total_credits)
            break

    # write to the file
    student_tree.write(STUDENT_FILE)

def has_passed(student_id, subject_code):
    # Return True if the student passed the given subject_code.
    grade_tree = ET.parse(GRADE_FILE)
    for g in grade_tree.getroot().findall("grade"):
        if g.get("student_id") == student_id and g.get("subject_code") == subject_code:
            grade = g.find("grade_value").text.upper()
            #return true is grade is not F
            return grade != "F"
    return False

# If this file is executed, redirect to main.py
if __name__ == "__main__":
    import main
    main.main()