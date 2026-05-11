<template>
  <view class="page-shell home-page">
    <view class="hero-banner" v-if="slider.length">
      <swiper class="hero-swiper" circular autoplay indicator-dots>
        <swiper-item v-for="item in slider" :key="item.id">
          <image class="hero-image" :src="item.image_url" mode="aspectFill" />
        </swiper-item>
      </swiper>
    </view>

    <view class="hero-banner hero-banner--placeholder" v-else>
      <view class="placeholder-copy">
        <text>考试试卷 / 资料文档 / 讲义复印</text>
        <text class="placeholder-strong">80g / 100g 高白纸 健康护眼</text>
      </view>
    </view>

    <view class="entry-card">
      <button class="entry-item plain-button" @tap="openTutorial">
        <text class="entry-icon">教</text>
        <text class="entry-label">打印教程</text>
      </button>
      <view class="entry-divider"></view>
      <button class="entry-item plain-button" @tap="openPrices">
        <text class="entry-icon">价</text>
        <text class="entry-label">价格列表</text>
      </button>
    </view>

    <view class="box upload-card">
      <view class="upload-head">
        <view class="upload-badge"><text>文</text></view>
        <view>
          <text class="section-title">资料文档打印</text>
          <text class="section-desc">支持从本地、微信、百度网盘上传文件</text>
        </view>
      </view>

      <button class="start-print" @tap="goToMeTab">开始打印</button>
      <text class="upload-foot">当前仅支持 PDF 文件打印</text>
    </view>

    <view class="box tutorial-meta" v-if="tutorial && tutorial.title">
      <view class="tutorial-head">
        <text class="section-title">{{ tutorial.title }}</text>
        <button class="pill-button" @tap="openTutorial">查看详情</button>
      </view>
      <text class="section-desc">最近更新：{{ tutorial.updated_at || '-' }}</text>
    </view>

    <button class="customer-service" @tap="openCustomerService">客服</button>
  </view>
</template>

<script>
import { useMiniStore } from '../../store/miniApp';

const miniStore = useMiniStore();

export default {
  computed: {
    slider() {
      return miniStore.state.slider;
    },
    tutorial() {
      return miniStore.state.tutorial;
    }
  },
  onShow() {
    miniStore.loadHome();
  },
  methods: {
    openTutorial() {
      miniStore.openTutorial();
    },
    openPrices() {
      miniStore.openPrices();
    },
    goToMeTab() {
      miniStore.goToMeTab();
    },
    openCustomerService() {
      miniStore.openCustomerService();
    }
  }
};
</script>

<style scoped>
.page-shell {
  min-height: 100vh;
  padding: calc(18px + env(safe-area-inset-top)) 16px 24px;
}

.home-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.hero-banner {
  overflow: hidden;
  border-radius: 0 0 30px 30px;
  min-height: 240px;
  margin: -18px -16px 0;
  background: linear-gradient(140deg, #b78353 0%, #c49a6a 36%, #d9c09d 100%);
  box-shadow: 0 24px 40px rgba(39, 82, 62, 0.16);
}

.hero-swiper,
.hero-image {
  width: 100%;
  height: 240px;
}

.hero-banner--placeholder {
  padding: 18px;
}

.placeholder-copy {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 240px;
  color: #fff6e8;
}

.placeholder-strong {
  font-size: 28px;
  line-height: 1.25;
  color: #ff9b2c;
  font-weight: 700;
}

.entry-card,
.box {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), #ffffff);
  border-radius: 28px;
  box-shadow: 0 16px 36px rgba(31, 83, 61, 0.12);
}

.entry-card {
  display: flex;
  align-items: center;
  padding: 22px 18px;
}

.plain-button {
  margin: 0;
  padding: 0;
  line-height: 1;
  background: transparent;
}

.entry-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.entry-icon {
  width: 64px;
  height: 64px;
  border-radius: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, #f6fff8, #def7ec);
  border: 2px solid rgba(11, 201, 140, 0.32);
  font-size: 24px;
  font-weight: 700;
}

.entry-label {
  font-size: 16px;
  font-weight: 600;
}

.entry-divider {
  width: 1px;
  height: 86px;
  background: rgba(148, 163, 184, 0.28);
}

.box {
  padding: 22px;
}

.upload-head {
  display: flex;
  gap: 16px;
}

.upload-badge {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, #ffd789, #ffb54d);
  font-size: 24px;
  font-weight: 700;
}

.section-title {
  display: block;
  font-size: 18px;
  font-weight: 700;
}

.section-desc {
  display: block;
  margin-top: 10px;
  color: #8b8b8b;
  line-height: 1.5;
}

.start-print {
  margin-top: 28px;
  border: 0;
  border-radius: 999px;
  background: #11c98c;
  color: #111827;
  font-size: 26px;
  font-weight: 500;
  padding: 18px 20px;
  box-shadow: 0 16px 26px rgba(17, 201, 140, 0.28);
}

.upload-foot {
  display: block;
  margin-top: 18px;
  text-align: center;
  color: #a1a1aa;
}

.tutorial-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.pill-button {
  margin: 0;
  border-radius: 999px;
  border: 1px solid rgba(17, 201, 140, 0.24);
  background: rgba(17, 201, 140, 0.1);
  color: #059669;
  font-size: 14px;
  padding: 8px 14px;
}

.customer-service {
  position: fixed;
  right: 18px;
  bottom: calc(96px + env(safe-area-inset-bottom));
  width: 64px;
  height: 64px;
  border-radius: 50%;
  border: 6px solid rgba(255, 255, 255, 0.9);
  background: linear-gradient(135deg, #18c98e, #0fbf82);
  color: #ffffff;
  font-size: 18px;
  font-weight: 700;
  box-shadow: 0 18px 28px rgba(17, 201, 140, 0.26);
}
</style>
