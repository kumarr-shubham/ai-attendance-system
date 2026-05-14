import { BrowserRouter, Routes, Route } from "react-router-dom";

import Home from "./pages/Home";
import TeacherLogin from "./pages/TeacherLogin";
import TeacherDashboard from "./pages/TeacherDashboard";
import StudentPortal from "./pages/StudentPortal";
import StudentAuth from "./pages/StudentAuth";

function App() {

  return (

    <BrowserRouter>

      <Routes>

        <Route
          path="/"
          element={<Home />}
        />

        <Route
          path="/teacher-login"
          element={<TeacherLogin />}
        />

        <Route
          path="/teacher-dashboard"
          element={<TeacherDashboard />}
        />

        <Route
          path="/student-auth"
          element={<StudentAuth />}
        />

        <Route
          path="/student"
          element={<StudentPortal />}
        />

      </Routes>

    </BrowserRouter>

  );
}

export default App;