import { useState, useEffect } from 'react'
import { fetchTrendingSectors } from '../api'

export default function TrendingSectors({ dark, activeSector, onSectorClick }) {
  const [trending, setTrending] = useState([])
  const [loading,  setLoading]  = useState(true)

  useEffect(() => {
    fetchTrendingSectors()
      .then(d => { setTrending(d.trending); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  if (loading) return (
    <div className={`ts-wrap ${dark?'dark':''}`}>
      <span className="ts-label">Trending Sectors</span>
      <span className="ts-loading">Loading…</span>
    </div>
  )

  return (
    <div className={`ts-wrap ${dark?'dark':''}`}>
      <span className="ts-label">🔥 Trending Sectors</span>
      <div className="ts-pills">
        {trending.map(s => (
          <button
            key={s.name}
            className={`ts-pill ${activeSector === s.name ? 'active' : ''}`}
            style={activeSector === s.name ? { background: s.color, borderColor: s.color } : {}}
            onClick={() => onSectorClick(s.name === activeSector ? '' : s.name)}
            title={s.index}
          >
            <span className="ts-pill-icon">{s.icon}</span>
            <span className="ts-pill-name">{s.name}</span>
            <span className="ts-pill-count">{s.count}</span>
          </button>
        ))}
      </div>
    </div>
  )
}
