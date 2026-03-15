const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const get  = p => fetch(BASE+p).then(r => { if(!r.ok) throw new Error(`API ${r.status}`); return r.json() })

export const fetchNews           = ({category='all',source='all',sector='',q='',limit=60}={}) => {
  const p = new URLSearchParams({category,source,limit})
  if(sector) p.set('sector', sector)
  if(q)      p.set('q', q)
  return get(`/api/news?${p}`)
}
export const fetchCategories     = () => get('/api/categories')
export const fetchSources        = () => get('/api/sources')
export const fetchSectors        = () => get('/api/sectors')
export const fetchTrendingSectors= () => get('/api/sectors/trending')
export const fetchStats          = () => get('/api/stats')

export const analyzeArticle = payload =>
  fetch(`${BASE}/api/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }).then(async r => {
    if (!r.ok) { const e = await r.json().catch(()=>({})); throw new Error(e.detail || `API ${r.status}`) }
    return r.json()
  })
