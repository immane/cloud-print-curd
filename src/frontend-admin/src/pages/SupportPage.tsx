import { Card, Col, Input, List, Row, Tag } from "antd";
import { useState } from "react";

const MOCK = [
  { id: 1, user: "Alice", order: "CP123", unread: 2, last: "When can it be shipped?" },
  { id: 2, user: "Bob", order: "CP124", unread: 0, last: "Thanks" }
];

export default function SupportPage() {
  const [selected, setSelected] = useState<any>(MOCK[0]);
  return (
    <Row gutter={16}>
      <Col span={8}>
        <Card title="Conversations">
          <Input.Search placeholder="Search by user/order" style={{ marginBottom: 12 }} />
          <List
            dataSource={MOCK}
            renderItem={(item) => (
              <List.Item onClick={() => setSelected(item)} style={{ cursor: "pointer" }}>
                <List.Item.Meta title={`${item.user} (${item.order})`} description={item.last} />
                {item.unread > 0 ? <Tag color="red">{item.unread}</Tag> : null}
              </List.Item>
            )}
          />
        </Card>
      </Col>
      <Col span={16}>
        <Card title={`Conversation #${selected.id}`}>
          <p>User: {selected.user}</p>
          <p>Order: {selected.order}</p>
          <p>Last message: {selected.last}</p>
          <Input.TextArea rows={6} placeholder="Reply..." />
        </Card>
      </Col>
    </Row>
  );
}
