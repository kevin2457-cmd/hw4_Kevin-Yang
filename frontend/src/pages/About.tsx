import { Link } from 'react-router-dom'
import { openChat } from '../chatEvents'

export default function About() {
  return (
    <>
      <section className="page-hero">
        <div className="container">
          <p className="eyebrow">About us</p>
          <h1>Clothes that feel like they belong on campus.</h1>
          <p className="page-hero-sub">
            Campus Customs is a small Yale apparel shop in New Haven, built for the people who live the Yale year:
            from move-in to The Game to Commencement.
          </p>
        </div>
      </section>

      <section className="container section about">
        <div className="about-grid">
          <div className="about-card">
            <span className="about-num">01</span>
            <h3>What we carry</h3>
            <p>
              Heavyweight hoodies for January on Cross Campus, crewnecks for section, tees for move-in day, and
              quarter-zips that work for a recruiting coffee. Our catalogue covers residential colleges, graduate
              and professional schools, varsity sports, and classic Bulldog designs.
            </p>
          </div>
          <div className="about-card">
            <span className="about-num">02</span>
            <h3>Who we’re for</h3>
            <p>
              First-years buying their first college sweatshirt, seniors grabbing one last piece before
              Commencement, parents visiting for Family Weekend, and alumni who still show up for The Game.
            </p>
          </div>
          <div className="about-card">
            <span className="about-num">03</span>
            <h3>How we help</h3>
            <p>
              Every product page shows real prices and live stock by size, so you know what’s available before you
              decide. Our shopping assistant can search the catalogue, check your size, and compare items for you.
            </p>
          </div>
        </div>
        <div className="hero-actions">
          <Link to="/products" className="btn btn-lg">
            Browse the catalogue
          </Link>
          <button type="button" className="btn btn-outline btn-lg" onClick={openChat}>
            Chat with the assistant
          </button>
        </div>
      </section>
    </>
  )
}
