<template>
  <view class="page-shell library-page">
    <scroll-view class="tag-row" scroll-x>
      <view class="tag-track">
        <button
          v-for="category in categories"
          :key="category.id"
          :class="['tag', { active: selectedCategoryId === category.id }]"
          @tap="selectCategory(category.id)"
        >
          {{ category.name }}
        </button>
      </view>
    </scroll-view>

    <view class="box tip-card">
      <text class="tip-title">精选资料库</text>
      <text class="tip-desc">支持预览共享资料，确认后可直接下单打印。</text>
    </view>

    <view class="resource-list" v-if="resources.length">
      <view v-for="resource in resources" :key="resource.id" class="resource-card">
        <image class="resource-thumb" :src="resource.thumbnail_url || placeholderImage" mode="aspectFill" />
        <view class="resource-body">
          <view class="resource-top">
            <text class="title">{{ resource.title }}</text>
            <text class="resource-state">{{ resource.is_public === false ? '未开放' : '可打印' }}</text>
          </view>
          <text class="meta">{{ resource.page_count || '-' }} 页资料 · 支持在线预览</text>
          <view class="resource-actions">
            <button class="ghost-btn" @tap="previewResource(resource)">预览</button>
            <button class="order-btn" :disabled="resource.is_public === false" @tap="createFromResource(resource)">立即下单</button>
          </view>
        </view>
      </view>
    </view>

    <view class="box empty" v-else>
      <text class="empty-title">当前分类暂无资料</text>
      <text class="empty-desc">可以切换分类查看，或者稍后再来。</text>
    </view>
  </view>
</template>

<script>
import { useMiniStore } from '../../store/miniApp';

const miniStore = useMiniStore();

export default {
  computed: {
    categories() {
      return miniStore.state.categories;
    },
    resources() {
      return miniStore.state.resources;
    },
    selectedCategoryId() {
      return miniStore.state.selectedCategoryId;
    },
    placeholderImage() {
      return miniStore.placeholderImage;
    }
  },
  onShow() {
    miniStore.loadLibrary();
  },
  methods: {
    selectCategory(categoryId) {
      miniStore.selectCategory(categoryId);
    },
    previewResource(resource) {
      miniStore.previewResource(resource);
    },
    createFromResource(resource) {
      miniStore.createFromResource(resource);
    }
  }
};
</script>

<style scoped>
.page-shell {
  min-height: 100vh;
  padding: calc(18px + env(safe-area-inset-top)) 16px 24px;
}

.library-page {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.tag-row {
  width: 100%;
  white-space: nowrap;
}

.tag-track {
  display: inline-flex;
  gap: 10px;
  padding: 2px 2px 4px;
}

.tag {
  border: 0;
  background: rgba(255, 255, 255, 0.72);
  color: #5d5d5d;
  border-radius: 999px;
  padding: 10px 16px;
  font-size: 14px;
  box-shadow: 0 8px 18px rgba(31, 83, 61, 0.08);
}

.tag.active {
  background: linear-gradient(135deg, #16c98d, #6fe0b7);
  color: #0f172a;
}

.box,
.resource-card {
  background: #ffffff;
  border-radius: 28px;
  box-shadow: 0 16px 34px rgba(31, 83, 61, 0.12);
}

.box {
  padding: 18px;
}

.tip-title,
.title,
.empty-title {
  display: block;
  font-size: 18px;
  font-weight: 700;
}

.tip-desc,
.meta,
.empty-desc {
  display: block;
  margin-top: 8px;
  color: #8b8b8b;
  line-height: 1.5;
}

.resource-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.resource-card {
  display: flex;
  gap: 14px;
  padding: 14px;
}

.resource-thumb {
  width: 108px;
  height: 124px;
  border-radius: 20px;
  flex-shrink: 0;
}

.resource-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.resource-top {
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.resource-state {
  align-self: flex-start;
  border-radius: 999px;
  background: rgba(17, 201, 140, 0.12);
  color: #059669;
  padding: 6px 10px;
  font-size: 12px;
}

.resource-actions {
  display: flex;
  gap: 10px;
  margin-top: auto;
}

.ghost-btn,
.order-btn {
  margin: 0;
  border-radius: 999px;
  font-weight: 700;
  padding: 10px 16px;
}

.ghost-btn {
  border: 1px solid #d6ddd8;
  background: #ffffff;
  color: #111827;
}

.order-btn {
  border: 0;
  background: #11c98c;
  color: #111827;
}
</style>
