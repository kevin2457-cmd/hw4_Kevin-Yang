import { Link } from 'react-router-dom'
import { openChat } from '../chatEvents'

export default function Footer() {
  return (
    <footer className="footer">
      <div className="container footer-grid">
        <div className="footer-brand">
          <span className="brand-mark" aria-hidden>
            CC
          </span>
          <div>
            <strong>Campus Customs</strong>
            <p>Yale apparel for students, families, and alumni. New Haven, CT.</p>
          </div>
        </div>
        <nav aria-label="Shop">
          <h4>Shop</h4>
          <Link to="/products">All products</Link>
          <Link to="/products?category=Hoodies">Hoodies</Link>
          <Link to="/products?category=Crewnecks">Crewnecks</Link>
          <Link to="/products?category=T-Shirts">T-Shirts</Link>
          <Link to="/products?category=Quarter-Zips">Quarter-Zips</Link>
        </nav>
        <nav aria-label="Account">
          <h4>Account</h4>
          <Link to="/login">Log in</Link>
          <Link to="/create-account">Create account</Link>
          <button type="button" className="link-btn" onClick={openChat}>
            Chat with our assistant
          </button>
        </nav>
        <nav aria-label="Company">
          <h4>Campus Customs</h4>
          <Link to="/about">About us</Link>
        </nav>
      </div>
      <div className="container footer-copy">© {new Date().getFullYear()} Campus Customs · MGT 409 class project storefront</div>
    </footer>
  )
}
