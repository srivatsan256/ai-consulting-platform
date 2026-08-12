// components/ui/navigation-menu.jsx
"use client";

import * as React from "react";
import { motion, useScroll, useMotionValueEvent } from "framer-motion";
import { Menu, Cpu } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { cn } from "@/lib/utils";
import "../../styles/components/ui/navigation-menu.css";

const navItems = [
  { name: "Home", href: "#home" },
  { name: "Platform", href: "#platform" },
  { name: "Features", href: "#features" },
  { name: "Solutions", href: "#solutions" },
  { name: "Pricing", href: "#pricing" },
  { name: "Resources", href: "#resources" },
  { name: "About", href: "#about" },
  { name: "Contact", href: "#contact" },
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
    transition: {
      type: "spring",
      damping: 15,
      stiffness: 300,
      delay: 0.15,
    },
  },
};

const ctaVariants = {
  expanded: { opacity: 1, x: 0, scale: 1, transition: { type: "spring", damping: 15, delay: 0.1 } },
  collapsed: { opacity: 0, x: 20, scale: 0.95, transition: { duration: 0.15 } },
};

export function AnimatedNavFramer() {
  const [isExpanded, setExpanded] = React.useState(true);
  const [scrolled, setScrolled] = React.useState(false);
  const navigate = useNavigate();

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

  const handleNavClick = (e) => {
    if (!isExpanded) {
      e.preventDefault();
      setExpanded(true);
    }
  };

  return (
    <div className="uinavmenu-wrapper">
      <motion.nav
        initial={{ y: -80, opacity: 0 }}
        animate={isExpanded ? "expanded" : "collapsed"}
        variants={containerVariants}
        whileHover={!isExpanded ? { scale: 1.1 } : {}}
        whileTap={!isExpanded ? { scale: 0.95 } : {}}
        onClick={handleNavClick}
        className={cn(
          "uinavmenu-bar",
          scrolled
            ? "uinavmenu-bar-scrolled"
            : "uinavmenu-bar-default",
          !isExpanded && "cursor-pointer justify-center"
        )}
      >
        {/* Logo */}
        <motion.div
          variants={logoVariants}
          className="uinavmenu-logo"
        >
          <div className="uinavmenu-logo-icon">
            <Cpu className="h-4 w-4 text-white" />
          </div>
          <span className="uinavmenu-logo-text">
            Consulting Delivery OS
          </span>
        </motion.div>

        {/* Nav Links */}
        <motion.div
          className={cn(
            "uinavmenu-links",
            !isExpanded && "pointer-events-none"
          )}
        >
          {navItems.map((item) => (
            <motion.a
              key={item.name}
              href={item.href}
              variants={itemVariants}
              onClick={(e) => e.stopPropagation()}
              className={cn(
                "uinavmenu-link",
                scrolled
                  ? "uinavmenu-link-scrolled"
                  : "uinavmenu-link-default"
              )}
            >
              {item.name}
            </motion.a>
          ))}
        </motion.div>

        {/* CTA Buttons */}
        <motion.div
          variants={ctaVariants}
          className={cn(
            "uinavmenu-cta",
            !isExpanded && "pointer-events-none"
          )}
        >
          <motion.a
            href="#demo"
            onClick={(e) => e.stopPropagation()}
            className={cn(
              "uinavmenu-demo",
              scrolled
                ? "uinavmenu-demo-scrolled"
                : "uinavmenu-demo-default"
            )}
          >
            Request Demo
          </motion.a>
          <button
            onClick={(e) => { e.stopPropagation(); navigate("/login"); }}
            className="uinavmenu-cta-btn"
          >
            Get Started
          </button>
        </motion.div>

        {/* Collapsed Icon */}
        <div className="uinavmenu-collapsed-wrap">
          <motion.div
            variants={collapsedIconVariants}
            animate={isExpanded ? "expanded" : "collapsed"}
          >
            <Menu className="h-5 w-5 text-white" />
          </motion.div>
        </div>
      </motion.nav>
    </div>
  );
}
