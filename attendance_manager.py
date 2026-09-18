"""
Student Attendance Management System
A class-based implementation using PyMongo for MongoDB operations.
"""

import os
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import PyMongoError, DuplicateKeyError, ConnectionFailure
from bson import ObjectId


class AttendanceManager:
    """
    Manages student records and attendance data using MongoDB.
    
    The constructor establishes the MongoDB connection and initializes
    the students and attendance collections.
    """
    
    def __init__(self, connection_string, database_name):
        """
        Initialize the AttendanceManager with MongoDB connection.
        
        Args:
            connection_string: MongoDB connection URI
            database_name: Name of the database to use
            
        Raises:
            ConnectionFailure: If unable to connect to MongoDB
        """
        try:
            self.client = MongoClient(connection_string)
            # Test the connection
            self.client.admin.command('ping')
            
            self.db = self.client[database_name]
            self.students_collection = self.db.students
            self.attendance_collection = self.db.attendance
            
            # Create indexes for better performance and data integrity
            self._create_indexes()
            
            print(f"Successfully connected to MongoDB database: {database_name}")
            
        except ConnectionFailure as e:
            raise ConnectionFailure(f"Failed to connect to MongoDB: {e}")
    
    def _create_indexes(self):
        """
        Create indexes for collections to ensure data integrity and performance.
        """
        try:
            # Unique index on roll_no to prevent duplicates
            self.students_collection.create_index(
                [("roll_no", 1)],
                unique=True,
                name="roll_no_unique"
            )
            
            # Compound index on roll_no and date for attendance queries
            self.attendance_collection.create_index(
                [("roll_no", 1), ("date", 1)],
                name="roll_no_date_compound"
            )
            
            # Index on date for date-based queries
            self.attendance_collection.create_index(
                [("date", 1)],
                name="date_index"
            )
            
        except PyMongoError as e:
            print(f"Warning: Could not create indexes: {e}")
    
    def add_student(self, name, roll_no, email, course):
        """
        Add a new student to the students collection.
        
        Args:
            name: Student's full name
            roll_no: Unique roll number
            email: Student's email address
            course: Student's course/program
            
        Returns:
            dict: Result message with success status and student ID
            
        Raises:
            ValueError: If any required field is empty
            DuplicateKeyError: If roll_no already exists
        """
        # Validate input
        if not all([name, roll_no, email, course]):
            raise ValueError("All fields (name, roll_no, email, course) are required")
        
        student_doc = {
            "name": name.strip(),
            "roll_no": roll_no.strip(),
            "email": email.strip(),
            "course": course.strip(),
            "created_at": datetime.utcnow()
        }
        
        try:
            result = self.students_collection.insert_one(student_doc)
            return {
                "success": True,
                "message": f"Student {name} added successfully",
                "student_id": str(result.inserted_id)
            }
        except DuplicateKeyError:
            return {
                "success": False,
                "message": f"Student with roll_no {roll_no} already exists"
            }
        except PyMongoError as e:
            return {
                "success": False,
                "message": f"Database error: {e}"
            }
    
    def add_attendance(self, roll_no, date, status):
        """
        Add an attendance record for an existing student.
        
        Args:
            roll_no: Student's roll number
            date: Attendance date (YYYY-MM-DD format)
            status: Attendance status ("Present" or "Absent")
            
        Returns:
            dict: Result message with success status and record ID
            
        Raises:
            ValueError: If status is invalid or date format is incorrect
        """
        # Validate status
        valid_statuses = ["Present", "Absent"]
        if status not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        
        # Validate date format
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
        
        # Check if student exists
        student = self.students_collection.find_one({"roll_no": roll_no.strip()})
        if not student:
            return {
                "success": False,
                "message": f"Student with roll_no {roll_no} does not exist"
            }
        
        # Check if attendance record already exists for this student on this date
        existing = self.attendance_collection.find_one({
            "roll_no": roll_no.strip(),
            "date": date
        })
        
        if existing:
            return {
                "success": False,
                "message": f"Attendance record already exists for {roll_no} on {date}"
            }
        
        attendance_doc = {
            "roll_no": roll_no.strip(),
            "date": date,
            "status": status,
            "created_at": datetime.utcnow()
        }
        
        try:
            result = self.attendance_collection.insert_one(attendance_doc)
            return {
                "success": True,
                "message": f"Attendance record added for {roll_no} on {date}",
                "record_id": str(result.inserted_id)
            }
        except PyMongoError as e:
            return {
                "success": False,
                "message": f"Database error: {e}"
            }
    
    def get_all_attendance(self):
        """
        Retrieve all attendance records from the attendance collection.
        
        Returns:
            list: List of attendance records as dictionaries
        """
        try:
            records = list(self.attendance_collection.find().sort("date", -1))
            # Convert ObjectId to string for JSON serialization
            for record in records:
                record["_id"] = str(record["_id"])
            return records
        except PyMongoError as e:
            print(f"Error retrieving attendance records: {e}")
            return []
    
    def delete_student(self, roll_no):
        """
        Delete a student from the students collection using roll number.
        
        Args:
            roll_no: Student's roll number to delete
            
        Returns:
            dict: Result message with success status
        """
        # Check if student exists
        student = self.students_collection.find_one({"roll_no": roll_no.strip()})
        if not student:
            return {
                "success": False,
                "message": f"Student with roll_no {roll_no} does not exist"
            }
        
        try:
            # Delete the student
            result = self.students_collection.delete_one({"roll_no": roll_no.strip()})
            
            # Optionally: Delete associated attendance records
            self.attendance_collection.delete_many({"roll_no": roll_no.strip()})
            
            if result.deleted_count > 0:
                return {
                    "success": True,
                    "message": f"Student {roll_no} deleted successfully"
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to delete student {roll_no}"
                }
        except PyMongoError as e:
            return {
                "success": False,
                "message": f"Database error: {e}"
            }
    
    def find_student_by_roll(self, roll_no):
        """
        Find a student by their roll number.
        
        Args:
            roll_no: Student's roll number
            
        Returns:
            dict: Student document if found, None otherwise
        """
        try:
            student = self.students_collection.find_one({"roll_no": roll_no.strip()})
            if student:
                student["_id"] = str(student["_id"])
            return student
        except PyMongoError as e:
            print(f"Error finding student: {e}")
            return None
    
    def get_student_attendance(self, roll_no):
        """
        Get all attendance records for a specific student.
        
        Args:
            roll_no: Student's roll number
            
        Returns:
            list: List of attendance records for the student
        """
        try:
            records = list(self.attendance_collection.find(
                {"roll_no": roll_no.strip()}
            ).sort("date", -1))
            
            for record in records:
                record["_id"] = str(record["_id"])
            
            return records
        except PyMongoError as e:
            print(f"Error retrieving student attendance: {e}")
            return []
    
    def calculate_attendance_percentage(self, roll_no):
        """
        Calculate the attendance percentage for a student.
        
        Args:
            roll_no: Student's roll number
            
        Returns:
            dict: Result with percentage and statistics
        """
        try:
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
        except Exception as e:
            return {
                "success": False,
                "message": f"Error calculating attendance: {e}"
            }
    
    def close_connection(self):
        """
        Close the MongoDB connection.
        """
        if self.client:
            self.client.close()
            print("MongoDB connection closed")
    
    def __del__(self):
        """
        Destructor to ensure connection is closed when object is destroyed.
        """
        self.close_connection()


def get_connection_string():
    """
    Get MongoDB connection string from environment variable or use default.
    
    Returns:
        str: MongoDB connection string
    """
    return os.getenv("MONGO_URI", "mongodb://localhost:27017/")


if __name__ == "__main__":
    # Example usage (this is for demonstration purposes)
    print("Attendance Management System")
    print("=" * 50)
    
    try:
        # Initialize the manager
        mongo_uri = get_connection_string()
        manager = AttendanceManager(mongo_uri, "college_attendance")
        
        # Add students
        print("\n--- Adding Students ---")
        result1 = manager.add_student("Rahul Sharma", "CS101", "rahul@example.com", "B.Tech CSE")
        print(f"Result 1: {result1}")
        
        result2 = manager.add_student("Priya Singh", "CS102", "priya@example.com", "B.Tech CSE")
        print(f"Result 2: {result2}")
        
        # Add attendance
        print("\n--- Adding Attendance ---")
        result3 = manager.add_attendance("CS101", "2026-09-18", "Present")
        print(f"Result 3: {result3}")
        
        result4 = manager.add_attendance("CS102", "2026-09-18", "Absent")
        print(f"Result 4: {result4}")
        
        # Get all attendance
        print("\n--- All Attendance Records ---")
        records = manager.get_all_attendance()
        for record in records:
            print(record)
        
        # Find student
        print("\n--- Find Student by Roll No ---")
        student = manager.find_student_by_roll("CS101")
        print(f"Student: {student}")
        
        # Get student attendance
        print("\n--- Student Attendance ---")
        student_attendance = manager.get_student_attendance("CS101")
        for record in student_attendance:
            print(record)
        
        # Calculate attendance percentage
        print("\n--- Attendance Percentage ---")
        stats = manager.calculate_attendance_percentage("CS101")
        print(f"Statistics: {stats}")
        
        # Delete student
        print("\n--- Delete Student ---")
        result5 = manager.delete_student("CS102")
        print(f"Result 5: {result5}")
        
    except Exception as e:
        print(f"Error: {e}")
