import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./StudentPortal.css";

function StudentPortal() {
  const navigate = useNavigate();
  const studentId = localStorage.getItem("student_id");
  const studentName = localStorage.getItem("student_name");

  const [stats, setStats] = useState({ enrolled_count: 0, classes_attended: 0, overall_attendance: 0 });
  const [subjects, setSubjects] = useState([]);
  const [allSubjects, setAllSubjects] = useState([]);
  const [showEnroll, setShowEnroll] = useState(false);

  const greeting = () => {
    const h = new Date().getHours();
    if (h < 12) return "Good Morning";
    if (h < 17) return "Good Afternoon";
    return "Good Evening";
  };

  const initials = studentName ? studentName.split(" ").map(w => w[0]).join("").toUpperCase().slice(0, 2) : "S";

  useEffect(() => {
    if (!studentId) { navigate("/student-auth"); return; }
    fetchStats();
    fetchSubjects();
  }, [studentId]);

  const fetchStats = async () => {
    const res = await fetch(`https://smartattend-api-8xk0.onrender.com/student-stats/${studentId}`);
    const data = await res.json();
    setStats(data);
  };

  const fetchSubjects = async () => {
    const res = await fetch(`https://smartattend-api-8xk0.onrender.com/student-subjects/${studentId}`);
    const data = await res.json();
    setSubjects(data);
  };

  const fetchAllSubjects = async () => {
    const res = await fetch("https://smartattend-api-8xk0.onrender.com/all-subjects");
    const data = await res.json();
    setAllSubjects(data);
    setShowEnroll(true);
  };

  const enroll = async (subjectId) => {
    const res = await fetch("https://smartattend-api-8xk0.onrender.com/enroll", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ student_id: parseInt(studentId), subject_id: subjectId }),
    });
    const data = await res.json();
    if (data.error) return alert(data.error);
    setShowEnroll(false);
    fetchStats();
    fetchSubjects();
  };

  const unenroll = async (subjectId) => {
    await fetch("https://smartattend-api-8xk0.onrender.com/unenroll", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ student_id: parseInt(studentId), subject_id: subjectId }),
    });
    fetchStats();
    fetchSubjects();
  };

  const logout = () => {
    localStorage.removeItem("student_id");
    localStorage.removeItem("student_name");
    navigate("/");
  };

  return (
    <div className="student-portal">

      <div className="top-navbar">
        <div className="logo-section">
          <img src="https://cdn-icons-png.flaticon.com/512/6843/6843783.png" alt="logo" className="portal-logo" />
          <div>
            <h2>SmartAttend <span>AI</span></h2>
            <p>Smart Attendance System using Face Recognition</p>
          </div>
        </div>
        <div className="profile-section">
          <div className="profile-circle">{initials}</div>
          <div>
            <h4>{studentName}</h4>
            <p>Student</p>
          </div>
        </div>
      </div>

      <div className="hero-card">
        <h1>{greeting()}, {studentName}! 🎓</h1>
        <p>Track your attendance and enrolled subjects below.</p>
      </div>

      <div className="logout-container">
        <button className="logout-btn" onClick={logout}>⏻ Logout</button>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">🗓️</div>
          <div>
            <h2>{stats.enrolled_count}</h2>
            <p>Enrolled Subjects</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">✅</div>
          <div>
            <h2>{stats.classes_attended}</h2>
            <p>Classes Attended</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div>
            <h2>{stats.overall_attendance}%</h2>
            <p>Overall Attendance</p>
          </div>
        </div>
      </div>

      <div className="subjects-header">
        <h2>📖 Your Enrolled Subjects</h2>
        <button className="enroll-btn" onClick={fetchAllSubjects}>+ Enroll in Subject</button>
      </div>

      {showEnroll && (
        <div className="enroll-modal">
          <h3>Available Subjects</h3>
          {allSubjects.map(s => (
            <div key={s.subject_id} className="enroll-row">
              <span>{s.name} — {s.subject_code} | Section: {s.section}</span>
              <button onClick={() => enroll(s.subject_id)}>Enroll</button>
            </div>
          ))}
          <button className="close-btn" onClick={() => setShowEnroll(false)}>Close</button>
        </div>
      )}

      <div className="subjects-grid">
        {subjects.map((subject) => (
          <div className="subject-wrapper" key={subject.subject_id}>
            <div className="subject-card">
              <h2>{subject.name}</h2>
              <p><strong>Code:</strong> <span className="code-badge">{subject.subject_code}</span> | Section: {subject.section}</p>
              <div className="subject-stats-row">
                <div className="subject-stat-box">
                  <span>🗓️</span>
                  <small>{subject.total_classes} Total</small>
                </div>
                <div className="subject-stat-box">
                  <span>✅</span>
                  <small>{subject.classes_attended} Present</small>
                </div>
                <div className="subject-stat-box">
                  <span>📊</span>
                  <small>{subject.attendance_pct}%</small>
                </div>
              </div>
            </div>
            <button className="unenroll-btn" onClick={() => unenroll(subject.subject_id)}>
              🚪 Unenroll from this course
            </button>
          </div>
        ))}
      </div>

      {/* <div className="portal-footer">🛡️ Powered by AI Face Recognition</div> */}
    </div>
  );
}

export default StudentPortal;
