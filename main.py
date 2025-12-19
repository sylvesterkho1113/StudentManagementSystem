# -------------------------------------------
# |TSW6223 Semantic Web Technology - Project|
# |SW2 (Section 2A) - Group 33              |
# |Title: STUDENT MANAGEMENT SYSTEM         |
# ------------------------------------------
# |242UT2449P SEE CHWAN KAI                 |
# |242UT24490 TEO JING AN                   |
# |242UT244B2 TEE KIAN HAO                  |
# |242UT2449Z KHO WEI CONG                  |
# -------------------------------------------

from student_module import *
from subject_module import *
from grading_module import *
from rdf_utils import *

from os import system, name
from time import sleep

# This function is used to clear the screen
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# main function
def main():
    init_student_xml()
    init_subject_xml()
    init_grade_xml()

    while True:
        clear_screen()
        # home page of the system
        print("\n-------------------------------------------------------------")
        print("|                 Student Management System                 |")
        print("-------------------------------------------------------------")
        print("1. Student Module\n2. Subject Module\n3. Grading Module\n4. Exit Program")
        choice = input("Enter your choice: ")
        if choice == "1":
            student_menu()
        elif choice == "2":
            subject_menu()
        elif choice == "3":
            grading_menu()
        elif choice == "4":
            clear_screen()
            print("\nThanks for using the system...")
            print("Have a nice day ahead :)")
            exit(0)
        else:
            clear_screen()
            print("Invalid code, please try again, Press any key to continue...")
            getchar = input()
            
if __name__ == "__main__":
    main()
