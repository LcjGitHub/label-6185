export const MARKER_FILTER_TYPES = {
  ALL: 'all',
  WATER: '水源',
  REST: '休息',
}

export const MARKER_FILTER_OPTIONS = [
  { label: '全部', value: MARKER_FILTER_TYPES.ALL },
  { label: '仅水源', value: MARKER_FILTER_TYPES.WATER },
  { label: '仅休息', value: MARKER_FILTER_TYPES.REST },
]

/**
 * 按类型筛选标记点
 * @param {import('../api').Marker[]} markers - 标记点数组
 * @param {string} filterType - 筛选类型，值来自 MARKER_FILTER_TYPES
 * @returns {import('../api').Marker[]} 筛选后的标记点数组
 */
export function filterMarkersByType(markers, filterType) {
  if (!Array.isArray(markers)) {
    return []
  }
  if (filterType === MARKER_FILTER_TYPES.ALL) {
    return markers
  }
  return markers.filter((marker) => marker.type === filterType)
}
