import { Card, Col, Row, Statistic, Table } from "antd";
import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";

export default function DashboardPage() {
  const { data } = useQuery({
    queryKey: ["admin-metrics"],
    queryFn: async () => (await api.get("/admin/metrics")).data
  });

  const { data: orders } = useQuery({
    queryKey: ["admin-orders-latest"],
    queryFn: async () => (await api.get("/admin/orders", { params: { page_size: 20 } })).data
  });

  return (
    <Row gutter={[16, 16]}>
      <Col span={6}><Card><Statistic title="Orders Today" value={data?.orders_today || 0} /></Card></Col>
      <Col span={6}><Card><Statistic title="Revenue Today" value={(data?.revenue_today_cents || 0) / 100} prefix="¥" precision={2} /></Card></Col>
      <Col span={6}><Card><Statistic title="New Users" value={data?.new_users_today || 0} /></Card></Col>
      <Col span={6}><Card><Statistic title="Pending Webhooks" value={data?.pending_webhooks || 0} /></Card></Col>
      <Col span={24}>
        <Card title="Incoming Queue">
          <Table
            rowKey="id"
            dataSource={orders?.items || []}
            pagination={false}
            columns={[
              { title: "Order", dataIndex: "out_trade_no" },
              { title: "Status", dataIndex: "status" },
              { title: "Total", render: (_, r: any) => `¥${(r.total_cents / 100).toFixed(2)}` },
              { title: "Created", dataIndex: "created_at" }
            ]}
          />
        </Card>
      </Col>
    </Row>
  );
}
