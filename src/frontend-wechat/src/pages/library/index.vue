<template>
  <section class="panel">
    <div class="tag-row">
      <button
        v-for="c in categories"
        :key="c.id"
        :class="['tag', { active: selectedCategoryId === c.id }]"
        @click="$emit('select-category', c.id)"
      >
        {{ c.name }}
      </button>
    </div>

    <div class="resource-grid" v-if="resources.length">
      <article v-for="r in resources" :key="r.id" class="resource-card">
        <img :src="r.thumbnail_url || placeholderImage" alt="thumb" class="resource-thumb" @click="$emit('preview-resource', r)" />
        <h4 class="title">{{ r.title }}</h4>
        <p class="meta">Pages: {{ r.page_count || '-' }}</p>
        <button class="order-btn" :disabled="r.is_public === false" @click="$emit('create-from-resource', r)">Order</button>
      </article>
    </div>

    <div class="box empty" v-else>
      <h4>No resources in this category</h4>
      <p>Try switching category or add resources from admin.</p>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{ categories: any[]; resources: any[]; selectedCategoryId?: number; placeholderImage: string }>();
defineEmits(["select-category", "preview-resource", "create-from-resource"]);
</script>

<style scoped>
.tag-row {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 4px;
}

.tag {
  border: 1px solid #dce4ef;
  background: #fff;
  color: #334155;
  border-radius: 999px;
  padding: 6px 10px;
  font-size: 12px;
  white-space: nowrap;
}

.tag.active {
  background: linear-gradient(135deg, #0f766e, #0284c7);
  border-color: transparent;
  color: #fff;
}

.resource-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.resource-card {
  background: #fff;
  border: 1px solid #dce4ef;
  border-radius: 12px;
  padding: 10px;
  display: grid;
  gap: 8px;
}

.resource-thumb {
  width: 100%;
  height: 90px;
  object-fit: cover;
  border-radius: 8px;
}

.title {
  margin: 0;
  font-size: 14px;
  line-height: 1.35;
}

.meta {
  margin: 0;
  color: #64748b;
  font-size: 12px;
}

.order-btn {
  border: 0;
  border-radius: 9px;
  background: #0f766e;
  color: #fff;
  font-weight: 700;
  padding: 8px 0;
}

.order-btn:disabled {
  opacity: 0.45;
}

.empty h4 {
  margin: 0;
}

.empty p {
  margin: 8px 0 0;
  color: #64748b;
}

@media (max-width: 360px) {
  .resource-grid {
    grid-template-columns: 1fr;
  }
}
</style>
