import { AutoComplete, Space, Typography } from "antd";
import { useState } from "react";
import { api } from "../api/client";

export default function TopSearchBar() {
  const [options, setOptions] = useState<{ value: string; label: string }[]>([]);

  const onSearch = async (q: string) => {
    if (!q) {
      setOptions([]);
      return;
    }
    const { data } = await api.get("/admin/search", { params: { q } });
    const orderOptions = (data.orders || []).map((o: any) => ({
      value: `order:${o.id}`,
      label: `Order ${o.out_trade_no || o.id}`
    }));
    const userOptions = (data.users || []).map((u: any) => ({
      value: `user:${u.id}`,
      label: `User ${u.display_name || u.email || u.id}`
    }));
    setOptions([...orderOptions, ...userOptions]);
  };

  return (
    <Space style={{ width: "100%", justifyContent: "space-between" }}>
      <Typography.Text strong>Operations Console</Typography.Text>
      <AutoComplete
        style={{ width: 360 }}
        options={options}
        onSearch={onSearch}
        placeholder="Search order/user"
      />
    </Space>
  );
}
