import os
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import (
    PyMongoError,
    DuplicateKeyError,
    ServerSelectionTimeoutError
)
from bson import ObjectId


class AttendanceManager:

    def __init__(self, connection_string, database_name):
        try:
            self.client = MongoClient(
                connection_string,
                serverSelectionTimeoutMS=5000
            )

            # Test connection
            self.client.admin.command("ping")

            self.db = self.client[database_name]

            self.students = self.db["students"]
            self.attendance = self.db["attendance"]

            # Unique roll number
            self.students.create_index(
                "roll_no",
                unique=True
            )

            # Useful attendance index
            self.attendance.create_index(
                [("roll_no", 1), ("date", 1)]
            )

            print("MongoDB connected successfully.")

        except ServerSelectionTimeoutError:
            print("Unable to connect to MongoDB.")
            raise
        except PyMongoError as e:
            print(f"Database error: {e}")
            raise
    def add_student(self, name, roll_no, email, course):

        if not all([name, roll_no, email, course]):
            print("All student fields are required.")
            return None

        try:
            student = {
                "name": name.strip(),
                "roll_no": roll_no.strip(),
                "email": email.strip(),
                "course": course.strip()
            }

            result = self.students.insert_one(student)

            print(
                f"Student added successfully. "
                f"ID: {result.inserted_id}"
            )

            return result.inserted_id

        except DuplicateKeyError:
            print(f"Student with roll number '{roll_no}' already exists.")
            return None

        except PyMongoError as e:
            print(f"Error adding student: {e}")
            return None
    def add_attendance(self, roll_no, attendance_date, status):

        if not roll_no or not attendance_date or not status:
            print("Roll number, date and status are required.")
            return None

        status = status.strip().capitalize()

        if status not in ["Present", "Absent"]:
            print("Attendance status must be 'Present' or 'Absent'.")
            return None

        try:
        
            student = self.students.find_one(
                {"roll_no": roll_no.strip()}
            )

            if student is None:
                print(
                    f"No student found with roll number '{roll_no}'."
                )
                return None
            try:
                datetime.strptime(attendance_date, "%Y-%m-%d")
            except ValueError:
                print("Invalid date. Use YYYY-MM-DD format.")
                return None

            attendance_record = {
                "roll_no": roll_no.strip(),
                "date": attendance_date,
                "status": status
            }

            result = self.attendance.insert_one(attendance_record)

            print(
                f"Attendance added successfully. "
                f"ID: {result.inserted_id}"
            )

            return result.inserted_id

        except PyMongoError as e:
            print(f"Error adding attendance: {e}")
            return None
    def get_all_attendance(self):

        try:
            records = list(self.attendance.find())

            for record in records:
                record["_id"] = str(record["_id"])

            return records

        except PyMongoError as e:
            print(f"Error retrieving attendance: {e}")
            return []
    def delete_student(self, roll_no):

        if not roll_no:
            print("Roll number is required.")
            return False

        try:
            student = self.students.find_one(
                {"roll_no": roll_no.strip()}
            )

            if student is None:
                print(
                    f"No student found with roll number '{roll_no}'."
                )
                return False

            result = self.students.delete_one(
                {"roll_no": roll_no.strip()}
            )

            if result.deleted_count == 1:
                print(
                    f"Student '{roll_no}' deleted successfully."
                )
                return True

            print("Student could not be deleted.")
            return False

        except PyMongoError as e:
            print(f"Error deleting student: {e}")
            return False
    def find_student(self, roll_no):

        try:
            student = self.students.find_one(
                {"roll_no": roll_no.strip()}
            )

            if student is None:
                print("Student not found.")
                return None

            student["_id"] = str(student["_id"])

            return student

        except PyMongoError as e:
            print(f"Error finding student: {e}")
            return None
    def get_student_attendance(self, roll_no):

        try:
            student = self.students.find_one(
                {"roll_no": roll_no.strip()}
            )

            if student is None:
                print("Student not found.")
                return []

            records = list(
                self.attendance.find(
                    {"roll_no": roll_no.strip()}
                ).sort("date", 1)
            )

            for record in records:
                record["_id"] = str(record["_id"])

            return records

        except PyMongoError as e:
            print(f"Error retrieving student attendance: {e}")
            return []
    def attendance_percentage(self, roll_no):

        try:
            student = self.students.find_one(
                {"roll_no": roll_no.strip()}
            )

            if student is None:
                print("Student not found.")
                return None

            records = list(
                self.attendance.find(
                    {"roll_no": roll_no.strip()}
                )
            )

            if not records:
                print("No attendance records found.")
                return 0.0

            present_count = sum(
                1 for record in records
                if record.get("status") == "Present"
            )

            total_count = len(records)

            percentage = (present_count / total_count) * 100

            return round(percentage, 2)

        except PyMongoError as e:
            print(f"Error calculating attendance: {e}")
            return None

    # ---------------------------------------------------------
    # Bonus: Delete Attendance
    # ---------------------------------------------------------
    def delete_attendance(self, attendance_id):

        try:
            if not ObjectId.is_valid(attendance_id):
                print("Invalid attendance ID.")
                return False

            result = self.attendance.delete_one(
                {"_id": ObjectId(attendance_id)}
            )

            if result.deleted_count == 0:
                print("Attendance record not found.")
                return False

            print("Attendance record deleted successfully.")
            return True

        except PyMongoError as e:
            print(f"Error deleting attendance: {e}")
            return False
    def close(self):
        self.client.close()
        print("MongoDB connection closed.")

if __name__ == "__main__":

    MONGO_URI = os.getenv(
        "MONGO_URI",
        "mongodb://localhost:27017/"
    )

    manager = AttendanceManager(
        MONGO_URI,
        "college_attendance"
    )

    
    manager.add_student(
        "Arjun Kumar",
        "CS201",
        "arjun@example.com",
        "B.Tech CSE"
    )

    manager.add_student(
        "Sneha Reddy",
        "CS202",
        "sneha@example.com",
        "B.Tech CSE"
    )

    manager.add_attendance(
        "CS201",
        "2026-09-21",
        "Present"
    )

    manager.add_attendance(
        "CS202",
        "2026-09-21",
        "Absent"
    )

    
    records = manager.get_all_attendance()

    print("\nAll Attendance Records:")
    for record in records:
        print(record)

    student = manager.find_student("CS201")

    print("\nStudent:")
    print(student)


    attendance = manager.get_student_attendance("CS201")

    print("\nCS201 Attendance:")
    for record in attendance:
        print(record)

    
    percentage = manager.attendance_percentage("CS201")

    print(f"\nCS201 Attendance Percentage: {percentage}%")
    manager.delete_student("CS202")


    manager.close()