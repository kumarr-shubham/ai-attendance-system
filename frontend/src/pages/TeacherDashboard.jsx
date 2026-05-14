import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { QRCodeSVG } from "qrcode.react";
import Webcam from "react-webcam";
import "./TeacherDashboard.css";

function TeacherDashboard() {
  const navigate = useNavigate();
  const teacherId = localStorage.getItem("teacher_id");
  const teacherName = localStorage.getItem("teacher_name");

  const [activeTab, setActiveTab] = useState("attendance");
  const [subjects, setSubjects] = useState([]);
  const [selectedSubject, setSelectedSubject] = useState("");
  const [photos, setPhotos] = useState([]);
  const [attendanceResults, setAttendanceResults] = useState([]);
  const [loading, setLoading] = useState(false);

  // Manage Subjects
  const [subjectName, setSubjectName] = useState("");
  const [subjectCode, setSubjectCode] = useState("");
  const [section, setSection] = useState("");

  // Attendance Records
  const [records, setRecords] = useState([]);
  const [recordSubject, setRecordSubject] = useState("");

  // Share Modal
  const [shareSubject, setShareSubject] = useState(null);

  // Photo source modal
  const [showPhotoOptions, setShowPhotoOptions] = useState(false);
  const [showCamera, setShowCamera] = useState(false);
  const webcamRef = useRef(null);

  const greeting = () => {
    const h = new Date().getHours();
    if (h < 12) return "Good Morning";
    if (h < 17) return "Good Afternoon";
    return "Good Evening";
  };

  const initials = teacherName
    ? teacherName.split(" ").map((w) => w[0]).join("").toUpperCase().slice(0, 2)
    : "T";

  useEffect(() => {
    if (!teacherId) { navigate("/teacher-login"); return; }
    fetchSubjects();
  }, []);

  const fetchSubjects = async () => {
    const res = await fetch(`https://smartattend-api-8xk0.onrender.com/subjects/${teacherId}`);
    const data = await res.json();
    setSubjects(data);
    if (data.length > 0) {
      setSelectedSubject(data[0].subject_id);
      setRecordSubject(data[0].subject_id);
    }
  };

  const handlePhotos = (e) => {
    const files = Array.from(e.target.files);
    const readers = files.map(
      (file) =>
        new Promise((resolve) => {
          const reader = new FileReader();
          reader.onload = (ev) => resolve(ev.target.result);
          reader.readAsDataURL(file);
        })
    );
    Promise.all(readers).then((results) => setPhotos(results));
  };

  const takeAttendance = async () => {
    if (!selectedSubject) return alert("Please select a subject");
    if (photos.length === 0) return alert("Please add at least one photo");
    setLoading(true);
    try {
      const res = await fetch("https://smartattend-api-8xk0.onrender.com/take-attendance", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ subject_id: parseInt(selectedSubject), images: photos }),
      });
      const data = await res.json();
      if (data.error) return alert(data.error);
      setAttendanceResults(data.results);
      setPhotos([]);
    } catch {
      alert("Failed to connect to backend");
    }
    setLoading(false);
  };

  const createSubject = async () => {
    if (!subjectName || !subjectCode || !section) return alert("Fill all fields");
    const res = await fetch("https://smartattend-api-8xk0.onrender.com/create-subject", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: subjectName,
        subject_code: subjectCode,
        section,
        teacher_id: parseInt(teacherId),
      }),
    });
    const data = await res.json();
    if (data.error) return alert(data.error);
    setSubjectName(""); setSubjectCode(""); setSection("");
    fetchSubjects();
  };

  const deleteSubject = async (subjectId) => {
    if (!window.confirm("Delete this subject?")) return;
    await fetch(`https://smartattend-api-8xk0.onrender.com/delete-subject/${subjectId}`, { method: "DELETE" });
    fetchSubjects();
  };

  const fetchRecords = async () => {
    if (!recordSubject) return;
    const res = await fetch(`https://smartattend-api-8xk0.onrender.com/attendance-records/${recordSubject}`);
    const data = await res.json();
    setRecords(data);
  };

  const selectedSubjectName = () => {
    const s = subjects.find((s) => String(s.subject_id) === String(recordSubject));
    return s ? s.name : "";
  };

  const selectedSubjectCode = () => {
    const s = subjects.find((s) => String(s.subject_id) === String(recordSubject));
    return s ? s.subject_code : "";
  };

  const logout = () => {
    localStorage.removeItem("teacher_token");
    localStorage.removeItem("teacher_name");
    localStorage.removeItem("teacher_id");
    navigate("/");
  };

  return (
    <div className="dashboard-page">

      {/* NAVBAR */}
      <div className="dash-navbar">
        <div className="dash-logo">
          <img src="https://cdn-icons-png.flaticon.com/512/6843/6843783.png" alt="logo" />
          <div>
            <h2>SmartAttend <span>AI</span></h2>
            <p>Smart Attendance System using Face Recognition</p>
          </div>
        </div>
        <div className="dash-profile">
          <div className="profile-circle">{initials}</div>
          <div>
            <h4>{teacherName}</h4>
            <p>Teacher</p>
          </div>
        </div>
      </div>

      <div className="dash-body">

        {/* HERO */}
        <div className="dash-hero">
          <h1>{greeting()}, {teacherName}! 👋</h1>
          <p>Here's a summary of your attendance activity today.</p>
        </div>

        <div className="logout-container">
          <button className="logout-btn" onClick={logout}>⏻ Logout</button>
        </div>

        {/* TABS */}
        <div className="tabs">
          <button
            className={`tab-btn ${activeTab === "attendance" ? "tab-active-red" : ""}`}
            onClick={() => setActiveTab("attendance")}
          >
            🖥️ Take Attendance
          </button>
          <button
            className={`tab-btn ${activeTab === "subjects" ? "tab-active-grey" : ""}`}
            onClick={() => setActiveTab("subjects")}
          >
            📋 Manage Subjects
          </button>
          <button
            className={`tab-btn ${activeTab === "records" ? "tab-active-black" : ""}`}
            onClick={() => { setActiveTab("records"); fetchRecords(); }}
          >
            📊 Attendance Records
          </button>
        </div>

        {/* TAB: TAKE ATTENDANCE */}
        {activeTab === "attendance" && (
          <div className="tab-content">
            <h2>Take AI Attendance</h2>
            <p className="tab-sub">Select Subject</p>
            <div className="attendance-controls">
              <select
                value={selectedSubject}
                onChange={(e) => setSelectedSubject(e.target.value)}
                className="subject-select"
              >
                {subjects.map((s) => (
                  <option key={s.subject_id} value={s.subject_id}>
                    {s.name} - {s.subject_code}
                  </option>
                ))}
              </select>
              <button className="add-photos-btn" onClick={() => setShowPhotoOptions(true)}>
                🖼️ Add Photos
              </button>
            </div>

            {/* PHOTO OPTIONS MODAL */}
            {showPhotoOptions && (
              <div className="photo-options-overlay" onClick={() => setShowPhotoOptions(false)}>
                <div className="photo-options-box" onClick={(e) => e.stopPropagation()}>
                  <h3>Choose Photo Source</h3>
                  <div className="photo-options-btns">
                    <button
                      className="photo-opt-btn"
                      onClick={() => { setShowPhotoOptions(false); setShowCamera(true); }}
                    >
                      📷 Camera
                    </button>
                    <label className="photo-opt-btn">
                      📁 Upload Photo
                      <input type="file" accept="image/*" multiple onChange={(e) => { handlePhotos(e); setShowPhotoOptions(false); }} hidden />
                    </label>
                  </div>
                  <button className="photo-opt-close" onClick={() => setShowPhotoOptions(false)}>Cancel</button>
                </div>
              </div>
            )}

            {/* CAMERA MODAL */}
            {showCamera && (
              <div className="photo-options-overlay" onClick={() => setShowCamera(false)}>
                <div className="camera-modal-box" onClick={(e) => e.stopPropagation()}>
                  <h3>Take Class Photo</h3>
                  <Webcam
                    ref={webcamRef}
                    screenshotFormat="image/jpeg"
                    className="teacher-webcam"
                  />
                  <div className="camera-modal-btns">
                    <button
                      className="photo-opt-btn"
                      onClick={() => {
                        const img = webcamRef.current.getScreenshot();
                        if (img) setPhotos((prev) => [...prev, img]);
                        setShowCamera(false);
                      }}
                    >
                      📸 Capture
                    </button>
                    <button className="photo-opt-close" onClick={() => setShowCamera(false)}>Cancel</button>
                  </div>
                </div>
              </div>
            )}

            {photos.length > 0 && (
              <div className="photo-preview">
                {photos.map((p, i) => (
                  <img key={i} src={p} alt={`photo-${i}`} className="preview-img" />
                ))}
              </div>
            )}

            {photos.length > 0 && (
              <button className="process-btn" onClick={takeAttendance} disabled={loading}>
                {loading ? "Processing..." : "▶ Process Attendance"}
              </button>
            )}

            {attendanceResults.length > 0 && (
              <div className="results-box">
                <h3>Attendance Results</h3>
                {attendanceResults.map((r) => (
                  <div key={r.student_id} className={`result-row ${r.is_present ? "present" : "absent"}`}>
                    <span>{r.is_present ? "✅" : "❌"} {r.name}</span>
                    <span>{r.is_present ? "Present" : "Absent"}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* TAB: MANAGE SUBJECTS */}
        {activeTab === "subjects" && (
          <div className="tab-content">
            <h2>Manage Subjects</h2>
            <div className="create-subject-form">
              <input
                type="text"
                placeholder="Subject Name"
                value={subjectName}
                onChange={(e) => setSubjectName(e.target.value)}
              />
              <input
                type="text"
                placeholder="Subject Code (e.g. IT601)"
                value={subjectCode}
                onChange={(e) => setSubjectCode(e.target.value)}
              />
              <input
                type="text"
                placeholder="Section (e.g. B)"
                value={section}
                onChange={(e) => setSection(e.target.value)}
              />
              <button className="create-btn" onClick={createSubject}>+ Create Subject</button>
            </div>

            <div className="subjects-list">
              {subjects.length === 0 && <p className="empty-msg">No subjects created yet.</p>}
              {subjects.map((s) => (
                <div key={s.subject_id} className="subject-wrapper-manage">
                  <div className="subject-row">
                    <div>
                      <strong>{s.name}</strong>
                      <span className="subject-meta"> — {s.subject_code} | Section: {s.section}</span>
                    </div>
                    <button className="delete-btn" onClick={() => deleteSubject(s.subject_id)}>Delete</button>
                  </div>
                  <button className="share-btn" onClick={() => setShareSubject(s)}>
                    🔗 Share Code: {s.name}
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* SHARE MODAL */}
        {shareSubject && (
          <div className="modal-overlay" onClick={() => setShareSubject(null)}>
            <div className="modal-box" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h2>Share Class Link</h2>
                <button className="modal-close" onClick={() => setShareSubject(null)}>✕</button>
              </div>
              <h3 className="modal-sub">Scan to Join</h3>
              <div className="modal-body">
                <div className="modal-left">
                  <p className="modal-label">Copy Link</p>
                  <div className="modal-link-box">
                    {`${window.location.origin}/student-auth?subject_id=${shareSubject.subject_id}`}
                  </div>
                  <div className="modal-code-box">{shareSubject.subject_code}</div>
                  <button
                    className="modal-copy-btn"
                    onClick={() => {
                      navigator.clipboard.writeText(
                        `${window.location.origin}/student-auth?subject_id=${shareSubject.subject_id}`
                      );
                      alert("Link copied!");
                    }}
                  >
                    Copy this link to share on WhatsApp or Email
                  </button>
                </div>
                <div className="modal-right">
                  <p className="modal-label">Scan to Join</p>
                  <QRCodeSVG
                    value={`${window.location.origin}/student-auth?subject_id=${shareSubject.subject_id}`}
                    size={180}
                  />
                  <p className="modal-qr-label">QRCODE for class joining</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB: ATTENDANCE RECORDS */}
        {activeTab === "records" && (
          <div className="tab-content">
            <h2>Attendance Records</h2>
            <div className="records-controls">
              <select
                value={recordSubject}
                onChange={(e) => setRecordSubject(e.target.value)}
                className="subject-select"
              >
                {subjects.map((s) => (
                  <option key={s.subject_id} value={s.subject_id}>
                    {s.name} - {s.subject_code}
                  </option>
                ))}
              </select>
              <button className="fetch-btn" onClick={fetchRecords}>View Records</button>
            </div>

            {records.length === 0 && <p className="empty-msg">No records found.</p>}
            <div className="records-table-wrapper">
              {records.length > 0 && (() => {
                // Group by minute-level timestamp to identify sessions
                const sessions = {};
                records.forEach((r) => {
                  const key = new Date(r.timestamp).toLocaleString("en-US", { minute: "2-digit", hour: "2-digit", day: "2-digit", month: "2-digit", year: "numeric" });
                  if (!sessions[key]) {
                    sessions[key] = { time: r.timestamp, subject: selectedSubjectName(), code: selectedSubjectCode(), present: 0, total: 0 };
                  }
                  sessions[key].total += 1;
                  if (r.is_present) sessions[key].present += 1;
                });
                return (
                  <table className="records-table">
                    <thead>
                      <tr>
                        <th>Time</th>
                        <th>Subject</th>
                        <th>Subject Code</th>
                        <th>Attendance Stats</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.values(sessions).map((s, i) => (
                        <tr key={i}>
                          <td>{new Date(s.time).toLocaleString()}</td>
                          <td>{s.subject}</td>
                          <td>{s.code}</td>
                          <td><span className="att-badge">✅ {s.present} / {s.total} Students</span></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                );
              })()}
            </div>
          </div>
        )}

      </div>
    </div>
  );
}

export default TeacherDashboard;
