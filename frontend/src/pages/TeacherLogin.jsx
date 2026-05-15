import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./TeacherLogin.css";

function TeacherLogin() {
  const navigate = useNavigate();
  const [isLogin, setIsLogin] = useState(true);
  const [name, setName] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!username || !password) return alert("Please fill all fields");
    if (!isLogin && password !== confirmPassword) return alert("Passwords do not match");
    if (!isLogin && !name) return alert("Please enter your name");

    setLoading(true);
    try {
      const url = isLogin
        ? "http://127.0.0.1:5000/login-teacher"
        : "http://127.0.0.1:5000/register-teacher";

      const body = isLogin
        ? { username, password }
        : { username, password, name };

      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      const data = await res.json();
      if (data.error) return alert(data.error);

      localStorage.setItem("teacher_token", data.token);
      localStorage.setItem("teacher_name", data.name);
      localStorage.setItem("teacher_id", data.teacher_id);
      navigate("/teacher-dashboard");
    } catch {
      alert("Failed to connect to backend");
    }
    setLoading(false);
  };

  return (
    <div className="login-container">

      {/* HEADER */}
      <div className="login-header">
        <div className="login-header-logo">
          <img src="https://cdn-icons-png.flaticon.com/512/6843/6843783.png" alt="logo" />
          <div>
            <h2>SmartAttend <span>AI</span></h2>
            <p>Smart Attendance System using Face Recognition</p>
          </div>
        </div>
        {/* <h1 className="login-header-title">
          {isLogin ? "Login using Password" : "Create your teacher account to get started"} 
        </h1> */}
      </div>

      <div className="login-card">

        <div className="left-section">
          <button className="back-btn" onClick={() => navigate("/")}>← Back to Home</button>
          <img
            src="https://cdn-icons-png.flaticon.com/512/1995/1995574.png"
            alt="teacher"
            className="teacher-img"
          />
          <div className="welcome-box">
            <h2>{isLogin ? "Welcome Back!" : "Join SmartAttend AI"}</h2>
            <p>
              {isLogin
                ? "Login to mark attendance, manage students and view reports seamlessly."
                : "Register to create your teacher account and start managing attendance."}
            </p>
          </div>
        </div>

        <div className="right-section">
          <h1>{isLogin ? "Login using Password" : "Register Your Teacher Profile"}</h1>
          <p className="login-subtitle">
            {isLogin ? "Login to your teacher account" : "Create your teacher account to get started"}
          </p>

          {!isLogin && (
            <input
              type="text"
              placeholder="Enter your full name"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          )}

          <input
            type="text"
            placeholder="Enter your username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />

          <input
            type="password"
            placeholder="Enter your password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          {!isLogin && (
            <input
              type="password"
              placeholder="Confirm your password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
            />
          )}

          <button className="login-btn" onClick={handleSubmit} disabled={loading}>
            {loading ? "Please wait..." : isLogin ? "Login" : "Register Now"}
          </button>

          <button className="switch-btn" onClick={() => setIsLogin(!isLogin)}>
            {isLogin
              ? "Don't have an account? Register instead"
              : "Already have an account? Login instead"}
          </button>
        </div>
      
      </div>
    </div>
  );
}

export default TeacherLogin;
