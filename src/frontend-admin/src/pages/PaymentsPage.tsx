import { Table, Tag } from "antd";
import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";

export default function PaymentsPage() {
  const { data } = useQuery({
    queryKey: ["admin-orders-as-payments"],
    queryFn: async () => (await api.get("/admin/orders", { params: { page_size: 50 } })).data
  });

  return (
    <Table
      rowKey="id"
      dataSource={data?.items || []}
      columns={[
        { title: "Order", dataIndex: "out_trade_no" },
        { title: "Provider", dataIndex: "payment_provider" },
        { title: "Amount", render: (_, r: any) => `¥${(r.total_cents / 100).toFixed(2)}` },
        { title: "Status", dataIndex: "status", render: (s) => <Tag>{s}</Tag> },
        { title: "Captured At", dataIndex: "updated_at" }
      ]}
    />
  );
}
