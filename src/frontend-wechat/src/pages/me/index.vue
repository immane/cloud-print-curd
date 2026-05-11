<template>
  <view class="page-shell me-page">
    <view class="profile-hero">
      <image class="avatar" :src="profile.avatar_url || placeholderImage" mode="aspectFill" />
      <view class="profile-copy">
        <text class="profile-id">编号：{{ profile.id || '--' }}</text>
        <view class="profile-name-row">
          <text class="profile-name">昵称：{{ profile.display_name || '微信用户' }}</text>
          <text class="profile-arrow">›</text>
        </view>
      </view>
    </view>

    <view class="box balance-card">
      <view>
        <text class="section-kicker">账户积分</text>
        <text class="balance-value">¥{{ ((profile.balance_cents || 0) / 100).toFixed(2) }}</text>
      </view>
      <button class="section-link" @tap="openPrices">去充值</button>
    </view>

    <view class="box orders-card">
      <view class="section-head">
        <text class="section-title">我的订单</text>
        <button class="section-link" @tap="filterOrdersByStatus('ALL')">全部订单</button>
      </view>
      <view class="status-grid">
        <button v-for="status in orderStatusCards" :key="status.key" class="status-button" @tap="filterOrdersByStatus(status.key)">
          <text class="status-icon">{{ statusSymbolMap[status.key] || '单' }}</text>
          <text class="status-label">{{ status.label }}</text>
        </button>
      </view>
    </view>

    <view class="box shortcuts-card">
      <button class="shortcut-item" @tap="openPrices"><text class="shortcut-icon">价</text><text>价格列表</text></button>
      <button class="shortcut-item" @tap="chooseAndUploadFile"><text class="shortcut-icon">传</text><text>上传文件</text></button>
      <button class="shortcut-item" @tap="openCustomerService"><text class="shortcut-icon">服</text><text>联系客服</text></button>
      <button class="shortcut-item" @tap="filterOrdersByStatus('ALL')"><text class="shortcut-icon">单</text><text>订单筛选</text></button>
      <button class="shortcut-item" @tap="scrollToFiles"><text class="shortcut-icon">文</text><text>文件列表</text></button>
      <button class="shortcut-item shortcut-item--danger" @tap="logout"><text class="shortcut-icon">退</text><text>退出登录</text></button>
    </view>

    <view class="box upload-card">
      <view class="section-head">
        <text class="section-title">上传文件</text>
        <text class="muted" v-if="uploadProgress > 0">已完成 {{ uploadProgress }}%</text>
      </view>
      <button class="upload-trigger" @tap="chooseAndUploadFile">选择 PDF 文件</button>
    </view>

    <view id="files-anchor" class="files-panel">
      <view class="section-head section-head--files">
        <text class="section-title">文件列表</text>
        <text class="muted">{{ files.length }} 个文件</text>
      </view>

      <view v-for="file in files" :key="file.id" class="file-row">
        <view class="file-selector"></view>
        <view class="file-body">
          <view class="file-top">
            <text class="file-title">{{ file.filename }}</text>
            <button class="file-delete" @tap="deleteFile(file)">删</button>
          </view>

          <view class="file-tags">
            <text>A4</text>
            <text>{{ colorLabel(file) }}</text>
            <text>单面</text>
            <text>{{ paperLabel(file) }}</text>
            <text>不装订</text>
            <text>{{ printModeLabel(file) }}</text>
            <text>{{ pageRangeLabel(file) }}</text>
          </view>

          <view class="file-stats">
            <view><text class="stat-number">{{ file.page_count || 0 }}</text><text class="stat-unit">页</text></view>
            <view><text class="stat-number">1</text><text class="stat-unit">份</text></view>
          </view>

          <view class="file-actions">
            <button class="ghost-btn" @tap="renameFile(file)">重命名</button>
            <button class="ghost-btn" @tap="previewFile(file)">预览</button>
            <button class="primary-btn" @tap="createOrderForFile(file)">立即下单</button>
          </view>
        </view>
      </view>

      <view v-if="!files.length" class="box empty-files">
        <text class="section-title">还没有上传文件</text>
        <text class="muted empty-desc">先上传一个 PDF 文件，再进行打印设置和下单。</text>
      </view>
    </view>
  </view>
</template>

<script>
import { useMiniStore } from '../../store/miniApp';

const miniStore = useMiniStore();

export default {
  data() {
    return {
      statusSymbolMap: {
        PENDING_PAYMENT: '付',
        PENDING_PRINT: '打',
        TO_RECEIVE: '收',
        COMPLETED: '成',
        AFTER_SALES: '售'
      }
    };
  },
  computed: {
    profile() {
      return miniStore.state.profile;
    },
    files() {
      return miniStore.state.files;
    },
    uploadProgress() {
      return miniStore.state.uploadProgress;
    },
    placeholderImage() {
      return miniStore.placeholderImage;
    },
    orderStatusCards() {
      return miniStore.getOrderStatusCards();
    }
  },
  onShow() {
    miniStore.loadMe();
  },
  methods: {
    openPrices() {
      miniStore.openPrices();
    },
    chooseAndUploadFile() {
      miniStore.chooseAndUploadFile();
    },
    openCustomerService() {
      miniStore.openCustomerService();
    },
    filterOrdersByStatus(status) {
      miniStore.filterOrdersByStatus(status);
    },
    previewFile(file) {
      miniStore.previewFile(file);
    },
    createOrderForFile(file) {
      miniStore.createOrderForFile(file);
    },
    deleteFile(file) {
      miniStore.deleteFile(file);
    },
    renameFile(file) {
      miniStore.renameFile(file);
    },
    logout() {
      miniStore.logout();
    },
    scrollToFiles() {
      uni.pageScrollTo({ selector: '#files-anchor', duration: 220 });
    },
    colorLabel(file) {
      return String(file.print_color || file.color || 'black_white') === 'color' ? '彩色' : '黑白';
    },
    paperLabel(file) {
      return (file.paper_weight || 70) + '克高白';
    },
    printModeLabel(file) {
      return file.binding || '竖版';
    },
    pageRangeLabel(file) {
      return '1-' + (file.page_count || 1) + '页';
    }
  }
};
</script>

<style scoped>
.page-shell {
  min-height: 100vh;
  padding: calc(18px + env(safe-area-inset-top)) 16px 24px;
}

.me-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.profile-hero {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 8px 2px 4px;
}

.avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  border: 1px solid rgba(0, 0, 0, 0.06);
  background: #fff;
}

.profile-copy {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.profile-name-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.profile-id,
.profile-name {
  font-size: 16px;
}

.profile-arrow {
  font-size: 18px;
}

.box,
.file-row {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), #ffffff);
  border-radius: 28px;
  box-shadow: 0 16px 36px rgba(31, 83, 61, 0.12);
}

.box {
  padding: 18px;
}

.balance-card,
.section-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.section-kicker,
.muted {
  color: #8b8b8b;
}

.balance-value {
  display: block;
  margin-top: 20px;
  font-size: 30px;
  font-weight: 700;
}

.section-link {
  margin: 0;
  padding: 0;
  background: transparent;
  color: #4b5563;
  font-size: 16px;
}

.section-title {
  font-size: 18px;
  font-weight: 700;
}

.orders-card,
.upload-card,
.files-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 10px;
}

.status-button,
.shortcut-item {
  margin: 0;
  padding: 0;
  background: transparent;
}

.status-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.status-icon {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, #f4fff8, #d8f8ea);
  box-shadow: inset 0 0 0 2px rgba(17, 201, 140, 0.28);
  font-size: 20px;
  font-weight: 700;
}

.status-label {
  font-size: 12px;
  text-align: center;
}

.shortcuts-card {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px 10px;
}

.shortcut-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  color: #111827;
}

.shortcut-item--danger {
  color: #b91c1c;
}

.shortcut-icon {
  width: 52px;
  height: 52px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f7faf8;
  box-shadow: inset 0 0 0 2px rgba(17, 201, 140, 0.28);
  font-weight: 700;
}

.upload-trigger,
.primary-btn,
.ghost-btn {
  margin: 0;
  border-radius: 999px;
  padding: 14px 18px;
  font-weight: 700;
}

.upload-trigger,
.primary-btn {
  border: 0;
  background: #12c98d;
  color: #111827;
}

.ghost-btn {
  border: 1px solid #d6ddd8;
  background: #ffffff;
  color: #111827;
}

.file-row {
  display: flex;
  gap: 14px;
  padding: 18px;
}

.file-selector {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  border: 2px solid #11c98c;
  margin-top: 8px;
  flex-shrink: 0;
}

.file-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.file-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
}

.file-title {
  font-size: 18px;
  line-height: 1.35;
  font-weight: 700;
}

.file-delete {
  margin: 0;
  padding: 0 4px;
  background: transparent;
  color: #ff3b30;
  font-size: 16px;
  font-weight: 700;
}

.file-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  color: #a1a1aa;
  font-size: 13px;
  line-height: 1.5;
}

.file-stats {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.file-stats view {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 8px;
}

.stat-number {
  font-size: 24px;
  font-weight: 600;
}

.stat-unit {
  font-size: 18px;
  color: #525252;
}

.file-actions {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.empty-desc {
  display: block;
  margin-top: 8px;
}
</style>
