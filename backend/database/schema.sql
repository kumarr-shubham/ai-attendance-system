CREATE TABLE students (

    student_id BIGSERIAL PRIMARY KEY,

    name TEXT,

    roll_number TEXT,

    face_embedding JSONB,

    created_at TIMESTAMPTZ DEFAULT NOW()

);



CREATE TABLE teachers (

    teacher_id BIGSERIAL PRIMARY KEY,

    username TEXT,

    password TEXT,

    name TEXT

);



CREATE TABLE subjects (

    subject_id BIGSERIAL PRIMARY KEY,

    subject_code TEXT,

    name TEXT,

    section TEXT,

    teacher_id BIGINT REFERENCES teachers(teacher_id)

);



CREATE TABLE attendance_logs (

    id BIGSERIAL PRIMARY KEY,

    timestamp TIMESTAMPTZ DEFAULT NOW(),

    subject_id BIGINT REFERENCES subjects(subject_id),

    student_id BIGINT REFERENCES students(student_id),

    is_present BOOLEAN

);



CREATE TABLE subject_students (

    subject_id BIGINT REFERENCES subjects(subject_id),

    student_id BIGINT REFERENCES students(student_id)

);