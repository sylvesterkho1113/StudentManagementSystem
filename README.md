# 🧑🏻‍🎓 Student Management System using Semantic Web Technology

A comprehensive and modern **Student Management System** that leverages semantic web technologies including **XML, RDF**, and **SPARQL**. Fully implemented in Python, this project showcases how semantic web standards can be applied to real-world educational data management to provide intelligent querying, reporting, and reasoning capabilities.

---

## 🛠️ Key Features

- **Data Management with XML:** Seamlessly manage student profiles and subject records using XML as the foundational storage structure.
- **Grades & CGPA Calculation:** Store and update student grades while automatically calculating CGPA based on course credit hours and grading systems.
- **Semantic Reasoning (SPARQL & RDF):** Utilize RDF graphs and execute SPARQL queries to intelligently recommend subjects based on a student's academic programme and prerequisite completion status.
- **Automated Reporting:** Generate professional, downloadable PDF reports (such as result slips) automatically using the `fpdf` library.
- **Interactive CLI:** An easy-to-navigate command-line interface that provides direct access to the Student, Subject, and Grading modules.

---

## 📂 Project Structure

```text
StudentManagementSystem/
├── main.py                 # Main entry point. Provides a menu to access student, subject, grading, and reporting modules.
├── student_module.py       # Handles student-related operations (add, display, delete).
├── subject_module.py       # Manages subjects, prerequisite checks, and filtering by programme.
├── grading_module.py       # Allows grade entry, GPA calculation, CGPA update, and eligibility filtering.
├── rdf_utils.py            # Converts XML data into RDF graphs and executes SPARQL queries.
├── grading_share_utils.py  # Shared utility functions used by both rdf_utils and grading_module.
├── data/                   # Directory where generated XML and RDF files are stored.
│   ├── grades.xml / .rdf
│   ├── subjects.xml / .rdf
│   └── students.xml / .rdf
└── report/                 # Directory where system-generated PDF reports and result slips are saved.
```

---

## 🚀 Getting Started

### Prerequisites
Make sure you have Python installed on your system. You will also need to install the required Python libraries:
```bash
pip install fpdf rdflib
```

### Installation

Clone this repository to your local machine:
```bash
git clone https://github.com/sylvesterkho1113/StudentManagementSystem.git
cd StudentManagementSystem
```

### Execution

Run the application through the main entry point:
```bash
python main.py
```

---

## 👨‍💻 Authors
Developed as part of the **TSW6223 Semantic Web Technology** Project by **Group 33**:
- See Chwan Kai
- Teo Jing An
- Tee Kian Hao
- Kho Wei Cong

---

*This system was designed to provide an efficient and intelligent approach to managing academic records using the power of Semantic Web paradigms.*
