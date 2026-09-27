import { Link } from 'react-router-dom'
import { formatPrice } from '../api'
import type { Product } from '../types'

const SIZE_COUNT = 6
const FEW_SIZES = 3 // show a "limited sizes" badge at or below this many sizes in stock

export default function ProductCard({ product }: { product: Product }) {
  const sizes = product.in_stock_sizes
  // Real stock signal from the DB: flag items that are down to a few sizes.
  const badge =
    sizes && sizes.length === 0 ? 'Sold out' : sizes && sizes.length <= FEW_SIZES ? `Only ${sizes.length} of ${SIZE_COUNT} sizes left` : null

  return (
    <Link to={`/products/${product.product_id}`} className="product-card">
      <div className="product-card-image">
        <img src={product.image_url} alt={product.name} loading="lazy" />
        {badge && <span className="product-badge">{badge}</span>}
      </div>
      <div className="product-card-body">
        <span className="product-card-type">{product.category}</span>
        <h3>{product.name}</h3>
        {product.colors.length > 0 && <span className="product-card-colors">{product.colors.join(' · ')}</span>}
        <span className="product-card-price">{formatPrice(product.price)}</span>
      </div>
    </Link>
  )
}
