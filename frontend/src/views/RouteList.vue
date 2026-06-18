<script setup>
import { ref, computed, onMounted, onActivated } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import Select from 'primevue/select'
import Tag from 'primevue/tag'
import Toast from 'primevue/toast'
import ConfirmDialog from 'primevue/confirmdialog'
import { routeApi, statsApi } from '../api'

const router = useRouter()
const toast = useToast()
const confirm = useConfirm()

const routes = ref([])
const stats = ref(null)
const statsLoading = ref(false)
const difficultyStats = ref({简单: 0, 中等: 0, 困难: 0, 极难: 0})
const difficultyStatsLoading = ref(false)
const loading = ref(false)

const difficultyTotal = computed(() => {
  const d = difficultyStats.value
  return d.简单 + d.中等 + d.困难 + d.极难
})

const difficultyBars = computed(() => {
  const d = difficultyStats.value
  const total = difficultyTotal.value || 1
  return [
    { label: '简单', count: d.简单, color: '#22c55e', percent: Math.round((d.简单 / total) * 100) },
    { label: '中等', count: d.中等, color: '#3b82f6', percent: Math.round((d.中等 / total) * 100) },
    { label: '困难', count: d.困难, color: '#f59e0b', percent: Math.round((d.困难 / total) * 100) },
    { label: '极难', count: d.极难, color: '#ef4444', percent: Math.round((d.极难 / total) * 100) },
  ]
})

const dialogVisible = ref(false)
const editingRoute = ref(null)
const form = ref({ name: '', difficulty: '', region: '', bestMonth: '', mileage: 0, days: 0 })
const selectedRegion = ref('')
const selectedDifficulty = ref('')
const searchNameInput = ref('')
const activeSearchName = ref('')
const regionOptions = ref([])
const difficultyFilterOptions = ref([])

const difficultyOptions = [
  { label: '简单', value: '简单' },
  { label: '中等', value: '中等' },
  { label: '困难', value: '困难' },
  { label: '极难', value: '极难' },
]

const monthOptions = [
  { label: '一月', value: '一月' },
  { label: '二月', value: '二月' },
  { label: '三月', value: '三月' },
  { label: '四月', value: '四月' },
  { label: '五月', value: '五月' },
  { label: '六月', value: '六月' },
  { label: '七月', value: '七月' },
  { label: '八月', value: '八月' },
  { label: '九月', value: '九月' },
  { label: '十月', value: '十月' },
  { label: '十一月', value: '十一月' },
  { label: '十二月', value: '十二月' },
]

/** 难度对应 Tag 颜色 */
const difficultySeverity = {
  简单: 'success',
  中等: 'info',
  困难: 'warn',
  极难: 'danger',
}

/** @param {string} difficulty */
function getSeverity(difficulty) {
  return difficultySeverity[difficulty] || 'secondary'
}

async function loadRoutes() {
  loading.value = true
  try {
    const params = {}
    if (activeSearchName.value) params.name = activeSearchName.value
    if (selectedRegion.value) params.region = selectedRegion.value
    if (selectedDifficulty.value) params.difficulty = selectedDifficulty.value
    routes.value = await routeApi.list(params)
  } catch {
    toast.add({ severity: 'error', summary: '加载失败', detail: '无法获取路线列表', life: 3000 })
  } finally {
    loading.value = false
  }
}

async function loadStats() {
  statsLoading.value = true
  try {
    stats.value = await statsApi.get()
  } catch {
    stats.value = null
    toast.add({ severity: 'error', summary: '加载失败', detail: '无法获取统计数据', life: 3000 })
  } finally {
    statsLoading.value = false
  }
}

async function loadDifficultyStats() {
  difficultyStatsLoading.value = true
  try {
    difficultyStats.value = await statsApi.difficultyStats()
  } catch {
    difficultyStats.value = {简单: 0, 中等: 0, 困难: 0, 极难: 0}
    toast.add({ severity: 'error', summary: '加载失败', detail: '无法获取难度分布', life: 3000 })
  } finally {
    difficultyStatsLoading.value = false
  }
}

async function loadRegions() {
  try {
    const regions = await routeApi.regions()
    regionOptions.value = [
      { label: '全部地区', value: '' },
      ...regions.map((r) => ({ label: r, value: r })),
    ]
  } catch {
    regionOptions.value = [{ label: '全部地区', value: '' }]
  }
}

async function onRegionChange() {
  await loadRoutes()
}

async function loadDifficulties() {
  try {
    const difficulties = await routeApi.difficulties()
    difficultyFilterOptions.value = [
      { label: '全部难度', value: '' },
      ...difficulties.map((d) => ({ label: d, value: d })),
    ]
  } catch {
    difficultyFilterOptions.value = [{ label: '全部难度', value: '' }]
  }
}

async function onDifficultyChange() {
  await loadRoutes()
}

async function resetFilters() {
  selectedRegion.value = ''
  selectedDifficulty.value = ''
  searchNameInput.value = ''
  activeSearchName.value = ''
  await loadRoutes()
}

async function searchByName() {
  activeSearchName.value = searchNameInput.value.trim()
  await loadRoutes()
}

function clearSearch() {
  searchNameInput.value = ''
  activeSearchName.value = ''
  loadRoutes()
}

function openCreate() {
  editingRoute.value = null
  form.value = { name: '', difficulty: '中等', region: '', bestMonth: '', mileage: 0, days: 0 }
  dialogVisible.value = true
}

/** @param {import('../api').Route} route */
function openEdit(route) {
  editingRoute.value = route
  form.value = {
    name: route.name,
    difficulty: route.difficulty,
    region: route.region,
    bestMonth: route.best_month ?? '',
    mileage: route.mileage ?? 0,
    days: route.days ?? 0,
  }
  dialogVisible.value = true
}

async function saveRoute() {
  if (!form.value.name.trim() || !form.value.difficulty || !form.value.region.trim() || !form.value.bestMonth) {
    toast.add({ severity: 'warn', summary: '请填写完整', life: 2500 })
    return
  }
  try {
    if (editingRoute.value) {
      await routeApi.update(editingRoute.value.id, form.value)
      toast.add({ severity: 'success', summary: '已更新', life: 2000 })
    } else {
      await routeApi.create(form.value)
      toast.add({ severity: 'success', summary: '已创建', life: 2000 })
    }
    dialogVisible.value = false
    await Promise.all([loadRoutes(), loadRegions(), loadDifficulties(), loadStats(), loadDifficultyStats()])
  } catch (err) {
    const detail = err?.response?.data?.error || '请稍后重试'
    toast.add({ severity: 'error', summary: '保存失败', detail, life: 3000 })
  }
}

/** @param {import('../api').Route} route */
async function cloneRoute(route) {
  try {
    await routeApi.clone(route.id)
    toast.add({ severity: 'success', summary: '克隆成功', detail: `已创建「${route.name}副本」`, life: 3000 })
    await Promise.all([loadRoutes(), loadRegions(), loadDifficulties(), loadStats(), loadDifficultyStats()])
  } catch (err) {
    const detail = err?.response?.data?.error || '请稍后重试'
    toast.add({ severity: 'error', summary: '克隆失败', detail, life: 3000 })
  }
}

/** @param {import('../api').Route} route */
function confirmDelete(route) {
  confirm.require({
    message: `确定删除「${route.name}」及其全部标记点？`,
    header: '确认删除',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await routeApi.remove(route.id)
        toast.add({ severity: 'success', summary: '已删除', life: 2000 })
        await Promise.all([loadRoutes(), loadDifficulties(), loadStats(), loadDifficultyStats()])
      } catch {
        toast.add({ severity: 'error', summary: '删除失败', life: 3000 })
      }
    },
  })
}

/** @param {import('../api').Route} route */
function goDetail(route) {
  router.push(`/routes/${route.id}`)
}

onMounted(async () => {
  await Promise.all([loadRegions(), loadDifficulties(), loadStats(), loadDifficultyStats()])
  await loadRoutes()
})

onActivated(() => {
  loadRoutes()
  loadStats()
  loadDifficultyStats()
})
</script>

<template>
  <Toast />
  <ConfirmDialog />

  <div class="page-header">
    <h1>徒步路线</h1>
    <div class="header-actions">
      <IconField class="search-field">
        <InputIcon class="pi pi-search" />
        <InputText
          v-model="searchNameInput"
          placeholder="搜索路线名称"
          class="search-input"
          @keyup.enter="searchByName"
        />
      </IconField>
      <Button label="查询" icon="pi pi-search" @click="searchByName" />
      <Button
        v-if="activeSearchName || searchNameInput"
        label="清空"
        icon="pi pi-times"
        text
        @click="clearSearch"
      />
      <Select
        v-model="selectedRegion"
        :options="regionOptions"
        option-label="label"
        option-value="value"
        placeholder="选择地区"
        class="filter-select"
        @change="onRegionChange"
      />
      <Select
        v-model="selectedDifficulty"
        :options="difficultyFilterOptions"
        option-label="label"
        option-value="value"
        placeholder="选择难度"
        class="filter-select"
        @change="onDifficultyChange"
      />
      <Button
        label="重置"
        icon="pi pi-filter-slash"
        text
        @click="resetFilters"
      />
      <Button label="新建路线" icon="pi pi-plus" @click="openCreate" />
    </div>
  </div>

  <div class="difficulty-distribution">
    <div class="difficulty-distribution-title">路线难度分布</div>
    <div v-if="difficultyStatsLoading" class="difficulty-loading">加载中...</div>
    <template v-else>
      <div class="difficulty-bar-container">
        <div
          v-for="bar in difficultyBars"
          :key="bar.label"
          class="difficulty-bar-segment"
          :style="{ width: bar.percent + '%', backgroundColor: bar.color }"
        >
          <span v-if="bar.percent >= 15" class="difficulty-bar-text">{{ bar.label }} {{ bar.count }}</span>
        </div>
      </div>
      <div class="difficulty-legend">
        <div v-for="bar in difficultyBars" :key="bar.label" class="difficulty-legend-item">
          <span class="difficulty-legend-dot" :style="{ backgroundColor: bar.color }"></span>
          <span class="difficulty-legend-label">{{ bar.label }}</span>
          <span class="difficulty-legend-count">{{ bar.count }} 条</span>
          <span class="difficulty-legend-percent">({{ bar.percent }}%)</span>
        </div>
      </div>
    </template>
  </div>

  <div class="stats-bar">
    <div class="stat-row">
      <span class="stat-label">路线总数</span>
      <span class="stat-value">{{ statsLoading ? '--' : (stats?.routeCount ?? 0) }}</span>
      <span class="stat-unit">条</span>
    </div>
    <div class="stat-row stat-row-secondary">
      <span class="stat-label">标记点总数</span>
      <span class="stat-value stat-value-secondary">{{ statsLoading ? '--' : (stats?.markerCount ?? 0) }}</span>
      <span class="stat-unit">个</span>
    </div>
  </div>

  <DataTable
    :value="routes"
    :loading="loading"
    striped-rows
    row-hover
    data-key="id"
    class="route-table"
  >
    <Column field="name" header="路线名称">
      <template #body="{ data }">
        <a class="route-link" href="#" @click.prevent="goDetail(data)">{{ data.name }}</a>
      </template>
    </Column>
    <Column field="difficulty" header="难度" style="width: 8rem">
      <template #body="{ data }">
        <Tag :value="data.difficulty" :severity="getSeverity(data.difficulty)" />
      </template>
    </Column>
    <Column field="region" header="地区" style="width: 8rem">
      <template #body="{ data }">
        <Tag :value="data.region" severity="info" icon="pi pi-map-marker" />
      </template>
    </Column>
    <Column field="best_month" header="最佳月份" style="width: 8rem">
      <template #body="{ data }">
        <Tag :value="data.best_month" severity="warning" icon="pi pi-calendar" />
      </template>
    </Column>
    <Column field="mileage" header="里程(公里)" style="width: 8rem">
      <template #body="{ data }">
        <span class="mileage-text">{{ data.mileage ?? 0 }} 公里</span>
      </template>
    </Column>
    <Column field="marker_count" header="标记点数量" style="width: 10rem">
      <template #body="{ data }">
        <span class="marker-count-text">{{ data.marker_count ?? 0 }} 个</span>
      </template>
    </Column>
    <Column field="days" header="徒步天数" style="width: 8rem">
      <template #body="{ data }">
        <span class="days-text">{{ data.days ?? 0 }} 天</span>
      </template>
    </Column>
    <Column header="操作" style="width: 14rem">
      <template #body="{ data }">
        <div class="actions">
          <Button icon="pi pi-eye" text rounded severity="info" @click="goDetail(data)" v-tooltip.top="'查看详情'" />
          <Button icon="pi pi-copy" text rounded severity="success" @click="cloneRoute(data)" v-tooltip.top="'克隆路线'" />
          <Button icon="pi pi-pencil" text rounded @click="openEdit(data)" v-tooltip.top="'编辑'" />
          <Button icon="pi pi-trash" text rounded severity="danger" @click="confirmDelete(data)" v-tooltip.top="'删除'" />
        </div>
      </template>
    </Column>
    <template #empty>
      <div class="empty">
        {{ activeSearchName ? '未找到匹配的路线' : '暂无路线，点击「新建路线」添加' }}
      </div>
    </template>
  </DataTable>

  <Dialog
    v-model:visible="dialogVisible"
    :header="editingRoute ? '编辑路线' : '新建路线'"
    modal
    style="width: 24rem"
  >
    <div class="form-field">
      <label for="route-name">路线名称</label>
      <InputText id="route-name" v-model="form.name" class="w-full" placeholder="如：雨崩冰湖线" />
    </div>
    <div class="form-field">
      <label for="route-difficulty">难度</label>
      <Select
        id="route-difficulty"
        v-model="form.difficulty"
        :options="difficultyOptions"
        option-label="label"
        option-value="value"
        class="w-full"
      />
    </div>
    <div class="form-field">
      <label for="route-region">地区</label>
      <InputText id="route-region" v-model="form.region" class="w-full" placeholder="如：云南" />
    </div>
    <div class="form-field">
      <label for="route-best-month">最佳徒步月份</label>
      <Select
        id="route-best-month"
        v-model="form.bestMonth"
        :options="monthOptions"
        option-label="label"
        option-value="value"
        placeholder="选择月份"
        class="w-full"
      />
    </div>
    <div class="form-field">
      <label for="route-mileage">里程(公里)</label>
      <InputNumber id="route-mileage" v-model="form.mileage" :min="0" :min-fraction-digits="0" :max-fraction-digits="2" class="w-full" placeholder="如：18.5" />
    </div>
    <div class="form-field">
      <label for="route-days">建议徒步天数</label>
      <InputNumber id="route-days" v-model="form.days" :min="0" :min-fraction-digits="0" :max-fraction-digits="1" class="w-full" placeholder="如：2.5" />
    </div>
    <template #footer>
      <Button label="取消" text @click="dialogVisible = false" />
      <Button label="保存" icon="pi pi-check" @click="saveRoute" />
    </template>
  </Dialog>
</template>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.25rem;
}

.page-header h1 {
  font-size: 1.5rem;
  font-weight: 700;
}

.difficulty-distribution {
  background: #ffffff;
  border-radius: 0.75rem;
  padding: 1rem 1.25rem;
  margin-bottom: 1rem;
  border: 1px solid #e2e8f0;
}

.difficulty-distribution-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: #334155;
  margin-bottom: 0.75rem;
}

.difficulty-loading {
  font-size: 0.85rem;
  color: #94a3b8;
}

.difficulty-bar-container {
  display: flex;
  height: 2rem;
  border-radius: 0.375rem;
  overflow: hidden;
  background: #f1f5f9;
}

.difficulty-bar-segment {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 2px;
  transition: width 0.4s ease;
}

.difficulty-bar-text {
  font-size: 0.75rem;
  font-weight: 600;
  color: #ffffff;
  white-space: nowrap;
}

.difficulty-legend {
  display: flex;
  gap: 1.5rem;
  margin-top: 0.75rem;
  flex-wrap: wrap;
}

.difficulty-legend-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.difficulty-legend-dot {
  width: 0.625rem;
  height: 0.625rem;
  border-radius: 50%;
  flex-shrink: 0;
}

.difficulty-legend-label {
  font-size: 0.8rem;
  font-weight: 500;
  color: #475569;
}

.difficulty-legend-count {
  font-size: 0.8rem;
  font-weight: 600;
  color: #1e293b;
}

.difficulty-legend-percent {
  font-size: 0.75rem;
  color: #94a3b8;
}

.stats-bar {
  background: linear-gradient(135deg, #eff6ff 0%, #f0fdf4 100%);
  border-radius: 0.75rem;
  padding: 1rem 1.25rem;
  margin-bottom: 1.25rem;
  border: 1px solid #dbeafe;
}

.stat-row {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
}

.stat-row-secondary {
  margin-top: 0.625rem;
}

.stat-label {
  font-size: 0.875rem;
  color: #64748b;
  font-weight: 500;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e40af;
}

.stat-value-secondary {
  font-size: 1.125rem;
  font-weight: 600;
  color: #0f766e;
}

.stat-unit {
  font-size: 0.875rem;
  color: #64748b;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.search-field {
  position: relative;
}

.search-input {
  padding-left: 2.25rem;
  width: 14rem;
}

.filter-select {
  width: 10rem;
}

.route-link {
  color: #2563eb;
  text-decoration: none;
  font-weight: 500;
}

.route-link:hover {
  text-decoration: underline;
}

.actions {
  display: flex;
  gap: 0.25rem;
}

.empty {
  text-align: center;
  padding: 2rem;
  color: #64748b;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  margin-bottom: 1rem;
}

.form-field label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #475569;
}

.w-full {
  width: 100%;
}

.mileage-text,
.marker-count-text,
.days-text {
  font-weight: 500;
  color: #475569;
}
</style>
