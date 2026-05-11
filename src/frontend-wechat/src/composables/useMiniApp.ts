import { computed, onMounted, reactive, ref } from "vue";
import api from "../api";

export function useMiniApp() {
  const placeholderImage = "https://picsum.photos/400/240";

  const tab = ref<"home" | "library" | "me">("home");
  const slider = ref<any[]>([]);
  const tutorial = ref<any>(null);
  const categories = ref<any[]>([]);
  const resources = ref<any[]>([]);
  const selectedCategoryId = ref<number | undefined>(undefined);
  const profile = reactive<any>({});
  const files = ref<any[]>([]);
  const orders = ref<any[]>([]);
  const addresses = ref<any[]>([]);
  const newAddress = reactive({ title: "", recipient_name: "", phone: "", address_line1: "" });
  const uploadProgress = ref(0);

  const priceTip = ref("");
  const prices = ref<any[]>([]);
  const priceFilter = reactive({ paper_type: "", size: "" });

  const showTutorial = ref(false);
  const showResourcePreview = ref(false);
  const showPricePanel = ref(false);
  const showCheckout = ref(false);
  const showAddressPanel = ref(false);
  const showFaqPanel = ref(false);
  const messageBox = reactive({ show: false, text: "", type: "info" as "info" | "success" | "error" });

  const previewingResource = ref<any>(null);
  const checkoutFile = ref<any>(null);
  const checkout = reactive({ size: "A4", color: "black_white", duplex: false, copies: 1 });

  const groupedPrices = computed(() => {
    const filtered = prices.value.filter(
      (p) =>
        (!priceFilter.paper_type || String(p.paper_type).includes(priceFilter.paper_type)) &&
        (!priceFilter.size || String(p.size).includes(priceFilter.size))
    );
    return filtered.reduce((acc: any, p: any) => {
      const key = `${p.size} / ${p.paper_type}`;
      acc[key] = acc[key] || [];
      acc[key].push(p);
      return acc;
    }, {});
  });

  const orderStatusCards = computed(() => {
    const by = (s: string[]) => orders.value.filter((o) => s.includes(o.status)).length;
    return [
      { key: "PENDING_PAYMENT", label: "Pending Payment", count: by(["CREATED", "PENDING_PAYMENT"]) },
      { key: "PENDING_PRINT", label: "Pending Print", count: by(["PAID", "PROCESSING"]) },
      { key: "TO_RECEIVE", label: "To Receive", count: by(["PRINTED", "SHIPPED"]) },
      { key: "COMPLETED", label: "Completed", count: by(["COMPLETED"]) },
      { key: "AFTER_SALES", label: "After-sales", count: by(["REFUNDED", "CANCELLED"]) }
    ];
  });

  const checkoutPreview = computed(() => {
    const base = checkout.size === "A3" ? 30 : 20;
    const colorFee = checkout.color === "color" ? 30 : 0;
    const duplexFee = checkout.duplex ? 10 : 0;
    return ((base + colorFee + duplexFee) * checkout.copies / 100).toFixed(2);
  });

  const notify = (text: string, type: "info" | "success" | "error" = "info") => {
    messageBox.text = text;
    messageBox.type = type;
    messageBox.show = true;
    setTimeout(() => {
      messageBox.show = false;
    }, 2200);
  };

  const fetchHome = async () => {
    const [s, t, p, tip] = await Promise.all([
      api.get("/v1/home/slider"),
      api.get("/v1/home/tutorial"),
      api.get("/v1/prices"),
      api.get("/v1/prices/tip")
    ]);
    slider.value = s.data || [];
    tutorial.value = t.data;
    prices.value = p.data || [];
    priceTip.value = tip.data?.text || "";
  };

  const fetchResources = async (categoryId?: number) => {
    const { data } = await api.get("/v1/library/resources", { params: { category_id: categoryId } });
    resources.value = data.items || data || [];
  };

  const fetchLibrary = async () => {
    const { data } = await api.get("/v1/library/categories");
    categories.value = data || [];
    if (categories.value.length) {
      selectedCategoryId.value = categories.value[0].id;
      await fetchResources(categories.value[0].id);
    }
  };

  const fetchMe = async () => {
    try {
      const [me, fs, os, as] = await Promise.all([
        api.get("/v1/users/me"),
        api.get("/v1/files"),
        api.get("/v1/orders"),
        api.get("/v1/addresses")
      ]);
      Object.assign(profile, me.data || {});
      files.value = fs.data.items || [];
      orders.value = os.data.items || [];
      addresses.value = as.data || [];
    } catch {
      Object.assign(profile, { display_name: "Guest", balance_cents: 0 });
      files.value = [];
      orders.value = [];
    }
  };

  const onSlideClick = (item: any) => {
    if (item.link_payload === "price") showPricePanel.value = true;
  };
  const openTutorial = () => {
    showTutorial.value = true;
  };
  const selectCategory = async (id: number) => {
    selectedCategoryId.value = id;
    await fetchResources(id);
  };
  const previewResource = (resource: any) => {
    previewingResource.value = resource;
    showResourcePreview.value = true;
  };
  const closeResourcePreview = () => {
    showResourcePreview.value = false;
    previewingResource.value = null;
  };

  const createFromResource = async (resource: any) => {
    await api.post("/v1/orders/create-from-resource", {
      resource_id: resource.id,
      options: { size: "A4", color: "black_white", duplex: false, copies: 1 }
    });
    notify("Resource order created", "success");
    closeResourcePreview();
    await fetchMe();
  };

  const onFileChange = async (event: Event) => {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;
    if (file.size > 50 * 1024 * 1024) {
      notify("File too large (> 50MB)", "error");
      return;
    }
    const create = await api.post("/v1/files/create-upload", {
      filename: file.name,
      size: file.size,
      content_type: file.type || "application/octet-stream"
    });
    const formData = new FormData();
    Object.keys(create.data.fields).forEach((key) => formData.append(key, create.data.fields[key]));
    formData.append("file", file);
    await fetch(create.data.upload_url, { method: "POST", body: formData });
    uploadProgress.value = 100;
    await api.post("/v1/files/complete", { upload_id: create.data.upload_id });
    await fetchMe();
  };

  const previewFile = async (file: any) => {
    const { data } = await api.get(`/v1/files/${file.id}/download`);
    window.open(data.url, "_blank");
  };

  const openCheckout = (file: any) => {
    checkoutFile.value = file;
    showCheckout.value = true;
  };

  const createOrderAndPay = async () => {
    if (!checkoutFile.value) return;
    const { data } = await api.post("/v1/orders/create", {
      items: [{ file_id: checkoutFile.value.id, options: { ...checkout } }]
    });
    const ok = window.confirm(`Proceed payment for order ${data.order_id}?`);
    if (ok) {
      notify("Payment success", "success");
      showCheckout.value = false;
      await fetchMe();
    } else {
      notify("Payment cancelled");
    }
  };

  const deleteFile = async (file: any) => {
    if (!window.confirm("Delete this file?")) return;
    await api.delete(`/v1/files/${file.id}`);
    await fetchMe();
  };

  const renameFile = async (file: any) => {
    const name = window.prompt("Rename file", file.filename);
    if (!name || name === file.filename) return;
    await api.patch(`/v1/files/${file.id}`, { filename: name });
    await fetchMe();
    notify("File renamed", "success");
  };

  const filterOrdersByStatus = (status: string) => {
    const filtered = orders.value.filter((o) => {
      if (status === "PENDING_PAYMENT") return ["CREATED", "PENDING_PAYMENT"].includes(o.status);
      if (status === "PENDING_PRINT") return ["PAID", "PROCESSING"].includes(o.status);
      if (status === "TO_RECEIVE") return ["PRINTED", "SHIPPED"].includes(o.status);
      if (status === "COMPLETED") return ["COMPLETED"].includes(o.status);
      if (status === "AFTER_SALES") return ["REFUNDED", "CANCELLED"].includes(o.status);
      return true;
    });
    notify(`Found ${filtered.length} orders in ${status}`);
  };

  const createAddress = async () => {
    await api.post("/v1/addresses", newAddress);
    Object.assign(newAddress, { title: "", recipient_name: "", phone: "", address_line1: "" });
    await fetchMe();
  };

  const deleteAddress = async (id: number) => {
    await api.delete(`/v1/addresses/${id}`);
    await fetchMe();
  };

  const openCustomerService = async () => {
    const { data } = await api.get("/v1/support/session-info", { params: { order_id: orders.value[0]?.id } });
    notify(`Customer service: ${data.sendMessageTitle}`);
  };

  const logout = async () => {
    try {
      await api.post("/v1/auth/logout", {});
    } catch {
      // no-op
    }
    localStorage.removeItem("token");
    Object.assign(profile, { display_name: "Guest", balance_cents: 0 });
    files.value = [];
    orders.value = [];
    notify("Logged out", "success");
  };

  onMounted(async () => {
    await Promise.all([fetchHome(), fetchLibrary(), fetchMe()]);
  });

  return {
    placeholderImage,
    tab,
    slider,
    tutorial,
    categories,
    resources,
    selectedCategoryId,
    profile,
    files,
    orders,
    addresses,
    newAddress,
    uploadProgress,
    priceTip,
    prices,
    priceFilter,
    showTutorial,
    showResourcePreview,
    showPricePanel,
    showCheckout,
    showAddressPanel,
    showFaqPanel,
    messageBox,
    previewingResource,
    checkoutFile,
    checkout,
    groupedPrices,
    orderStatusCards,
    checkoutPreview,
    onSlideClick,
    openTutorial,
    selectCategory,
    previewResource,
    closeResourcePreview,
    createFromResource,
    onFileChange,
    previewFile,
    openCheckout,
    createOrderAndPay,
    deleteFile,
    renameFile,
    filterOrdersByStatus,
    createAddress,
    deleteAddress,
    openCustomerService,
    logout
  };
}
