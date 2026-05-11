<template>
  <div v-if="open && file" class="modal" @click="$emit('close')">
    <div class="modal-card" @click.stop>
      <h3>Checkout: {{ file.filename }}</h3>
      <div class="filters">
        <select :value="checkout.size" @change="$emit('update:size', ($event.target as HTMLSelectElement).value)"><option>A4</option><option>A3</option></select>
        <select :value="checkout.color" @change="$emit('update:color', ($event.target as HTMLSelectElement).value)"><option value="black_white">B/W</option><option value="color">Color</option></select>
        <label><input type="checkbox" :checked="checkout.duplex" @change="$emit('update:duplex', ($event.target as HTMLInputElement).checked)" /> Duplex</label>
        <input type="number" min="1" :value="checkout.copies" placeholder="Copies" @input="$emit('update:copies', Number(($event.target as HTMLInputElement).value || 1))" />
      </div>
      <p>Estimated: ¥{{ preview }}</p>
      <button class="primary" @click="$emit('pay')">Pay Now</button>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ open: boolean; file: any | null; checkout: { size: string; color: string; duplex: boolean; copies: number }; preview: string }>();
defineEmits(["close", "pay", "update:size", "update:color", "update:duplex", "update:copies"]);
</script>
