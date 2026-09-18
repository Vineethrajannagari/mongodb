"""
Mock demo for testing the AttendanceManager without MongoDB
This demonstrates the code structure and logic without requiring a running MongoDB instance
"""

from datetime import datetime, timedelta


class MockAttendanceManager:
    """
    Mock version of AttendanceManager for demonstration without MongoDB
    """
    
    def __init__(self, connection_string, database_name):
        """Initialize mock manager with in-memory storage"""
        print(f"Mock mode: Would connect to {database_name} at {connection_string}")
        self.students = []
        self.attendance = []
        self.student_id_counter = 1
        self.attendance_id_counter = 1
    
    def add_student(self, name, roll_no, email, course):
        """Add a new student (mock implementation)"""
        # Check for duplicate roll_no
        for student in self.students:
            if student["roll_no"] == roll_no:
                return {
                    "success": False,
                    "message": f"Student with roll_no {roll_no} already exists"
                }
        
        student = {
            "_id": f"mock_id_{self.student_id_counter}",
            "name": name,
            "roll_no": roll_no,
            "email": email,
            "course": course,
            "created_at": datetime.utcnow()
        }
        self.student_id_counter += 1
        self.students.append(student)
        
        return {
            "success": True,
            "message": f"Student {name} added successfully",
            "student_id": student["_id"]
        }
    
    def add_attendance(self, roll_no, date, status):
        """Add attendance record (mock implementation)"""
        # Validate status
        valid_statuses = ["Present", "Absent"]
        if status not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        
        # Check if student exists
        student_exists = any(s["roll_no"] == roll_no for s in self.students)
        if not student_exists:
            return {
                "success": False,
                "message": f"Student with roll_no {roll_no} does not exist"
            }
        
        # Check for duplicate attendance
        for record in self.attendance:
            if record["roll_no"] == roll_no and record["date"] == date:
                return {
                    "success": False,
                    "message": f"Attendance record already exists for {roll_no} on {date}"
                }
        
        attendance = {
            "_id": f"mock_att_{self.attendance_id_counter}",
            "roll_no": roll_no,
            "date": date,
            "status": status,
            "created_at": datetime.utcnow()
        }
        self.attendance_id_counter += 1
        self.attendance.append(attendance)
        
        return {
            "success": True,
            "message": f"Attendance record added for {roll_no} on {date}",
            "record_id": attendance["_id"]
        }
    
    def get_all_attendance(self):
        """Get all attendance records (mock implementation)"""
        return sorted(self.attendance, key=lambda x: x["date"], reverse=True)
    
    def delete_student(self, roll_no):
        """Delete student (mock implementation)"""
        # Check if student exists
        student_exists = any(s["roll_no"] == roll_no for s in self.students)
        if not student_exists:
            return {
                "success": False,
                "message": f"Student with roll_no {roll_no} does not exist"
            }
        
        # Remove student
        self.students = [s for s in self.students if s["roll_no"] != roll_no]
        # Remove associated attendance
        self.attendance = [a for a in self.attendance if a["roll_no"] != roll_no]
        
        return {
            "success": True,
            "message": f"Student {roll_no} deleted successfully"
        }
    
    def find_student_by_roll(self, roll_no):
        """Find student by roll number (mock implementation)"""
        for student in self.students:
            if student["roll_no"] == roll_no:
                return student
        return None
    
    def get_student_attendance(self, roll_no):
        """Get student attendance (mock implementation)"""
        return [a for a in self.attendance if a["roll_no"] == roll_no]
    
    def calculate_attendance_percentage(self, roll_no):
        """Calculate attendance percentage (mock implementation)"""
        records = self.get_student_attendance(roll_no)
        
        if not records:
            return {
                "success": False,
                "message": f"No attendance records found for {roll_no}"
            }
        
        total = len(records)
        present = sum(1 for record in records if record["status"] == "Present")
        absent = total - present
        percentage = (present / total) * 100 if total > 0 else 0
        
        return {
            "success": True,
            "roll_no": roll_no,
            "total_classes": total,
            "present": present,
            "absent": absent,
            "percentage": round(percentage, 2)
        }


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_result(result):
    """Print a result dictionary in a readable format"""
    if isinstance(result, dict):
        for key, value in result.items():
            print(f"  {key}: {value}")
    else:
        print(f"  {result}")


def main():
    """Main demo function with mock data"""
    print_section("Student Attendance Management System - MOCK DEMO")
    print("\nNOTE: This is a mock demonstration without MongoDB connection.")
    print("The actual implementation uses PyMongo with real MongoDB.")
    
    # Initialize mock manager
    print("\nInitializing Mock AttendanceManager...")
    manager = MockAttendanceManager("mongodb://localhost:27017/", "college_attendance")
    
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
    print(f"Total students in database: {len(manager.students)}")
    for student in manager.students:
        print(f"  - {student['name']} ({student['roll_no']})")
    
    print(f"\nTotal attendance records: {len(manager.attendance)}")
    
    print("\n" + "=" * 60)
    print("  Mock demo completed successfully!")
    print("=" * 60)
    print("\nTo run with real MongoDB:")
    print("1. Install and start MongoDB")
    print("2. Create .env file with MONGO_URI")
    print("3. Run: python demo.py")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
