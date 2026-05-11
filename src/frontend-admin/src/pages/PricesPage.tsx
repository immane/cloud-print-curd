import { Button, Card, Form, Input, InputNumber, Select, Space, Table } from "antd";
import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";

export default function PricesPage() {
  const [form] = Form.useForm();
  const { data, refetch } = useQuery({
    queryKey: ["admin-price-versions"],
    queryFn: async () => (await api.get("/admin/prices/versions")).data
  });

  const createVersion = async () => {
    const name = form.getFieldValue("name") || "new version";
    const rules = {
      A4: { black_white: { single: 20, duplex: 30 }, color: { single: 50, duplex: 80 } },
      A3: { black_white: { single: 30, duplex: 45 }, color: { single: 75, duplex: 120 } },
      default: 30
    };
    await api.post("/admin/prices/versions", { name, rules_json: rules });
    refetch();
  };

  const publish = async (id: number) => {
    await api.post(`/admin/prices/versions/${id}/publish`);
    refetch();
  };

  const preview = async () => {
    const values = await form.validateFields(["pages", "copies", "size", "color"]);
    const payload = {
      items: [{ file_id: 1, options: { pages: values.pages, copies: values.copies, size: values.size, color: values.color, duplex: false } }]
    };
    const { data } = await api.post("/admin/prices/export-sample", payload);
    form.setFieldValue("preview", `Total: ${(data.calculation.total_cents / 100).toFixed(2)} CNY`);
  };

  return (
    <Space direction="vertical" style={{ width: "100%" }}>
      <Card title="Price Versions">
        <Space style={{ marginBottom: 12 }}>
          <Form form={form} layout="inline">
            <Form.Item name="name"><Input placeholder="Version Name" /></Form.Item>
            <Button type="primary" onClick={createVersion}>Create Version</Button>
          </Form>
        </Space>
        <Table
          rowKey="id"
          dataSource={data || []}
          columns={[
            { title: "ID", dataIndex: "id" },
            { title: "Version", dataIndex: "version" },
            { title: "Name", dataIndex: "name" },
            { title: "Published", dataIndex: "published", render: (v) => (v ? "Yes" : "No") },
            { title: "Action", render: (_, r: any) => <Button onClick={() => publish(r.id)}>Publish</Button> }
          ]}
        />
      </Card>

      <Card title="Price Preview">
        <Form form={form} layout="inline">
          <Form.Item name="pages" initialValue={10}><InputNumber min={1} placeholder="Pages" /></Form.Item>
          <Form.Item name="copies" initialValue={1}><InputNumber min={1} placeholder="Copies" /></Form.Item>
          <Form.Item name="size" initialValue="A4"><Select style={{ width: 100 }} options={[{ label: "A4", value: "A4" }, { label: "A3", value: "A3" }]} /></Form.Item>
          <Form.Item name="color" initialValue="black_white"><Select style={{ width: 150 }} options={[{ label: "B/W", value: "black_white" }, { label: "Color", value: "color" }]} /></Form.Item>
          <Button onClick={preview}>Preview</Button>
          <Form.Item name="preview"><Input style={{ width: 220 }} readOnly /></Form.Item>
        </Form>
      </Card>
    </Space>
  );
}
