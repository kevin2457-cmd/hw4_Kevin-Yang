# Design

## Overall Direction

Campus Customs should look like a real campus apparel shop, not a template: **Yale blue, clean white, and warm "paper" neutrals**, a traditional serif for headings (a nod to Yale's own typography), and a plain modern sans-serif for everything you read or click. The product photos do the selling, so the layout keeps them large, evenly framed and uncluttered. Motion is limited to small hover and entrance effects, and it's turned off for people who prefer reduced motion.

**Why it helps customers stick around and buy:** a site that looks like a trustworthy store makes people more willing to browse and purchase. Clear hierarchy (category → name → price → sizes) gets shoppers to "is it available in my size and budget?" in seconds. The assistant is promoted throughout the site, which turns hesitation into a conversation instead of a bounce.

## Visual System

All design tokens are CSS custom properties at the top of `frontend/src/index.css`, so every page shares one system.

- **Typography:** *Libre Caslon Text* (serif) for h1/h2, the logo wordmark, hero stats and category names. It feels collegiate and traditional, like printed college signage. *Inter* for body text, navigation, forms, prices and chat, for legibility at small sizes. Small uppercase, letter-spaced "eyebrow" labels (e.g. `SHOP BY CATEGORY`) sit above section headings. Heading sizes use `clamp()` so they scale smoothly between phone and desktop. Both fonts load from Google Fonts with Georgia / system-font fallbacks.
- **Color:** Yale blue `#00356b` is the brand and primary-action color (header, hero, buttons, prices). A darker navy `#00223f` is used for the announcement bar, footer and button hover. A lighter accent blue `#286dc0` is used for links, eyebrows and focus rings. Warm neutrals (`--paper #f7f5f0`, `--line #e2ded5`) are used for image frames, tiles and borders, which is softer than gray and reads as "shop," not "dashboard." Stock status has its own semantic colors used everywhere: green = in stock, amber = low (≤ 5), red / hatched = sold out. There is no decorative gradient. The hero only has a very faint vertical pinstripe texture.
- **Spacing:** a consistent rhythm (sections 3rem, card gaps 1.25–1.5rem, form gaps 1rem), a 1200px max-width container, and 12px / 18px corner radii.
- **Buttons:** pill-shaped. Solid Yale blue for primary actions, outlined for secondary, and white / outline-white variants on blue backgrounds. Each has a clear hover color, a 1px press effect, a gray disabled state with a not-allowed cursor, and a visible 3px focus ring for keyboard users.
- **Cards:** product photos sit in a 4:5 frame on the paper color with a thin border, so the mixed photo backgrounds (white, black, gray) look like one consistent grid. Below the photo: category eyebrow, product name, colors, and a bold blue price. Hover gently zooms the photo, adds a shadow and underlines the name. A small amber badge ("Only 2 of 6 sizes left") appears only when an item is down to 3 or fewer sizes in stock, based on real inventory.

## Page Improvements

- **Header (all pages):** a three-layer header in the style of real stores. (1) A navy announcement bar with two true statements ("Yale apparel for students, families & alumni · Live stock by size on every product"). (2) The blue main bar with a circular "CC" crest + serif wordmark, a **site-wide search box** (it submits to `/products?q=…` and fills the Products search), and the account area ("Log in" / "Create account", or "Hi, Name" / "Log out"). (3) A white category bar: Home, Shop All, Hoodies, Crewnecks, Tees, About Us. The active link has a blue underline, and category links highlight when that filter is on. The header is sticky.
- **Home:** a split hero with a large serif headline ("Bulldog blue, *made for every day* on campus."), two clear CTAs ("Shop all products" and "Ask our assistant"), live store stats computed from the catalogue (102 styles · 6 categories · from $32), and a collage of three **real products** (Basic Hoodie Big Yale $68, District Vit Crewneck Vintage Bulldog $58, 2025 Yale vs Harvard T-Shirt $32) that link to their pages. Below it: **Shop by category** tiles with a real product photo and real style count for each category, the **Campus favorites** grid, an **assistant band** with example prompts that opens the chat, and a "Join Campus Customs" panel for guests.
- **Products:** a page header with an eyebrow and a title that changes with the category ("Hoodies"), plus a live "N of 102 items" count. The Problem 9 filter bar (search, size, max price, sort) and category chips are restyled but work the same. Responsive auto-fill grid with the new cards. Empty state in a soft panel.
- **Product Detail:** breadcrumb (Home / Shop / Hoodies / *Product*). A large framed photo that stays in view (sticky) while you scroll the info column. The info column has the garment-type eyebrow, a serif name, a large price and color chips. The **size picker** has a legend (in stock / low / sold out): available sizes show "In stock" or "3 left" in amber, and sold-out sizes are **disabled, hatched, dashed and struck through**. A live status line reads "In stock in S, M, L, XXL · sold out in XS, XL" and updates when you pick a size ("Size S: 25 in stock"). Then a full-width "Ask the assistant about this item" button, the description under "Details", and the per-size table folded into an "Availability by size" disclosure so it doesn't crowd the page.
- **Login / Create Account:** a two-panel card. The form is on the left. A blue panel on the right explains why to sign in (saved chats, being greeted by name, live prices), which gives a reason to create an account. Inputs share one style: 1.5px border, 10px radius, and a blue focus ring. Validation errors appear in a red left-bordered box. Buttons are full-width, and the auth logic is unchanged.
- **About:** a blue page hero with a serif headline, then three numbered cards (01 What we carry / 02 Who we're for / 03 How we help) and CTAs to shop or chat. The outdated "will soon be able to answer" text was corrected.
- **Chat:** the launcher is now a labeled pill (chat icon + "Ask us") with a white ring and shadow, so it's findable without being loud. It turns into a × when open. The panel opens with a short fade/rise. The header has a "CC" avatar, a green status dot and "Chat saved to your account" / "Log in to save this chat". Shopper bubbles are solid Yale blue on the right, and assistant bubbles are white cards on the left, both on a paper background. Product cards in chat have a photo thumbnail, name, bold price, colors and in-stock sizes, and nudge on hover. The typing indicator uses animated dots. The "Viewing: product" bar and suggestion chips (Problem 9) are styled to match. The input is a pill with a focus ring, and the round send button shows an icon and is grayed out when disabled. Scrolling stays inside the panel (`overscroll-behavior: contain`), and a new reply scrolls to its first line.
- **Footer:** navy, with a four-column layout (brand; Shop links to each category; Account links plus "Chat with our assistant"; About).

## Responsive Design

- **≤ 1024px:** category tiles go to 3 columns and the hero collage shrinks.
- **≤ 860px:** the header wraps. The search box moves to its own full-width row, the category bar collapses behind a **hamburger menu** (it closes automatically after you navigate), the account area becomes icons, and the announcement bar shows one message. The hero, product detail, About cards, auth panel and footer stack into one column. The product photo stops being sticky.
- **≤ 560px (phones):** the product grid is 2 columns, category tiles 2 columns, the size picker 3 columns, and filter dropdowns pair up two per row. "Log in / Create account" move into the hamburger menu so the top bar fits on one line. The **chat becomes a full-screen sheet** (100vw × 100dvh), with the launcher hidden while it's open and the header × to close it.
- Tested in the preview at 1280px, 375px (mobile preset) and a 250px pane: `scrollWidth − innerWidth = 0` on Home, Products, Product Detail, Log in, Create Account and About at 375px and at 250px, so there is no horizontal overflow. Grid columns use `minmax(0, 1fr)` and flex items use `min-width: 0` so long names ellipsize instead of pushing the layout.
- **Accessibility:** a global `:focus-visible` ring; `aria-current` on the active nav link and breadcrumb; `aria-pressed` and full labels on size buttons ("Size XL: Sold out"); `aria-expanded` on the menu and chat toggles; `aria-live` on the result count, stock line and chat; icon-only buttons have `aria-label`s; muted text colors were darkened for contrast; `prefers-reduced-motion` turns off all animation.

## Files Changed

- `frontend/index.html`: Google Fonts (Libre Caslon Text + Inter), meta description, theme color
- `frontend/src/index.css`: complete rewrite into a token-based design system and responsive rules
- `frontend/src/components/NavBar.tsx`: announcement bar, header search, category bar, mobile menu
- `frontend/src/components/Icons.tsx` (new): inline SVG icons (search, user, menu, close, chat, send, arrow)
- `frontend/src/components/Footer.tsx`: multi-column footer
- `frontend/src/components/ProductCard.tsx`: new card layout + limited-sizes badge from real stock
- `frontend/src/components/AuthLayout.tsx` (new): two-panel auth layout
- `frontend/src/components/ChatWidget.tsx`: launcher, avatar header, status line, icon send button (logic unchanged)
- `frontend/src/pages/Home.tsx`: hero with real-product collage and live stats, category tiles, assistant band
- `frontend/src/pages/Products.tsx`: page header / title per category
- `frontend/src/pages/ProductDetail.tsx`: breadcrumb, size legend, stock status line, availability disclosure
- `frontend/src/pages/About.tsx`: page hero + numbered cards
- `frontend/src/pages/Login.tsx`, `frontend/src/pages/CreateAccount.tsx`: wrapped in `AuthLayout` (form logic unchanged)

**Verified after the redesign:** catalogue (102 products), header search (`saybrook` → 3), category links (Hoodies → 27), filters/sort, product detail with real prices and sold-out sizes (Champion Reverse Weave Hoodie 1: XS & XL disabled), wrong-password error and login, logout, chat with DB-backed answers and product cards, saved history restored (8 messages, 8 cards for the test user), current-product context ("Viewing: Basic Hoodie Big Yale" → "comes in navy blue and white"), and the suggestion chips and "Ask about this item" button.
