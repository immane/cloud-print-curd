import { Button, Card, Form, Input, InputNumber, Select, Space, Table } from "antd";
import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";

export default function LibraryPage() {
  const [form] = Form.useForm();
  const { data: categories, refetch: refetchCategories } = useQuery({
    queryKey: ["admin-library-categories"],
    queryFn: async () => (await api.get("/admin/library/categories")).data
  });

  const createCategory = async () => {
    const values = await form.validateFields(["name", "slug"]);
    await api.post("/admin/library/categories", { ...values, order: 0 });
    refetchCategories();
  };

  const createResource = async () => {
    const values = await form.validateFields(["title", "category_id", "file_id", "page_count", "price_override_cents"]);
    await api.post("/admin/library/resources", values);
  };

  return (
    <Space direction="vertical" style={{ width: "100%" }}>
      <Card title="Categories">
        <Space>
          <Form form={form} layout="inline">
            <Form.Item name="name" rules={[{ required: true }]}><Input placeholder="Name" /></Form.Item>
            <Form.Item name="slug" rules={[{ required: true }]}><Input placeholder="Slug" /></Form.Item>
            <Button type="primary" onClick={createCategory}>Create Category</Button>
          </Form>
        </Space>
        <Table rowKey="id" dataSource={categories || []} pagination={false} columns={[{ title: "ID", dataIndex: "id" }, { title: "Name", dataIndex: "name" }, { title: "Slug", dataIndex: "slug" }]} />
      </Card>

      <Card title="Create Resource">
        <Form form={form} layout="inline">
          <Form.Item name="title" rules={[{ required: true }]}><Input placeholder="Title" /></Form.Item>
          <Form.Item name="category_id" rules={[{ required: true }]}><Select style={{ width: 140 }} options={(categories || []).map((c: any) => ({ label: c.name, value: c.id }))} /></Form.Item>
          <Form.Item name="file_id" rules={[{ required: true }]}><InputNumber placeholder="File ID" /></Form.Item>
          <Form.Item name="page_count"><InputNumber placeholder="Pages" /></Form.Item>
          <Form.Item name="price_override_cents"><InputNumber placeholder="Override(cents)" /></Form.Item>
          <Button type="primary" onClick={createResource}>Create Resource</Button>
        </Form>
      </Card>
    </Space>
  );
}
