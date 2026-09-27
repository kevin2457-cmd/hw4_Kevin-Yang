import { useEffect, useRef, useState, type FormEvent } from 'react'
import Markdown from 'react-markdown'
import { matchPath, useLocation } from 'react-router-dom'
import { ApiError, fetchChatHistory, fetchProduct, sendChatMessage } from '../api'
import { useAuth } from '../auth'
import { OPEN_CHAT_EVENT } from '../chatEvents'
import ChatProductCard from './ChatProductCard'
import { ChatIcon, CloseIcon, SendIcon } from './Icons'
import type { ChatMessage } from '../types'

// One-click starter questions; product-page ones rely on the current-product context.
const PRODUCT_SUGGESTIONS = ['Is this in stock in M?', 'What colors does this come in?', 'Show me similar items']
const GENERAL_SUGGESTIONS = ['What hoodies do you have?', 'T-shirts under $40 in size M', 'Compare two quarter-zips']

export default function ChatWidget() {
  const { user, token, logout } = useAuth()
  const { pathname } = useLocation()
  // The product page the shopper is on (if any) is sent with each message as context.
  const currentProductId = matchPath('/products/:productId', pathname)?.params.productId ?? null

  const [open, setOpen] = useState(false)
  // Logged in: loaded from / saved to the DB. Guest: kept for this page visit only.
  // The greeting is UI-only and never sent or saved.
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [loadingHistory, setLoadingHistory] = useState(false)
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  // Which account the widget is currently showing; replies that arrive after a
  // login/logout switch are dropped so they never land in another user's chat.
  const sessionRef = useRef<number | null>(null)

  const greeting = user
    ? `Hi ${user.first_name}! I’m the Campus Customs assistant. Ask me what we carry or for help finding Yale gear.`
    : 'Hi! I’m the Campus Customs assistant. Ask me what we carry or for help finding Yale gear.'

  // Whenever the logged-in user changes: clear the widget, then load that user's saved chat.
  useEffect(() => {
    sessionRef.current = user?.id ?? null
    setMessages([])
    setError(null)
    if (!user || !token) return
    let cancelled = false
    setLoadingHistory(true)
    fetchChatHistory(token)
      .then((saved) => !cancelled && setMessages(saved))
      .catch((err: Error) => !cancelled && setError(`Couldn't load your saved chat: ${err.message}`))
      .finally(() => !cancelled && setLoadingHistory(false))
    return () => {
      cancelled = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user?.id])

  const lastTurnRef = useRef<HTMLDivElement>(null)

  // New assistant reply: scroll to its top so the text is read before the cards.
  // Anything else (user message, typing dots, error): scroll to the bottom.
  useEffect(() => {
    const last = messages[messages.length - 1]
    if (last?.role === 'assistant' && !sending && !error) {
      lastTurnRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    } else {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages, sending, error, open])

  useEffect(() => {
    if (open && !sending) inputRef.current?.focus()
  }, [open, sending])

  // Name of the product page that is open, shown as a "Viewing: …" chip so the shopper can
  // see what "this" refers to. Looked up from the DB via the product API.
  const [currentProductName, setCurrentProductName] = useState<string | null>(null)
  useEffect(() => {
    setCurrentProductName(null)
    if (!currentProductId) return
    let cancelled = false
    fetchProduct(currentProductId)
      .then((p) => !cancelled && setCurrentProductName(p.name))
      .catch(() => {})
    return () => {
      cancelled = true
    }
  }, [currentProductId])

  // "Ask about this item" on a product page opens the chat.
  useEffect(() => {
    const openChat = () => setOpen(true)
    window.addEventListener(OPEN_CHAT_EVENT, openChat)
    return () => window.removeEventListener(OPEN_CHAT_EVENT, openChat)
  }, [])

  const suggestions = currentProductId ? PRODUCT_SUGGESTIONS : GENERAL_SUGGESTIONS

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    void send(input)
  }

  async function send(raw: string) {
    const text = raw.trim()
    if (!text || sending) return // blocks duplicate sends while a reply is pending

    const history = messages
    const session = sessionRef.current
    setMessages([...history, { role: 'user', content: text }])
    setInput('')
    setError(null)
    setSending(true)
    try {
      const { reply, products } = await sendChatMessage(text, history, { token: user ? token : null, currentProductId })
      if (sessionRef.current !== session) return
      setMessages((m) => [...m, { role: 'assistant', content: reply, products }])
    } catch (err) {
      if (sessionRef.current !== session) return
      // Roll back the unanswered message and put it back in the box so the shopper can retry.
      setMessages(history)
      setInput(text)
      if (err instanceof ApiError && err.status === 401) logout() // token expired
      setError((err as Error).message)
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="chat-root">
      {open && (
        <section className="chat-panel" aria-label="Campus Customs chat">
          <header className="chat-header">
            <span className="chat-avatar" aria-hidden>
              CC
            </span>
            <div className="chat-title">
              <strong>Campus Customs Assistant</strong>
              <small>
                <i className="online-dot" aria-hidden /> {user ? 'Chat saved to your account' : 'Log in to save this chat'}
              </small>
            </div>
            <button className="chat-close" onClick={() => setOpen(false)} aria-label="Close chat">
              <CloseIcon size={20} />
            </button>
          </header>
          <div className="chat-messages" aria-live="polite">
            <div className="chat-bubble assistant">{greeting}</div>
            {loadingHistory && <div className="chat-bubble assistant muted">Loading your saved chat…</div>}
            {messages.map((m, i) => (
              <div key={i} className={`chat-turn ${m.role}`} ref={i === messages.length - 1 ? lastTurnRef : undefined}>
                <div className={`chat-bubble ${m.role}`}>
                  {m.role === 'assistant' ? <Markdown>{m.content}</Markdown> : m.content}
                </div>
                {m.products && m.products.length > 0 && (
                  <div className="chat-cards" aria-label="Recommended products">
                    {m.products.map((p) => (
                      <ChatProductCard key={p.product_id} product={p} />
                    ))}
                  </div>
                )}
              </div>
            ))}
            {sending && (
              <div className="chat-bubble assistant typing" aria-label="Assistant is typing">
                <span />
                <span />
                <span />
              </div>
            )}
            {error && (
              <div className="chat-error" role="alert">
                {error}
              </div>
            )}
            <div ref={bottomRef} />
          </div>
          {currentProductName && (
            <div className="chat-context" title="Questions about “this” refer to this product">
              Viewing: <strong>{currentProductName}</strong>
            </div>
          )}
          {!sending && (
            <div className="chat-suggestions" aria-label="Suggested questions">
              {suggestions.map((s) => (
                <button key={s} type="button" className="chat-suggestion" onClick={() => void send(s)}>
                  {s}
                </button>
              ))}
            </div>
          )}
          <form className="chat-input" onSubmit={handleSubmit}>
            <input
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={sending ? 'Waiting for reply…' : 'Type a message…'}
              aria-label="Chat message"
              maxLength={2000}
              disabled={sending}
            />
            <button type="submit" className="chat-send" disabled={!input.trim() || sending} aria-label="Send message">
              <SendIcon />
            </button>
          </form>
        </section>
      )}
      <button
        className={`chat-toggle ${open ? 'is-open' : ''}`}
        onClick={() => setOpen((o) => !o)}
        aria-label={open ? 'Close chat' : 'Open chat with the shopping assistant'}
        aria-expanded={open}
      >
        {open ? (
          <CloseIcon />
        ) : (
          <>
            <ChatIcon /> <span>Ask us</span>
          </>
        )}
      </button>
    </div>
  )
}
