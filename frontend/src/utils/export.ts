/** 通用导出工具 */

export function exportCSV(headers: string[], rows: string[][], filename: string) {
  const BOM = '\uFEFF'
  const csvContent = BOM + [
    headers.join(','),
    ...rows.map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(',')),
  ].join('\n')

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${filename}.csv`
  link.click()
  URL.revokeObjectURL(url)
}

/** 将对象数组导出为 CSV */
export function exportObjectsCSV(data: Record<string, any>[], filename: string) {
  if (!data || data.length === 0) return
  const headers = Object.keys(data[0])
  const rows = data.map(item => headers.map(h => String(item[h] ?? '')))
  exportCSV(headers, rows, filename)
}

/** 通用 fetch + 导出 */
export async function fetchAndExport(url: string, filename: string, mapper?: (data: any) => Record<string, any>[]) {
  const request = (await import('@/api/http')).default
  const data = await request.get(url)
  const items = Array.isArray(data?.list) ? data.list : Array.isArray(data) ? data : []
  const mapped = mapper ? items.map(mapper) : items
  exportObjectsCSV(mapped, filename)
}