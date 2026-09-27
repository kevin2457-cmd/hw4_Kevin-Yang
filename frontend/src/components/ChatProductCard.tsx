import { Link } from 'react-router-dom'
import { formatPrice } from '../api'
import type { ChatProduct } from '../types'

/** Compact product card shown under an assistant message; opens the normal product page. */
export default function ChatProductCard({ product }: { product: ChatProduct }) {
  const soldOut = product.total_stock === 0
  return (
    <Link to={`/products/${product.product_id}`} className="chat-card" title={`View ${product.name}`}>
      <img src={product.image_url} alt={product.name} loading="lazy" />
      <div className="chat-card-body">
        <span className="chat-card-name">{product.name}</span>
        <span className="chat-card-price">{formatPrice(product.price)}</span>
        {product.colors.length > 0 && <span className="chat-card-meta colors">{product.colors.join(' · ')}</span>}
        <span className={`chat-card-meta ${soldOut ? 'out' : ''}`}>
          {soldOut ? 'Sold out' : `In stock: ${product.in_stock_sizes.join(', ')}`}
        </span>
      </div>
    </Link>
  )
}
