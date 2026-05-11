import { Button, Card, Form, Input, Typography, message } from "antd";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";

export default function LoginPage() {
  const navigate = useNavigate();

  const onFinish = async (values: { username: string; password: string }) => {
    try {
      const { data } = await api.post("/admin/auth/login", values);
      localStorage.setItem("admin_token", data.access_token);
      navigate("/orders");
    } catch {
      message.error("Login failed");
    }
  };

  return (
    <div style={{ minHeight: "100vh", display: "grid", placeItems: "center", background: "linear-gradient(135deg, #f4f6fb, #dde6f7)" }}>
      <Card style={{ width: 360 }}>
        <Typography.Title level={3}>Admin Login</Typography.Title>
        <Form layout="vertical" onFinish={onFinish}>
          <Form.Item name="username" label="Username" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="password" label="Password" rules={[{ required: true }]}>
            <Input.Password />
          </Form.Item>
          <Button type="primary" htmlType="submit" block>Sign In</Button>
        </Form>
      </Card>
    </div>
  );
}
