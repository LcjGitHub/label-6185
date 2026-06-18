<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Select from 'primevue/select'
import Tag from 'primevue/tag'
import Toast from 'primevue/toast'
import ConfirmDialog from 'primevue/confirmdialog'
import { routeApi, markerApi } from '../api'

const props = defineProps({
  id: { type: [String, Number], required: true },
})

const router = useRouter()
const toast = useToast()
const confirm = useConfirm()

const routeId = computed(() => Number(props.id))
const route = ref(null)
const markers = ref([])
const loadingRoute = ref(false)
const loadingMarkers = ref(false)
const dialogVisible = ref(false)
const editingMarker = ref(null)
const form = ref({ type: '水源', coordinates: '', notes: '', reliability: '中' })

const typeOptions = [
  { label: '水源', value: '水源' },
  { label: '休息', value: '休息' },
]

const reliabilityOptions = [
  { label: '高', value: '高' },
  { label: '中', value: '中' },
  { label: '低', value: '低' },
]

const reliabilitySeverity = {
  高: 'success',
  中: 'warn',
  低: 'danger',
}

const difficultySeverity = {
  简单: 'success',
  中等: 'info',
  困难: 'warn',
  极难: 'danger',
}

async function loadRoute() {
  loadingRoute.value = true
  try {
    route.value = await routeApi.get(routeId.value)
  } catch {
    toast.add({ severity: 'error', summary: '路线不存在', life: 3000 })
    router.push('/')
  } finally {
    loadingRoute.value = false
  }
}

async function loadMarkers() {
  loadingMarkers.value = true
  try {
    markers.value = await markerApi.list(routeId.value)
  } catch {
    toast.add({ severity: 'error', summary: '加载标记失败', life: 3000 })
  } finally {
    loadingMarkers.value = false
  }
}

function openCreate() {
  editingMarker.value = null
  form.value = { type: '水源', coordinates: '', notes: '', reliability: '中' }
  dialogVisible.value = true
}

/** @param {import('../api').Marker} marker */
function openEdit(marker) {
  editingMarker.value = marker
  form.value = {
    type: marker.type,
    coordinates: marker.coordinates,
    notes: marker.notes || '',
    reliability: marker.reliability || '',
  }
  dialogVisible.value = true
}

async function saveMarker() {
  if (!form.value.coordinates.trim()) {
    toast.add({ severity: 'warn', summary: '请填写坐标', life: 2500 })
    return
  }
  const payload = { ...form.value }
  if (payload.type !== '水源') {
    payload.reliability = null
  }
  try {
    if (editingMarker.value) {
      await markerApi.update(editingMarker.value.id, payload)
      toast.add({ severity: 'success', summary: '标记已更新', life: 2000 })
    } else {
      await markerApi.create(routeId.value, payload)
      toast.add({ severity: 'success', summary: '标记已创建', life: 2000 })
    }
    dialogVisible.value = false
    await loadMarkers()
  } catch (err) {
    const detail = err?.response?.data?.error || '请稍后重试'
    toast.add({ severity: 'error', summary: '保存失败', detail, life: 3000 })
  }
}

/** @param {import('../api').Marker} marker */
function confirmDelete(marker) {
  confirm.require({
    message: `确定删除该${marker.type}标记点？`,
    header: '确认删除',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await markerApi.remove(marker.id)
        toast.add({ severity: 'success', summary: '已删除', life: 2000 })
        await loadMarkers()
      } catch {
        toast.add({ severity: 'error', summary: '删除失败', life: 3000 })
      }
    },
  })
}

onMounted(async () => {
  await loadRoute()
  await loadMarkers()
})
</script>

<template>
  <Toast />
  <ConfirmDialog />

  <div class="breadcrumb">
    <Button label="返回列表" icon="pi pi-arrow-left" text @click="router.push('/')" />
  </div>

  <div v-if="route" class="route-info">
    <h1>{{ route.name }}</h1>
    <Tag :value="route.difficulty" :severity="difficultySeverity[route.difficulty] || 'secondary'" />
    <Tag :value="`${route.mileage ?? 0} 公里`" severity="info" icon="pi pi-route" />
    <Tag :value="`${route.days ?? 0} 天`" severity="success" icon="pi pi-clock" />
  </div>
  <div v-else-if="loadingRoute" class="loading-hint">加载中…</div>

  <div class="section-header">
    <h2>标记点</h2>
    <Button label="添加标记" icon="pi pi-map-marker" size="small" @click="openCreate" />
  </div>

  <DataTable
    :value="markers"
    :loading="loadingMarkers"
    striped-rows
    row-hover
    data-key="id"
    class="marker-table"
  >
    <Column field="type" header="类型" style="width: 6rem">
      <template #body="{ data }">
        <Tag
          :value="data.type"
          :severity="data.type === '水源' ? 'info' : 'success'"
          :icon="data.type === '水源' ? 'pi pi-tint' : 'pi pi-sun'"
        />
      </template>
    </Column>
    <Column field="coordinates" header="坐标">
      <template #body="{ data }">
        <code class="coords">{{ data.coordinates }}</code>
      </template>
    </Column>
    <Column field="reliability" header="可靠性" style="width: 6rem">
      <template #body="{ data }">
        <Tag
          v-if="data.reliability"
          :value="data.reliability"
          :severity="reliabilitySeverity[data.reliability]"
        />
        <span v-else class="notes">—</span>
      </template>
    </Column>
    <Column field="notes" header="备注">
      <template #body="{ data }">
        <span class="notes">{{ data.notes || '—' }}</span>
      </template>
    </Column>
    <Column header="操作" style="width: 8rem">
      <template #body="{ data }">
        <div class="actions">
          <Button icon="pi pi-pencil" text rounded @click="openEdit(data)" />
          <Button icon="pi pi-trash" text rounded severity="danger" @click="confirmDelete(data)" />
        </div>
      </template>
    </Column>
    <template #empty>
      <div class="empty">暂无标记点</div>
    </template>
  </DataTable>

  <Dialog
    v-model:visible="dialogVisible"
    :header="editingMarker ? '编辑标记点' : '添加标记点'"
    modal
    style="width: 26rem"
  >
    <div class="form-field">
      <label for="marker-type">类型</label>
      <Select
        id="marker-type"
        v-model="form.type"
        :options="typeOptions"
        option-label="label"
        option-value="value"
        class="w-full"
      />
    </div>
    <div v-if="form.type === '水源'" class="form-field">
      <label for="marker-reliability">可靠性</label>
      <Select
        id="marker-reliability"
        v-model="form.reliability"
        :options="reliabilityOptions"
        option-label="label"
        option-value="value"
        class="w-full"
      />
    </div>
    <div class="form-field">
      <label for="marker-coords">坐标</label>
      <InputText
        id="marker-coords"
        v-model="form.coordinates"
        class="w-full"
        placeholder="如：N28.4123 E98.7891"
      />
    </div>
    <div class="form-field">
      <label for="marker-notes">备注</label>
      <Textarea id="marker-notes" v-model="form.notes" rows="3" class="w-full" placeholder="水源状况、休息点说明等" />
    </div>
    <template #footer>
      <Button label="取消" text @click="dialogVisible = false" />
      <Button label="保存" icon="pi pi-check" @click="saveMarker" />
    </template>
  </Dialog>
</template>

<style scoped>
.breadcrumb {
  margin-bottom: 1rem;
}

.route-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.route-info h1 {
  font-size: 1.5rem;
  font-weight: 700;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}

.section-header h2 {
  font-size: 1.125rem;
  font-weight: 600;
}

.coords {
  font-family: 'Consolas', 'Courier New', monospace;
  font-size: 0.875rem;
  background: #f1f5f9;
  padding: 0.125rem 0.375rem;
  border-radius: 4px;
}

.notes {
  color: #475569;
  font-size: 0.9rem;
}

.actions {
  display: flex;
  gap: 0.25rem;
}

.empty,
.loading-hint {
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
</style>
