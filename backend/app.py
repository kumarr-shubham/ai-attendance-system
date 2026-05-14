from flask import Flask, jsonify, request
from flask_cors import CORS
from supabase import create_client, Client
from dotenv import load_dotenv
import os
#import face_recognition
import numpy as np
import base64
import bcrypt
import jwt
import datetime
from PIL import Image
import io

load_dotenv()

app = Flask(__name__)
CORS(app)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
JWT_SECRET = os.getenv("JWT_SECRET", "smartattend_secret")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def decode_image(base64_str):
    if "," in base64_str:
        base64_str = base64_str.split(",")[1]
    img_bytes = base64.b64decode(base64_str)
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    return np.array(img)


def get_face_embedding(image_array):
    encodings = face_recognition.face_encodings(image_array)
    if len(encodings) == 0:
        return None
    return encodings[0].tolist()


# ---------------- HOME ----------------

@app.route("/")
def home():
    return jsonify({"message": "SmartAttend AI Backend Running"})


# ---------------- TEACHER REGISTER ----------------

@app.route("/register-teacher", methods=["POST"])
def register_teacher():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    name = data.get("name")

    existing = supabase.table("teachers").select("*").eq("username", username).execute()
    if existing.data:
        return jsonify({"error": "Username already exists"}), 400

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    response = supabase.table("teachers").insert({
        "username": username,
        "password": hashed,
        "name": name
    }).execute()

    teacher = response.data[0]
    token = jwt.encode({
        "teacher_id": teacher["teacher_id"],
        "name": teacher["name"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }, JWT_SECRET, algorithm="HS256")

    return jsonify({"token": token, "name": teacher["name"], "teacher_id": teacher["teacher_id"]})


# ---------------- TEACHER LOGIN ----------------

@app.route("/login-teacher", methods=["POST"])
def login_teacher():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    response = supabase.table("teachers").select("*").eq("username", username).execute()
    if not response.data:
        return jsonify({"error": "Invalid credentials"}), 401

    teacher = response.data[0]
    if not bcrypt.checkpw(password.encode(), teacher["password"].encode()):
        return jsonify({"error": "Invalid credentials"}), 401

    token = jwt.encode({
        "teacher_id": teacher["teacher_id"],
        "name": teacher["name"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }, JWT_SECRET, algorithm="HS256")

    return jsonify({"token": token, "name": teacher["name"], "teacher_id": teacher["teacher_id"]})


# ---------------- VERIFY STUDENT FACE ----------------

@app.route("/verify-student", methods=["POST"])
def verify_student():
    data = request.json
    image_base64 = data.get("image")

    img_array = decode_image(image_base64)
    new_embedding = get_face_embedding(img_array)

    if new_embedding is None:
        return jsonify({"matched": False, "error": "No face detected"}), 200

    students = supabase.table("students").select("*").execute().data

    for student in students:
        stored = student.get("face_embedding")
        if not stored or "encoding" not in stored:
            continue
        stored_encoding = np.array(stored["encoding"])
        distance = face_recognition.face_distance([stored_encoding], np.array(new_embedding))[0]
        if distance < 0.5:
            return jsonify({
                "matched": True,
                "student_id": student["student_id"],
                "name": student["name"],
                "roll_number": student["roll_number"]
            })

    return jsonify({"matched": False})


# ---------------- REGISTER STUDENT ----------------

@app.route("/register-student", methods=["POST"])
def register_student():
    data = request.json
    name = data.get("name")
    image_base64 = data.get("image")

    img_array = decode_image(image_base64)
    embedding = get_face_embedding(img_array)

    if embedding is None:
        return jsonify({"error": "No face detected in image"}), 400

    response = supabase.table("students").insert({
        "name": name,
        "roll_number": "",
        "face_embedding": {"encoding": embedding}
    }).execute()

    student = response.data[0]
    return jsonify({
        "message": "Student Registered Successfully",
        "student_id": student["student_id"],
        "name": student["name"]
    })


# ---------------- GET ALL SUBJECTS (for teacher) ----------------

@app.route("/subjects/<int:teacher_id>", methods=["GET"])
def get_subjects(teacher_id):
    response = supabase.table("subjects").select("*").eq("teacher_id", teacher_id).execute()
    return jsonify(response.data)


# ---------------- GET ALL SUBJECTS (for student enrollment) ----------------

@app.route("/all-subjects", methods=["GET"])
def get_all_subjects():
    response = supabase.table("subjects").select("*, teachers(name)").execute()
    return jsonify(response.data)


# ---------------- CREATE SUBJECT ----------------

@app.route("/create-subject", methods=["POST"])
def create_subject():
    data = request.json
    response = supabase.table("subjects").insert({
        "name": data.get("name"),
        "subject_code": data.get("subject_code"),
        "section": data.get("section"),
        "teacher_id": data.get("teacher_id")
    }).execute()
    return jsonify({"message": "Subject created", "data": response.data[0]})


# ---------------- DELETE SUBJECT ----------------

@app.route("/delete-subject/<int:subject_id>", methods=["DELETE"])
def delete_subject(subject_id):
    supabase.table("subjects").delete().eq("subject_id", subject_id).execute()
    return jsonify({"message": "Subject deleted"})


# ---------------- ENROLL STUDENT IN SUBJECT ----------------

@app.route("/enroll", methods=["POST"])
def enroll():
    data = request.json
    student_id = data.get("student_id")
    subject_id = data.get("subject_id")

    existing = supabase.table("subject_students") \
        .select("*").eq("student_id", student_id).eq("subject_id", subject_id).execute()
    if existing.data:
        return jsonify({"error": "Already enrolled"}), 400

    supabase.table("subject_students").insert({
        "student_id": student_id,
        "subject_id": subject_id
    }).execute()
    return jsonify({"message": "Enrolled successfully"})


# ---------------- UNENROLL STUDENT ----------------

@app.route("/unenroll", methods=["POST"])
def unenroll():
    data = request.json
    supabase.table("subject_students") \
        .delete() \
        .eq("student_id", data.get("student_id")) \
        .eq("subject_id", data.get("subject_id")) \
        .execute()
    return jsonify({"message": "Unenrolled successfully"})


# ---------------- TAKE ATTENDANCE (classroom photo) ----------------

@app.route("/take-attendance", methods=["POST"])
def take_attendance():
    data = request.json
    subject_id = data.get("subject_id")
    images = data.get("images")  # list of base64 images

    # Get all enrolled students for this subject
    enrolled = supabase.table("subject_students") \
        .select("student_id, students(student_id, name, face_embedding)") \
        .eq("subject_id", subject_id).execute().data

    if not enrolled:
        return jsonify({"error": "No students enrolled in this subject"}), 400

    present_ids = set()

    for image_base64 in images:
        img_array = decode_image(image_base64)
        locations = face_recognition.face_locations(img_array)
        detected_encodings = face_recognition.face_encodings(img_array, locations)

        for detected_enc in detected_encodings:
            for row in enrolled:
                student = row["students"]
                stored = student.get("face_embedding")
                if not stored or "encoding" not in stored:
                    continue
                stored_enc = np.array(stored["encoding"])
                distance = face_recognition.face_distance([stored_enc], detected_enc)[0]
                if distance < 0.5:
                    present_ids.add(student["student_id"])

    results = []
    logs = []

    for row in enrolled:
        student = row["students"]
        sid = student["student_id"]
        is_present = sid in present_ids
        logs.append({
            "subject_id": subject_id,
            "student_id": sid,
            "is_present": is_present
        })
        results.append({
            "student_id": sid,
            "name": student["name"],
            "is_present": is_present
        })

    supabase.table("attendance_logs").insert(logs).execute()

    return jsonify({"message": "Attendance marked", "results": results})


# ---------------- STUDENT STATS ----------------

@app.route("/student-stats/<int:student_id>", methods=["GET"])
def student_stats(student_id):
    enrolled = supabase.table("subject_students") \
        .select("subject_id").eq("student_id", student_id).execute().data
    enrolled_count = len(enrolled)

    all_logs = supabase.table("attendance_logs") \
        .select("is_present").eq("student_id", student_id).execute().data
    total = len(all_logs)
    present = sum(1 for l in all_logs if l["is_present"])
    overall = round((present / total * 100)) if total > 0 else 0

    return jsonify({
        "enrolled_count": enrolled_count,
        "classes_attended": present,
        "overall_attendance": overall
    })


# ---------------- STUDENT SUBJECTS WITH ATTENDANCE ----------------

@app.route("/student-subjects/<int:student_id>", methods=["GET"])
def student_subjects(student_id):
    enrolled = supabase.table("subject_students") \
        .select("subject_id, subjects(subject_id, name, subject_code, section)") \
        .eq("student_id", student_id).execute().data

    result = []
    for row in enrolled:
        subject = row["subjects"]
        sid = subject["subject_id"]

        total_logs = supabase.table("attendance_logs") \
            .select("id").eq("subject_id", sid).execute().data
        total = len(total_logs)

        present_logs = supabase.table("attendance_logs") \
            .select("id").eq("subject_id", sid).eq("student_id", student_id).eq("is_present", True).execute().data
        present = len(present_logs)

        attendance_pct = round((present / total * 100)) if total > 0 else 0

        result.append({
            "subject_id": sid,
            "name": subject["name"],
            "subject_code": subject["subject_code"],
            "section": subject["section"],
            "total_classes": total,
            "classes_attended": present,
            "attendance_pct": attendance_pct
        })

    return jsonify(result)


# ---------------- ATTENDANCE RECORDS (for teacher) ----------------

@app.route("/attendance-records/<int:subject_id>", methods=["GET"])
def attendance_records(subject_id):
    logs = supabase.table("attendance_logs") \
        .select("*, students(name)") \
        .eq("subject_id", subject_id) \
        .order("timestamp", desc=True) \
        .execute().data
    return jsonify(logs)


if __name__ == "__main__":
    app.run(debug=True)
