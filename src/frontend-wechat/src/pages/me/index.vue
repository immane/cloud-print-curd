<template>
  <section class="panel">
    <div class="profile box">
      <img :src="profile.avatar_url || placeholderImage" class="avatar" />
      <div>
        <h3>{{ profile.display_name || 'Guest' }}</h3>
        <p class="muted">Balance: ¥{{ ((profile.balance_cents || 0) / 100).toFixed(2) }}</p>
      </div>
    </div>

    <div class="status-grid box">
      <button v-for="s in orderStatusCards" :key="s.key" @click="$emit('filter-orders', s.key)">
        <strong>{{ s.count }}</strong>
        <span>{{ s.label }}</span>
      </button>
    </div>

    <div class="box">
      <h4>Upload File</h4>
      <input class="file-input" type="file" @change="$emit('file-change', $event)" />
      <p class="muted" v-if="uploadProgress > 0">Progress: {{ uploadProgress }}%</p>
    </div>

    <div class="box">
      <h4>My Files</h4>
      <article v-for="f in files" :key="f.id" class="file-row" >
        <div>
          <strong>{{ f.filename }}</strong>
          <p class="muted">{{ f.page_count || '-' }} pages · {{ f.size_bytes || 0 }} bytes · {{ f.status }}</p>
        </div>
        <div class="file-actions">
          <button @click="$emit('preview-file', f)">Preview</button>
          <button @click="$emit('open-checkout', f)">Create Order</button>
          <button @click="$emit('rename-file', f)">Rename</button>
          <button @click="$emit('delete-file', f)">Delete</button>
        </div>
      </article>
    </div>

    <div class="box links">
      <button @click="$emit('open-prices')">Price List</button>
      <button @click="$emit('open-address')">Address Management</button>
      <button @click="$emit('open-faq')">FAQ</button>
      <button @click="$emit('logout')">Logout</button>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  profile: any;
  files: any[];
  orderStatusCards: any[];
  uploadProgress: number;
  placeholderImage: string;
}>();

defineEmits([
  "filter-orders",
  "file-change",
  "preview-file",
  "open-checkout",
  "rename-file",
  "delete-file",
  "open-prices",
  "open-address",
  "open-faq",
  "logout"
]);
</script>

<style scoped>
.profile {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #dce4ef;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
}

.status-grid button {
  border: 1px solid #dce4ef;
  background: #fff;
  border-radius: 10px;
  padding: 8px 6px;
  display: grid;
  gap: 2px;
}

.status-grid strong {
  font-size: 16px;
  line-height: 1.1;
}

.status-grid span {
  color: #64748b;
  font-size: 11px;
}

.file-input {
  width: 100%;
}

.file-row {
  border: 1px solid #dce4ef;
  border-radius: 12px;
  padding: 10px;
  display: grid;
  gap: 8px;
  margin-bottom: 10px;
}

.file-actions {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.file-actions button,
.links button {
  border: 1px solid #dce4ef;
  background: #fff;
  color: #1f2937;
  border-radius: 10px;
  padding: 8px 10px;
  font-weight: 600;
}

.links {
  display: grid;
  gap: 8px;
}

.links button:last-child {
  border-color: #fecaca;
  color: #b91c1c;
}

.muted {
  color: #64748b;
  margin: 4px 0 0;
}

@media (max-width: 420px) {
  .status-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
