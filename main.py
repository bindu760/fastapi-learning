# Import FastAPI and HTTPException
from fastapi import FastAPI, HTTPException

# Import BaseModel for request data validation
from pydantic import BaseModel

# Import SQLite database module
import sqlite3


# Create FastAPI application
app = FastAPI()


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

# Function to create a database connection
def get_db():

    # Connect to the SQLite database
    # If the file does not exist, SQLite creates it
    connection = sqlite3.connect("students.db")

    # Return database rows as dictionary-like objects
    connection.row_factory = sqlite3.Row

    # Return the database connection
    return connection


# --------------------------------------------------
# CREATE TABLE
# --------------------------------------------------

# Function to create the students table
def create_table():

    # Open database connection
    connection = get_db()

    # Create students table if it does not already exist
    connection.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
    """)

    # Save the changes to the database
    connection.commit()

    # Close the database connection
    connection.close()


# Create the table when the application starts
create_table()


# --------------------------------------------------
# PYDANTIC MODEL
# --------------------------------------------------

# Define the structure of a student
class Student(BaseModel):

    # Student ID must be an integer
    id: int

    # Student name must be a string
    name: str


# --------------------------------------------------
# ROOT ENDPOINT
# --------------------------------------------------

# GET /
# Root endpoint of the API
@app.get("/")
def home():

    # Return a simple message
    return {"message": "FastAPI is running"}


# --------------------------------------------------
# READ ALL STUDENTS
# --------------------------------------------------

# GET /students
# Get all students from the database
@app.get("/students")
def get_students():

    # Open database connection
    connection = get_db()

    # Fetch all students from the students table
    students = connection.execute(
        "SELECT * FROM students"
    ).fetchall()

    # Close database connection
    connection.close()

    # Convert SQLite rows into dictionaries and return them
    return [dict(student) for student in students]


# --------------------------------------------------
# READ ONE STUDENT
# --------------------------------------------------

# GET /students/{student_id}
# Get a specific student by ID
@app.get("/students/{student_id}")
def get_student(student_id: int):

    # Open database connection
    connection = get_db()

    # Find the student with the given ID
    student = connection.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    ).fetchone()

    # Close database connection
    connection.close()

    # If the student does not exist, return 404 error
    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    # Convert the SQLite row into a dictionary
    return dict(student)


# --------------------------------------------------
# CREATE STUDENTS
# --------------------------------------------------

# POST /students
# Add multiple students at once
@app.post("/students", status_code=201)
def add_students(students_data: list[Student]):

    # Open database connection
    connection = get_db()

    try:

        # Loop through each student in the request
        for student in students_data:

            # Insert the student into the database
            connection.execute(
                "INSERT INTO students (id, name) VALUES (?, ?)",
                (student.id, student.name)
            )

        # Save all inserted records
        connection.commit()

    # Handle duplicate primary key / ID
    except sqlite3.IntegrityError:

        # Undo changes if an error occurs
        connection.rollback()

        # Close database connection
        connection.close()

        # Return a 400 Bad Request error
        raise HTTPException(
            status_code=400,
            detail="Student ID already exists"
        )

    # Close database connection
    connection.close()

    # Return the added students
    return students_data


# --------------------------------------------------
# UPDATE STUDENT
# --------------------------------------------------

# PUT /students/{student_id}
# Update an existing student's name
@app.put("/students/{student_id}")
def update_student(student_id: int, student: Student):

    # Open database connection
    connection = get_db()

    # Update the student's name using the given ID
    result = connection.execute(
        "UPDATE students SET name = ? WHERE id = ?",
        (student.name, student_id)
    )

    # Save the update to the database
    connection.commit()

    # If no row was updated, the student does not exist
    if result.rowcount == 0:

        # Close database connection
        connection.close()

        # Return 404 Not Found error
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    # Fetch the updated student
    updated_student = connection.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    ).fetchone()

    # Close database connection
    connection.close()

    # Return the updated student
    return dict(updated_student)


# --------------------------------------------------
# DELETE STUDENT
# --------------------------------------------------

# DELETE /students/{student_id}
# Delete a student by ID
@app.delete("/students/{student_id}")
def delete_student(student_id: int):

    # Open database connection
    connection = get_db()

    # Delete the student with the given ID
    result = connection.execute(
        "DELETE FROM students WHERE id = ?",
        (student_id,)
    )

    # Save the deletion
    connection.commit()

    # Close database connection
    connection.close()

    # If no row was deleted, the student does not exist
    if result.rowcount == 0:

        # Return 404 Not Found error
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    # Return success message
    return {"message": "Student deleted successfully"}