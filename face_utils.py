import cv2
import numpy as np
from database import Database

class FaceRecognizer:
    def __init__(self):
        self.db = Database()
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.known_faces = []
        self.known_face_ids = []
        self.known_face_names = []
        self.load_known_faces()
    
    def load_known_faces(self):
        employees = self.db.get_all_employees()
        for emp in employees:
            self.known_face_ids.append(emp[2])  # employee_id
            self.known_face_names.append(emp[1])  # name
    
    def detect_faces(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            image=gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        results = []
        for (x, y, w, h) in faces:
            results.append({
                'face_location': (x, y, w, h),
                'name': "Unknown",
                'emp_id': "Unknown"
            })
        
        return results