<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Select from 'primevue/select'
import Tag from 'primevue/tag'
import Toast from 'primevue/toast'
import ConfirmDialog from 'primevue/confirmdialog'
import { routeApi } from '../api'

const router = useRouter()
const toast = useToast()
const confirm = useConfirm()

const routes = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const editingRoute = ref(null)
const form = ref({ name: '', difficulty: '', region: '', mileage: 0, days: 0 })
const selectedRegion = ref('')
const regionOptions = ref([])

const difficultyOptions = [
  { label: '简单', value: '简单' },
  { label: '中等', value: '中等' },
  { label: '困难', value: '困难' },
  { label: '极难', value: '极难' },
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
    routes.value = await routeApi.list(selectedRegion.value || undefined)
  } catch {
    toast.add({ severity: 'error', summary: '加载失败', detail: '无法获取路线列表', life: 3000 })
  } finally {
    loading.value = false
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

function openCreate() {
  editingRoute.value = null
  form.value = { name: '', difficulty: '中等', region: '', mileage: 0, days: 0 }
  dialogVisible.value = true
}

/** @param {import('../api').Route} route */
function openEdit(route) {
  editingRoute.value = route
  form.value = {
    name: route.name,
    difficulty: route.difficulty,
    region: route.region,
    mileage: route.mileage ?? 0,
    days: route.days ?? 0,
  }
  dialogVisible.value = true
}

async function saveRoute() {
  if (!form.value.name.trim() || !form.value.difficulty || !form.value.region.trim()) {
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
    await Promise.all([loadRoutes(), loadRegions()])
  } catch {
    toast.add({ severity: 'error', summary: '保存失败', life: 3000 })
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
        await loadRoutes()
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
  await loadRegions()
  await loadRoutes()
})
</script>

<template>
  <Toast />
  <ConfirmDialog />

  <div class="page-header">
    <h1>徒步路线</h1>
    <div class="header-actions">
      <Select
        v-model="selectedRegion"
        :options="regionOptions"
        option-label="label"
        option-value="value"
        placeholder="选择地区"
        class="region-filter"
        @change="onRegionChange"
      />
      <Button label="新建路线" icon="pi pi-plus" @click="openCreate" />
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
    <Column field="mileage" header="里程(km)" style="width: 8rem">
      <template #body="{ data }">
        <span class="mileage-text">{{ data.mileage ?? 0 }} km</span>
      </template>
    </Column>
    <Column field="days" header="徒步天数" style="width: 8rem">
      <template #body="{ data }">
        <span class="days-text">{{ data.days ?? 0 }} 天</span>
      </template>
    </Column>
    <Column header="操作" style="width: 12rem">
      <template #body="{ data }">
        <div class="actions">
          <Button icon="pi pi-eye" text rounded severity="info" @click="goDetail(data)" v-tooltip.top="'查看详情'" />
          <Button icon="pi pi-pencil" text rounded @click="openEdit(data)" v-tooltip.top="'编辑'" />
          <Button icon="pi pi-trash" text rounded severity="danger" @click="confirmDelete(data)" v-tooltip.top="'删除'" />
        </div>
      </template>
    </Column>
    <template #empty>
      <div class="empty">暂无路线，点击「新建路线」添加</div>
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.region-filter {
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
.days-text {
  font-weight: 500;
  color: #475569;
}
</style>
