<template>
  <div v-if="open" class="modal" @click="$emit('close')">
    <div class="modal-card" @click.stop>
      <h3>Price List</h3>
      <p>{{ tip }}</p>
      <div class="filters">
        <input :value="paperType" placeholder="Filter paper type" @input="$emit('update:paperType', ($event.target as HTMLInputElement).value)" />
        <input :value="size" placeholder="Filter size" @input="$emit('update:size', ($event.target as HTMLInputElement).value)" />
      </div>
      <div class="price-group" v-for="(group, key) in groupedPrices" :key="key">
        <h4>{{ key }}</h4>
        <ul>
          <li v-for="p in group" :key="p.description">{{ p.description }} - ¥{{ (p.unit_price_cents / 100).toFixed(2) }}</li>
        </ul>
      </div>
      <footer class="sticky-footer">
        <span>Unit: per page/per copy</span>
        <button class="primary" @click="$emit('order-now')">Order Now</button>
      </footer>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ open: boolean; tip: string; groupedPrices: Record<string, any[]>; paperType: string; size: string }>();
defineEmits(["close", "order-now", "update:paperType", "update:size"]);
</script>
