<template>
  <section class="panel">
    <div class="hero box">
      <h2>Print Smarter</h2>
      <p>Upload once, place orders in seconds, and track status anytime.</p>
    </div>

    <div class="carousel box" v-if="slider.length">
      <div
        v-for="item in slider"
        :key="item.id"
        class="slide"
        @click="$emit('slide-click', item)"
      >
        <img :src="item.image_url" alt="slide" />
        <span class="slide-tip">Tap for details</span>
      </div>
    </div>

    <div class="cards">
      <button class="card tutorial" @click="$emit('open-tutorial')">Printing Tutorial</button>
      <button class="card price" @click="$emit('open-prices')">Price List</button>
    </div>

    <div class="box tutorial-meta" v-if="tutorial?.title">
      <h3>{{ tutorial.title }}</h3>
      <p>Updated: {{ tutorial.updated_at || '-' }}</p>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{ slider: any[]; tutorial: any }>();
defineEmits(["slide-click", "open-tutorial", "open-prices"]);
</script>

<style scoped>
.hero h2 {
  margin: 0;
  font-size: 22px;
}

.hero p {
  margin: 8px 0 0;
  color: #5e6a7d;
  line-height: 1.45;
}

.carousel {
  display: grid;
  gap: 10px;
}

.slide {
  position: relative;
  overflow: hidden;
  border-radius: 12px;
  cursor: pointer;
}

.slide img {
  width: 100%;
  height: 160px;
  object-fit: cover;
  display: block;
}

.slide-tip {
  position: absolute;
  right: 10px;
  bottom: 10px;
  background: rgba(17, 24, 39, 0.72);
  color: #fff;
  font-size: 12px;
  border-radius: 999px;
  padding: 4px 8px;
}

.cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.card {
  border: 0;
  border-radius: 12px;
  padding: 14px 12px;
  color: #fff;
  font-weight: 700;
  min-height: 72px;
}

.card.tutorial {
  background: linear-gradient(135deg, #0284c7, #06b6d4);
}

.card.price {
  background: linear-gradient(135deg, #0f766e, #22c55e);
}

.tutorial-meta h3 {
  margin: 0;
}

.tutorial-meta p {
  color: #5e6a7d;
  margin: 8px 0 0;
}
</style>
