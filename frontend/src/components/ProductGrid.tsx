import type { Product } from '../types'
import ProductCard from './ProductCard'

export default function ProductGrid({ products }: { products: Product[] }) {
  if (products.length === 0) return <p className="muted">No products found.</p>
  return (
    <div className="product-grid">
      {products.map((p) => (
        <ProductCard key={p.product_id} product={p} />
      ))}
    </div>
  )
}
