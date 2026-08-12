import * as React from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { motion, useScroll, useMotionValueEvent } from "framer-motion";
import { Menu, X, Cpu, Sun, Moon, ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { useTheme } from "@/context/ThemeContext";
import "./LandingNavbar.css";

const navItems = [
  { name: "Pricing", href: "/pricing", active: (p) => p.startsWith("/pricing") },
  { name: "Resources", href: "/resources", active: (p) => p.startsWith("/resources") },
  { name: "Contact", href: "/contact", active: (p) => p.startsWith("/contact") },
];

const EXPAND_SCROLL_THRESHOLD = 80;

const containerVariants = {
  expanded: {
    y: 0,
    opacity: 1,
    width: "auto",
    transition: {
      y: { type: "spring", damping: 18, stiffness: 250 },
      opacity: { duration: 0.3 },
      type: "spring",
      damping: 20,
      stiffness: 300,
      staggerChildren: 0.07,
      delayChildren: 0.2,
    },
  },
  collapsed: {
    y: 0,
    opacity: 1,
    width: "3rem",
    transition: {
      type: "spring",
      damping: 20,
      stiffness: 300,
      when: "afterChildren",
      staggerChildren: 0.05,
      staggerDirection: -1,
    },
  },
};

const logoVariants = {
  expanded: { opacity: 1, x: 0, rotate: 0, transition: { type: "spring", damping: 15 } },
  collapsed: { opacity: 0, x: -25, rotate: -180, transition: { duration: 0.3 } },
};

const itemVariants = {
  expanded: { opacity: 1, x: 0, scale: 1, transition: { type: "spring", damping: 15 } },
  collapsed: { opacity: 0, x: -20, scale: 0.95, transition: { duration: 0.2 } },
};

const collapsedIconVariants = {
  expanded: { opacity: 0, scale: 0.8, transition: { duration: 0.2 } },
  collapsed: {
    opacity: 1,
    scale: 1,
    transition: { type: "spring", damping: 15, stiffness: 300, delay: 0.15 },
  },
};

const ctaVariants = {
  expanded: { opacity: 1, x: 0, scale: 1, transition: { type: "spring", damping: 15, delay: 0.1 } },
  collapsed: { opacity: 0, x: 20, scale: 0.95, transition: { duration: 0.15 } },
};

function ThemeToggle({ className }) {
  const { theme, toggleTheme } = useTheme();
  return (
    <button
      onClick={toggleTheme}
      aria-label={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
      className={cn(
        "nav-theme-toggle",
        theme === "dark" ? "nav-theme-toggle-dark" : "nav-theme-toggle-light",
        className
      )}
    >
      {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
    </button>
  );
}

export default function LandingNavbar() {
  const [isExpanded, setExpanded] = React.useState(true);
  const [scrolled, setScrolled] = React.useState(false);
  const [mobileOpen, setMobileOpen] = React.useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { theme } = useTheme();

  const { scrollY } = useScroll();
  const lastScrollY = React.useRef(0);
  const scrollPositionOnCollapse = React.useRef(0);

  useMotionValueEvent(scrollY, "change", (latest) => {
    const previous = lastScrollY.current;

    setScrolled(latest > 20);

    if (isExpanded && latest > previous && latest > 150) {
      setExpanded(false);
      scrollPositionOnCollapse.current = latest;
    } else if (
      !isExpanded &&
      latest < previous &&
      scrollPositionOnCollapse.current - latest > EXPAND_SCROLL_THRESHOLD
    ) {
      setExpanded(true);
    }

    lastScrollY.current = latest;
  });

  React.useEffect(() => {
    setMobileOpen(false);
  }, [location.pathname]);

  const handleNavClick = (e) => {
    if (!isExpanded) {
      e.preventDefault();
      setExpanded(true);
    }
  };

  const go = (path) => {
    setMobileOpen(false);
    navigate(path);
  };

  const isOnDarkHero =
    location.pathname === "/" ||
    location.pathname === "/pricing" ||
    location.pathname === "/resources" ||
    location.pathname === "/contact";

  const lightTheme = theme === "light";
  const useDarkNavbar = lightTheme && !scrolled && isOnDarkHero;

  return (
    <>
      <div className="nav-wrapper">
        <motion.nav
          initial={{ y: -80, opacity: 0 }}
          animate={isExpanded ? "expanded" : "collapsed"}
          variants={containerVariants}
          whileHover={!isExpanded ? { scale: 1.1 } : {}}
          whileTap={!isExpanded ? { scale: 0.95 } : {}}
          onClick={handleNavClick}
          className={cn(
            "nav-bar",
            useDarkNavbar
              ? "nav-bar-darkhero"
              : scrolled
              ? "nav-bar-scrolled"
              : "nav-bar-default",
            !isExpanded && "cursor-pointer justify-center"
          )}
        >
          {/* Logo */}
          <motion.div
            variants={logoVariants}
            onClick={() => go("/")}
            className="nav-logo"
          >
            <div className="nav-logo-icon">
              <Cpu className="h-4 w-4 text-white" />
            </div>
            <span
              className={cn(
                "nav-logo-text",
                useDarkNavbar ? "text-white" : "text-slate-900 dark:text-white"
              )}
            >
              Consulting Delivery OS
            </span>
          </motion.div>

          {/* Nav Links */}
          <motion.div
            className={cn(
              "nav-links",
              !isExpanded && "pointer-events-none"
            )}
          >
            {navItems.map((item) => (
              <motion.button
                key={item.name}
                variants={itemVariants}
                onClick={(e) => {
                  e.stopPropagation();
                  go(item.href);
                }}
                className={cn(
                  "nav-item",
                  useDarkNavbar
                    ? item.active(location.pathname)
                      ? "nav-item-darkhero-active"
                      : "nav-item-darkhero"
                    : item.active(location.pathname)
                    ? "nav-item-active"
                    : "nav-item-default"
                )}
              >
                {item.name}
              </motion.button>
            ))}
          </motion.div>

          {/* CTA Buttons */}
          <motion.div
            variants={ctaVariants}
            className={cn(
              "nav-cta",
              !isExpanded && "pointer-events-none"
            )}
          >
            <ThemeToggle />
            <button
              onClick={(e) => {
                e.stopPropagation();
                go("/contact");
              }}
              className={cn(
                "nav-demo",
                useDarkNavbar ? "nav-demo-darkhero" : "nav-demo-default"
              )}
            >
              Request Demo
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation();
                go("/login");
              }}
              className="nav-cta-btn"
            >
              Get Started
            </button>
          </motion.div>

          {/* Mobile menu button */}
          <motion.div variants={itemVariants} className="nav-mobile">
            <ThemeToggle />
            <button
              onClick={(e) => {
                e.stopPropagation();
                setMobileOpen((v) => !v);
              }}
              aria-label="Toggle navigation menu"
              className={cn(
                "nav-mobile-toggle",
                useDarkNavbar ? "nav-mobile-toggle-darkhero" : "nav-mobile-toggle-default"
              )}
            >
              {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </motion.div>

          {/* Collapsed Icon */}
          <div className="nav-collapsed-wrap">
            <motion.div
              variants={collapsedIconVariants}
              animate={isExpanded ? "expanded" : "collapsed"}
            >
              <Menu className="h-5 w-5 text-slate-900 dark:text-white" />
            </motion.div>
          </div>
        </motion.nav>
      </div>

      {/* Mobile dropdown menu */}
      {mobileOpen && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          className="nav-mobile-menu"
        >
          <div className="nav-mobile-list">
            {navItems.map((item) => (
              <button
                key={item.name}
                onClick={() => go(item.href)}
                className={cn(
                  "nav-mobile-item",
                  item.active(location.pathname)
                    ? "nav-mobile-item-active"
                    : "nav-mobile-item-default"
                )}
              >
                {item.name}
              </button>
            ))}
            <div className="nav-mobile-actions">
              <button
                onClick={() => go("/contact")}
                className="nav-mobile-demo"
              >
                Request Demo
              </button>
              <button
                onClick={() => go("/login")}
                className="nav-mobile-cta"
              >
                Get Started <ArrowRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        </motion.div>
      )}
    </>
  );
}
