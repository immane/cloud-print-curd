import { Card, Col, Row, Table } from "antd";
import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";

export default function ReportsPage() {
  const { data } = useQuery({
    queryKey: ["admin-orders-report"],
    queryFn: async () => (await api.get("/admin/orders", { params: { page_size: 100 } })).data
  });

  const rows = data?.items || [];
  const totalRevenue = rows.reduce((acc: number, r: any) => acc + (r.total_cents || 0), 0);

  const byStatus = Object.entries(
    rows.reduce((acc: any, r: any) => {
      acc[r.status] = (acc[r.status] || 0) + 1;
      return acc;
    }, {})
  ).map(([status, count]) => ({ status, count }));

  return (
    <Row gutter={16}>
      <Col span={12}><Card title="Revenue">¥{(totalRevenue / 100).toFixed(2)}</Card></Col>
      <Col span={12}><Card title="Orders">{rows.length}</Card></Col>
      <Col span={24}>
        <Card title="Orders by Status">
          <Table rowKey="status" dataSource={byStatus} pagination={false} columns={[{ title: "Status", dataIndex: "status" }, { title: "Count", dataIndex: "count" }]} />
        </Card>
      </Col>
    </Row>
  );
}
