import React, { useRef, useState } from "react";
import Webcam from "react-webcam";
import { useNavigate } from "react-router-dom";
import "./StudentAuth.css";

function StudentAuth() {
  const webcamRef = useRef(null);
  const navigate = useNavigate();

  const [photo, setPhoto] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showRegister, setShowRegister] = useState(false);
  const [name, setName] = useState("");

  const takePhoto = () => {
    const img = webcamRef.current.getScreenshot();
    setPhoto(img);
    setShowRegister(false);
  };

  const verifyPhoto = async () => {
    if (!photo) return alert("Please take a photo first");
    setLoading(true);
    try {
      const res = await fetch("https://smartattend-api-8xk0.onrender.com", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: photo }),
      });
      const data = await res.json();

      if (data.matched) {
        localStorage.setItem("student_id", data.student_id);
        localStorage.setItem("student_name", data.name);
        navigate("/student");
      } else {
        setShowRegister(true);
      }
    } catch {
      alert("Failed to connect to backend");
    }
    setLoading(false);
  };

  const registerStudent = async () => {
    if (!name.trim()) return alert("Please enter your name");
    setLoading(true);
    try {
      const res = await fetch("https://smartattend-api-8xk0.onrender.com/verify-student", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, image: photo }),
      });
      const data = await res.json();
      if (data.error) return alert(data.error);
      localStorage.setItem("student_id", data.student_id);
      localStorage.setItem("student_name", data.name);
      navigate("/student");
    } catch {
      alert("Failed to connect to backend");
    }
    setLoading(false);
  };

  return (
    <div className="auth-page">
      <div className="auth-navbar">
        <div className="auth-logo">
          <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" alt="logo" />
          <div>
            <h2>SmartAttend <span>AI</span></h2>
            <p>Smart Attendance System using Face Recognition</p>
          </div>
        </div>
        <button className="back-home-btn" onClick={() => navigate("/")}>← Go back to Home</button>
      </div>

      <div className="auth-body">
        <h1>Verify Your Photo</h1>
        <p>Position your face in the center</p>

        <div className="webcam-box">
          {photo ? (
            <img src={photo} alt="captured" className="captured-photo" />
          ) : (
            <Webcam ref={webcamRef} screenshotFormat="image/jpeg" className="webcam-feed" />
          )}
          <button className="take-photo-btn" onClick={photo ? () => setPhoto(null) : takePhoto}>
            {photo ? "Retake Photo" : "Take Photo"}
          </button>
        </div>

        <button className="verify-btn" onClick={verifyPhoto} disabled={loading}>
          {loading ? "Verifying..." : " Verify Photo"}
        </button>

        {showRegister && (
          <div className="register-section">
            <h3>Face not recognized. Register below:</h3>
            <input
              type="text"
              placeholder="Enter your full name"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
            <button className="register-btn" onClick={registerStudent} disabled={loading}>
              {loading ? "Registering..." : "Register"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default StudentAuth;
