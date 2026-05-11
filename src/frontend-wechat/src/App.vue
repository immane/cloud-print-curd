<template>
  <div class="app-shell">
    <header class="app-header">
      <div class="brand-wrap">
        <div class="brand-mark">CP</div>
        <div class="brand-text">
          <div class="brand">Cloud Print</div>
          <div class="brand-sub">Fast, clean, reliable prints</div>
        </div>
      </div>
      <div class="icons" aria-label="header actions">🔍 🔔</div>
    </header>

    <main class="app-main">
      <HomePage
        v-if="tab === 'home'"
        :slider="slider"
        :tutorial="tutorial"
        @slide-click="onSlideClick"
        @open-tutorial="openTutorial"
        @open-prices="showPricePanel = true"
      />

      <LibraryPage
        v-if="tab === 'library'"
        :categories="categories"
        :resources="resources"
        :selected-category-id="selectedCategoryId"
        :placeholder-image="placeholderImage"
        @select-category="selectCategory"
        @preview-resource="previewResource"
        @create-from-resource="createFromResource"
      />

      <MePage
        v-if="tab === 'me'"
        :profile="profile"
        :files="files"
        :order-status-cards="orderStatusCards"
        :upload-progress="uploadProgress"
        :placeholder-image="placeholderImage"
        @filter-orders="filterOrdersByStatus"
        @file-change="onFileChange"
        @preview-file="previewFile"
        @open-checkout="openCheckout"
        @rename-file="renameFile"
        @delete-file="deleteFile"
        @open-prices="showPricePanel = true"
        @open-address="showAddressPanel = true"
        @open-faq="showFaqPanel = true"
        @logout="logout"
      />
    </main>

    <button class="customer-service" @click="openCustomerService" aria-label="Customer service">💬</button>
    <ToastMessage :show="messageBox.show" :text="messageBox.text" :type="messageBox.type" />
    <BottomTabBar :tab="tab" @change="tab = $event" />

    <TutorialModal
      :open="showTutorial"
      :image-url="tutorial?.image_url || placeholderImage"
      @close="showTutorial = false"
    />

    <ResourcePreviewModal
      :open="showResourcePreview"
      :resource="previewingResource"
      :fallback="placeholderImage"
      @close="closeResourcePreview"
      @order="createFromResource"
    />

    <PriceModal
      :open="showPricePanel"
      :tip="priceTip"
      :grouped-prices="groupedPrices"
      :paper-type="priceFilter.paper_type"
      :size="priceFilter.size"
      @close="showPricePanel = false"
      @update:paper-type="priceFilter.paper_type = $event"
      @update:size="priceFilter.size = $event"
      @order-now="tab = 'me'; showPricePanel = false"
    />

    <CheckoutModal
      :open="showCheckout"
      :file="checkoutFile"
      :checkout="checkout"
      :preview="checkoutPreview"
      @close="showCheckout = false"
      @update:size="checkout.size = $event"
      @update:color="checkout.color = $event"
      @update:duplex="checkout.duplex = $event"
      @update:copies="checkout.copies = $event"
      @pay="createOrderAndPay"
    />

    <AddressModal
      :open="showAddressPanel"
      :addresses="addresses"
      :form="newAddress"
      @close="showAddressPanel = false"
      @add="createAddress"
      @delete="deleteAddress"
      @update:field="updateAddressField"
    />

    <FaqModal :open="showFaqPanel" @close="showFaqPanel = false" />
  </div>
</template>

<script setup lang="ts">
import HomePage from "./pages/home/index.vue";
import LibraryPage from "./pages/library/index.vue";
import MePage from "./pages/me/index.vue";
import BottomTabBar from "./components/BottomTabBar.vue";
import ToastMessage from "./components/ToastMessage.vue";
import TutorialModal from "./components/modals/TutorialModal.vue";
import ResourcePreviewModal from "./components/modals/ResourcePreviewModal.vue";
import PriceModal from "./components/modals/PriceModal.vue";
import CheckoutModal from "./components/modals/CheckoutModal.vue";
import AddressModal from "./components/modals/AddressModal.vue";
import FaqModal from "./components/modals/FaqModal.vue";
import { useMiniApp } from "./composables/useMiniApp";

const {
  placeholderImage,
  tab,
  slider,
  tutorial,
  categories,
  resources,
  selectedCategoryId,
  profile,
  files,
  addresses,
  newAddress,
  uploadProgress,
  priceTip,
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
} = useMiniApp();

const updateAddressField = (field: "title" | "recipient_name" | "phone" | "address_line1", value: string) => {
  newAddress[field] = value;
};
</script>

<style>
:root {
  --bg: #f4f6fa;
  --panel: #ffffff;
  --panel-soft: #f9fbff;
  --primary: #0f766e;
  --primary-2: #0284c7;
  --accent: #ea580c;
  --text: #152033;
  --muted: #5e6a7d;
  --line: #dce4ef;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
  background:
    radial-gradient(circle at 12% -10%, #d7e8ff 0%, transparent 40%),
    radial-gradient(circle at 86% -20%, #c7f8f3 0%, transparent 36%),
    linear-gradient(180deg, #f8fbff, var(--bg));
  color: var(--text);
}
.app-shell {
  min-height: 100vh;
  max-width: 460px;
  margin: 0 auto;
  display: grid;
  grid-template-rows: auto 1fr auto;
  position: relative;
  animation: app-fade-in 280ms ease-out;
}
.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  background: linear-gradient(135deg, #0f766e, #0284c7 72%);
  color: #fff;
  box-shadow: 0 8px 24px rgba(2, 41, 66, 0.16);
}
.brand-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
}
.brand-mark {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.24);
  font-weight: 800;
  font-size: 13px;
}
.brand-text {
  display: grid;
  gap: 2px;
}
.brand {
  font-weight: 800;
  letter-spacing: 0.5px;
}
.brand-sub {
  font-size: 11px;
  opacity: 0.88;
}
.icons {
  font-size: 18px;
  letter-spacing: 2px;
}
.app-main {
  padding: 14px;
}
.panel {
  display: grid;
  gap: 12px;
}
.box {
  background: linear-gradient(180deg, var(--panel) 10%, var(--panel-soft));
  border-radius: 14px;
  padding: 12px;
  box-shadow: 0 10px 26px rgba(11, 30, 65, 0.08);
  border: 1px solid rgba(220, 228, 239, 0.8);
}
.customer-service {
  position: fixed;
  right: 18px;
  bottom: 76px;
  width: 54px;
  height: 54px;
  border-radius: 50%;
  border: 0;
  background: linear-gradient(135deg, #ea580c, #dc2626);
  color: #fff;
  font-size: 22px;
  box-shadow: 0 12px 24px rgba(139, 45, 4, 0.28);
  cursor: pointer;
}
.toast { position: fixed; left: 50%; transform: translateX(-50%); top: 78px; z-index: 30; padding: 8px 12px; border-radius: 999px; color: #fff; font-size: 13px; }
.toast.info { background: #34495e; }
.toast.success { background: #27ae60; }
.toast.error { background: #e74c3c; }
.modal { position: fixed; inset: 0; background: rgba(0, 0, 0, 0.45); display: grid; place-items: center; z-index: 20; }
.modal-card { width: min(92vw, 420px); max-height: 85vh; overflow: auto; background: #fff; border-radius: 14px; padding: 14px; }
.modal-card.full { width: min(96vw, 420px); padding: 6px; }
.full-img { width: 100%; border-radius: 10px; }
.filters { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 10px; }
.primary {
  background: linear-gradient(135deg, var(--primary), var(--primary-2));
  color: #fff;
  border: 0;
  border-radius: 10px;
  padding: 10px 12px;
}
.sticky-footer { position: sticky; bottom: 0; background: #fff; border-top: 1px solid #edf2f8; padding-top: 10px; display: flex; justify-content: space-between; align-items: center; }
.tabbar {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  padding: 10px 12px calc(12px + env(safe-area-inset-bottom));
  background: rgba(255, 255, 255, 0.96);
  border-top: 1px solid var(--line);
  backdrop-filter: blur(10px);
}
.tabbar button {
  border: 1px solid var(--line);
  background: #fff;
  color: var(--muted);
  border-radius: 10px;
  padding: 8px 6px;
  font-weight: 600;
}
.tabbar button.active {
  color: #fff;
  border-color: transparent;
  background: linear-gradient(135deg, var(--primary), var(--primary-2));
  box-shadow: 0 8px 18px rgba(2, 132, 199, 0.2);
}

@keyframes app-fade-in {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 380px) {
  .brand-sub { display: none; }
}
</style>
