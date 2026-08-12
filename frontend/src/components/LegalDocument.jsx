import React, { useState, useEffect } from "react";
import { Scroll } from "lucide-react";
import LandingNavbar from "./LandingNavbar";
import LandingFooter from "./LandingFooter";
import "../styles/components/LegalDocument.css";

const tocLinkClass = "legal-toc-link";

export default function LegalDocument({
  eyebrow,
  title,
  lastUpdated,
  sections = [],
  withToc = true,
}) {
  const [active, setActive] = useState(sections[0]?.id || "");

  useEffect(() => {
    const ids = sections.map((s) => s.id).filter(Boolean);
    if (!ids.length) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) setActive(entry.target.id);
        });
      },
      { rootMargin: "-20% 0px -70% 0px" }
    );

    ids.forEach((id) => {
      const el = document.getElementById(id);
      if (el) observer.observe(el);
    });
    return () => observer.disconnect();
  }, [sections]);

  return (
    <div className="legal-root">
      <LandingNavbar />

      <main className="legal-main">
        <header className="legal-header">
          <div className="legal-header-inner">
            <p className="legal-eyebrow">
              {eyebrow}
            </p>
            <h1 className="legal-title">
              {title}
            </h1>
            <p className="legal-updated">Last updated: {lastUpdated}</p>
          </div>
        </header>

        <div className="legal-grid">
          {withToc && (
            <aside className="legal-aside">
              <div className="legal-toc">
                <h3 className="legal-toc-title">
                  <Scroll className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
                  Contents
                </h3>
                <nav className="legal-toc-nav">
                  {sections.map((section, idx) => (
                    <a
                      key={section.id}
                      href={`#${section.id}`}
                      className={
                        active === section.id
                          ? "legal-toc-link-active"
                          : tocLinkClass
                      }
                    >
                      {idx + 1}. {section.title}
                    </a>
                  ))}
                </nav>
              </div>
            </aside>
          )}

          <article
            className={`legal-article ${
              withToc ? "legal-article-toc" : "legal-article-full"
            }`}
          >
            {sections.map((section) => (
              <div key={section.id}>
                <section className="scroll-mt-24" id={section.id}>
                  <h2 className="legal-section-title">
                    {section.title}
                  </h2>
                  <div className="legal-section-body">{section.body}</div>
                </section>
              </div>
            ))}
          </article>
        </div>
      </main>

      <LandingFooter />
    </div>
  );
}
