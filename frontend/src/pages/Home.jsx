import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Home.css";

function Home() {
  const navigate = useNavigate();
  const [showPortal, setShowPortal] = useState(false);

  return (
    <div className="home-wrapper">

      {/* NAVBAR */}
      <nav className="navbar">
        <div className="nav-logo">
          <img src="https://cdn-icons-png.flaticon.com/512/6843/6843783.png" alt="logo" />
          <div>
            <h2>SmartAttend <span>AI</span></h2>
            <p>Smart Attendance System using Face Recognition</p>
          </div>
        </div>
        <ul className="nav-links">
          <li><a href="#home">Home</a></li>
          <li><a href="#features">Features</a></li>
          <li><a href="#about">About</a></li>
          <li><a href="#how">How It Works</a></li>
          <li><a href="#contact">Contact</a></li>
        </ul>
        <button className="nav-cta" onClick={() => setShowPortal(true)}>Get Started</button>
      </nav>

      {/* HERO */}
      <section className="hero" id="home" style={{ backgroundImage: `url(${process.env.PUBLIC_URL}/ai-face.png), radial-gradient(ellipse at top right, #1a1a3e 0%, #0a0a1a 60%)`, backgroundPosition: 'center, center', backgroundSize: 'cover, cover', backgroundRepeat: 'no-repeat' }}>
        <div className="hero-left">
          <div className="hero-badge">AI-Powered | Smart | Secure</div>
          <h1>Smart Attendance<br />with <span>AI Power</span></h1>
          <p>SmartAttend AI uses advanced face recognition technology to automate attendance tracking, save time, and ensure accuracy.</p>
          <div className="hero-btns">
            <button className="btn-primary" onClick={() => setShowPortal(true)}>Get Started →</button>
            {/* <button className="btn-secondary">Learn More ▶</button> */}
          </div>
        </div>
        {/* <div className="hero-right">
          <div className="hero-badge-card top-left">
            <span>🎯</span>
            <div><strong>Face Recognition</strong><small>Accuracy 99.9%</small></div>
          </div>
          <div className="hero-badge-card bottom-left">
            <span>⏱️</span>
            <div><strong>Real-Time</strong><small>Attendance</small></div>
          </div>
          <div className="hero-badge-card top-right">
            <span>🛡️</span>
            <div><strong>Secure</strong><small>& Reliable</small></div>
          </div>
          <div className="hero-badge-card bottom-right">
            <span>☁️</span>
            <div><strong>Cloud</strong><small>Database</small></div>
          </div>
        </div> */}
      </section>

      {/* FEATURES */}
      <section className="features-section" id="features">
        <p className="section-tag">FEATURES</p>
        <h2>Powerful Features for Smart Management</h2>
        <div className="features-divider"></div>
        <div className="features-grid">
          {[
            { icon: "🧑", title: "Face Recognition", desc: "Advanced AI algorithm for accurate and fast face recognition." },
            { icon: "⏱️", title: "Real-Time Tracking", desc: "Track attendance in real-time with instant updates." },
            { icon: "☁️", title: "Cloud Database", desc: "Secure cloud storage with easy access and data management." },
            { icon: "📱", title: "QR Code Attendance", desc: "Flexible attendance marking using QR code scanning." },
            { icon: "📊", title: "AI Analytics", desc: "Get insights and reports with AI-powered analytics." },
          ].map((f, i) => (
            <div className="feature-card" key={i}>
              <div className="feature-icon">{f.icon}</div>
              <h3>{f.title}</h3>
              <p>{f.desc}</p>
            </div>
          ))}
        </div>

        {/* STATS */}
        <div className="stats-bar">
          <div className="stat-item"><span>👥</span><div><strong>1,200+</strong><small>Students</small></div></div>
          <div className="stat-item"><span>🏛️</span><div><strong>50+</strong><small>Departments</small></div></div>
          <div className="stat-item green"><span>🎯</span><div><strong>98.9%</strong><small>Accuracy</small></div></div>
          <div className="stat-item"><span>🛡️</span><div><strong>100%</strong><small>Secure</small></div></div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="how-section" id="how">
        <p className="section-tag">HOW IT WORKS</p>
        <h2>How SmartAttend <span>AI</span> Works</h2>
        <div className="features-divider"></div>
        <p className="how-subtitle">Simple, secure and AI-powered attendance management in just a few steps</p>
        <div className="how-grid">
          {[
            { num: "01", icon: "📖", title: "Create Subject", desc: "Teachers create subjects and attendance sessions instantly." },
            { num: "02", icon: "🧑", title: "Face Registration", desc: "Students register securely using AI face authentication." },
            { num: "03", icon: "🤖", title: "AI Recognition", desc: "System scans and recognizes faces in real time." },
            { num: "04", icon: "☁️", title: "Cloud Storage", desc: "Attendance records are stored securely in Supabase cloud database." },
            { num: "05", icon: "📊", title: "Analytics Dashboard", desc: "Teachers and students can track attendance reports instantly." },
          ].map((step, i, arr) => (
            <div key={i} className="how-step-wrapper">
              <div className="how-card">
                <div className="how-num">{step.num}</div>
                <div className="how-icon">{step.icon}</div>
                <h3>{step.title}</h3>
                <p>{step.desc}</p>
              </div>
              {i < arr.length - 1 && <div className="how-arrow">→</div>}
            </div>
          ))}
        </div>
        <div className="how-timeline">
          {[0,1,2,3,4].map(i => <div key={i} className="how-dot"></div>)}
        </div>
        <div className="how-processing">● AI Processing...</div>
      </section>

      {/* FOOTER */}
      <footer className="home-footer" id="contact">
        <div className="footer-col">
          <div className="footer-logo">
            <img src="https://cdn-icons-png.flaticon.com/512/6843/6843783.png" alt="logo" />
            <div>
              <h3>SmartAttend <span>AI</span></h3>
              <small>Smart Attendance System using Face Recognition</small>
            </div>
          </div>
          <p>Making attendance smart, easy and reliable with AI technology.</p>
        </div>
        <div className="footer-col">
          <h4>Quick Links</h4>
          <ul>
            <li><a href="#home">Home</a></li>
            <li><a href="#features">Features</a></li>
            <li><a href="#about">About Us</a></li>
            <li><a href="#how">How It Works</a></li>
            <li><a href="#contact">Contact</a></li>
          </ul>
        </div>
        <div className="footer-col">
          <h4>Support</h4>
          <ul>
            <li><a href="#Help">Help Center</a></li>
            <li><a href="#Documentation">Documentation</a></li>
            <li><a href="#Privacy">Privacy Policy</a></li>
            <li><a href="#Terms ">Terms & Conditions</a></li>
            <li><a href="#FAQ">FAQ</a></li>
          </ul>
        </div>
        <div className="footer-col">
          <h4>Contact Us</h4>
          <p>✉️ support@smartattend.ai</p>
          {/* <p>📞 +91 99 43210</p> */}
          <p>📍 Kolkata, West Bengal, India</p>
        </div>
        <div className="footer-col">
          <h4>Follow Us</h4>
          <div className="social-icons">
            <span>f</span>
            <span>𝕏</span>
            <span>in</span>
            <span>📷</span>
          </div>
        </div>
        <div className="footer-bottom">
          © 2024 SmartAttend AI. All rights reserved.
        </div>
      </footer>

      {/* PORTAL POPUP */}
      {showPortal && (
        <div className="portal-overlay" onClick={() => setShowPortal(false)}>
          <div className="portal-modal" onClick={(e) => e.stopPropagation()}>
            <button className="portal-close" onClick={() => setShowPortal(false)}>✕</button>
            <p className="portal-tag">PORTAL ACCESS</p>
            <h2>Choose Your Portal</h2>
            <div className="portal-divider"></div>
            <div className="portal-cards">
              <div className="portal-card">
                <img src="https://cdn-icons-png.flaticon.com/512/2995/2995620.png" alt="student" />
                <div>
                  <h3>Student Portal</h3>
                  <p>Mark your attendance and view your records easily.</p>
                  <button onClick={() => navigate("/student-auth")}>Go to Student Portal →</button>
                </div>
              </div>
              <div className="portal-card">
                <img src="https://cdn-icons-png.flaticon.com/512/1995/1995574.png" alt="teacher" />
                <div>
                  <h3>Teacher Portal</h3>
                  <p>Manage classes, view reports and automate attendance.</p>
                  <button onClick={() => navigate("/teacher-login")}>Go to Teacher Portal →</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}

export default Home;
