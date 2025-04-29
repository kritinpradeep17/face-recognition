import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
from datetime import datetime, date
from database import Database  # Assuming you have this file
import os
from tkcalendar import Calendar
import csv
from tkinter import filedialog
import imagehash  # You might need to install this: pip install imagehash

class AttendanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Attendance System")
        self.root.geometry("1280x720")
        self.root.configure(bg="#e6f7ff")  # Light blue background

        # Style configuration with more color
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Using a modern theme

        self.style.configure('TFrame', background="#e6f7ff")
        self.style.configure('TLabel', background="#e6f7ff", font=('Segoe UI', 11), foreground="#333")
        self.style.configure('TButton', font=('Segoe UI', 11, 'bold'), padding=8,
                             background="#4CAF50", foreground="white",
                             relief=tk.RAISED, borderwidth=2)
        self.style.map('TButton',
                       background=[('active', '#45a049'), ('disabled', '#ccc')],
                       foreground=[('disabled', '#888')])
        self.style.configure('Header.TLabel', font=('Segoe UI', 20, 'bold'), foreground="#2c3e50", background="#e6f7ff", padding=(0, 10))
        self.style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), foreground="#3498db", background="#e6f7ff", padding=(0, 5))
        self.style.configure('TLabelframe', background="#f9f9f9", borderwidth=2, relief=tk.GROOVE)
        self.style.configure('TLabelframe.Label', font=('Segoe UI', 12, 'bold'), foreground="#2c3e50", background="#f9f9f9")
        self.style.configure('TEntry', font=('Segoe UI', 11), foreground="#555", padding=5)
        self.style.configure('Treeview', font=('Segoe UI', 10), foreground="#333")
        self.style.configure('Treeview.Heading', font=('Segoe UI', 11, 'bold'), foreground="#2c3e50")

        # Initialize systems
        self.db = Database()
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.captured_face = None
        self.video_capture = None
        self.current_attendance = {}
        self.selected_date = date.today()
        self.attendance_capture = None  # To store the captured image for attendance

        # Create menu
        self.create_menu()

        # Main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Show home frame by default
        self.show_home_frame()

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_menu(self):
        menubar = tk.Menu(self.root, bg="#f0f0f0", fg="black")

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg="#f0f0f0", fg="black")
        file_menu.add_command(label="Home", command=self.show_home_frame)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        menubar.add_cascade(label="File", menu=file_menu)

        # Student menu
        student_menu = tk.Menu(menubar, tearoff=0, bg="#f0f0f0", fg="black")
        student_menu.add_command(label="Register Student", command=self.show_registration_window)
        student_menu.add_command(label="View Students", command=self.show_students_frame)
        menubar.add_cascade(label="Students", menu=student_menu)

        # Attendance menu
        attendance_menu = tk.Menu(menubar, tearoff=0, bg="#f0f0f0", fg="black")
        attendance_menu.add_command(label="Mark Attendance", command=self.show_attendance_date_picker)
        attendance_menu.add_command(label="View Reports", command=self.show_reports_frame)
        menubar.add_cascade(label="Attendance", menu=attendance_menu)

        self.root.config(menu=menubar)

    def show_home_frame(self):
        self.clear_main_frame()

        # Header
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 30))

        ttk.Label(header_frame, text="Student Attendance System",
                  style="Header.TLabel").pack(pady=10)

        # Quick actions
        action_frame = ttk.Frame(self.main_frame)
        action_frame.pack(pady=20)

        # Action buttons with icons (using more visually appealing icons)
        icons = {
            "register": "➕",
            "attendance": "✔️",
            "students": "🧑‍🎓",
            "reports": "📊"
        }

        ttk.Button(action_frame, text=f"{icons['register']} Register Student",
                   command=self.show_registration_window, style="TButton", width=25).pack(pady=10)
        ttk.Button(action_frame, text=f"{icons['attendance']} Mark Attendance",
                   command=self.show_attendance_date_picker, style="TButton", width=25).pack(pady=10)
        ttk.Button(action_frame, text=f"{icons['students']} View Students",
                   command=self.show_students_frame, style="TButton", width=25).pack(pady=10)
        ttk.Button(action_frame, text=f"{icons['reports']} View Reports",
                   command=self.show_reports_frame, style="TButton", width=25).pack(pady=10)

    def show_registration_window(self):
        self.clear_main_frame()
        self.captured_face = None

        # Header
        ttk.Label(self.main_frame, text="Register New Student",
                  style="Title.TLabel").pack(pady=20)

        # Form frame
        form_frame = ttk.Frame(self.main_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10) # Reduced pady

        # Student details (using grid for more structured layout)
        ttk.Label(form_frame, text="Full Name:", style="TLabel").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.name_entry = ttk.Entry(form_frame, width=40, style="TEntry")
        self.name_entry.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=5)

        ttk.Label(form_frame, text="Student ID:", style="TLabel").grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        self.student_id_entry = ttk.Entry(form_frame, width=40, style="TEntry")
        self.student_id_entry.grid(row=1, column=1, sticky=tk.EW, pady=5, padx=5)

        ttk.Label(form_frame, text="Class/Grade:", style="TLabel").grid(row=2, column=0, sticky=tk.W, pady=5, padx=5)
        self.class_entry = ttk.Entry(form_frame, width=40, style="TEntry")
        self.class_entry.grid(row=2, column=1, sticky=tk.EW, pady=5, padx=5)

        # Video feed frame
        video_frame = ttk.LabelFrame(self.main_frame, text="Student Photo Capture", style="TLabelframe")
        video_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10) # Reduced pady

        self.video_label = ttk.Label(video_frame, text="Video Feed Placeholder")
        self.video_label.pack(pady=15, padx=15)

        # Buttons frame - Ensuring it's packed *before* starting video
        self.button_frame = tk.Frame(self.main_frame, borderwidth=2, relief="solid") # Make it visible for debugging
        self.button_frame.pack(pady=10) # Reduced pady

        self.capture_btn = tk.Button(self.button_frame, text="📸 Capture Photo",
                                     command=self.capture_face, width=15)
        self.capture_btn.pack(side=tk.LEFT, padx=10)

        self.register_btn = tk.Button(self.button_frame, text="💾 Register Student",
                                      command=self.register_student,
                                      state=tk.DISABLED, width=15)
        self.register_btn.pack(side=tk.LEFT, padx=10)

        back_btn = tk.Button(self.button_frame, text="⬅ Back",
                               command=self.show_home_frame, width=10)
        back_btn.pack(side=tk.LEFT, padx=10)

        # Start video feed
        self.video_capture = cv2.VideoCapture(0)
        self.update_video_feed()

    def update_video_feed(self):
        if self.video_capture is None or not self.video_capture.isOpened():
            print("Video capture is not initialized or opened.")
            return

        ret, frame = self.video_capture.read()
        print(f"ret: {ret}")
        if ret:
            try:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)

                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)
            except Exception as e:
                print(f"Error processing video frame: {e}")
        else:
            print("Failed to read frame from video capture.")

        self.video_label.after(10, self.update_video_feed)

    def capture_face(self):
        ret, frame = self.video_capture.read()
        if ret:
            self.captured_face = frame
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

            if len(faces) > 0:
                self.register_btn.config(state=tk.NORMAL)
                messagebox.showinfo("Success", "Face captured successfully!")
            else:
                messagebox.showerror("Error", "No face detected in the image!")
        else:
            messagebox.showerror("Error", "Failed to capture image")

    def register_student(self):
        name = self.name_entry.get().strip()
        student_id = self.student_id_entry.get().strip()
        student_class = self.class_entry.get().strip()

        if not name or not student_id:
            messagebox.showerror("Error", "Name and Student ID are required!")
            return

        if self.captured_face is None:
            messagebox.showerror("Error", "No face captured!")
            return

        try:
            # Save the face image
            face_filename = f"faces/{student_id}.jpg"
            os.makedirs("faces", exist_ok=True)
            cv2.imwrite(face_filename, self.captured_face)

            # Save to database
            if self.db.add_student(name, student_id, face_filename, student_class):
                messagebox.showinfo("Success", "Student registered successfully!")
                self.show_home_frame()
            else:
                messagebox.showerror("Error", "Student ID already exists!")
        except Exception as e:
            messagebox.showerror("Error", f"Registration failed: {str(e)}")

    def show_students_frame(self):
        self.clear_main_frame()

        # Header
        ttk.Label(self.main_frame, text="Student Database",
                  style="Title.TLabel").pack(pady=20)

        # Search frame
        search_frame = ttk.Frame(self.main_frame)
        search_frame.pack(fill=tk.X, padx=30, pady=10)

        ttk.Label(search_frame, text="Search:", style="TLabel").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame, width=40, style="TEntry")
        self.search_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        ttk.Button(search_frame, text="🔍 Search",
                   command=self.search_students, style="TButton", width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="🔄 Refresh",
                   command=self.load_student_data, style="TButton", width=10).pack(side=tk.LEFT, padx=5)

        # Treeview frame
        tree_frame = ttk.Frame(self.main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        # Create scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create treeview with improved styling
        self.student_tree = ttk.Treeview(tree_frame, yscrollcommand=scrollbar.set,
                                        columns=("ID", "Name", "Class"), show="headings",
                                        style="Treeview")

        # Configure columns
        self.student_tree.heading("ID", text="Student ID", anchor=tk.W)
        self.student_tree.heading("Name", text="Full Name", anchor=tk.W)
        self.student_tree.heading("Class", text="Class/Grade", anchor=tk.W)

        self.student_tree.column("ID", width=150, anchor=tk.W)
        self.student_tree.column("Name", width=300, anchor=tk.W)
        self.student_tree.column("Class", width=150, anchor=tk.W)

        self.student_tree.pack(fill=tk.BOTH, expand=True)

        # Configure scrollbar
        scrollbar.config(command=self.student_tree.yview)

        # Load data
        self.load_student_data()

        # Button frame
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=20)

        ttk.Button(button_frame, text="⬅ Back",
                   command=self.show_home_frame, style="TButton", width=10).pack(side=tk.LEFT, padx=10)

    def load_student_data(self):
        # Clear existing data
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)

        # Get students from database
        students = self.db.get_all_students()

        # Add to treeview
        for student in students:
            self.student_tree.insert("", tk.END, values=(student[2], student[1], student[4]))

    def search_students(self):
        query = self.search_entry.get().lower()
        if not query:
            self.load_student_data()
            return

        # Clear existing data
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)

        students = self.db.get_all_students()
        for student in students:
            if (query in student[1].lower() or  # Name
                    query in student[2].lower() or  # Student ID
                    query in student[4].lower()):  # Class
                self.student_tree.insert("", tk.END, values=(student[2], student[1], student[4]))

    def show_attendance_date_picker(self):
        self.clear_main_frame()

        # Header
        ttk.Label(self.main_frame, text="Select Date for Attendance",
                  style="Title.TLabel").pack(pady=20)

        # Calendar frame
        cal_frame = ttk.Frame(self.main_frame)
        cal_frame.pack(pady=30)

        # Calendar widget with improved styling
        self.cal = Calendar(cal_frame, selectmode='day',
                            year=date.today().year,
                            month=date.today().month,
                            day=date.today().day,
                            background="#ffffff",
                            foreground="#333",
                            selectbackground="#3498db",
                            selectforeground="white",
                            font=('Segoe UI', 11))
        self.cal.pack(pady=15)

        # Button frame
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=20)

        ttk.Button(button_frame, text="📅 Select Date",
                   command=self.on_date_selected, style="TButton", width=15).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="⬅ Back",
                   command=self.show_home_frame, style="TButton", width=10).pack(side=tk.LEFT, padx=10)

    def on_date_selected(self):
        self.selected_date = self.cal.get_date()
        self.show_attendance_frame()

    def show_attendance_frame(self):
        self.clear_main_frame()
        self.current_attendance = {}
        self.attendance_capture = None

        # Header
        ttk.Label(self.main_frame,
                  text=f"Marking Attendance for {self.selected_date}",
                  style="Title.TLabel").grid(row=0, column=0, columnspan=2, pady=20)

        # Video frame
        video_frame = ttk.LabelFrame(self.main_frame, text="Live Camera Feed", style="TLabelframe")
        video_frame.grid(row=1, column=0, padx=30, pady=10, sticky="nsew")

        self.attendance_video_label = ttk.Label(video_frame, text="Live Video Placeholder")
        self.attendance_video_label.pack(pady=15, padx=15)

        # Buttons frame
        button_frame = tk.Frame(self.main_frame, borderwidth=2, relief="solid")
        button_frame.grid(row=1, column=1, padx=30, pady=10, sticky="ew")

        self.capture_attendance_btn = tk.Button(button_frame, text="📸 Capture Face for Attendance",
                                                command=self.capture_attendance_face, width=25)
        self.capture_attendance_btn.pack(pady=5)

        back_btn = tk.Button(button_frame, text="⬅ Back",
                               command=self.show_home_frame, width=10)
        back_btn.pack(pady=5)

        # Attendance log frame
        log_frame = ttk.LabelFrame(self.main_frame, text="Attendance Log", style="TLabelframe")
        log_frame.grid(row=2, column=0, columnspan=2, padx=30, pady=10, sticky="nsew")

        self.attendance_log = tk.Text(log_frame, height=5, state=tk.DISABLED,
                                     font=('Segoe UI', 10), wrap=tk.WORD)
        self.attendance_log.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(log_frame, command=self.attendance_log.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.attendance_log.config(yscrollcommand=scrollbar.set)

        # Manual entry frame at the bottom
        manual_frame = tk.Frame(self.main_frame, height=80, bg="lightblue", borderwidth=2, relief="solid")
        manual_frame.grid(row=3, column=0, columnspan=2, padx=30, pady=20, sticky="ew")

        ttk.Label(manual_frame, text="Enter Student ID:", style="TLabel").pack(side=tk.LEFT, padx=5, pady=10)
        self.manual_id_entry = ttk.Entry(manual_frame, width=20, style="TEntry")
        self.manual_id_entry.pack(side=tk.LEFT, padx=5, pady=10)
        manual_present_btn = tk.Button(manual_frame, text="✅ Mark Present",
                                       command=self.manual_attendance, width=15)
        manual_present_btn.pack(side=tk.LEFT, padx=10, pady=10)

        # Configure row and column weights so frames expand correctly
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)

        # Start video
        self.video_capture = cv2.VideoCapture(0)
        self.update_attendance_video()

    def update_attendance_video(self):
        if self.video_capture is None or not self.video_capture.isOpened():
            print("Video capture is not initialized or opened.")
            return

        ret, frame = self.video_capture.read()
        print(f"ret: {ret}")
        if ret:
            try:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)

                self.attendance_video_label.imgtk = imgtk
                self.attendance_video_label.configure(image=imgtk)
            except Exception as e:
                print(f"Error processing video frame: {e}")
        else:
            print("Failed to read frame from video capture.")

        self.attendance_video_label.after(10, self.update_attendance_video)

    def capture_attendance_face(self):
        ret, frame = self.video_capture.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            if len(faces) == 1:
                x, y, w, h = faces[0]
                self.attendance_capture = frame[y:y + h, x:x + w]
                self.compare_captured_face()
            elif len(faces) > 1:
                messagebox.showerror("Error", "Multiple faces detected. Please ensure only one person is in front of the camera.")
            else:
                messagebox.showerror("Error", "No face detected. Please try again.")
        else:
            messagebox.showerror("Error", "Could not capture frame.")

    def compare_captured_face(self):
        if self.attendance_capture is None:
            messagebox.showerror("Error", "No face captured for comparison.")
            return

        captured_face_gray = cv2.cvtColor(self.attendance_capture, cv2.COLOR_BGR2GRAY)
        captured_face_resized = cv2.resize(captured_face_gray, (100, 100))  # Standardize size

        students = self.db.get_all_students()
        for student in students:
            face_path = student[3]
            if os.path.exists(face_path):
                try:
                    registered_face = cv2.imread(face_path, cv2.IMREAD_GRAYSCALE)
                    registered_face_resized = cv2.resize(registered_face, (100, 100))

                    # Using image hashing for comparison (requires 'imagehash' library)
                    captured_hash = imagehash.average_hash(Image.fromarray(captured_face_resized))
                    registered_hash = imagehash.average_hash(Image.fromarray(registered_face_resized))

                    # Hamming distance for similarity (lower is more similar)
                    hamming_distance = captured_hash - registered_hash
                    similarity_threshold = 10  # Adjust this value based on experimentation

                    if hamming_distance <= similarity_threshold:
                        current_time = datetime.now().strftime("%H:%M:%S")
                        if student[2] not in self.current_attendance:
                            self.db.mark_attendance(student[2], self.selected_date, time_in=current_time)
                            self.current_attendance[student[2]] = True
                            self._update_attendance_log(f"{student[1]} ({student[2]}) - Present (Face Match) at {current_time}\n")
                            messagebox.showinfo("Success", f"Attendance marked for {student[1]} ({student[2]})")
                            return  # Exit after first match
                        else:
                            messagebox.showinfo("Info", f"Attendance already marked for {student[1]} today.")
                            return

                except Exception as e:
                    print(f"Error comparing face for {student[1]}: {e}")

        messagebox.showerror("Error", "No matching face found.")

    def _update_attendance_log(self, message):
        self.attendance_log.config(state=tk.NORMAL)
        self.attendance_log.insert(tk.END, message)
        self.attendance_log.config(state=tk.DISABLED)
        self.attendance_log.see(tk.END)

    def manual_attendance(self):
        student_id = self.manual_id_entry.get().strip()
        print(f"Manual Attendance - Entered Student ID: '{student_id}'")
        print(f"Manual Attendance - Selected Date: '{self.selected_date}'")

        if student_id:
            current_time = datetime.now().strftime("%H:%M:%S")
            print(f"Manual Attendance - Current Time: '{current_time}'")

            student_data = self.db.get_student(student_id)
            print(f"Manual Attendance - Student Data from DB: {student_data}")

            if student_data:
                if student_id not in self.current_attendance:
                    print(f"Manual Attendance - Marking attendance for ID: '{student_id}'")
                    self.db.mark_attendance(student_id, self.selected_date, time_in=current_time)
                    print("Manual Attendance - mark_attendance() called")
                    self.current_attendance[student_id] = True
                    print(f"Manual Attendance - current_attendance updated: {self.current_attendance}")
                    self._update_attendance_log(f"{student_data[1]} ({student_id}) - Present at {current_time}\n")
                    print("Manual Attendance - _update_attendance_log() called")
                    self.manual_id_entry.delete(0, tk.END)
                    print("Manual Attendance - Entry field cleared")
                else:
                    messagebox.showinfo("Info", "Attendance already marked for this student today")
                    print("Manual Attendance - Already marked")
            else:
                messagebox.showerror("Error", "Student ID not found")
                print("Manual Attendance - Student ID not found")
        else:
            print("Manual Attendance - Student ID field is empty")
            
    def show_reports_frame(self):
        self.clear_main_frame()

        # Header
        ttk.Label(self.main_frame, text="Attendance Reports",
                  style="Title.TLabel").pack(pady=20)

        # Date selection frame
        date_frame = ttk.Frame(self.main_frame)
        date_frame.pack(pady=15)

        ttk.Label(date_frame, text="From:", style="TLabel").pack(side=tk.LEFT)
        self.start_date_entry = ttk.Entry(date_frame, width=12, style="TEntry")
        self.start_date_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(date_frame, text="📅",
                   command=lambda: self._show_calendar(self.start_date_entry),
                   style="TButton", width=3).pack(side=tk.LEFT, padx=5)

        ttk.Label(date_frame, text="To:", style="TLabel").pack(side=tk.LEFT, padx=10)
        self.end_date_entry = ttk.Entry(date_frame, width=12, style="TEntry")
        self.end_date_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(date_frame, text="📅",
                   command=lambda: self._show_calendar(self.end_date_entry),
                   style="TButton", width=3).pack(side=tk.LEFT, padx=5)

        ttk.Button(date_frame, text="🔍 Generate Report",
                   command=self.generate_report, style="TButton", width=15).pack(side=tk.LEFT, padx=15)

        # Report display frame
        report_frame = ttk.Frame(self.main_frame)
        report_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        self.report_tree = ttk.Treeview(report_frame,
                                        columns=("Name", "ID", "Date", "Time In"),
                                        show="headings", style="Treeview")
        self.report_tree.heading("Name", text="Student Name", anchor=tk.W)
        self.report_tree.heading("ID", text="Student ID", anchor=tk.W)
        self.report_tree.heading("Date", text="Date", anchor=tk.W)
        self.report_tree.heading("Time In", text="Time In", anchor=tk.W)

        self.report_tree.column("Name", width=200, anchor=tk.W)
        self.report_tree.column("ID", width=100, anchor=tk.W)
        self.report_tree.column("Date", width=120, anchor=tk.W)
        self.report_tree.column("Time In", width=120, anchor=tk.W)

        self.report_tree.pack(fill=tk.BOTH, expand=True)

        # Button frame
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=20)

        ttk.Button(button_frame, text="📄 Export to CSV",
                   command=self.export_report, style="TButton", width=15).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="⬅ Back",
                   command=self.show_home_frame, style="TButton", width=10).pack(side=tk.LEFT, padx=10)

    def generate_report(self):
        start_date_str = self.start_date_entry.get()
        end_date_str = self.end_date_entry.get()

        if not start_date_str or not end_date_str:
            messagebox.showerror("Error", "Please select date range")
            return

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Error", "Invalid date format (YYYY-MM-DD)")
            return

        # Clear existing data
        for item in self.report_tree.get_children():
            self.report_tree.delete(item)

        # Get report data
        report_data = self.db.get_attendance_report(start_date, end_date)

        # Add to treeview
        for record in report_data:
            self.report_tree.insert("", tk.END, values=record)

    def export_report(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if file_path:
            report_data = []
            for item in self.report_tree.get_children():
                report_data.append(self.report_tree.item(item, 'values'))

            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(["Student Name", "Student ID", "Date", "Time In"])  # Write header
                    writer.writerows(report_data)
                messagebox.showinfo("Success", f"Report exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export report: {e}")

    def _show_calendar(self, entry_widget):
        def set_date():
            selected_date = cal.get_date()
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, selected_date)
            top.destroy()

        top = tk.Toplevel(self.root)
        top.title("Select Date")

        today = date.today()
        cal = Calendar(top, selectmode='day',
                       year=today.year,
                       month=today.month,
                       day=today.day,
                       background="#ffffff",
                       foreground="#333",
                       selectbackground="#3498db",
                       selectforeground="white",
                       font=('Segoe UI', 11))
        cal.pack(pady=10)

        ttk.Button(top, text="OK", command=set_date, style="TButton").pack(pady=5)

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Release camera if active
        if self.video_capture and self.video_capture.isOpened():
            self.video_capture.release()
            self.video_capture = None

    def on_closing(self):
        """Clean up resources when closing the application"""
        if self.video_capture and self.video_capture.isOpened():
            self.video_capture.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceApp(root)
    root.mainloop()