<script setup>
import { ref, onMounted, onActivated } from 'vue'
import { useToast } from 'primevue/usetoast'
import Toast from 'primevue/toast'
import { statsApi } from '../api'

const toast = useToast()

const stats = ref({ routeCount: 0, markerCount: 0, waterCount: 0, restCount: 0 })
const loading = ref(false)

const cards = [
  { key: 'routeCount', label: '路线总数', icon: 'pi pi-map', color: '#2563eb', bg: '#eff6ff' },
  { key: 'markerCount', label: '标记点总数', icon: 'pi pi-map-marker', color: '#7c3aed', bg: '#f5f3ff' },
  { key: 'waterCount', label: '水源数量', icon: 'pi pi-cloud', color: '#0891b2', bg: '#ecfeff' },
  { key: 'restCount', label: '休息点数量', icon: 'pi pi-home', color: '#16a34a', bg: '#f0fdf4' },
]

async function loadStats() {
  loading.value = true
  try {
    stats.value = await statsApi.get()
  } catch {
    toast.add({ severity: 'error', summary: '加载失败', detail: '无法获取统计数据', life: 3000 })
  } finally {
    loading.value = false
  }
}

onMounted(loadStats)
onActivated(loadStats)
</script>

<template>
  <Toast />

  <div class="page-header">
    <h1>路线统计概览</h1>
  </div>

  <div class="stats-grid" v-if="!loading">
    <div
      v-for="card in cards"
      :key="card.key"
      class="stat-card"
      :style="{ '--card-color': card.color, '--card-bg': card.bg }"
    >
      <div class="stat-icon">
        <i :class="card.icon" />
      </div>
      <div class="stat-info">
        <span class="stat-value">{{ stats[card.key] }}</span>
        <span class="stat-label">{{ card.label }}</span>
      </div>
    </div>
  </div>

  <div class="stats-grid" v-else>
    <div v-for="card in cards" :key="card.key" class="stat-card stat-card--loading">
      <div class="stat-icon">
        <i :class="card.icon" />
      </div>
      <div class="stat-info">
        <span class="stat-value">--</span>
        <span class="stat-label">{{ card.label }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.page-header h1 {
  font-size: 1.5rem;
  font-weight: 700;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.25rem;
}

.stat-card {
  background: var(--card-bg);
  border-radius: 0.75rem;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  border: 1px solid color-mix(in srgb, var(--card-color) 15%, transparent);
  transition: box-shadow 0.2s, transform 0.2s;
}

.stat-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.stat-card--loading {
  opacity: 0.6;
}

.stat-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 0.625rem;
  background: var(--card-color);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.375rem;
  flex-shrink: 0;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--card-color);
  line-height: 1.2;
}

.stat-label {
  font-size: 0.875rem;
  color: #64748b;
  font-weight: 500;
}
</style>
