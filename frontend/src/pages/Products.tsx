import { useMemo } from 'react'
import { useSearchParams } from 'react-router-dom'
import { fetchProducts } from '../api'
import ProductGrid from '../components/ProductGrid'
import { ErrorMessage, Loading } from '../components/Status'
import { useAsync } from '../hooks'
import type { Product } from '../types'

const SIZES = ['XS', 'S', 'M', 'L', 'XL', 'XXL']
const PRICE_LIMITS = [40, 60, 80, 100]
const SORTS = {
  name: { label: 'Name (A–Z)', compare: (a: Product, b: Product) => a.name.localeCompare(b.name) },
  'price-asc': { label: 'Price: low to high', compare: (a: Product, b: Product) => a.price - b.price || a.name.localeCompare(b.name) },
  'price-desc': { label: 'Price: high to low', compare: (a: Product, b: Product) => b.price - a.price || a.name.localeCompare(b.name) },
} as const
type SortKey = keyof typeof SORTS

/** Text the search box looks through: the same catalogue fields the chat agent searches. */
function searchText(p: Product): string {
  return [p.name, p.garment_type, p.category, p.description, ...p.colors, ...p.search_tags].join(' ').toLowerCase()
}

export default function Products() {
  const { data, error, loading } = useAsync(fetchProducts, [])
  // Filters live in the URL (?q=&category=&size=&max=&sort=) so Back, refresh and shared links keep them.
  const [params, setParams] = useSearchParams()
  const q = params.get('q') ?? ''
  const category = params.get('category') ?? 'All'
  const size = params.get('size') ?? ''
  const maxPrice = Number(params.get('max')) || 0
  const sort: SortKey = (params.get('sort') as SortKey) in SORTS ? (params.get('sort') as SortKey) : 'name'

  function setParam(key: string, value: string) {
    const next = new URLSearchParams(params)
    if (value && value !== 'All') next.set(key, value)
    else next.delete(key)
    setParams(next, { replace: true })
  }

  const categories = useMemo(
    () => ['All', ...[...new Set((data ?? []).map((p) => p.category))].sort()],
    [data],
  )

  const visible = useMemo(() => {
    const words = q.toLowerCase().split(/\s+/).filter(Boolean)
    return (data ?? [])
      .filter((p) => category === 'All' || p.category === category)
      .filter((p) => !size || (p.in_stock_sizes ?? []).includes(size))
      .filter((p) => !maxPrice || p.price <= maxPrice)
      .filter((p) => {
        const text = searchText(p)
        return words.every((w) => text.includes(w))
      })
      .sort(SORTS[sort].compare)
  }, [data, q, category, size, maxPrice, sort])

  const activeFilters = Boolean(q || category !== 'All' || size || maxPrice)

  return (
    <section className="container section">
      <div className="section-head products-head">
        <div>
          <p className="eyebrow eyebrow-dark">Shop</p>
          <h1>{category === 'All' ? 'All products' : category}</h1>
        </div>
        {data && (
          <p className="result-count" aria-live="polite">
            {visible.length} of {data.length} items
          </p>
        )}
      </div>

      {data && (
        <>
          <div className="filter-bar">
            <input
              type="search"
              className="filter-search"
              placeholder="Search by name, color, sport, college…"
              value={q}
              onChange={(e) => setParam('q', e.target.value)}
              aria-label="Search products"
            />
            <label className="filter-select">
              <span>Available in size</span>
              <select value={size} onChange={(e) => setParam('size', e.target.value)}>
                <option value="">Any size</option>
                {SIZES.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </label>
            <label className="filter-select">
              <span>Max price</span>
              <select value={maxPrice || ''} onChange={(e) => setParam('max', e.target.value)}>
                <option value="">Any price</option>
                {PRICE_LIMITS.map((p) => (
                  <option key={p} value={p}>
                    Under ${p}
                  </option>
                ))}
              </select>
            </label>
            <label className="filter-select">
              <span>Sort by</span>
              <select value={sort} onChange={(e) => setParam('sort', e.target.value === 'name' ? '' : e.target.value)}>
                {Object.entries(SORTS).map(([key, s]) => (
                  <option key={key} value={key}>
                    {s.label}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div className="filter-chips" role="group" aria-label="Filter by category">
            {categories.map((c) => (
              <button
                key={c}
                className={`chip ${c === category ? 'active' : ''}`}
                onClick={() => setParam('category', c)}
                aria-pressed={c === category}
              >
                {c}
              </button>
            ))}
            {activeFilters && (
              <button className="chip chip-clear" onClick={() => setParams(sort === 'name' ? {} : { sort }, { replace: true })}>
                Clear filters ×
              </button>
            )}
          </div>
        </>
      )}

      {loading && <Loading />}
      {error && <ErrorMessage message={error} />}
      {data && visible.length === 0 ? (
        <div className="empty-state">
          <p>No products match these filters.</p>
          <button className="btn btn-outline" onClick={() => setParams({}, { replace: true })}>
            Clear all filters
          </button>
        </div>
      ) : (
        data && <ProductGrid products={visible} />
      )}
    </section>
  )
}
