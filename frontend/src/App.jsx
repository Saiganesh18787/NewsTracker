import { useState } from 'react'
import { useNews } from './hooks/useNews'
import ArticleCard from './components/ArticleCard'
import TrendingSectors from './components/TrendingSectors'
import SectorPanel from './components/SectorPanel'

const CAT_ICONS = {
  all:'⚡', top:'🔥', national:'🇮🇳', policy:'📜',
  markets:'📈', business:'💼', economy:'🏛', technology:'💻',
  startups:'🚀', commodities:'🪙',
  world:'🌍', 'global-markets':'💹', 'global-tech':'🖥',
  geopolitics:'🗺', science:'🔬',
}

const INDIA_CATS   = ['top','national','policy','markets','business','economy','technology','startups','commodities']
const INTL_CATS    = ['world','global-markets','global-tech','geopolitics','science']

export default function App() {
  const [dark, setDark]           = useState(false)
  const [regionTab, setRegionTab] = useState('all') // all | india | international

  const {
    articles, categories, sources, stats,
    category, setCategory, source, setSource,
    sector, setSector, query, setQuery,
    loading, error, total,
  } = useNews()

  function handleSectorClick(name) {
    setSector(s => s === name ? '' : name)
    setCategory('all')
  }

  // Filter categories based on region tab
  const visibleCats = regionTab === 'all'
    ? ['all', ...INDIA_CATS, ...INTL_CATS].filter(c => c === 'all' || categories.includes(c))
    : regionTab === 'india'
    ? ['all', ...INDIA_CATS].filter(c => c === 'all' || categories.includes(c))
    : ['all', ...INTL_CATS].filter(c => c === 'all' || categories.includes(c))

  return (
    <div className={`it-root ${dark?'dark':''}`}>

      {/* ── HEADER ── */}
      <header className="it-header">
        <div className="it-header-inner">
          <div className="it-logo">
            <div className="it-logo-flag">🇮🇳</div>
            <div>
              <div className="it-logo-name">IndiaTrack</div>
              <div className="it-logo-tag">News · Sectors · Market Impact</div>
            </div>
          </div>

          <div className="it-search-wrap">
            <span className="it-search-icon">🔍</span>
            <input className="it-search" type="search"
              placeholder="Search news, sectors, policies…"
              value={query} onChange={e => setQuery(e.target.value)}/>
            {query && (
              <button className="it-search-clear" onClick={() => setQuery('')}>✕</button>
            )}
          </div>

          <div className="it-controls">
            {sector && (
              <div className="it-active-filter">
                <span>Sector: <strong>{sector}</strong></span>
                <button onClick={() => setSector('')}>✕</button>
              </div>
            )}
            <select className="it-select" value={source}
              onChange={e => setSource(e.target.value)}>
              {sources.map(s => (
                <option key={s} value={s}>{s === 'all' ? 'All Sources' : s}</option>
              ))}
            </select>
            <button className="it-dark-btn" onClick={() => setDark(d => !d)}>
              {dark ? '☀️' : '🌙'}
            </button>
          </div>
        </div>

        {/* ── REGION TABS ── */}
        <div className="it-region-tabs">
          {[
            { key: 'all',           label: '⚡ All News' },
            { key: 'india',         label: '🇮🇳 India' },
            { key: 'international', label: '🌍 International' },
          ].map(r => (
            <button
              key={r.key}
              className={`it-region-tab ${regionTab === r.key ? 'active' : ''}`}
              onClick={() => { setRegionTab(r.key); setCategory('all'); setSector('') }}
            >
              {r.label}
            </button>
          ))}
          {stats && (
            <div className="it-region-counts">
              <span>🇮🇳 {stats.india || 0}</span>
              <span>🌍 {stats.international || 0}</span>
            </div>
          )}
        </div>

        {/* ── CATEGORY TABS ── */}
        <div className="it-tabs-wrap">
          <div className="it-tabs">
            {visibleCats.map(cat => (
              <button key={cat}
                className={`it-tab ${category === cat ? 'active' : ''}`}
                onClick={() => { setCategory(cat); setSector('') }}>
                {CAT_ICONS[cat] || '📌'} {cat === 'all' ? 'All' : cat.charAt(0).toUpperCase() + cat.slice(1).replace('-', ' ')}
              </button>
            ))}
          </div>
        </div>
      </header>

      {/* ── TRENDING SECTORS ── */}
      <TrendingSectors dark={dark} activeSector={sector} onSectorClick={handleSectorClick}/>

      {/* ── DISCLAIMER ── */}
      <div className={`it-disclaimer ${dark?'dark':''}`}>
        ⚠️ Sector tags are auto-generated for informational purposes only. This is not SEBI-registered investment advice.
      </div>

      {/* ── BODY ── */}
      <div className="it-body">
        <main className="it-main">

          {stats && !loading && (
            <div className="it-stats">
              <span>📰 <strong>{total}</strong> stories
                {regionTab === 'india' ? ' · 🇮🇳 India' :
                 regionTab === 'international' ? ' · 🌍 International' : ''}
                {sector ? ` in ${sector}` : ''}
              </span>
              <span>🏷 Top sector: <strong>{stats.top_sectors?.[0]?.[0] || '—'}</strong></span>
              <span>📡 <strong>{Object.keys(stats.by_source||{}).length}</strong> sources</span>
            </div>
          )}

          {error && (
            <div className="it-error">
              <strong>⚠ Cannot connect to backend</strong>
              <p>Make sure FastAPI is running on <code>http://localhost:8000</code></p>
            </div>
          )}

          {loading && !articles.length && (
            <div className="it-grid">
              {Array.from({ length: 9 }).map((_, i) => (
                <div key={i} className="it-skeleton"/>
              ))}
            </div>
          )}

          {!loading && !error && articles.length === 0 && (
            <div className="it-empty">
              <div style={{ fontSize: 52 }}>🔍</div>
              <p>No articles found{query ? ` for "${query}"` : ''}{sector ? ` in ${sector}` : ''}</p>
            </div>
          )}

          {articles.length > 0 && (
            <div className="it-grid">
              {articles.map(a => (
                <ArticleCard key={a.id || a.url} article={a} dark={dark}
                  onSectorClick={handleSectorClick}/>
              ))}
            </div>
          )}
        </main>

        <SectorPanel dark={dark} activeSector={sector} onSectorClick={handleSectorClick}/>
      </div>

      <footer className="it-footer">
        IndiaTrack · India & International news · Sector tags are indicative only · Not SEBI registered · Not financial advice
      </footer>
    </div>
  )
}