import { useEffect, useState, type FormEvent } from 'react'
import { Link, NavLink, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'
import { SearchIcon, UserIcon, MenuIcon, CloseIcon } from './Icons'

const links = [
  { to: '/', label: 'Home', end: true },
  { to: '/products', label: 'Shop All', end: true },
  { to: '/products?category=Hoodies', label: 'Hoodies' },
  { to: '/products?category=Crewnecks', label: 'Crewnecks' },
  { to: '/products?category=T-Shirts', label: 'Tees' },
  { to: '/about', label: 'About Us' },
]

export default function NavBar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [menuOpen, setMenuOpen] = useState(false)
  const [query, setQuery] = useState('')

  // Close the mobile menu after navigating.
  useEffect(() => {
    setMenuOpen(false)
  }, [location.pathname, location.search])

  function handleLogout() {
    logout()
    navigate('/')
  }

  function handleSearch(e: FormEvent) {
    e.preventDefault()
    const q = query.trim()
    navigate(q ? `/products?q=${encodeURIComponent(q)}` : '/products')
    setQuery('')
  }

  // A category link is "active" only when that category filter is on.
  const isActive = (to: string) => {
    const [path, search] = to.split('?')
    if (search) return location.pathname === path && location.search.includes(search)
    if (path === '/products') return location.pathname.startsWith('/products') && !location.search.includes('category=')
    return location.pathname === path
  }

  return (
    <header className="site-header">
      <div className="announce">
        <div className="container announce-inner">
          <span>Yale apparel for students, families &amp; alumni</span>
          <span className="announce-sep" aria-hidden>
            ·
          </span>
          <span>Live stock by size on every product</span>
        </div>
      </div>

      <div className="navbar">
        <div className="container navbar-inner">
          <button
            className="icon-btn menu-toggle"
            onClick={() => setMenuOpen((o) => !o)}
            aria-label={menuOpen ? 'Close menu' : 'Open menu'}
            aria-expanded={menuOpen}
          >
            {menuOpen ? <CloseIcon /> : <MenuIcon />}
          </button>

          <Link to="/" className="brand" aria-label="Campus Customs home">
            <span className="brand-mark" aria-hidden>
              CC
            </span>
            <span className="brand-text">
              Campus Customs
              <small>New Haven · Yale Apparel</small>
            </span>
          </Link>

          <form className="nav-search" role="search" onSubmit={handleSearch}>
            <SearchIcon />
            <input
              type="search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search hoodies, colleges, sports…"
              aria-label="Search products"
            />
          </form>

          <div className="nav-account">
            {user ? (
              <>
                <span className="nav-user" title={user.email}>
                  <UserIcon />
                  <span>Hi, {user.first_name}</span>
                </span>
                <button className="btn btn-small btn-ghost-light" onClick={handleLogout}>
                  Log out
                </button>
              </>
            ) : (
              <>
                <NavLink to="/login" className="nav-login">
                  <UserIcon />
                  <span>Log in</span>
                </NavLink>
                <NavLink to="/create-account" className="btn btn-small btn-light nav-join">
                  Create account
                </NavLink>
              </>
            )}
          </div>
        </div>
      </div>

      <nav className={`subnav ${menuOpen ? 'open' : ''}`} aria-label="Main">
        <div className="container subnav-inner">
          {links.map((l) => (
            <Link key={l.to} to={l.to} className={isActive(l.to) ? 'active' : ''} aria-current={isActive(l.to) ? 'page' : undefined}>
              {l.label}
            </Link>
          ))}
          {!user && (
            <>
              <Link to="/login" className="mobile-only">
                Log in
              </Link>
              <Link to="/create-account" className="mobile-only">
                Create account
              </Link>
            </>
          )}
        </div>
      </nav>
    </header>
  )
}
