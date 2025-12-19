import xml.etree.ElementTree as ET
import os
from fpdf import FPDF

from student_module import *
from subject_module import *
from rdf_utils import *
from grading_share_utils import *

# This function is used to clear the screen
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

STUDENT_FILE = "data/students.xml"
SUBJECT_FILE = "data/subjects.xml"
GRADE_FILE = "data/grades.xml"

def generate_result_slip(student_id):
    # Load student info
    stu_tree = ET.parse(STUDENT_FILE)
    stu_root = stu_tree.getroot()
    student = None
    for s in stu_root.findall("student"):
        if s.get("id") == student_id:
            student = s
            break

    if student is None:
        print("Student not found.")
        return

    name = student.find("name").text
    programme = student.find("programme").text
    email = student.find("email").text
    taken_ch = student.find("taken_CH").text
    cgpa = student.find("cgpa").text

    # Load subject info into a dict
    subj_tree = ET.parse(SUBJECT_FILE)
    subj_root = subj_tree.getroot()
    subject_dict = {}
    for subj in subj_root.findall("subject"):
        code = subj.get("code")
        subject_dict[code] = {
            "name": subj.find("name").text,
            "credit": subj.find("credit").text
        }

    # Load grades
    grade_tree = ET.parse(GRADE_FILE)
    grade_root = grade_tree.getroot()
    student_grades = []
    for g in grade_root.findall("grade"):
        if g.get("student_id") == student_id:
            code = g.get("subject_code")
            mark = g.find("mark").text
            grade = g.find("grade_value").text
            subject_name = subject_dict[code]["name"] if code in subject_dict else "Unknown"
            credit = subject_dict[code]["credit"] if code in subject_dict else "0"
            student_grades.append((code, subject_name, credit, mark, grade))

    if not student_grades:
        print("No grades found for this student.")
        return

    # Generate PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Courier", "B", 14)
    pdf.cell(0, 10, "Student Result Slip", ln=True, align="C")

    # Student info
    pdf.set_font("Courier", "", 12)
    pdf.ln(5)
    label_width = 22 
    pdf.cell(0, 10, f"{'Student ID'.ljust(label_width)}: {student_id}", ln=True)
    pdf.cell(0, 10, f"{'Student Name'.ljust(label_width)}: {name}", ln=True)
    pdf.cell(0, 10, f"{'Student Email'.ljust(label_width)}: {email}", ln=True)
    pdf.cell(0, 10, f"{'Programme'.ljust(label_width)}: {programme}", ln=True)
    pdf.cell(0, 10, f"{'Taken Credit Hours'.ljust(label_width)}: {taken_ch}", ln=True)
    pdf.cell(0, 10, f"{'CGPA'.ljust(label_width)}: {cgpa} / 4.00", ln=True)
    pdf.ln(10)

    # Table headers
    pdf.set_font("Courier", "B", 11)
    headers = ["Code", "Subject Name", "Credit Hour", "Mark", "Grade"]
    widths = [30, 80, 30, 20, 20]
    for i in range(len(headers)):
        pdf.cell(widths[i], 10, headers[i], 1)
    pdf.ln()

    # Table rows
    pdf.set_font("Courier", "", 11)
    for row in student_grades:
        for i in range(len(row)):
            pdf.cell(widths[i], 10, str(row[i]), 1)
        pdf.ln()

    output_path = f"report/resultslip_{student_id}.pdf"
    pdf.output(output_path)
    print(f"\nResult slip generated: {output_path}")

def init_grade_xml():
    # check if grade.xml exist
    if not os.path.exists(GRADE_FILE):
        root = ET.Element("grades")
        tree = ET.ElementTree(root)
        tree.write(GRADE_FILE)

def get_students():
    tree = ET.parse(STUDENT_FILE)
    return tree.getroot().findall("student")

def get_subjects():
    tree = ET.parse(SUBJECT_FILE)
    return tree.getroot().findall("subject")

def add_grade():
    students = get_students()
    clear_screen()
    # display all student name and id
    for idx, s in enumerate(students):
        print(f"{idx+1}. {s.get('id')} - {s.find('name').text}")
    #ask for selection
    while True:
        try:
            sidx = int(input("Select student: ")) - 1
            if 0 <= sidx < len(students):
                break
            else:
                print("Invalid number. Please select a valid student number.\n")
        except ValueError:
            print("Invalid input. Please enter a number.\n")

    #once student selected, find its id, name, and programme, and save to variable
    student = students[sidx]
    student_id = student.get("id")
    student_name = student.find("name").text
    student_programme = student.find("programme").text.strip() if student.find("programme") is not None else ""

    clear_screen()
    print(f"\nAdding grades for: {student_name}\n")

    # Filter and classify subjects
    all_subjects = get_subjects()
    eligible_subjects = []
    ineligible_subjects = []  # subjects not passed prerequisites

    for subj in all_subjects:
        subj_prog = subj.find("programme").text.strip() if subj.find("programme") is not None else "For All Programmes"
        if subj_prog not in [student_programme, "For All Programmes", "All"]:
            continue

        prerequisite = subj.find("prerequisite")
        if prerequisite is not None and prerequisite.text and prerequisite.text.strip():
            prereq_code = prerequisite.text.strip()
            if not has_passed(student_id, prereq_code):
                ineligible_subjects.append((subj, prereq_code))
                continue

        eligible_subjects.append(subj)

    # if this student do not have eligible subjects
    if not eligible_subjects:
        print("\nNo eligible subjects found for this student.")
        return

    while True:
        # Re-filter subjects every time to account for newly added grades
        eligible_subjects = []
        ineligible_subjects = []

        for subj in all_subjects:
            subj_prog = subj.find("programme").text.strip() if subj.find("programme") is not None else "For All Programmes"
            if subj_prog not in [student_programme, "For All Programmes", "All"]:
                continue

            prerequisite = subj.find("prerequisite")
            if prerequisite is not None and prerequisite.text and prerequisite.text.strip():
                prereq_code = prerequisite.text.strip()
                if not has_passed(student_id, prereq_code):
                    ineligible_subjects.append((subj, prereq_code))
                    continue

            # Avoid re-adding a subject with existing grade
            grade_tree = ET.parse(GRADE_FILE)
            existing = grade_tree.getroot().find(f"./grade[@student_id='{student_id}'][@subject_code='{subj.get('code')}']")
            if existing is None:
                eligible_subjects.append(subj)

        if not eligible_subjects:
            print("\nNo more eligible subjects available for this student.")
            break

        print("Available subjects:\n")
        for idx, s in enumerate(eligible_subjects):
            print(f"{idx+1}. {s.get('code')}: {s.find('name').text}")

        # prerequisite subject that can't take yet
        if ineligible_subjects:
            print("\nSubjects not shown due to unmet prerequisites:")
            for s, prereq in ineligible_subjects:
                print(f"- {s.get('code')} ({s.find('name').text}) requires {prereq}")

        # ask to select a subject
        try:
            subidx = int(input("\nSelect subject: ")) - 1
            if not (0 <= subidx < len(eligible_subjects)):
                print("Invalid number. Please select a valid subject number.\n")
                continue
        except ValueError:
            print("Invalid input. Please enter a number.\n")
            continue

        subject = eligible_subjects[subidx]
        subject_code = subject.get("code")
        subject_name = subject.find("name").text
        credit_hour = int(subject.find("credit").text)
        grading_type = subject.find("grading").text

        # Check if grade already exists
        grade_tree = ET.parse(GRADE_FILE)
        grade_root = grade_tree.getroot()
        existing = grade_root.find(f"./grade[@student_id='{student_id}'][@subject_code='{subject_code}']")
        # show error if grade already exists
        if existing is not None:
            print(f"\nGrade for {subject_code} already exists for {student_name}.")
            print("Use 'edit marks' to modify it.\n")
            continue

        # ask for mark
        while True:
            mark = input("Enter mark (0-100): ")
            if mark.isdigit() and 0 <= int(mark) <= 100:
                break
            print("Invalid mark. Enter a number between 0 and 100.")

        grade, gpa = calculate_grade(mark, grading_type)

        # Save grade
        record = ET.SubElement(grade_root, "grade", student_id=student_id, subject_code=subject_code)
        ET.SubElement(record, "mark").text = mark
        ET.SubElement(record, "grade_value").text = grade
        ET.SubElement(record, "gpa").text = str(gpa)
        grade_tree.write(GRADE_FILE)

        # Display summary
        clear_screen()
        print("\nMarks Added. Summary below:")
        print(f"Student: {student_name}")
        print("=" * 56)
        print(f"{'Subject Code':<15}{'Mark':<10}{'Grade':<10}{'GPA':<10}{'Credit Hour':<15}")
        print(f"{subject_code:<15}{str(mark) + '%':<10}{grade:<10}{gpa:<10.2f}{credit_hour:<15}")
        print("=" * 56)

        # Update CGPA and display updated info
        update_cgpa(student_id)
        student_tree = ET.parse(STUDENT_FILE)
        for stu in student_tree.getroot().findall("student"):
            if stu.get("id") == student_id:
                cgpa = stu.find("cgpa").text
                taken_CH = stu.find("taken_CH").text
                break

        print(f"\n{'Total Taken Credit Hours':<25}: {taken_CH}")
        print(f"{'Latest CGPA':<25}: {cgpa}")

        again = input(f"\nAdd another mark for {student_name}? (y/n): ").strip().lower()
        if again != 'y':
            break

def display_grades():
    # read from tree
    students = get_students()
    subjects = get_subjects()

    # Create a lookup dictionary for subject details
    subject_dict = {
        s.get("code"): {
            "name": s.find("name").text,
            "credit": s.find("credit").text,
            "grading": s.find("grading").text
        } for s in subjects
    }

    # Load grade records
    grade_tree = ET.parse(GRADE_FILE)
    grade_root = grade_tree.getroot()

    clear_screen()
    print("Display All Marks")
    print("Notes: Pass/Fail subject won't be included in the calculation of CGPA")
    
    for idx, student in enumerate(students, start=1):
        student_id = student.get("id")
        student_name = student.find("name").text
        taken_CH = student.find("taken_CH").text
        cgpa = student.find("cgpa").text

        grades_found = False
        for record in grade_root.findall(f"./grade[@student_id='{student_id}']"):
            grades_found = True

        if grades_found == True:
            print("-" * 105)
            print(f" {student_id}: {student_name:<61}  Total Credit Hours: {taken_CH:<2}, CGPA: {cgpa}")
            print("-" * 105)
            print(f"{'Code':<10}{'Subject Name':<45}{'Credit Hours':<15}{'Grade Mode':<14}{'Mark':<8}{'Grade':<8}{'GPA':<8}")

        for record in grade_root.findall(f"./grade[@student_id='{student_id}']"):
            grades_found = True
            subject_code = record.get("subject_code")
            subject = subject_dict.get(subject_code)

            if subject:
                subject_name = subject["name"]
                credit = subject["credit"]
                raw_grading = subject["grading"].strip().upper()
                if raw_grading == "G":
                    grading = "With Grade"
                elif raw_grading in ("P", "PASS/FAIL"):
                    grading = "Pass/Fail Only"
                else:
                    grading = raw_grading
            else:
                # for abnormal row
                subject_name = "N/A"
                credit = "?"
                grading = "?"

            mark = record.find("mark").text
            grade = record.find("grade_value").text
            gpa = f"{float(record.find('gpa').text):.2f}"

            print(f"{subject_code:<10}{subject_name:<45}{credit:<15}{grading:<14}{mark:<8}{grade:<8}{gpa:<8}")

    print("-" * 105)

def grading_menu():
    while True:
        clear_screen()
        print("\n======================================================")
        print("                    Grading Module                    ")
        print("======================================================")
        print("1. Add Marks\n2. Edit Marks\n3. Display All Marks\n4. Search Marks\n5. Grading Dashboard\n6. Export Student Result Slip\n7. Back to Home Page")
        
        option = str(input("Select an option on the menu [1-7] : "))
        
        # Add marks
        if option == '1':
            while True:
                add_grade()
                again = input("Do you want to continue add marks for other student? (y/n): ").strip().lower()
                if again != 'y':
                    break
            clear_screen()    
        # Edit marks
        elif option == '2':
            clear_screen()
            display_grades()
            ID = input("Enter Student ID to edit: ")
            code = input("Enter Subject Code to edit: ")
            edit_grade(ID, code)
            print("Press any key to back to grading menu...")
            getchar = input()
            clear_screen()
        # Display marks
        elif option == '3':
            display_grades()
            print("Press any key to back to grading menu...")
            getchar = input()
            clear_screen()
        # Search marks
        elif option == '4':
            clear_screen()
            key = input("Enter information to search (student ID, subject code): ")
            search_grade_by_key(key)
            print("Press any key to back to grading menu...")
            getchar = input()
            clear_screen()
        # Grading dashboard
        elif option == '5':
            clear_screen()
            print("=" * 60)
            print("Grading Dashboard")
            print("=" * 60)
            show_top_3_students()
            show_student_summary()
            show_failure_insight()
            print("Press any key to back to grading menu...")
            getchar = input()
            clear_screen()
        # Generate Result slip
        elif option == '6':
            clear_screen()
            print("\nGenerate Result Slip")
            print("=" * 60)
            sid = input("Enter Student ID: ")
            generate_result_slip(sid)
            print("Press any key to back to grading menu...")
            getchar = input()
            clear_screen()
        # Back to home page
        elif option == '7':
            break
        # Invalid option
        else:
            print("Invalid code, please try again. Press any key to continue...")
            getchar = input()
            clear_screen()

# If this file is executed, redirect to main.py
if __name__ == "__main__":
    import main
    main.main()