import { Table } from "antd";
import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";

export default function AuditLogsPage() {
  const { data } = useQuery({
    queryKey: ["admin-audit"],
    queryFn: async () => (await api.get("/admin/audit-logs", { params: { page_size: 100 } })).data
  });

  return (
    <Table
      rowKey="id"
      dataSource={data?.items || []}
      columns={[
        { title: "ID", dataIndex: "id" },
        { title: "Admin", dataIndex: "admin_user_id" },
        { title: "Action", dataIndex: "action" },
        { title: "Target", render: (_, r: any) => `${r.target_type}:${r.target_id}` },
        { title: "At", dataIndex: "created_at" }
      ]}
    />
  );
}
