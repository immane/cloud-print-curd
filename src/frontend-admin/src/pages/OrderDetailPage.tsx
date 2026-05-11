import { Button, Card, Descriptions, Space, Table, Tag } from "antd";
import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { api } from "../api/client";

export default function OrderDetailPage() {
  const params = useParams();
  const orderId = params.id;

  const { data, refetch } = useQuery({
    queryKey: ["order", orderId],
    queryFn: async () => {
      const { data } = await api.get(`/admin/orders/${orderId}`);
      return data;
    }
  });

  const updateStatus = async (status: string) => {
    await api.patch(`/admin/orders/${orderId}`, { status });
    refetch();
  };

  const refund = async () => {
    await api.post(`/admin/orders/${orderId}/refund`, { amount_cents: data.total_cents, reason: "manual refund" });
    refetch();
  };

  if (!data) return null;

  return (
    <Space direction="vertical" style={{ width: "100%" }}>
      <Card title="Order Summary">
        <Descriptions column={2}>
          <Descriptions.Item label="Order No">{data.out_trade_no}</Descriptions.Item>
          <Descriptions.Item label="Status"><Tag>{data.status}</Tag></Descriptions.Item>
          <Descriptions.Item label="Amount">¥{(data.total_cents / 100).toFixed(2)}</Descriptions.Item>
          <Descriptions.Item label="User">{data.user?.display_name || data.user_id}</Descriptions.Item>
        </Descriptions>
        <Space>
          <Button onClick={() => updateStatus("PROCESSING")}>Mark Processing</Button>
          <Button onClick={() => updateStatus("COMPLETED")}>Mark Completed</Button>
          <Button danger onClick={refund}>Refund</Button>
        </Space>
      </Card>

      <Card title="Items">
        <Table
          rowKey="id"
          dataSource={data.items || []}
          pagination={false}
          columns={[
            { title: "Description", dataIndex: "description" },
            { title: "Quantity", dataIndex: "quantity" },
            { title: "Unit Price", render: (_: any, r: any) => `¥${(r.unit_price_cents / 100).toFixed(2)}` }
          ]}
        />
      </Card>

      <Card title="Payment Records">
        <Table
          rowKey="id"
          dataSource={data.payments || []}
          pagination={false}
          columns={[
            { title: "Provider", dataIndex: "provider" },
            { title: "Status", dataIndex: "provider_status" },
            { title: "Amount", render: (_: any, r: any) => `¥${((r.amount_cents || 0) / 100).toFixed(2)}` },
            { title: "At", dataIndex: "created_at" }
          ]}
        />
      </Card>

      <Card title="Audit Timeline">
        <Table
          rowKey="id"
          dataSource={data.audit_logs || []}
          pagination={false}
          columns={[
            { title: "Action", dataIndex: "action" },
            { title: "Admin", dataIndex: "admin_user_id" },
            { title: "At", dataIndex: "created_at" }
          ]}
        />
      </Card>
    </Space>
  );
}
