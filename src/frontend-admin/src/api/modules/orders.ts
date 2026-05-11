import { api } from "../client";

export const OrdersApi = {
  list: async (params?: Record<string, unknown>) => (await api.get("/admin/orders", { params })).data,
  detail: async (id: string | number) => (await api.get(`/admin/orders/${id}`)).data,
  patch: async (id: string | number, body: Record<string, unknown>) => (await api.patch(`/admin/orders/${id}`, body)).data,
  refund: async (id: string | number, body: Record<string, unknown>) => (await api.post(`/admin/orders/${id}/refund`, body)).data
};
