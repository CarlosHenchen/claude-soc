import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider, useAuth } from "@/lib/auth";
import { AppLayout } from "@/components/layout/AppLayout";
import { Login } from "@/pages/Login";
import { Assessments } from "@/pages/Assessments";
import { AssessmentRun } from "@/pages/AssessmentRun";
import { Dashboard } from "@/pages/Dashboard";
import { Frameworks } from "@/pages/Frameworks";
import { Users } from "@/pages/Users";

function Protected({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="p-8 text-muted-foreground">Carregando…</div>;
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

function AdminOnly({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();
  if (!user?.is_admin) return <Navigate to="/assessments" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            element={
              <Protected>
                <AppLayout />
              </Protected>
            }
          >
            <Route path="/assessments" element={<Assessments />} />
            <Route path="/assessments/:id/run" element={<AssessmentRun />} />
            <Route path="/assessments/:id/dashboard" element={<Dashboard />} />
            <Route path="/frameworks" element={<Frameworks />} />
            <Route
              path="/users"
              element={
                <AdminOnly>
                  <Users />
                </AdminOnly>
              }
            />
            <Route path="/" element={<Navigate to="/assessments" replace />} />
          </Route>
          <Route path="*" element={<Navigate to="/assessments" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
