import * as React from "react";
import { motion, useScroll, useMotionValueEvent } from "framer-motion";
import { Menu, Cpu } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { cn } from "@/lib/utils";

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
    transition: { type: "spring", damping: 15, stiffness: 300, delay: 0.15 },
  },
};

const ctaVariants = {
  expanded: { opacity: 1, x: 0, scale: 1, transition: { type: "spring", damping: 15, delay: 0.1 } },
  collapsed: { opacity: 0, x: 20, scale: 0.95, transition: { duration: 0.15 } },
};

export default function LandingNavbar() {
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
    <div className="fixed top-5 left-1/2 -translate-x-1/2 z-50">
      <motion.nav
        initial={{ y: -80, opacity: 0 }}
        animate={isExpanded ? "expanded" : "collapsed"}
        variants={containerVariants}
        whileHover={!isExpanded ? { scale: 1.1 } : {}}
        whileTap={!isExpanded ? { scale: 0.95 } : {}}
        onClick={handleNavClick}
        className={cn(
          "flex items-center overflow-hidden rounded-full border shadow-xl backdrop-blur-md h-12 transition-all duration-300",
          scrolled ? "bg-slate-900/90 border-slate-700/60" : "bg-white/10 border-white/20",
          !isExpanded && "cursor-pointer justify-center"
        )}
      >
        {/* Logo */}
        <motion.div
          variants={logoVariants}
          className="flex-shrink-0 flex items-center gap-2 font-semibold pl-4 pr-3"
        >
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center">
            <Cpu className="h-4 w-4 text-white" />
          </div>
          <span className="text-sm font-bold tracking-tight whitespace-nowrap text-white">
            Consulting Delivery OS
          </span>
        </motion.div>

        {/* Nav Links */}
        <motion.div
          className={cn(
            "flex items-center gap-0.5 px-2",
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
                "text-xs font-medium transition-colors px-2.5 py-1.5 rounded-full whitespace-nowrap",
                scrolled
                  ? "text-slate-300 hover:text-white hover:bg-white/10"
                  : "text-white/80 hover:text-white hover:bg-white/15"
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
            "flex items-center gap-2 pr-3 pl-2",
            !isExpanded && "pointer-events-none"
          )}
        >
          <motion.a
            href="#demo"
            onClick={(e) => e.stopPropagation()}
            className={cn(
              "text-xs font-medium px-3 py-1.5 rounded-full border transition-all whitespace-nowrap",
              scrolled
                ? "border-slate-600 text-slate-300 hover:border-indigo-500 hover:text-indigo-400"
                : "border-white/30 text-white hover:border-white/60 hover:bg-white/10"
            )}
          >
            Request Demo
          </motion.a>
          <button
            onClick={(e) => { e.stopPropagation(); navigate("/login"); }}
            className="text-xs font-semibold px-3.5 py-1.5 rounded-full bg-gradient-to-r from-indigo-600 to-violet-600 text-white hover:from-indigo-500 hover:to-violet-500 transition-all whitespace-nowrap shadow-md shadow-indigo-900/40"
          >
            Get Started
          </button>
        </motion.div>

        {/* Collapsed Icon */}
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
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
