import sqlite3

class Database:
    def __init__(self, db_name="attendance_system.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                student_id TEXT UNIQUE NOT NULL,
                face_image_path TEXT,
                class TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                attendance_date DATE NOT NULL,
                time_in TEXT NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students(student_id)
            )
        """)
        self.conn.commit()

    def add_student(self, name, student_id, face_image_path=None, student_class=None):
        try:
            self.cursor.execute("INSERT INTO students (name, student_id, face_image_path, class) VALUES (?, ?, ?, ?)",
                                (name, student_id, face_image_path, student_class))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Student ID already exists

    def get_student(self, student_id):
        self.cursor.execute("SELECT * FROM students WHERE student_id=?", (student_id,))
        return self.cursor.fetchone()

    def get_all_students(self):
        self.cursor.execute("SELECT * FROM students")
        return self.cursor.fetchall()

    def update_student_info(self, student_id, name=None, face_image_path=None, student_class=None):
        query = "UPDATE students SET "
        updates = []
        params = []
        if name:
            updates.append("name=?")
            params.append(name)
        if face_image_path:
            updates.append("face_image_path=?")
            params.append(face_image_path)
        if student_class:
            updates.append("class=?")
            params.append(student_class)

        query += ", ".join(updates)
        query += " WHERE student_id=?"
        params.append(student_id)

        if updates:
            self.cursor.execute(query, tuple(params))
            self.conn.commit()
            return True
        return False

    def delete_student(self, student_id):
        self.cursor.execute("DELETE FROM students WHERE student_id=?", (student_id,))
        self.cursor.execute("DELETE FROM attendance WHERE student_id=?", (student_id,)) # Also delete attendance records
        self.conn.commit()
        return True

    def mark_attendance(self, student_id, date, time_in):
        print(f"DB - mark_attendance() called with ID: '{student_id}', Date: '{date}', Time: '{time_in}'")
        try:
            self.cursor.execute("INSERT INTO attendance (student_id, attendance_date, time_in) VALUES (?, ?, ?)",
                                (student_id, date, time_in))
            self.conn.commit()
            print("DB - Attendance record inserted successfully.")
            return True
        except sqlite3.Error as e:
            print(f"DB - Error inserting attendance: {e}")
            return False

    def get_attendance(self, date):
        self.cursor.execute("SELECT s.name, a.student_id, a.time_in FROM attendance a JOIN students s ON a.student_id = s.student_id WHERE a.attendance_date=?", (date,))
        return self.cursor.fetchall()

    def get_attendance_report(self, start_date, end_date):
        print(f"DB - get_attendance_report() called with Start Date: '{start_date}', End Date: '{end_date}'")
        try:
            self.cursor.execute("""
                SELECT s.name, a.student_id, a.attendance_date, a.time_in
                FROM attendance a
                JOIN students s ON a.student_id = s.student_id
                WHERE a.attendance_date BETWEEN ? AND ?
                ORDER BY a.attendance_date, a.time_in
            """, (start_date, end_date))
            report_data = self.cursor.fetchall()
            print(f"DB - Report Data fetched: {report_data}")
            return report_data
        except sqlite3.Error as e:
            print(f"DB - Error fetching report data: {e}")
            return []

    def close(self):
        self.conn.close()

if __name__ == '__main__':
    db = Database()
    # Example usage:
    # db.add_student("John Doe", "JD123", "faces/jd123.jpg", "10A")
    # student = db.get_student("JD123")
    # print(student)
    # all_students = db.get_all_students()
    # print(all_students)
    # db.mark_attendance("JD123", date.today(), datetime.now().strftime("%H:%M:%S"))
    # attendance = db.get_attendance(date.today())
    # print(attendance)
    # report = db.get_attendance_report(date(2023, 1, 1), date.today())
    # print(report)
    db.close()