import { useState, useEffect } from 'react'
import { fetchTrendingSectors } from '../api'

export default function SectorPanel({ dark, activeSector, onSectorClick }) {
  const [sectors, setSectors] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchTrendingSectors()
      .then(d => { setSectors(d.trending); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  return (
    <aside className={`sp-panel ${dark?'dark':''}`}>
      <div className="sp-header">
        <span className="sp-title">Sectors in News</span>
        {activeSector && (
          <button className="sp-clear" onClick={() => onSectorClick('')}>
            Clear ✕
          </button>
        )}
      </div>

      {loading ? (
        <div className="sp-loading">Loading…</div>
      ) : (
        <div className="sp-list">
          {sectors.map(s => (
            <div
              key={s.name}
              className={`sp-row ${activeSector === s.name ? 'active' : ''}`}
              onClick={() => onSectorClick(s.name === activeSector ? '' : s.name)}
              style={activeSector === s.name ? { borderLeft: `3px solid ${s.color}` } : {}}
            >
              <div className="sp-left">
                <span className="sp-icon">{s.icon}</span>
                <div>
                  <div className="sp-name">{s.name}</div>
                  <div className="sp-index">{s.index}</div>
                </div>
              </div>
              <span className="sp-count" style={{ background: s.color + '22', color: s.color }}>
                {s.count}
              </span>
            </div>
          ))}
        </div>
      )}

      <div className="sp-footer">
        Click a sector to filter news
      </div>
    </aside>
  )
}
