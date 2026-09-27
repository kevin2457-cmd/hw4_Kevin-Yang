import type { ReactNode } from 'react'

/** Two-column layout for Log in / Create account: the form plus a short "why sign in" panel. */
export default function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <section className="container section auth">
      <div className="auth-shell">
        {children}
        <aside className="auth-aside">
          <p className="eyebrow">Your Campus Customs account</p>
          <h2>Pick up where you left off.</h2>
          <ul>
            <li>Your chats with the shopping assistant are saved, including the products it recommended.</li>
            <li>The assistant greets you by name and remembers what you asked about last time.</li>
            <li>Prices and stock are always re-checked live from our catalogue.</li>
          </ul>
        </aside>
      </div>
    </section>
  )
}
