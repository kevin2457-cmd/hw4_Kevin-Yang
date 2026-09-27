import type { AuthResponse, ChatMessage, ChatProduct, Product, ProductDetail, User } from './types'

/** An HTTP error from the backend; `status` lets callers react to e.g. 401 (logged out). */
export class ApiError extends Error {
  status: number
  constructor(message: string, status: number) {
    super(message)
    this.status = status
  }
}

// Requests go to /api/... and Vite proxies them to FastAPI on port 8000.
async function getJson<T>(url: string, init?: RequestInit): Promise<T> {
  let res: Response
  try {
    res = await fetch(url, init)
  } catch {
    throw new Error('Could not reach the server. Is the backend running?')
  }
  if (!res.ok) {
    // FastAPI errors look like {"detail": "..."}; show that message to the user.
    const body = await res.json().catch(() => null)
    const fallback =
      res.status >= 500
        ? 'The Campus Customs server is unavailable right now. Please try again in a moment.'
        : `Request failed (${res.status})`
    const detail = typeof body?.detail === 'string' ? body.detail : fallback
    throw new ApiError(detail, res.status)
  }
  return res.json() as Promise<T>
}

function postJson<T>(url: string, body: unknown, token?: string | null): Promise<T> {
  return getJson<T>(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeader(token) },
    body: JSON.stringify(body),
  })
}

function authHeader(token?: string | null): Record<string, string> {
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export interface RegisterInput {
  first_name: string
  last_name: string
  email: string
  password: string
}

export function registerUser(input: RegisterInput): Promise<AuthResponse> {
  return postJson<AuthResponse>('/api/auth/register', input)
}

export function loginUser(email: string, password: string): Promise<AuthResponse> {
  return postJson<AuthResponse>('/api/auth/login', { email, password })
}

export function fetchMe(token: string): Promise<User> {
  return getJson<User>('/api/auth/me', { headers: authHeader(token) })
}

export function fetchProducts(): Promise<Product[]> {
  return getJson<Product[]>('/api/products')
}

export function fetchProduct(productId: string): Promise<ProductDetail> {
  return getJson<ProductDetail>(`/api/products/${encodeURIComponent(productId)}`)
}

export interface ChatReply {
  reply: string
  tools_used: string[]
  products: ChatProduct[]
  saved: boolean
}

interface ChatContext {
  /** Login token; when present the backend identifies the user and saves the chat. */
  token?: string | null
  /** product_id of the product page currently open, if any. */
  currentProductId?: string | null
}

/** Send a message to the agent. Guests also send the in-browser history (ids only for
 *  cards); for logged-in users the backend reads the saved history from the DB instead. */
export function sendChatMessage(message: string, history: ChatMessage[], ctx: ChatContext = {}): Promise<ChatReply> {
  const turns = ctx.token
    ? []
    : history.map((m) => ({
        role: m.role,
        content: m.content,
        product_ids: (m.products ?? []).map((p) => p.product_id),
      }))
  return postJson<ChatReply>(
    '/api/chat',
    { message, history: turns, current_product_id: ctx.currentProductId ?? null },
    ctx.token,
  )
}

/** The logged-in user's saved chat, oldest first, with product cards restored. */
export async function fetchChatHistory(token: string): Promise<ChatMessage[]> {
  const data = await getJson<{ messages: ChatMessage[] }>('/api/chat/history', { headers: authHeader(token) })
  return data.messages.map((m) => ({ role: m.role, content: m.content, products: m.products }))
}

export function formatPrice(price: number): string {
  return `$${price.toFixed(2)}`
}
