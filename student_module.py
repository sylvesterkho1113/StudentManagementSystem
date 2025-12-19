import xml.etree.ElementTree as ET
import os
from fpdf import FPDF

from subject_module import *
from grading_module import *
from rdf_utils import *

# This function is used to clear the screen
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

STUDENT_FILE = "data/students.xml"

def generate_student_pdf():
    if not os.path.exists(STUDENT_FILE):
        print("No student records found.")
        return

    tree = ET.parse(STUDENT_FILE)
    root = tree.getroot()

    pdf = FPDF()
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Courier", "B", 12)
    pdf.cell(0, 10, "Student Information", ln=True, align="C")

    # Table Header
    pdf.set_font("Courier", "B", 10)
    headers = ["ID", "Name", "Programme", "Email", "Taken CH", "CGPA"]
    col_widths = [20, 55, 70, 85, 20, 20]
    
    for i in range(len(headers)):
        pdf.cell(col_widths[i], 10, headers[i], 1)
    pdf.ln()

    # Table Rows
    pdf.set_font("Courier", "", 10)
    for student in root.findall("student"):
        row = [
            student.get("id"),
            student.find("name").text,
            student.find("programme").text,
            student.find("email").text,
            student.find("taken_CH").text,
            student.find("cgpa").text
        ]
        for i in range(len(row)):
            pdf.cell(col_widths[i], 10, str(row[i]), 1)
        pdf.ln()

    output_path = "report/students_report.pdf"
    pdf.output(output_path)
    print(f"\nPDF generated successfully: {output_path}")

def init_student_xml():
    if not os.path.exists(STUDENT_FILE):
        root = ET.Element("students")
        tree = ET.ElementTree(root)
        tree.write(STUDENT_FILE)

def add_student():
    tree = ET.parse(STUDENT_FILE)
    root = tree.getroot()

    clear_screen()
    sid = f"S{len(root) + 1:03}"
    name = input("Enter student name: ")
    programmes = {
        '1': "Degree in Computer Science (AI)",
        '2': "Degree in Computer Science (ST)",
        '3': "Degree in Computer Science (DCN)",
        '4': "Degree in Computer Science (BIA)"
    }

    print("\nSelect student's programme:")
    for key, value in programmes.items():
        print(f"{key}. {value}")
    
    while True:
        choice = input("Enter number [1-4]: ").strip()
        if choice in programmes:
            prog = programmes[choice]
            break
        else:
            print("Invalid code, please try again.\n")
    
    email = input("Enter student email: ")
    
    student = ET.SubElement(root, "student", id=sid)
    ET.SubElement(student, "name").text = name
    ET.SubElement(student, "programme").text = prog
    ET.SubElement(student, "email").text = email
    ET.SubElement(student, "taken_CH").text = "0"
    ET.SubElement(student, "cgpa").text = "0.00"
    ET.SubElement(student, "cgpa_CH").text = "0" # used to calculate cgpa as pass/fail subject wont count in CGPA calculation
    
    tree.write(STUDENT_FILE)
    print("---------------------------------")
    print("Student is added with ID:", sid)
    print("---------------------------------")
    load_students_to_graph("data/students.xml")

def display_students():
    if not os.path.exists(STUDENT_FILE):
        print("No student records found.")
        return
    
    tree = ET.parse(STUDENT_FILE)
    root = tree.getroot()

    clear_screen()
    print("-" * 115)
    print(f"{'ID':<10}{'Name':<20}{'Programme':<35}{'Email':<35}{'Taken CH':<10}{'CGPA':<6}")
    print("-" * 115)

    for student in root.findall("student"):
        sid = student.get("id")
        name = student.find("name").text
        programme = student.find("programme").text
        email = student.find("email").text
        CH = student.find("taken_CH").text
        cgpa = student.find("cgpa").text
        print(f"{sid:<10}{name:<20}{programme:<35}{email:<35}{CH:<10}{cgpa:<6}")

    print("-" * 115)

def delete_student(student_id):
    tree = ET.parse(STUDENT_FILE)
    root = tree.getroot()
    for student in root.findall("student"):
        if student.attrib['id'] == student_id:
            root.remove(student)
            tree.write(STUDENT_FILE)
            print("Student deleted.")
            load_students_to_graph("data/students.xml")
            return
    print("Student not found.")

def student_menu():
    while True:
        clear_screen()
        print("\n======================================================")
        print("                    Student Module                    ")
        print("======================================================")
        print("1. Add New Student\n2. Edit Student Info\n3. Delete Student\n4. Display All Student\n5. Search Student\n6. Export PDF Student Report\n7. Recommend Subject for Student\n8. Back to Home Page")
        
        option = str(input("Select an option on the menu [1-8] : "))
        
        # Add New Student
        if option == '1':
            while True:
                add_student()
                again = input("Do you want to add another student? (y/n): ").strip().lower()
                if again != 'y':
                    break
            clear_screen()    
        # Edit Student Info
        elif option == '2':
            clear_screen()
            display_students()
            sid = input("Enter student ID to edit: ")
            edit_student_by_id(sid)
            print("Press any key to back to student menu...")
            getchar = input()
            clear_screen()
        # Delete Student
        elif option == '3':
            display_students()
            sid = input("Enter student ID to delete: ")
            delete_student(sid)
            print("Press any key to back to student menu...")
            getchar = input()
            clear_screen()
        # Display All Student
        elif option == '4':
            display_students()
            print("Press any key to back to student menu...")
            getchar = input()
            clear_screen()
        # Search Student
        elif option == '5':
            clear_screen()
            key = input("Enter information to search (SID, Student Name, Student Email, Programme): ")
            search_student_by_key(key)
            print("Press any key to back to student menu...")
            getchar = input()
            clear_screen()
        # Export PDF Report
        elif option == '6':
            generate_student_pdf()
            input("Press any key to return to student menu...")
            clear_screen()
        elif option == '7':
            clear_screen()
            key = input("Enter Student ID: ")
            recommend_subjects_rdf(key)
            print("\nPress any key to back to student menu...")
            getchar = input()
            clear_screen()
        # Back to home page
        elif option == '8':
            break
        else:
            print("Invalid code, please try again. Press any key to continue...")
            getchar = input()
            clear_screen()

# If this file is executed, redirect to main.py
if __name__ == "__main__":
    import main
    main.main()