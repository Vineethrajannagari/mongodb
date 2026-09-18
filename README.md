# Student Attendance Management System

A Python-based Student Attendance Management System using Object-Oriented Programming principles and MongoDB with PyMongo. This system provides a clean, class-based interface for managing student records and attendance data.

## Features

- **Class-based Design**: Uses OOP principles with `__init__` for database connection setup
- **MongoDB Integration**: Direct PyMongo operations (no ODM like MongoEngine)
- **CRUD Operations**: Complete Create, Read, Update, Delete functionality
- **Data Validation**: Enforces business rules and data integrity
- **Error Handling**: Comprehensive exception handling for database operations
- **Indexing**: Optimized indexes for performance and data integrity
- **Bonus Features**: Attendance percentage calculation, student lookup, and more

## Requirements

- Python 3.7 or higher
- MongoDB 4.0 or higher
- PyMongo library

## Installation

### 1. Install MongoDB

#### Windows:
```bash
# Download MongoDB from https://www.mongodb.com/try/download/community
# Follow the installation wizard
# Start MongoDB service
net start MongoDB
```

#### macOS:
```bash
# Using Homebrew
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

#### Linux:
```bash
# Ubuntu/Debian
sudo apt-get install mongodb
sudo systemctl start mongodb
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Connection String

Create a `.env` file in the project root (copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` with your MongoDB connection string:

```
MONGO_URI=mongodb://localhost:27017/
```

For MongoDB Atlas (cloud):
```
MONGO_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/
```

## Project Structure

```
mongodb/
├── attendance_manager.py   # Main class implementation
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .env                   # Your actual environment variables (not in git)
├── demo.py                # Demo script (optional)
└── README.md             # This file
```

## Usage

### Basic Usage

```python
from attendance_manager import AttendanceManager, get_connection_string

# Initialize the manager
mongo_uri = get_connection_string()
manager = AttendanceManager(mongo_uri, "college_attendance")

# Add students
result = manager.add_student("Rahul Sharma", "CS101", "rahul@example.com", "B.Tech CSE")
print(result)

# Add attendance
result = manager.add_attendance("CS101", "2026-09-18", "Present")
print(result)

# Get all attendance records
records = manager.get_all_attendance()
for record in records:
    print(record)

# Delete a student
result = manager.delete_student("CS101")
print(result)

# Close connection when done
manager.close_connection()
```

### Method Reference

#### Required Methods

1. **add_student(name, roll_no, email, course)**
   - Adds a new student to the database
   - Validates that roll_no is unique
   - Returns: dict with success status and message

2. **add_attendance(roll_no, date, status)**
   - Adds attendance record for an existing student
   - Validates student existence and status (Present/Absent)
   - Returns: dict with success status and message

3. **get_all_attendance()**
   - Retrieves all attendance records
   - Returns: list of attendance dictionaries

4. **delete_student(roll_no)**
   - Deletes a student by roll number
   - Also deletes associated attendance records
   - Returns: dict with success status and message

#### Bonus Methods

5. **find_student_by_roll(roll_no)**
   - Finds a student by their roll number
   - Returns: student document or None

6. **get_student_attendance(roll_no)**
   - Gets all attendance records for a specific student
   - Returns: list of attendance records

7. **calculate_attendance_percentage(roll_no)**
   - Calculates attendance percentage for a student
   - Returns: dict with statistics (total, present, absent, percentage)

## Business Rules

- **Unique Roll Numbers**: No two students can have the same roll_no
- **Student Existence**: Attendance can only be added for existing students
- **Valid Status**: Attendance status must be "Present" or "Absent"
- **Date Format**: Dates must be in YYYY-MM-DD format
- **Safe Deletion**: Student deletion checks for existence before deletion

## Database Schema

### Students Collection
```json
{
  "_id": ObjectId("..."),
  "name": "Rahul Sharma",
  "roll_no": "CS101",
  "email": "rahul@example.com",
  "course": "B.Tech CSE",
  "created_at": ISODate("2026-09-18T00:00:00Z")
}
```

### Attendance Collection
```json
{
  "_id": ObjectId("..."),
  "roll_no": "CS101",
  "date": "2026-09-18",
  "status": "Present",
  "created_at": ISODate("2026-09-18T00:00:00Z")
}
```

## Indexes

The system automatically creates the following indexes:

1. **Unique Index** on `students.roll_no` - Ensures no duplicate roll numbers
2. **Compound Index** on `attendance.roll_no` and `attendance.date` - Optimizes attendance queries
3. **Date Index** on `attendance.date` - Optimizes date-based queries

## Error Handling

The system handles various error scenarios:

- **Connection Errors**: MongoDB connection failures
- **Duplicate Key Errors**: Attempting to add duplicate roll numbers
- **Validation Errors**: Invalid input data
- **Database Errors**: General MongoDB operation errors

All methods return consistent result dictionaries with success status and descriptive messages.

## Running the Demo

The main module includes a demo that can be run directly:

```bash
python attendance_manager.py
```

This will demonstrate:
- Adding students
- Adding attendance records
- Retrieving all attendance
- Finding students by roll number
- Calculating attendance percentage
- Deleting students

## Environment Variables

- `MONGO_URI`: MongoDB connection string (defaults to `mongodb://localhost:27017/`)

## Testing

To test the system manually:

```python
from attendance_manager import AttendanceManager, get_connection_string

manager = AttendanceManager(get_connection_string(), "college_attendance")

# Test 1: Add student
print("Test 1: Add Student")
result = manager.add_student("Test Student", "TEST001", "test@example.com", "B.Tech")
print(result)

# Test 2: Add duplicate (should fail)
print("\nTest 2: Add Duplicate Student")
result = manager.add_student("Test Student", "TEST001", "test2@example.com", "B.Tech")
print(result)

# Test 3: Add attendance
print("\nTest 3: Add Attendance")
result = manager.add_attendance("TEST001", "2026-09-18", "Present")
print(result)

# Test 4: Invalid status
print("\nTest 4: Invalid Status")
try:
    result = manager.add_attendance("TEST001", "2026-09-19", "Late")
    print(result)
except ValueError as e:
    print(f"Expected error: {e}")

# Test 5: Get all attendance
print("\nTest 5: Get All Attendance")
records = manager.get_all_attendance()
print(f"Total records: {len(records)}")

# Test 6: Calculate percentage
print("\nTest 6: Calculate Attendance Percentage")
stats = manager.calculate_attendance_percentage("TEST001")
print(stats)

# Test 7: Delete student
print("\nTest 7: Delete Student")
result = manager.delete_student("TEST001")
print(result)

manager.close_connection()
```

## Design Decisions

1. **Connection in __init__**: Database connection is established in the constructor as required, ensuring resources are available when the object is created.

2. **Index Creation**: Indexes are created automatically to ensure data integrity (unique roll_no) and optimize query performance.

3. **ObjectId Handling**: ObjectIds are converted to strings in return values for easier JSON serialization and usability.

4. **Cascade Deletion**: When a student is deleted, their attendance records are also deleted to maintain data consistency.

5. **Result Dictionaries**: All methods return consistent dictionary responses with success status, making error handling uniform.

6. **Environment Variables**: Connection string is read from environment variables to keep configuration separate from code.

## Troubleshooting

### MongoDB Connection Issues

If you get a connection error:
- Ensure MongoDB is running: `mongod` (or check service status)
- Verify your connection string in `.env`
- Check firewall settings if using remote MongoDB

### Import Errors

If you get import errors:
- Ensure you installed dependencies: `pip install -r requirements.txt`
- Check you're using Python 3.7+

### Duplicate Key Errors

If you get duplicate key errors:
- A student with that roll_no already exists
- Use `find_student_by_roll()` to check before adding

## License

This is a learning project for educational purposes.

## Author

Created as a coding challenge for OOP and MongoDB with PyMongo.
