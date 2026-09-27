export interface SizeStock {
  size: string
  quantity: number
}

export interface Product {
  product_id: string
  name: string
  garment_type: string
  category: string
  description: string
  colors: string[]
  search_tags: string[]
  image_url: string
  price: number
  total_stock: number
  /** Sizes with quantity > 0 (only on the product list endpoint). */
  in_stock_sizes?: string[]
}

export interface ProductDetail extends Product {
  inventory: SizeStock[]
}

export interface User {
  id: number
  first_name: string
  last_name: string
  name: string
  email: string
}

export interface AuthResponse {
  token: string
  user: User
}

/** A product card returned by /api/chat; every value comes from the database. */
export interface ChatProduct {
  product_id: string
  name: string
  garment_type: string
  category: string
  price: number
  image_url: string
  colors: string[]
  total_stock: number
  in_stock_sizes: string[]
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  products?: ChatProduct[]
}
