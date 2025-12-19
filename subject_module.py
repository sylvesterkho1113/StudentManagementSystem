import xml.etree.ElementTree as ET
import os
from fpdf import FPDF

from student_module import *
from grading_module import *
from rdf_utils import *

# This function is used to clear the screen
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

SUBJECT_FILE = "data/subjects.xml"

def generate_subject_pdf():
    if not os.path.exists(SUBJECT_FILE):
        print("No subject records found.")
        return

    # Programme abbreviation mapping
    programme_map = {
        "Degree in Computer Science (AI)": "BCS(AI)",
        "Degree in Computer Science (ST)": "BCS(ST)",
        "Degree in Computer Science (DCN)": "BCS(DCN)",
        "Degree in Computer Science (BIA)": "BCS(BIA)",
        "For All Programmes": "ALL"
    }

    tree = ET.parse(SUBJECT_FILE)
    root = tree.getroot()

    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Courier", "B", 12)
    pdf.cell(0, 10, "Subject Information", ln=True, align="C")

    # Table Header
    pdf.set_font("Courier", "B", 10)
    headers = ["Subject Code", "Subject Name", "Credit Hour", "Grading", "Programme", "Prerequisite"]
    col_widths = [35, 95, 30, 50, 30, 30] 

    for i in range(len(headers)):
        pdf.cell(col_widths[i], 10, headers[i], 1)
    pdf.ln()

    # Table Rows
    pdf.set_font("Courier", "", 10)
    for subject in root.findall("subject"):
        grading_raw = subject.find("grading").text
        if grading_raw == "G":
            grading_text = "With Grade A, B, C"
        elif grading_raw == "P":
            grading_text = "With Pass/Fail Only"
        else:
            grading_text = "Unknown"

        programme_elem = subject.find("programme")
        programme_full = programme_elem.text.strip() if programme_elem is not None and programme_elem.text else "All"
        programme_short = programme_map.get(programme_full, programme_full)  # Shorten if mapping exists

        prereq_elem = subject.find("prerequisite")
        prerequisite = prereq_elem.text.strip() if prereq_elem is not None and prereq_elem.text else "None"

        row = [
            subject.get("code"),
            subject.find("name").text,
            subject.find("credit").text,
            grading_text,
            programme_short,
            prerequisite
        ]

        for i in range(len(row)):
            pdf.cell(col_widths[i], 10, str(row[i]), 1)
        pdf.ln()

    output_path = "report/subjects_report.pdf"
    pdf.output(output_path)
    print(f"\nPDF generated successfully: {output_path}")

def init_subject_xml():
    if not os.path.exists(SUBJECT_FILE):
        root = ET.Element("subjects")
        tree = ET.ElementTree(root)
        tree.write(SUBJECT_FILE)

def subject_exists(code):
    if not os.path.exists(SUBJECT_FILE):
        return False
    tree = ET.parse(SUBJECT_FILE)
    root = tree.getroot()
    return any(subject.get("code") == code for subject in root.findall("subject"))

def add_subject():
    tree = ET.parse(SUBJECT_FILE)
    root = tree.getroot()

    clear_screen()
    code = input("Enter subject code: ").strip()

    # check if subject code duplicate in XML file
    if subject_exists(code):
        print("Subject code already exists.")
        return

    name = input("Enter subject name: ").strip()

    while True:
        credit = input("Enter credit hour (positive integer only): ").strip()
        if credit.isdigit() and int(credit) > 0:
            break
        else:
            print("Invalid input. Please enter a positive integer.\n")

    # Programme selection
    programmes = {
        '1': "Degree in Computer Science (AI)",
        '2': "Degree in Computer Science (ST)",
        '3': "Degree in Computer Science (DCN)",
        '4': "Degree in Computer Science (BIA)",
        "5": "For All Programmes"
    }

    print("\nSelect programme for this subject:")
    for key, value in programmes.items():
        print(f"{key}. {value}")

    while True:
        prog_choice = input("Select [1-5]: ").strip()
        if prog_choice in programmes:
            programme = programmes[prog_choice]  # convert number to text
            break
        else:
            print("Invalid selection. Please try again.\n")

    # Prerequisite subject
    prereq = input("\nEnter prerequisite subject code (leave blank if none): ").strip()

    while True:
        print("\nEnter grading system")
        print("1. With Grade (exp: A, B, C)")
        print("2. With Pass/Fail Only")
        choice = input("Select [1-2]: ").strip()
        if choice == '1':
            grading = 'G'
            break
        elif choice == '2':
            grading = 'P'
            break
        else:
            print("Invalid selection. Please choose 1 or 2.\n")

    subject = ET.SubElement(root, "subject", code=code)
    ET.SubElement(subject, "name").text = name
    ET.SubElement(subject, "credit").text = credit
    ET.SubElement(subject, "programme").text = programme
    ET.SubElement(subject, "prerequisite").text = prereq if prereq else ""
    ET.SubElement(subject, "grading").text = grading
    
    tree.write(SUBJECT_FILE)
    print("\nSubject", code, "has been added successfully.")

def display_subjects():
    if not os.path.exists(SUBJECT_FILE):
        print("Subject file not found.")
        return

    tree = ET.parse(SUBJECT_FILE)
    root = tree.getroot()

    clear_screen()
    print("\nList of Subjects")
    print("=" * 145)

    if len(root) == 0:
        print("No subjects found.")
        return

    # Table header with new columns
    print(f"{'Code':<10} {'Subject Name':<45} {'Credit Hours':<15} {'Grading System':<20} {'Programme':<35} {'Prerequisite':<15}")
    print("-" * 145)

    for subject in root.findall("subject"):
        code = subject.get("code")
        name = subject.find("name").text
        credit = subject.find("credit").text
        grading = subject.find("grading").text
        programme = subject.find("programme").text if subject.find("programme") is not None else "N/A"
        prereq_elem = subject.find("prerequisite")
        prerequisite = (
            prereq_elem.text.strip() if prereq_elem is not None and prereq_elem.text else "None"
        )
        grading_desc = "With Grade (G)" if grading == "G" else "With Pass/Fail (P)"

        print(f"{code:<10} {name:<45} {credit:<15} {grading_desc:<20} {programme:<35} {prerequisite:<15}")

    print("=" * 145)

def delete_subject(code):
    tree = ET.parse(SUBJECT_FILE)
    root = tree.getroot()
    for subject in root.findall("subject"):
        if subject.attrib['code'] == code:
            root.remove(subject)
            tree.write(SUBJECT_FILE)
            clear_screen()
            print("Subject [",code, "] is deleted.")
            return
    print("Subject not found.")

def subject_menu():
    while True:
        clear_screen()
        print("\n======================================================")
        print("                    Subject Module                    ")
        print("======================================================")
        print("1. Add New Subject\n2. Edit Subject Info\n3. Delete Subject\n4. Display All Subject\n5. Search Subject\n6. Export PDF Student Report\n7. Back to Home Page")
        
        option = str(input("Select an option on the menu [1-7] : "))
        
        # Add New Subject
        if option == '1':
            while True:
                add_subject()
                again = input("Do you want to add another Subject? (y/n): ").strip().lower()
                if again != 'y':
                    break
            clear_screen()    
        # Edit Subject Info
        elif option == '2':
            clear_screen()
            display_subjects()
            code = input("Enter subject code to edit: ")
            edit_subject_by_code(code)
            print("Press any key to back to subject menu...")
            getchar = input()
            clear_screen()
        # Delete Subject
        elif option == '3':
            display_subjects()
            sid = input("Enter subject code to delete: ")
            delete_subject(sid)
            print("Press any key to back to subject menu...")
            getchar = input()
            clear_screen()
        # Display All Subject
        elif option == '4':
            display_subjects()
            print("Press any key to back to subject menu...")
            getchar = input()
            clear_screen()
        # Search Subject
        elif option == '5':
            clear_screen()
            key = input("Enter information to search (Subject Code, Subject Name): ")
            search_subject_by_key(key)
            print("Press any key to back to subject menu...")
            getchar = input()
            clear_screen()
        # Back to home page
        elif option == '6':
            generate_subject_pdf()
            print("Press any key to back to subject menu...")
            getchar = input()
            clear_screen()
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