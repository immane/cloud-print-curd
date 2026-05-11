import { Navigate, Route, Routes } from "react-router-dom";
import LoginPage from "./pages/LoginPage";
import AdminLayout from "./layout/AdminLayout";
import { useAdminAuth } from "./hooks/useAdminAuth";

function RequireAuth({ children }: { children: JSX.Element }) {
  const { isAuthed } = useAdminAuth();
  if (!isAuthed) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/*" element={<RequireAuth><AdminLayout /></RequireAuth>} />
    </Routes>
  );
}
