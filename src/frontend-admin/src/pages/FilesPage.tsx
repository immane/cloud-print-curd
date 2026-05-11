import { Button, Space, Table, Tag, message } from "antd";
import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";

export default function FilesPage() {
  const { data, refetch } = useQuery({
    queryKey: ["admin-files"],
    queryFn: async () => (await api.get("/admin/files")).data
  });

  const reprocess = async (id: number) => {
    await api.post(`/admin/files/${id}/reprocess`);
    message.success("Reprocess queued");
    refetch();
  };

  return (
    <Table
      rowKey="id"
      dataSource={data?.items || []}
      columns={[
        { title: "ID", dataIndex: "id" },
        { title: "Owner", dataIndex: "user_id" },
        { title: "Filename", dataIndex: "filename" },
        { title: "Pages", dataIndex: "page_count" },
        { title: "Size", dataIndex: "size_bytes" },
        { title: "Status", dataIndex: "status", render: (s) => <Tag>{s}</Tag> },
        {
          title: "Actions",
          render: (_, r: any) => (
            <Space>
              <Button onClick={() => reprocess(r.id)}>Reprocess</Button>
              <Button onClick={() => window.open(`${import.meta.env.VITE_API_BASE || "http://localhost:8000"}/admin/files/${r.id}/download`)}>Download</Button>
            </Space>
          )
        }
      ]}
    />
  );
}
