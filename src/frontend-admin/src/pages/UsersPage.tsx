import { Button, Input, Modal, Space, Table } from "antd";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "../api/client";

export default function UsersPage() {
  const [search, setSearch] = useState("");
  const [adjust, setAdjust] = useState<{ userId: number; amount: number } | null>(null);

  const { data, refetch } = useQuery({
    queryKey: ["admin-users", search],
    queryFn: async () => (await api.get("/admin/users", { params: { search } })).data
  });

  const submitAdjust = async () => {
    if (!adjust) return;
    await api.post(`/admin/users/${adjust.userId}/adjust-balance`, {
      amount_cents: adjust.amount,
      reason: "manual adjustment"
    });
    setAdjust(null);
    refetch();
  };

  return (
    <>
      <Space style={{ marginBottom: 12 }}>
        <Input.Search placeholder="Search users" onSearch={setSearch} />
      </Space>
      <Table
        rowKey="id"
        dataSource={data?.items || []}
        columns={[
          { title: "ID", dataIndex: "id" },
          { title: "Name", dataIndex: "display_name" },
          { title: "Email", dataIndex: "email" },
          { title: "Role", dataIndex: "role" },
          { title: "Balance", render: (_, r: any) => `¥${((r.balance_cents || 0) / 100).toFixed(2)}` },
          { title: "Action", render: (_, r: any) => <Button onClick={() => setAdjust({ userId: r.id, amount: 0 })}>Adjust</Button> }
        ]}
      />

      <Modal open={!!adjust} onOk={submitAdjust} onCancel={() => setAdjust(null)} title="Adjust Balance">
        <Input
          type="number"
          placeholder="Amount in cents"
          value={adjust?.amount || 0}
          onChange={(e) => setAdjust((prev) => (prev ? { ...prev, amount: Number(e.target.value || 0) } : prev))}
        />
      </Modal>
    </>
  );
}
