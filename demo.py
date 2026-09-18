"""
Demo script for the Student Attendance Management System
This script demonstrates all the functionality of the AttendanceManager class.
"""

import os
from attendance_manager import AttendanceManager, get_connection_string
from datetime import datetime, timedelta


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_result(result):
    """Print a result dictionary in a readable format."""
    if isinstance(result, dict):
        for key, value in result.items():
            print(f"  {key}: {value}")
    else:
        print(f"  {result}")


def main():
    """Main demo function."""
    print_section("Student Attendance Management System - Demo")
    
    try:
        # Initialize the manager
        print("\nInitializing AttendanceManager...")
        
        # Use the working connection string directly
        mongo_uri = "mongodb+srv://vineethrajannagari_db_user:Mypassword123@cluster0.s78cfde.mongodb.net/?appName=cluster0"
        
        manager = AttendanceManager(mongo_uri, "college_attendance")
        
        # Clean up any existing test data
        print("\nCleaning up any existing test data...")
        manager.students_collection.delete_many({"roll_no": {"$in": ["DEMO001", "DEMO002", "DEMO003"]}})
        manager.attendance_collection.delete_many({"roll_no": {"$in": ["DEMO001", "DEMO002", "DEMO003"]}})
        
        # Test 1: Add Students
        print_section("Test 1: Adding Students")
        
        students = [
            ("John Doe", "DEMO001", "john@example.com", "B.Tech CSE"),
            ("Jane Smith", "DEMO002", "jane@example.com", "B.Tech ECE"),
            ("Bob Johnson", "DEMO003", "bob@example.com", "B.Tech ME")
        ]
        
        for name, roll_no, email, course in students:
            result = manager.add_student(name, roll_no, email, course)
            print(f"\nAdding {name} ({roll_no}):")
            print_result(result)
        
        # Test 2: Try to add duplicate student
        print_section("Test 2: Adding Duplicate Student (Should Fail)")
        result = manager.add_student("John Doe", "DEMO001", "john2@example.com", "B.Tech CSE")
        print_result(result)
        
        # Test 3: Find student by roll number
        print_section("Test 3: Finding Student by Roll Number")
        student = manager.find_student_by_roll("DEMO001")
        print("Finding student DEMO001:")
        print_result(student)
        
        # Test 4: Add attendance records
        print_section("Test 4: Adding Attendance Records")
        
        # Generate dates for the past 5 days
        base_date = datetime.now()
        attendance_data = [
            ("DEMO001", (base_date - timedelta(days=4)).strftime("%Y-%m-%d"), "Present"),
            ("DEMO001", (base_date - timedelta(days=3)).strftime("%Y-%m-%d"), "Present"),
            ("DEMO001", (base_date - timedelta(days=2)).strftime("%Y-%m-%d"), "Absent"),
            ("DEMO001", (base_date - timedelta(days=1)).strftime("%Y-%m-%d"), "Present"),
            ("DEMO001", base_date.strftime("%Y-%m-%d"), "Present"),
            ("DEMO002", (base_date - timedelta(days=3)).strftime("%Y-%m-%d"), "Present"),
            ("DEMO002", (base_date - timedelta(days=2)).strftime("%Y-%m-%d"), "Present"),
            ("DEMO002", (base_date - timedelta(days=1)).strftime("%Y-%m-%d"), "Absent"),
        ]
        
        for roll_no, date, status in attendance_data:
            result = manager.add_attendance(roll_no, date, status)
            print(f"\nAdding attendance for {roll_no} on {date}:")
            print_result(result)
        
        # Test 5: Try to add duplicate attendance
        print_section("Test 5: Adding Duplicate Attendance (Should Fail)")
        result = manager.add_attendance("DEMO001", base_date.strftime("%Y-%m-%d"), "Present")
        print_result(result)
        
        # Test 6: Try invalid status
        print_section("Test 6: Invalid Attendance Status (Should Fail)")
        try:
            result = manager.add_attendance("DEMO001", "2026-09-20", "Late")
            print_result(result)
        except ValueError as e:
            print(f"  Expected error caught: {e}")
        
        # Test 7: Try attendance for non-existent student
        print_section("Test 7: Attendance for Non-existent Student (Should Fail)")
        result = manager.add_attendance("NONEXISTENT", "2026-09-20", "Present")
        print_result(result)
        
        # Test 8: Get all attendance records
        print_section("Test 8: Getting All Attendance Records")
        records = manager.get_all_attendance()
        print(f"Total attendance records: {len(records)}")
        for i, record in enumerate(records, 1):
            print(f"\n  Record {i}:")
            print(f"    Roll No: {record['roll_no']}")
            print(f"    Date: {record['date']}")
            print(f"    Status: {record['status']}")
        
        # Test 9: Get attendance for specific student
        print_section("Test 9: Getting Attendance for Specific Student")
        student_attendance = manager.get_student_attendance("DEMO001")
        print(f"Attendance records for DEMO001: {len(student_attendance)}")
        for record in student_attendance:
            print(f"  {record['date']}: {record['status']}")
        
        # Test 10: Calculate attendance percentage
        print_section("Test 10: Calculating Attendance Percentage")
        
        for roll_no in ["DEMO001", "DEMO002", "DEMO003"]:
            stats = manager.calculate_attendance_percentage(roll_no)
            print(f"\nStatistics for {roll_no}:")
            print_result(stats)
        
        # Test 11: Delete student
        print_section("Test 11: Deleting Student")
        result = manager.delete_student("DEMO003")
        print("Deleting student DEMO003:")
        print_result(result)
        
        # Verify deletion
        print("\nVerifying deletion:")
        student = manager.find_student_by_roll("DEMO003")
        print(f"  Student DEMO003 exists: {student is not None}")
        
        attendance = manager.get_student_attendance("DEMO003")
        print(f"  Attendance records for DEMO003: {len(attendance)}")
        
        # Test 12: Try to delete non-existent student
        print_section("Test 12: Deleting Non-existent Student (Should Fail)")
        result = manager.delete_student("NONEXISTENT")
        print_result(result)
        
        # Final state
        print_section("Final State Summary")
        all_students = list(manager.students_collection.find())
        all_attendance = manager.get_all_attendance()
        
        print(f"Total students in database: {len(all_students)}")
        for student in all_students:
            print(f"  - {student['name']} ({student['roll_no']})")
        
        print(f"\nTotal attendance records: {len(all_attendance)}")
        
        # Close connection
        print_section("Closing Connection")
        manager.close_connection()
        
        print("\n" + "=" * 60)
        print("  Demo completed successfully!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\nError during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
