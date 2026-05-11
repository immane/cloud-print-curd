import { Button, Input, Modal, Select, Space, Table, Tag } from "antd";
import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";

type OrderItem = {
  id: number;
  out_trade_no: string;
  status: string;
  total_cents: number;
  created_at: string;
};

export default function OrdersPage() {
  const [status, setStatus] = useState<string | undefined>();
  const [search, setSearch] = useState<string | undefined>();
  const [assignOrderId, setAssignOrderId] = useState<number | null>(null);
  const [assignTo, setAssignTo] = useState<number>(0);
  const [note, setNote] = useState<string>("");

  const { data, refetch } = useQuery({
    queryKey: ["admin-orders", status, search],
    queryFn: async () => {
      const { data } = await api.get("/admin/orders", { params: { status, search } });
      return data;
    }
  });

  const rows: OrderItem[] = useMemo(() => data?.items ?? [], [data]);

  const updateStatus = async (id: number, nextStatus: string) => {
    await api.patch(`/admin/orders/${id}`, { status: nextStatus });
    refetch();
  };

  const exportCsv = () => {
    const header = ["id", "out_trade_no", "status", "total_cents", "created_at"];
    const body = rows.map((r) => [r.id, r.out_trade_no, r.status, r.total_cents, r.created_at]);
    const csv = [header, ...body].map((line) => line.join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "orders.csv";
    a.click();
  };

  const submitAssign = async () => {
    if (!assignOrderId) return;
    await api.patch(`/admin/orders/${assignOrderId}`, { assigned_to: assignTo || undefined, note: note || undefined });
    setAssignOrderId(null);
    setAssignTo(0);
    setNote("");
    refetch();
  };

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Select
          allowClear
          placeholder="Filter status"
          onChange={(value) => setStatus(value)}
          style={{ width: 180 }}
          options={[
            { label: "CREATED", value: "CREATED" },
            { label: "PAID", value: "PAID" },
            { label: "PROCESSING", value: "PROCESSING" },
            { label: "COMPLETED", value: "COMPLETED" }
          ]}
        />
        <Input.Search placeholder="Search order/user" onSearch={setSearch} style={{ width: 220 }} />
        <Button onClick={exportCsv}>Export CSV</Button>
      </Space>

      <Table
        rowKey="id"
        dataSource={rows}
        columns={[
          { title: "Order", dataIndex: "out_trade_no" },
          { title: "Amount", render: (_, r) => `¥${(r.total_cents / 100).toFixed(2)}` },
          { title: "Status", dataIndex: "status", render: (s) => <Tag>{s}</Tag> },
          { title: "Created", dataIndex: "created_at" },
          {
            title: "Actions",
            render: (_, r) => (
              <Space>
                <Link to={`/orders/${r.id}`}>View</Link>
                <Button size="small" onClick={() => updateStatus(r.id, "PROCESSING")}>Process</Button>
                <Button size="small" onClick={() => updateStatus(r.id, "COMPLETED")}>Complete</Button>
                <Button size="small" onClick={() => updateStatus(r.id, "CANCELLED")}>Cancel</Button>
                <Button size="small" onClick={() => setAssignOrderId(r.id)}>Assign/Note</Button>
              </Space>
            )
          }
        ]}
      />

      <Modal open={!!assignOrderId} onOk={submitAssign} onCancel={() => setAssignOrderId(null)} title="Assign Operator / Note">
        <Space direction="vertical" style={{ width: "100%" }}>
          <Input type="number" value={assignTo} onChange={(e) => setAssignTo(Number(e.target.value || 0))} placeholder="assigned_to user id" />
          <Input value={note} onChange={(e) => setNote(e.target.value)} placeholder="note" />
        </Space>
      </Modal>
    </div>
  );
}
