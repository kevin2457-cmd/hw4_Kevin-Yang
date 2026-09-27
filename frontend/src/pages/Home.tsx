import { Link } from 'react-router-dom'
import { fetchProducts } from '../api'
import { useAuth } from '../auth'
import { openChat } from '../chatEvents'
import { ArrowIcon, ChatIcon } from '../components/Icons'
import ProductGrid from '../components/ProductGrid'
import { ErrorMessage, Loading } from '../components/Status'
import { useAsync } from '../hooks'
import type { Product } from '../types'

// Categories shown as tiles, in shop order. Counts and images come from the loaded catalogue.
const CATEGORY_ORDER = ['Hoodies', 'Crewnecks', 'T-Shirts', 'Quarter-Zips', 'Jackets', 'Long Sleeves']
// Real catalogue products used for the hero collage.
const HERO_IDS = ['basic-hoodie-big-yale', 'district-vit-crewneck-vintage-bulldog', '2025-yale-vs-harvard-t-shirt']

/** Pick a varied preview: the first products of each category, round-robin. */
function featured(products: Product[], count: number): Product[] {
  const byCategory = new Map<string, Product[]>()
  for (const p of products) byCategory.set(p.category, [...(byCategory.get(p.category) ?? []), p])
  const groups = [...byCategory.values()]
  const picks: Product[] = []
  for (let i = 0; picks.length < count && groups.some((g) => g[i]); i++) {
    for (const g of groups) if (g[i] && picks.length < count) picks.push(g[i])
  }
  return picks
}

export default function Home() {
  const { data, error, loading } = useAsync(fetchProducts, [])
  const { user } = useAuth()

  const heroProducts = HERO_IDS.map((id) => data?.find((p) => p.product_id === id)).filter(Boolean) as Product[]
  const categories = CATEGORY_ORDER.map((name) => {
    const items = (data ?? []).filter((p) => p.category === name)
    return { name, count: items.length, image: items[0] }
  }).filter((c) => c.count > 0)
  const minPrice = data?.length ? Math.min(...data.map((p) => p.price)) : null

  return (
    <>
      <section className="hero">
        <div className="container hero-grid">
          <div className="hero-copy">
            <p className="eyebrow">Campus Customs · New Haven</p>
            <h1>
              Bulldog blue,
              <br />
              <em>made for every day</em> on campus.
            </h1>
            <p className="hero-sub">
              Hoodies, crewnecks, tees and quarter-zips for Yale students, families and alumni: residential college
              crests, varsity sports, and game-day classics.
            </p>
            <div className="hero-actions">
              <Link to="/products" className="btn btn-light btn-lg">
                Shop all products <ArrowIcon />
              </Link>
              <button type="button" className="btn btn-outline-light btn-lg" onClick={openChat}>
                <ChatIcon size={18} /> Ask our assistant
              </button>
            </div>
            {data && (
              <ul className="hero-stats" aria-label="Store at a glance">
                <li>
                  <strong>{data.length}</strong> styles
                </li>
                <li>
                  <strong>{categories.length}</strong> categories
                </li>
                {minPrice !== null && (
                  <li>
                    from <strong>${minPrice.toFixed(0)}</strong>
                  </li>
                )}
              </ul>
            )}
          </div>
          <div className="hero-collage">
            {heroProducts.map((p, i) => (
              <Link key={p.product_id} to={`/products/${p.product_id}`} className={`collage-item collage-${i}`}>
                <img src={p.image_url} alt={p.name} />
                <span className="collage-tag">
                  <span>{p.name}</span> <b>${p.price.toFixed(0)}</b>
                </span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {categories.length > 0 && (
        <section className="container section">
          <div className="section-head">
            <div>
              <p className="eyebrow eyebrow-dark">Shop by category</p>
              <h2>Find your fit</h2>
            </div>
          </div>
          <div className="category-grid">
            {categories.map((c) => (
              <Link key={c.name} to={`/products?category=${encodeURIComponent(c.name)}`} className="category-tile">
                {c.image && <img src={c.image.image_url} alt="" loading="lazy" />}
                <span className="category-name">{c.name}</span>
                <span className="category-count">{c.count} styles</span>
              </Link>
            ))}
          </div>
        </section>
      )}

      <section className="container section">
        <div className="section-head">
          <div>
            <p className="eyebrow eyebrow-dark">Featured</p>
            <h2>Campus favorites</h2>
          </div>
          <Link to="/products" className="section-link">
            View all <ArrowIcon />
          </Link>
        </div>
        {loading && <Loading />}
        {error && <ErrorMessage message={error} />}
        {data && <ProductGrid products={featured(data, 8)} />}
      </section>

      <section className="container section">
        <div className="assistant-band">
          <div className="assistant-band-icon" aria-hidden>
            <ChatIcon size={28} />
          </div>
          <div className="assistant-band-copy">
            <h2>Not sure what to get?</h2>
            <p>
              Our shopping assistant checks real prices and live stock by size. Try “hoodies under $50 in XL” or
              “compare two quarter-zips”.
            </p>
          </div>
          <button type="button" className="btn btn-lg" onClick={openChat}>
            Start a chat
          </button>
        </div>
      </section>

      {!user && (
        <section className="container section">
          <div className="account-cta">
            <div>
              <h2>Join Campus Customs</h2>
              <p>Create an account and your chats with the assistant are saved for next time.</p>
            </div>
            <div className="hero-actions">
              <Link to="/create-account" className="btn">
                Create account
              </Link>
              <Link to="/login" className="btn btn-outline">
                Log in
              </Link>
            </div>
          </div>
        </section>
      )}
    </>
  )
}
