import React, { useState } from "react";
import { motion, useInView } from "framer-motion";
import { Search, Book, Compass, PlayCircle, FileText, Code2, FileSearch } from "lucide-react";
import LandingNavbar from "../../components/LandingNavbar";
import LandingFooter from "../../components/LandingFooter";
import "../../styles/pages/marketing/ResourcesPage.css";

const fadeUp = {
  hidden: { opacity: 0, y: 40 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: "easeOut" } },
};

const staggerContainer = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.1 } },
};

function AnimatedSection({ children, className = "" }) {
  const ref = React.useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-80px" });
  return (
    <motion.div
      ref={ref}
      variants={staggerContainer}
      initial="hidden"
      animate={isInView ? "visible" : "hidden"}
      className={className}
    >
      {children}
    </motion.div>
  );
}

const categories = [
  {
    icon: Book,
    title: "Documentation",
    desc: "Comprehensive technical documentation, API references, and SDK guides.",
  },
  {
    icon: Compass,
    title: "Product Guides",
    desc: "Step-by-step instructions on setting up and optimizing your workspace.",
  },
  {
    icon: PlayCircle,
    title: "Tutorials",
    desc: "Video courses and interactive labs to help you build faster.",
  },
  {
    icon: FileText,
    title: "Blog",
    desc: "Industry insights, company news, and engineering deep-dives.",
  },
  {
    icon: FileSearch,
    title: "Whitepapers",
    desc: "In-depth research on AI trends, security architectures, and compliance.",
  },
  {
    icon: Code2,
    title: "Developer Tools",
    desc: "SDKs, CLI tools, and community-maintained open-source projects.",
  },
];

export default function ResourcesPage() {
  const [query, setQuery] = useState("");

  const filtered = categories.filter((c) =>
    (c.title + " " + c.desc).toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="resources-page">
      <LandingNavbar />

      <main className="resources-main">
        <header className="resources-header">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <p className="resources-eyebrow">
              Resources
            </p>
            <h1 className="resources-title">
              Resource Hub
            </h1>
            <p className="resources-subtitle">
              Everything you need to master the platform. Explore documentation, guides, and insights
              to elevate your AI workflows.
            </p>
            <div className="resources-search-wrap">
              <Search className="resources-search-icon" />
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search resources, tutorials, or documentation..."
                type="text"
                className="resources-search-input"
              />
            </div>
          </motion.div>
        </header>

        <AnimatedSection>
          <motion.div
            variants={staggerContainer}
            className="resources-grid"
          >
            {filtered.map(({ icon: Icon, title, desc }) => (
              <motion.div
                key={title}
                variants={fadeUp}
                className="group resources-card"
              >
                <div className="resources-card-overlay" />
                <div className="resources-card-content">
                  <div className="resources-card-icon">
                    <Icon className="resources-card-icon-svg" />
                  </div>
                  <h3 className="resources-card-title">{title}</h3>
                  <p className="resources-card-desc">
                    {desc}
                  </p>
                </div>
              </motion.div>
            ))}
          </motion.div>
          {filtered.length === 0 && (
            <p className="resources-empty">
              No resources match "{query}". Try a different search term.
            </p>
          )}
        </AnimatedSection>
      </main>

      <LandingFooter />
    </div>
  );
}
