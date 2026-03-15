import { useState, useEffect, useCallback } from 'react'
import { fetchNews, fetchCategories, fetchSources, fetchStats } from '../api'

export function useNews() {
  const [articles,   setArticles]   = useState([])
  const [categories, setCategories] = useState(['all'])
  const [sources,    setSources]    = useState(['all'])
  const [stats,      setStats]      = useState(null)
  const [category,   setCategory]   = useState('all')
  const [source,     setSource]     = useState('all')
  const [sector,     setSector]     = useState('')
  const [region,     setRegion]     = useState('all')
  const [query,      setQuery]      = useState('')
  const [loading,    setLoading]    = useState(true)
  const [error,      setError]      = useState(null)
  const [total,      setTotal]      = useState(0)

  useEffect(() => {
    fetchCategories().then(d => setCategories(d.categories)).catch(() => {})
    fetchSources().then(d => setSources(d.sources)).catch(() => {})
    fetchStats().then(setStats).catch(() => {})
  }, [])

  const load = useCallback(async () => {
    setLoading(true); setError(null)
    try {
      const d = await fetchNews({ category, source, sector, region, q: query })
      setArticles(d.articles); setTotal(d.total)
    } catch(e) { setError(e.message) }
    finally { setLoading(false) }
  }, [category, source, sector, region, query])

  useEffect(() => {
    const t = setTimeout(load, query ? 350 : 0)
    return () => clearTimeout(t)
  }, [load, query])

  return {
    articles, categories, sources, stats,
    category, setCategory,
    source,   setSource,
    sector,   setSector,
    region,   setRegion,
    query,    setQuery,
    loading,  error, total,
  }
}