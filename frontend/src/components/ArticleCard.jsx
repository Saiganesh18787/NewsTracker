import { useState } from 'react'
import { formatDistanceToNow } from 'date-fns'
import { analyzeArticle } from '../api'

const SOURCE_COLORS = {
  'Economic Times': '#f05a28', 'Mint': '#1a56db',
  'BusinessLine':   '#006400', 'MoneyControl': '#cc0000',
  'NDTV':           '#c0392b', 'The Hindu': '#1a1a2e',
  'Indian Express': '#d63031', 'Times of India': '#e74c3c',
  'Hindustan Times':'#0984e3', 'PIB India': '#27ae60',
}

const SIGNAL_CFG = {
  bullish: { label: '▲ Bullish', cls: 'bullish' },
  bearish: { label: '▼ Bearish', cls: 'bearish' },
  neutral: { label: '→ Neutral', cls: 'neutral'  },
}

function timeAgo(iso) {
  try { return formatDistanceToNow(new Date(iso), { addSuffix: true }) }
  catch { return '' }
}

function Spinner() {
  return (
    <svg width="13" height="13" viewBox="0 0 13 13"
      style={{ animation: 'it-spin .9s linear infinite', flexShrink: 0 }}>
      <circle cx="6.5" cy="6.5" r="5" fill="none"
        stroke="currentColor" strokeWidth="2" strokeDasharray="18 12"/>
    </svg>
  )
}

export default function ArticleCard({ article, dark, onSectorClick }) {
  const [state,    setState]    = useState('idle')
  const [analysis, setAnalysis] = useState(null)
  const [open,     setOpen]     = useState(false)

  const pillColor = SOURCE_COLORS[article.source] || '#555'

  async function handleAnalyze(e) {
    e.preventDefault()
    if (state === 'done') { setOpen(o => !o); return }
    setState('loading'); setOpen(true)
    try {
      const d = await analyzeArticle({
        url: article.url, title: article.title,
        summary: article.summary, sectors: article.sectors,
      })
      setAnalysis(d); setState('done')
    } catch(err) {
      setAnalysis({ error: err.message }); setState('error')
    }
  }

  const sig = analysis?.signal ? SIGNAL_CFG[analysis.signal] : null

  return (
    <div className={`it-card ${dark?'dark':''}`}>

      {/* Thumbnail */}
      {article.image && (
        <div className="it-thumb-wrap">
          <img src={article.image} alt="" className="it-thumb"
            onError={e => e.target.closest('.it-thumb-wrap').style.display='none'}/>
        </div>
      )}

      {/* Meta */}
      <div className="it-meta">
        <span className="it-source" style={{ background: pillColor }}>{article.source}</span>
        <span className="it-cat">{article.category}</span>
        <span className="it-time">{timeAgo(article.published)}</span>
      </div>

      {/* Title */}
      <a href={article.url} target="_blank" rel="noopener noreferrer" className="it-title">
        {article.title}
      </a>

      {/* Snippet */}
      {article.summary && <p className="it-snippet">{article.summary}</p>}

      {/* Sector tags */}
      {article.sectors?.length > 0 && (
        <div className="it-sectors">
          {article.sectors.map(s => (
            <button key={s} className="it-sector-tag" onClick={() => onSectorClick(s)}>
              {s}
            </button>
          ))}
        </div>
      )}

      {/* AI Analysis panel */}
      {open && state !== 'idle' && (
        <div className={`it-analysis ${sig ? sig.cls : ''}`}>
          {state === 'loading' ? (
            <div className="it-analysis-loading">
              <Spinner/><span>Analysing sector impact…</span>
            </div>
          ) : state === 'error' ? (
            <div className="it-analysis-err">⚠ {analysis?.error}</div>
          ) : (
            <>
              {/* Header row */}
              <div className="it-analysis-top">
                <span className="it-ai-badge">✦ Sector Impact</span>
                {sig && <span className={`it-signal ${sig.cls}`}>{sig.label}</span>}
              </div>

              {/* Summary */}
              <p className="it-analysis-summary">{analysis.summary}</p>

              {/* Overall reason */}
              {analysis.reason && (
                <p className="it-analysis-reason">💡 {analysis.reason}</p>
              )}

              {/* Per-sector impact cards */}
              {analysis.sector_impact?.length > 0 && (
                <div className="it-sector-impacts">
                  {analysis.sector_impact.map((si, i) => (
                    <div key={i} className={`it-impact-row ${si.impact}`}>
                      <div className="it-impact-top">
                        <button
                          className="it-sector-tag small"
                          onClick={() => onSectorClick(si.sector)}
                        >
                          {si.sector}
                        </button>
                        <span className={`it-impact-badge ${si.impact}`}>
                          {si.impact === 'bullish' ? '▲ Bullish'
                           : si.impact === 'bearish' ? '▼ Bearish'
                           : '→ Neutral'}
                        </span>
                      </div>
                      <p className="it-impact-reason">{si.reason}</p>
                      {si.index && (
                        <span className="it-impact-index">📊 {si.index}</span>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="it-actions">
        <button className="it-btn-analyze" onClick={handleAnalyze}
          disabled={state === 'loading'}>
          {state === 'loading' ? <><Spinner/> Analysing…</> :
           state === 'done'    ? (open ? '▲ Hide' : '▼ Show analysis') :
           '✦ Sector Impact'}
        </button>
        <a href={article.url} target="_blank" rel="noopener noreferrer"
          className="it-btn-read">Read ↗</a>
      </div>
    </div>
  )
}
