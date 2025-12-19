from rdflib import Graph, Namespace, Literal, RDF, URIRef
import xml.etree.ElementTree as ET
import os

from student_module import *
from subject_module import *
from grading_module import *
from grading_share_utils import *

STUDENT_FILE = "data/students.xml"
SUBJECT_FILE = "data/subjects.xml"
GRADE_FILE = "data/grades.xml"

# This function is used to clear the screen
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

EX = Namespace("http://example.org/")

#student module

def load_students_to_graph(xml_file):
    g = Graph()
    EXs = Namespace("http://example.org/student/")
    tree = ET.parse(xml_file)
    root = tree.getroot()
    for s in root.findall("student"):
        sid = URIRef(EXs[s.get("id")])
        g.add((sid, RDF.type, EXs.Student))
        g.add((sid, EXs.name, Literal(s.find("name").text)))
        g.add((sid, EXs.programme, Literal(s.find("programme").text)))
        g.add((sid, EXs.email, Literal(s.find("email").text)))
        g.add((sid, EXs.cgpa, Literal(s.find("cgpa").text)))

    # Save the graph to an RDF file
    g.serialize("data/students.rdf", "xml")

    return g

def search_student_by_key(keyword):
    g = load_students_to_graph("data/students.xml")
    keyword = keyword.lower()

    q = f"""
    PREFIX ex: <http://example.org/student/>

    SELECT ?id ?name ?programme ?email ?cgpa
    WHERE {{
        ?id a ex:Student ;
            ex:name ?name ;
            ex:programme ?programme ;
            ex:email ?email ;
            ex:cgpa ?cgpa .
        FILTER(
            CONTAINS(LCASE(STR(?name)), "{keyword}") ||
            CONTAINS(LCASE(STR(?programme)), "{keyword}") ||
            CONTAINS(LCASE(STR(?email)), "{keyword}") ||
            CONTAINS(LCASE(STR(?id)), "{keyword}")
        )
    }}
    """

    results = list(g.query(q))
    clear_screen()
    
    if results:
        print("Search result that match \"",keyword,"\":")
        print("-" * 105)
        print(f"{'ID':<10}{'Name':<20}{'Programme':<35}{'Email':<35}{'CGPA':<10}")
        print("-" * 105)
        for row in results:
            student_id = row.id.split("/")[-1]
            print(f"{student_id:<10}{row.name:<20}{row.programme:<35}{row.email:<35}{row.cgpa:<10}")
        print("-" * 105)
    else:
        print("No student found with that keyword.")

def edit_student_by_id(student_id, xml_file="data/students.xml"):
    if not os.path.exists(xml_file):
        print("Student XML file not found.")
        return

    tree = ET.parse(xml_file)
    root = tree.getroot()

    programmes = {
        '1': "Degree in Computer Science (AI)",
        '2': "Degree in Computer Science (ST)",
        '3': "Degree in Computer Science (DCN)",
        '4': "Degree in Computer Science (BIA)"
    }

    for student in root.findall("student"):
        if student.get("id") == student_id:
            print(f"\nEditing student {student_id}")

            current_name = student.find("name").text
            current_programme = student.find("programme").text
            current_email = student.find("email").text

            print(f"Current name: {current_name}")
            new_name = input("New name (leave blank to keep): ")
            if new_name.strip():
                student.find("name").text = new_name

            print(f"Current programme: {current_programme}")
            print("\nSelect new programme (leave blank to keep current):")
            for key, value in programmes.items():
                print(f"{key}. {value}")

            new_programme_choice = input("Enter option number [1-4] or leave blank: ").strip()
            if new_programme_choice in programmes:
                student.find("programme").text = programmes[new_programme_choice]

            print(f"Current email: {current_email}")
            new_email = input("New email (leave blank to keep): ")
            if new_email.strip():
                student.find("email").text = new_email

            tree.write(xml_file)
            print("Student record updated.")
            load_students_to_graph("data/students.xml")
            return

    print("Student ID not found.")

#Subject Module

def load_subjects_to_graph():
    g = Graph()
    g.bind("ex", EX)

    if not os.path.exists(SUBJECT_FILE):
        return g

    tree = ET.parse(SUBJECT_FILE)
    root = tree.getroot()

    for subj in root.findall("subject"):
        code = subj.get("code")
        name = subj.find("name").text
        credit = subj.find("credit").text
        programme = subj.find("programme").text if subj.find("programme") is not None else "For All Programmes"
        prereq_elem = subj.find("prerequisite")
        prerequisite = prereq_elem.text if prereq_elem is not None else None

        subj_uri = URIRef(f"http://example.org/subject/{code}")

        g.add((subj_uri, RDF.type, EX.Subject))
        g.add((subj_uri, EX.code, Literal(code)))
        g.add((subj_uri, EX.name, Literal(name)))
        g.add((subj_uri, EX.credit, Literal(credit)))
        g.add((subj_uri, EX.programme, Literal(programme)))

        if prerequisite and prerequisite.strip():
            g.add((subj_uri, EX.prerequisite, Literal(prerequisite.strip())))

    # Save the graph to an RDF file
    g.serialize("data/subjects.rdf", "xml")

    return g

def search_subject_by_key(key):
    g = load_subjects_to_graph()
    q = f"""
    SELECT ?code ?name ?credit ?programme ?prerequisite
    WHERE {{
        ?s a <http://example.org/Subject> ;
           <http://example.org/code> ?code ;
           <http://example.org/name> ?name ;
           <http://example.org/credit> ?credit ;
           <http://example.org/programme> ?programme.
        OPTIONAL {{ ?s <http://example.org/prerequisite> ?prerequisite. }}

        FILTER(
            CONTAINS(LCASE(STR(?code)), LCASE("{key}")) ||
            CONTAINS(LCASE(STR(?name)), LCASE("{key}"))
        )
    }}
    """
    results = list(g.query(q))
    
    if results:
        print(f'Search results that match "{key}":')
        print("-" * 110)
        print(f"{'Code':<10}{'Name':<30}{'Credit Hour':<13}{'Programme':<35}{'Prerequisite':<20}")
        print("-" * 110)
        for row in results:
            prerequisite = row.prerequisite.split("/")[-1] if row.prerequisite else "None"
            print(f"{row.code:<10}{row.name:<30}{row.credit:<13}{row.programme:<35}{prerequisite:<20}")
        print("-" * 110)
    else:
        print("No subject found with that keyword.")

def edit_subject_by_code(code):
    tree = ET.parse(SUBJECT_FILE)
    root = tree.getroot()

    for subject in root.findall("subject"):
        if subject.attrib['code'] == code:
            clear_screen()
            print("Reminder: Subject code can't be changed. If you wish to do so, please delete the subject instead.")
            print("        : Leave input empty to keep the existing value.")

            current_name = subject.find("name").text
            current_credit = subject.find("credit").text
            current_grading = subject.find("grading").text
            current_programme = subject.find("programme").text if subject.find("programme") is not None else "Not Set"
            current_prereq = subject.find("prerequisite").text if subject.find("prerequisite") is not None else ""

            name = input(f"\nEnter new name (current: {current_name}): ").strip()
            if name:
                subject.find("name").text = name

            while True:
                credit = input(f"Enter new credit hour (current: {current_credit}): ").strip()
                if not credit:
                    break
                elif credit.isdigit() and int(credit) > 0:
                    subject.find("credit").text = credit
                    break
                else:
                    print("Invalid credit hour. Must be a positive integer.")

            grading_display = "With Grade (A, B, C)" if current_grading == 'G' else "Pass/Fail"
            print(f"\nCurrent grading system: {grading_display}")
            print("Enter new grading system (leave empty to keep current):")
            print("1. With Grade (e.g., A, B, C)")
            print("2. Pass/Fail Only")
            while True:
                choice = input("Select [1-2]: ").strip()
                if not choice:
                    break
                elif choice == '1':
                    subject.find("grading").text = 'G'
                    break
                elif choice == '2':
                    subject.find("grading").text = 'P'
                    break
                else:
                    print("Invalid selection. Please choose 1 or 2.\n")

            # Programme selection
            print(f"\nCurrent programme: {current_programme}")
            programmes = ["Degree in Computer Science (AI)", "Degree in Computer Science (ST)", "Degree in Computer Science (DCN)", "Degree in Computer Science (BIA)", "For All Programmes"]
            for idx, prog in enumerate(programmes, start=1):
                print(f"{idx}. {prog}")
            prog_choice = input("Select new programme [1-5] (leave blank to keep current): ").strip()
            if prog_choice.isdigit() and 1 <= int(prog_choice) <= len(programmes):
                selected_prog = programmes[int(prog_choice) - 1]
                if subject.find("programme") is None:
                    ET.SubElement(subject, "programme").text = selected_prog
                else:
                    subject.find("programme").text = selected_prog

            # Prerequisite subject
            print(f"\nCurrent prerequisite subject: {current_prereq or 'None'}")
            new_prereq = input("Enter new prerequisite subject code (leave blank for none): ").strip()
            if new_prereq:
                if subject.find("prerequisite") is None:
                    ET.SubElement(subject, "prerequisite").text = new_prereq
                else:
                    subject.find("prerequisite").text = new_prereq
            else:
                if subject.find("prerequisite") is not None:
                    subject.remove(subject.find("prerequisite"))

            # Save changes
            tree.write(SUBJECT_FILE)

            # Show updated info
            clear_screen()
            print("\nSubject updated successfully. Latest information:")
            print("-" * 60)
            print(f"Code        : {subject.attrib['code']}")
            print(f"Name        : {subject.find('name').text}")
            print(f"Credit Hour : {subject.find('credit').text}")
            updated_grading = subject.find("grading").text
            grading_text = "With Grade (A, B, C)" if updated_grading == 'G' else "Pass/Fail Only"
            print(f"Grading     : {grading_text}")
            print(f"Programme   : {subject.find('programme').text}")
            updated_prereq = subject.find('prerequisite').text if subject.find('prerequisite') is not None else "None"
            print(f"Prerequisite: {updated_prereq}")
            print("-" * 60)
            return

    print("Subject code not found.")

# Grading module

def load_grades_to_graph():
    G = Graph()
    GR = Namespace("http://example.org/grade#")

    # read from grade.xml file
    tree = ET.parse(GRADE_FILE)
    root = tree.getroot()

    for grade in root.findall("grade"):
        sid = grade.get("student_id")
        subject_code = grade.get("subject_code")
        mark = grade.find("mark").text
        grade_val = grade.find("grade_value").text
        gpa = grade.find("gpa").text

        # add to RDF graph
        grade_uri = URIRef(f"http://example.org/grade/{sid}_{subject_code}")
        G.add((grade_uri, RDF.type, GR.Grade))
        G.add((grade_uri, GR.student_id, Literal(sid)))
        G.add((grade_uri, GR.subject_code, Literal(subject_code)))
        G.add((grade_uri, GR.mark, Literal(mark)))
        G.add((grade_uri, GR.grade_value, Literal(grade_val)))
        G.add((grade_uri, GR.gpa, Literal(gpa)))

    # Save the graph to an RDF file
    G.serialize("data/grades.rdf", "xml")

    return G

def edit_grade(student_id, subject_code):
    grades_file = GRADE_FILE

    if not os.path.exists(grades_file):
        print("grades.xml file not found.")
        return

    tree = ET.parse(grades_file)
    root = tree.getroot()

    found = False
    for grade in root.findall("grade"):
        if grade.get("student_id") == student_id and grade.get("subject_code") == subject_code:
            found = True
            current_mark = grade.find("mark").text
            print(f"Current mark: {current_mark}")
            new_mark = input("Enter new mark: ").strip()

            if not new_mark.isdigit() or not (0 <= int(new_mark) <= 100):
                print("Invalid mark. Please enter a number between 0 and 100.")
                return

            # Get grading type from subjects.xml
            grading_type = None
            subject_tree = ET.parse(SUBJECT_FILE)
            subject_root = subject_tree.getroot()
            for sub in subject_root.findall("subject"):
                if sub.get("code") == subject_code:
                    grading_type = sub.find("grading").text
                    break

            if grading_type is None:
                print("Grading type not found for the subject.")
                return
            
            grade_val, gpa = calculate_grade(new_mark, grading_type)

            # Update values in XML
            grade.find("mark").text = new_mark
            grade.find("grade_value").text = grade_val
            grade.find("gpa").text = str(gpa)

            tree.write(grades_file)
            update_cgpa(student_id)
            print("Grade updated successfully, please find below for reference.")

            # Re-fetch student to get updated CGPA and CH
            if not os.path.exists(STUDENT_FILE):
                print("students.xml file not found.")
                return

            student_tree = ET.parse(STUDENT_FILE)
            student_root = student_tree.getroot()

            for stu in student_root.findall("student"):
                if stu.get("id") == student_id:
                    cgpa = stu.find("cgpa").text
                    taken_CH = stu.find("taken_CH").text
                    break
            else:
                print("Student not found.")
                return

            # Get credit hour from subjects.xml
            if not os.path.exists(SUBJECT_FILE):
                print("subjects.xml file not found.")
                return

            subject_tree = ET.parse(SUBJECT_FILE)
            subject_root = subject_tree.getroot()

            credit_hour = "N/A"
            for subject in subject_root.findall("subject"):
                if subject.get("code") == subject_code:
                    credit_hour = subject.find("credit").text
                    break

            # Display summary
            clear_screen()
            print("\nGrade Summary for [",student_id,"]:")
            print("=" * 56)
            print(f"{'Subject Code':<15}{'Mark':<10}{'Grade':<10}{'GPA':<10}{'Credit Hour':<15}")
            print(f"{subject_code:<15}{str(new_mark) + '%':<10}{grade_val:<10}{gpa:<10.2f}{credit_hour:<15}")
            print("=" * 56)

            # Display CGPA & CH
            print(f"\n{'Total Taken Credit Hours':<25}: {taken_CH}")
            print(f"{'Latest CGPA':<25}: {cgpa}")
            break

    if not found:
        print("Grade not found for the given student ID and subject code.")

def search_grade_by_key(key):
    G = load_grades_to_graph()
    GR = Namespace("http://example.org/grade#")

    query = f"""
    PREFIX gr: <http://example.org/grade#>

    SELECT ?student_id ?subject_code ?mark ?grade_value ?gpa
    WHERE {{
        ?grade a gr:Grade ;
               gr:student_id ?student_id ;
               gr:subject_code ?subject_code ;
               gr:mark ?mark ;
               gr:grade_value ?grade_value ;
               gr:gpa ?gpa .

        FILTER (CONTAINS(LCASE(STR(?student_id)), LCASE("{key}")) ||
                CONTAINS(LCASE(STR(?subject_code)), LCASE("{key}")))
    }}
    """

    # run the query
    results = list(G.query(query))

    clear_screen()
    print(f"\nSearching for grades related to: {key}")
    if results:
        print("=" * 70)
        print(f"{'Student ID':<15}{'Subject Code':<15}{'Mark':<10}{'Grade':<10}{'GPA':<10}")
        print("=" * 70)
        for row in results:
            # Format mark with % and gpa with 2 decimal places
            try:
                mark = f"{int(row.mark)}%"
            except:
                mark = row.mark
            try:
                gpa = f"{float(row.gpa):.2f}"
            except:
                gpa = row.gpa

            print(f"{row.student_id:<15}{row.subject_code:<15}{mark:<10}{row.grade_value:<10}{gpa:<10}")
        print("=" * 70)
    else:
        print("No matching grade records found.")

def recommend_subjects_rdf(student_id):
    EX = Namespace("http://example.org/")
    EXS = Namespace("http://example.org/student/")

    GRADE_FILE = "xml/grade.xml"

    g = Graph()
    g.parse("data/subjects.rdf", format="xml")
    g.parse("data/students.rdf", format="xml")

    student_uri = EXS[student_id]

    # Step 1: Get student's programme
    student_prog_query = f"""
    PREFIX stu: <http://example.org/student/>

    SELECT ?programme WHERE {{
        stu:{student_id} stu:programme ?programme .
    }}
    """
    res = g.query(student_prog_query)
    programme = None
    for row in res:
        programme = str(row.programme)
        break

    if programme is None:
        print(f"No programme found for student {student_id}.")
        return

    # Step 2: Query all eligible subjects (matching programme & passed prerequisite)
    query = f"""
    PREFIX : <http://example.org/>
    PREFIX stu: <http://example.org/student/>

    SELECT ?subject ?code ?name
    WHERE {{
        ?subject a :Subject ;
                 :programme ?prog ;
                 :code ?code ;
                 :name ?name .

        FILTER(?prog = "{programme}" || ?prog = "For All Programmes")

        OPTIONAL {{ ?subject :prerequisite ?prereq . }}

        FILTER NOT EXISTS {{
            ?subject :prerequisite ?prereq .
            FILTER NOT EXISTS {{ stu:{student_id} :hasPassed ?prereq . }}
        }}
    }}
    ORDER BY ?code
    """

    results = g.query(query)

    # Step 3: Filter out already-passed subjects using your XML logic
    recommended = []
    for row in results:
        subject_code = str(row.code)
        if not has_passed(student_id, subject_code):
            recommended.append((subject_code, str(row.name)))

    # Step 4: Display
    print(f"\n")
    print("-" * 70)
    print(f"Recommended subjects for {student_id} ({programme}):")
    print("-" * 70)
    if not recommended:
        print("No eligible subjects found.\n")
        return

    for code, name in recommended:
        print(f"{code}: {name}")

# Dashboard

def show_top_3_students():
    g = load_students_to_graph("data/students.xml")

    query = """
    PREFIX stud: <http://example.org/student/>

    SELECT ?s ?name ?cgpa
    WHERE {
        ?s a stud:Student ;
           stud:name ?name ;
           stud:cgpa ?cgpa .
    }
    ORDER BY DESC(xsd:decimal(?cgpa))
    LIMIT 3
    """

    # load the query
    results = list(g.query(query, initNs={"xsd": Namespace("http://www.w3.org/2001/XMLSchema#")}))

    print("\nTop 3 Students by CGPA")
    print("-" * 60)
    print(f"{'ID':<10}{'Name':<25}{'CGPA':<10}")
    print("-" * 60)
    for row in results:
        student_id = row.s.split("/")[-1]
        print(f"{student_id:<10}{row.name:<25}{float(row.cgpa):<10.2f}")

def show_student_summary():
    g = load_students_to_graph("data/students.xml")

    query = """
    PREFIX stud: <http://example.org/student/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT (COUNT(?s) AS ?total) (AVG(xsd:decimal(?cgpa)) AS ?average)
    WHERE {
        ?s a stud:Student ;
           stud:cgpa ?cgpa .
    }
    """

    # load the query
    results = list(g.query(query))

    for row in results:
        print("\nStudent Summary")
        print("-" * 60)
        print(f"Total Students      : {row.total}")
        print(f"Average CGPA        : {float(row.average):.2f}")

def show_failure_insight():
    g = load_grades_to_graph()

    query = """
    PREFIX gr: <http://example.org/grade#>

    SELECT ?subject_code (COUNT(?g) AS ?failures)
    WHERE {
        ?g a gr:Grade ;
           gr:subject_code ?subject_code ;
           gr:gpa ?gpa .
        FILTER(xsd:float(?gpa) <= 0.0)
    }
    GROUP BY ?subject_code
    ORDER BY DESC(?failures)
    LIMIT 1
    """

    # load the query
    results = list(g.query(query, initNs={"xsd": Namespace("http://www.w3.org/2001/XMLSchema#")}))
    
    for row in results:
        print("\nSubject with Highest Failure Rate")
        print("-" * 60)
        print(f"Subject Code        : {row.subject_code}")
        print(f"Failure Count       : {row.failures}\n")

# If this file is executed, redirect to main.py
if __name__ == "__main__":
    import main
    main.main()