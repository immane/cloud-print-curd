import { Layout, Menu } from "antd";
import { Navigate, Route, Routes, useLocation, useNavigate } from "react-router-dom";
import DashboardPage from "../pages/DashboardPage";
import OrdersPage from "../pages/OrdersPage";
import OrderDetailPage from "../pages/OrderDetailPage";
import FilesPage from "../pages/FilesPage";
import LibraryPage from "../pages/LibraryPage";
import PricesPage from "../pages/PricesPage";
import UsersPage from "../pages/UsersPage";
import PaymentsPage from "../pages/PaymentsPage";
import SupportPage from "../pages/SupportPage";
import ReportsPage from "../pages/ReportsPage";
import AuditLogsPage from "../pages/AuditLogsPage";
import TopSearchBar from "../components/TopSearchBar";

export default function AdminLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { Header, Content, Sider } = Layout;

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Sider theme="light">
        <div style={{ padding: 16, fontWeight: 700 }}>Cloud Print</div>
        <Menu
          selectedKeys={[location.pathname.split("/")[1] || "dashboard"]}
          items={[
            { key: "dashboard", label: "Dashboard" },
            { key: "orders", label: "Orders" },
            { key: "files", label: "Files" },
            { key: "library", label: "Library" },
            { key: "prices", label: "Prices" },
            { key: "users", label: "Users" },
            { key: "payments", label: "Payments" },
            { key: "support", label: "Customer Service" },
            { key: "reports", label: "Reports" },
            { key: "audit", label: "Audit Logs" }
          ]}
          onClick={(e) => navigate(`/${e.key}`)}
        />
      </Sider>
      <Layout>
        <Header style={{ background: "#fff", paddingInline: 16 }}>
          <TopSearchBar />
        </Header>
        <Content style={{ margin: 24 }}>
          <Routes>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/orders" element={<OrdersPage />} />
            <Route path="/orders/:id" element={<OrderDetailPage />} />
            <Route path="/files" element={<FilesPage />} />
            <Route path="/library" element={<LibraryPage />} />
            <Route path="/prices" element={<PricesPage />} />
            <Route path="/users" element={<UsersPage />} />
            <Route path="/payments" element={<PaymentsPage />} />
            <Route path="/support" element={<SupportPage />} />
            <Route path="/reports" element={<ReportsPage />} />
            <Route path="/audit" element={<AuditLogsPage />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  );
}
