from datetime import datetime
from database import Database

class AttendanceSystem:
    def __init__(self):
        self.db = Database()
    
    def mark_attendance(self, emp_id, manual_override=False):
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M:%S")
        
        if manual_override:
            # For manual attendance marking (since we don't have face recognition)
            employee = self.db.get_employee(emp_id)
            if employee:
                # Check existing attendance for today
                c = self.db.conn.cursor()
                c.execute('''SELECT time_in, time_out FROM attendance 
                            WHERE employee_id=? AND date=?''', (emp_id, current_date))
                record = c.fetchone()
                
                if record:
                    time_in, time_out = record
                    if not time_out:
                        # Update time_out
                        self.db.mark_attendance(emp_id, current_date, time_out=current_time)
                        return f"Goodbye {employee[1]}! Time out recorded at {current_time}"
                    else:
                        return "Attendance already completed for today"
                else:
                    # Insert new record
                    self.db.mark_attendance(emp_id, current_date, time_in=current_time)
                    return f"Welcome {employee[1]}! Time in recorded at {current_time}"
            return "Employee not found"
        
        # In a real system, this would use face recognition results
        return "Face recognition not implemented in this simplified version"