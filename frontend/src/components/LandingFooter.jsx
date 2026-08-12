import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { Cpu, Star } from "lucide-react";
import "./LandingFooter.css";

const productLinks = [
  { name: "Platform", href: "/" },
  { name: "Pricing", href: "/pricing" },
  { name: "Resources", href: "/resources" },
  { name: "Contact", href: "/contact" },
];

const resourceLinks = [
  { name: "Documentation", href: "/resources" },
  { name: "Guides", href: "/resources" },
  { name: "FAQs", href: "/resources" },
  { name: "Support", href: "/contact" },
];

const companyLinks = [
  { name: "About Us", href: "/" },
  { name: "Contact", href: "/contact" },
];

const legalLinks = [
  { name: "Privacy Policy", href: "/privacy-policy" },
  { name: "Terms of Service", href: "/terms-of-service" },
];

function FooterColumn({ title, links }) {
  return (
    <div>
      <h4 className="footer-col-title">{title}</h4>
      <ul className="footer-col-list">
        {links.map((link) => (
          <li key={link.name}>
            <Link
              to={link.href}
              className="footer-col-link"
            >
              {link.name}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function LandingFooter() {
  const navigate = useNavigate();

  return (
    <footer className="footer-root">
      <div className="footer-container">
        <div className="footer-grid">
          {/* Brand */}
          <div className="footer-brand-col">
            <button
              onClick={() => navigate("/")}
              className="footer-logo-btn"
            >
              <div className="footer-logo-icon">
                <Cpu className="h-4 w-4 text-white" />
              </div>
              <span className="footer-logo-text">
                Consulting Delivery OS
              </span>
            </button>
            <p className="footer-brand-desc">
              The intelligent platform for modern consulting teams. Delivering projects faster with AI.
            </p>
            <div className="footer-contact-list">
              <p>
                <span className="footer-contact-label">Email:</span>{" "}
                <a href="mailto:info@yourcompany.com" className="footer-contact-link">
                  info@yourcompany.com
                </a>
              </p>
              <p>
                <span className="footer-contact-label">Phone:</span> +91 XXXXX XXXXX
              </p>
              <p>
                <span className="footer-contact-label">Web:</span>{" "}
                <a href="#" className="footer-contact-link">
                  www.yourcompany.com
                </a>
              </p>
            </div>
          </div>

          <FooterColumn title="Product" links={productLinks} />
          <FooterColumn title="Resources" links={resourceLinks} />
          <FooterColumn title="Company" links={companyLinks} />
          <FooterColumn title="Legal" links={legalLinks} />
        </div>

        <div className="footer-bottom">
          <p className="footer-copy">
            © 2026 Consulting Delivery OS. All rights reserved.
          </p>
          <div className="footer-stars">
            {[...Array(5)].map((_, i) => (
              <Star key={i} className="h-3.5 w-3.5 text-amber-400 fill-amber-400" />
            ))}
            <span className="footer-rating">Loved by 500+ consulting teams</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
