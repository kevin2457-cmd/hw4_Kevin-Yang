import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { fetchProduct, formatPrice } from '../api'
import { openChat } from '../chatEvents'
import { ChatIcon } from '../components/Icons'
import { ErrorMessage, Loading } from '../components/Status'
import { useAsync } from '../hooks'

const LOW_STOCK = 5

function stockLabel(quantity: number): string {
  if (quantity === 0) return 'Sold out'
  if (quantity <= LOW_STOCK) return `Only ${quantity} left`
  return `${quantity} in stock`
}

function stockLevel(quantity: number): 'out' | 'low' | 'ok' {
  return quantity === 0 ? 'out' : quantity <= LOW_STOCK ? 'low' : 'ok'
}

export default function ProductDetail() {
  const { productId = '' } = useParams()
  const { data: product, error, loading } = useAsync(() => fetchProduct(productId), [productId])
  const [selectedSize, setSelectedSize] = useState<string | null>(null)
  useEffect(() => {
    setSelectedSize(null)
  }, [productId])

  if (loading) return <div className="container section"><Loading /></div>
  if (error || !product) {
    return (
      <div className="container section">
        <ErrorMessage message={error ?? 'Product not found'} />
        <Link to="/products">← Back to products</Link>
      </div>
    )
  }

  const selected = product.inventory.find((i) => i.size === selectedSize)
  const inStock = product.inventory.filter((i) => i.quantity > 0)
  const soldOut = product.inventory.filter((i) => i.quantity === 0)

  return (
    <section className="container section detail-page">
      <nav className="breadcrumb" aria-label="Breadcrumb">
        <Link to="/">Home</Link>
        <span aria-hidden>/</span>
        <Link to="/products">Shop</Link>
        <span aria-hidden>/</span>
        <Link to={`/products?category=${encodeURIComponent(product.category)}`}>{product.category}</Link>
        <span aria-hidden>/</span>
        <span aria-current="page">{product.name}</span>
      </nav>

      <div className="detail">
        <div className="detail-image">
          <img src={product.image_url} alt={product.name} />
        </div>

        <div className="detail-info">
          <span className="product-card-type">{product.garment_type}</span>
          <h1>{product.name}</h1>
          <p className="detail-price">{formatPrice(product.price)}</p>

          {product.colors.length > 0 && (
            <div className="detail-block">
              <h3>Colors</h3>
              <div className="tag-list">
                {product.colors.map((c) => (
                  <span key={c} className="tag">
                    {c}
                  </span>
                ))}
              </div>
            </div>
          )}

          <div className="detail-block">
            <div className="block-head">
              <h3>Size</h3>
              <span className="size-legend">
                <i className="dot ok" /> In stock <i className="dot low" /> Low <i className="dot out" /> Sold out
              </span>
            </div>
            <div className="size-grid" role="group" aria-label="Choose a size">
              {product.inventory.map((i) => (
                <button
                  key={i.size}
                  className={`size-btn ${stockLevel(i.quantity)} ${selectedSize === i.size ? 'active' : ''}`}
                  disabled={i.quantity === 0}
                  onClick={() => setSelectedSize(i.size)}
                  aria-pressed={selectedSize === i.size}
                  aria-label={`Size ${i.size}: ${stockLabel(i.quantity)}`}
                >
                  <span>{i.size}</span>
                  <small>{i.quantity === 0 ? 'Sold out' : i.quantity <= LOW_STOCK ? `${i.quantity} left` : 'In stock'}</small>
                </button>
              ))}
            </div>
            <p className={`stock-message ${selected ? stockLevel(selected.quantity) : ''}`} aria-live="polite">
              {selected
                ? `Size ${selected.size}: ${stockLabel(selected.quantity)}`
                : soldOut.length
                  ? `In stock in ${inStock.map((i) => i.size).join(', ')} · sold out in ${soldOut.map((i) => i.size).join(', ')}`
                  : `All sizes in stock · ${product.total_stock} units available`}
            </p>
          </div>

          <button type="button" className="btn btn-block btn-lg ask-btn" onClick={openChat}>
            <ChatIcon size={18} /> Ask the assistant about this item
          </button>

          <div className="detail-block">
            <h3>Details</h3>
            <p className="detail-desc">{product.description}</p>
          </div>

          <details className="detail-block stock-details">
            <summary>Availability by size</summary>
            <table className="stock-table">
              <tbody>
                {product.inventory.map((i) => (
                  <tr key={i.size}>
                    <td>{i.size}</td>
                    <td className={stockLevel(i.quantity)}>{stockLabel(i.quantity)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </details>
        </div>
      </div>
    </section>
  )
}
