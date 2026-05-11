<template>
  <div v-if="open" class="modal" @click="$emit('close')">
    <div class="modal-card" @click.stop>
      <h3>Address Management</h3>
      <div class="filters">
        <input :value="form.title" placeholder="Title" @input="$emit('update:field', 'title', ($event.target as HTMLInputElement).value)" />
        <input :value="form.recipient_name" placeholder="Recipient" @input="$emit('update:field', 'recipient_name', ($event.target as HTMLInputElement).value)" />
        <input :value="form.phone" placeholder="Phone" @input="$emit('update:field', 'phone', ($event.target as HTMLInputElement).value)" />
        <input :value="form.address_line1" placeholder="Address" @input="$emit('update:field', 'address_line1', ($event.target as HTMLInputElement).value)" />
        <button class="primary" @click="$emit('add')">Add</button>
      </div>
      <article class="box" v-for="a in addresses" :key="a.id">
        <strong>{{ a.title || 'Address' }}</strong>
        <p>{{ a.recipient_name }} · {{ a.phone }}</p>
        <p>{{ a.address_line1 }}</p>
        <button @click="$emit('delete', a.id)">Delete</button>
      </article>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ open: boolean; addresses: any[]; form: { title: string; recipient_name: string; phone: string; address_line1: string } }>();
defineEmits(["close", "add", "delete", "update:field"]);
</script>
