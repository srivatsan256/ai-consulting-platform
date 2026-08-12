import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion, useInView } from "framer-motion";
import {
  Brain,
  FileText,
  CheckCircle2,
  Shield,
  BarChart3,
  Users,
  Zap,
  ArrowRight,
  ChevronDown,
  ChevronUp,
  Star,
  TrendingUp,
  Clock,
  Globe,
  Lock,
  MessageSquare,
  GitBranch,
  Target,
  Layers,
  FileSearch,
  PenTool,
  Upload,
  RefreshCw,
  Building2,
  Briefcase,
  Code2,
  Database,
  UserCheck,
  Rocket,
  AlertTriangle,
  XCircle,
} from "lucide-react";
import LandingNavbar from "../components/LandingNavbar";
import LandingFooter from "../components/LandingFooter";
import "./LandingPage.css";

// ─── Animation Variants ──────────────────────────────────────────────────────
const fadeUp = {
  hidden: { opacity: 0, y: 40 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: "easeOut" } },
};

const staggerContainer = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.12 } },
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

// ─── HERO ────────────────────────────────────────────────────────────────────
function HeroSection() {
  const navigate = useNavigate();
  return (
    <section
      id="home"
      className="landing-hero"
    >
      {/* Background Grid */}
      <div
        className="landing-hero-grid"
        style={{
          backgroundImage:
            "linear-gradient(rgba(99,102,241,0.15) 1px, transparent 1px), linear-gradient(90deg, rgba(99,102,241,0.15) 1px, transparent 1px)",
          backgroundSize: "60px 60px",
        }}
      />
      {/* Radial glows */}
      <div className="landing-hero-glow" />
      <div className="landing-hero-glow-violet" />
      <div className="landing-hero-glow-cyan" />

      <div className="landing-hero-content">
        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="landing-hero-badge"
        >
          <span className="text-base">🚀</span>
          <span>AI-Powered Enterprise Consulting Platform</span>
        </motion.div>

        {/* Headline */}
        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.15 }}
          className="landing-hero-h1"
        >
          Deliver Better{" "}
          <span className="landing-gradient">
            Consulting Projects
          </span>{" "}
          with AI
        </motion.h1>

        {/* Sub-description */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="landing-hero-sub"
        >
          Transform the way consulting teams gather requirements, analyze business processes, generate
          documentation, and collaborate with clients—all from a single intelligent platform.
        </motion.p>
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="landing-hero-sub2"
        >
          Our AI Consulting Delivery Platform streamlines every stage of the consulting lifecycle.
          From project onboarding and document analysis to AI-assisted documentation and stakeholder
          collaboration, teams can deliver projects faster, with greater accuracy and consistency.
        </motion.p>

        {/* CTA Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.5 }}
          className="landing-hero-cta"
        >
          <button
            id="get-started"
            onClick={() => navigate("/login")}
            className="landing-btn-primary"
          >
            Get Started <ArrowRight className="h-4 w-4" />
          </button>
          <a
            id="demo"
            href="#how-it-works"
            className="landing-btn-demo"
          >
            Request Demo
          </a>
        </motion.div>

        {/* Hero Highlights */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.65 }}
          className="landing-hero-highlights"
        >
          {[
            { icon: Brain, label: "AI-Powered Discovery" },
            { icon: FileText, label: "Intelligent Document Generation" },
            { icon: Target, label: "Project Readiness Assessment" },
            { icon: Shield, label: "Enterprise-Grade Security" },
          ].map(({ icon: Icon, label }) => (
            <div
              key={label}
              className="landing-hero-highlight"
            >
              <div className="landing-highlight-icon">
                <Icon className="h-3 w-3 text-indigo-400" />
              </div>
              <span>{label}</span>
            </div>
          ))}
        </motion.div>
      </div>

      {/* Hero image / dashboard mockup */}
      <motion.div
        initial={{ opacity: 0, y: 60 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.9, delay: 0.7 }}
        className="landing-hero-mockup"
      >
        <div className="landing-browser">
          <div className="landing-browser-bar">
            <div className="landing-browser-dot bg-red-500/70" />
            <div className="landing-browser-dot bg-yellow-500/70" />
            <div className="landing-browser-dot bg-green-500/70" />
            <div className="landing-browser-url">
              app.consultingdeliveryos.com/dashboard
            </div>
          </div>
          <img
            src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200&q=80&auto=format&fit=crop"
            alt="AI Consulting Delivery Platform Dashboard"
            className="w-full object-cover"
            style={{ height: "420px", objectPosition: "top" }}
          />
          <div className="landing-mockup-overlay" />
          {/* Floating stat cards */}
          <div className="landing-float-card">
            <p className="landing-float-label">Projects Delivered</p>
            <p className="landing-float-value text-white">2,847</p>
            <p className="landing-float-sub text-emerald-400">
              <TrendingUp className="h-3 w-3" /> +32% this quarter
            </p>
          </div>
          <div className="absolute bottom-8 right-8 bg-slate-900/90 backdrop-blur-md border border-slate-700/60 rounded-xl p-4 shadow-xl">
            <p className="landing-float-label">AI Readiness Score</p>
            <p className="landing-float-value text-indigo-400">94%</p>
            <p className="landing-float-note">Avg. across all projects</p>
          </div>
        </div>
      </motion.div>
    </section>
  );
}

// ─── TRUSTED BY ───────────────────────────────────────────────────────────────
function TrustedBySection() {
  const logos = [
    { name: "Consulting Firms", icon: Building2 },
    { name: "System Integrators", icon: Layers },
    { name: "Business Analysts", icon: BarChart3 },
    { name: "Solution Architects", icon: Code2 },
    { name: "Digital Transformation", icon: Zap },
    { name: "Enterprise Orgs", icon: Globe },
  ];

  return (
    <section className="landing-trusted">
      <div className="landing-container">
        <AnimatedSection>
          <motion.div variants={fadeUp} className="landing-section-head-sm">
            <h2 className="landing-h2-sm">
              Trusted by Modern Consulting Teams
            </h2>
            <p className="max-w-2xl mx-auto text-slate-400">
              Designed for consulting firms, system integrators, business analysts, solution architects,
              digital transformation teams, and enterprise organizations seeking a more efficient way to
              manage consulting engagements.
            </p>
          </motion.div>

          <motion.div
            variants={staggerContainer}
            className="landing-logo-grid"
          >
            {logos.map(({ name, icon: Icon }) => (
              <motion.div
                key={name}
                variants={fadeUp}
                className="landing-logo-card group"
              >
                <div className="landing-logo-icon-box">
                  <Icon className="h-5 w-5 text-indigo-400" />
                </div>
                <span className="landing-logo-name">
                  {name}
                </span>
              </motion.div>
            ))}
          </motion.div>
        </AnimatedSection>
      </div>
    </section>
  );
}

// ─── PLATFORM OVERVIEW ───────────────────────────────────────────────────────
function PlatformOverviewSection() {
  const highlights = [
    "Centralized project management",
    "AI-powered requirement analysis",
    "Automated document generation",
    "Structured collaboration",
    "Secure document repository",
    "Approval workflows",
    "Version history",
    "Analytics dashboard",
  ];

  return (
    <section id="platform" className="landing-section-dark">
      <div className="landing-container">
        <AnimatedSection>
          <div className="landing-overview-grid">
            <div>
              <motion.p
                variants={fadeUp}
                className="landing-eyebrow mb-4"
              >
                Platform Overview
              </motion.p>
              <motion.h2
                variants={fadeUp}
                className="landing-h2-tight"
              >
                One Platform for the{" "}
                <span className="landing-gradient-duo">
                  Entire Consulting Lifecycle
                </span>
              </motion.h2>
              <motion.p variants={fadeUp} className="landing-p mb-4">
                Managing consulting projects often requires multiple disconnected tools for
                documentation, collaboration, project tracking, and client communication.
              </motion.p>
              <motion.p variants={fadeUp} className="landing-p mb-8">
                Our platform brings everything together into one intelligent workspace, enabling
                consulting teams to manage projects from initial discovery through final delivery.
              </motion.p>
              <motion.div variants={staggerContainer} className="landing-check-grid">
                {highlights.map((h) => (
                  <motion.div
                    key={h}
                    variants={fadeUp}
                    className="landing-check-item"
                  >
                    <CheckCircle2 className="h-4 w-4 text-indigo-400 flex-shrink-0" />
                    {h}
                  </motion.div>
                ))}
              </motion.div>
            </div>

            <motion.div variants={fadeUp} className="relative">
              <div className="landing-img-frame">
                <img
                  src="https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&q=80&auto=format&fit=crop"
                  alt="Platform Overview"
                  className="w-full object-cover"
                  style={{ height: "480px", objectPosition: "center" }}
                />
                <div className="landing-img-overlay" />
              </div>
              {/* Floating badge */}
              <div className="landing-badge-card">
                <div className="flex items-center gap-3">
                  <div className="landing-badge-icon-box">
                    <Zap className="h-5 w-5 text-emerald-400" />
                  </div>
                  <div>
                    <p className="landing-badge-label">Time Saved</p>
                    <p className="landing-badge-value">60% Faster</p>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </AnimatedSection>
      </div>
    </section>
  );
}

// ─── WHY TRADITIONAL NEEDS AN UPGRADE ─────────────────────────────────────────
function WhyUpgradeSection() {
  const painPoints = [
    "Inconsistent documentation across teams and projects",
    "Missing or ambiguous requirements leading to scope creep",
    "Version confusion and fragmented collaboration tools",
    "Long review cycles and delayed delivery timelines",
    "Institutional knowledge lost when consultants transition",
  ];

  return (
    <section className="landing-section-slate">
      <div className="landing-container">
        <AnimatedSection>
          <div className="landing-upgrade-grid">
            <motion.div variants={fadeUp}>
              <p className="landing-eyebrow mb-4">
                The Problem
              </p>
              <h2 className="landing-h2-tight">
                Why Traditional Consulting Needs an{" "}
                <span className="landing-gradient-duo">
                  Upgrade
                </span>
              </h2>
              <p className="landing-p mb-4">
                Legacy consulting engagements rely on disconnected documents, manual coordination, and
                tribal knowledge. This leads to inconsistent deliverables, ambiguous requirements, and
                slow review cycles.
              </p>
              <p className="landing-p">
                ConsultAI OS replaces these fragile practices with a centralized, intelligent delivery
                process that keeps every engagement structured and auditable.
              </p>
            </motion.div>

            <motion.div
              variants={fadeUp}
              className="landing-pain-card"
            >
              <div className="landing-pain-bar" />
              <h3 className="landing-pain-title">
                <AlertTriangle className="h-5 w-5" />
                Common Pitfalls of Traditional Consulting
              </h3>
              <ul className="landing-pain-list">
                {painPoints.map((point) => (
                  <li key={point} className="landing-pain-item">
                    <XCircle className="h-5 w-5 text-rose-500 flex-shrink-0 mt-0.5" />
                    <span className="landing-pain-text">{point}</span>
                  </li>
                ))}
              </ul>
            </motion.div>
          </div>
        </AnimatedSection>
      </div>
    </section>
  );
}

// ─── WHY CHOOSE ──────────────────────────────────────────────────────────────
function WhyChooseSection() {
  const reasons = [
    {
      icon: Brain,
      title: "AI-Assisted Discovery",
      desc: "Analyze uploaded documents, identify missing information, and guide teams through structured requirement gathering.",
      color: "from-indigo-500 to-violet-600",
    },
    {
      icon: PenTool,
      title: "Intelligent Documentation",
      desc: "Generate consulting deliverables in minutes using AI while maintaining consistency and quality.",
      color: "from-violet-500 to-purple-600",
    },
    {
      icon: GitBranch,
      title: "Guided Consulting Workflow",
      desc: "Follow a structured methodology that ensures every consulting engagement progresses through the required phases.",
      color: "from-purple-500 to-pink-600",
    },
    {
      icon: Lock,
      title: "Secure Collaboration",
      desc: "Enable consultants and clients to review, comment, approve, and manage documents securely.",
      color: "from-cyan-500 to-blue-600",
    },
    {
      icon: BarChart3,
      title: "Project Visibility",
      desc: "Track project readiness, documentation progress, pending approvals, and overall delivery status from a centralized dashboard.",
      color: "from-emerald-500 to-teal-600",
    },
    {
      icon: Shield,
      title: "Enterprise Security",
      desc: "Protect project information with role-based access, encryption, audit logs, and secure file storage.",
      color: "from-orange-500 to-amber-600",
    },
  ];

  return (
    <section id="features" className="landing-section-slate">
      <div className="landing-container">
        <AnimatedSection>
          <motion.div variants={fadeUp} className="landing-section-head">
            <p className="landing-eyebrow mb-3">
              Why Choose Our Platform
            </p>
            <h2 className="landing-h2">
              Built Specifically for Consulting Teams
            </h2>
          </motion.div>

          <motion.div
            variants={staggerContainer}
            className="landing-cards-3"
          >
            {reasons.map(({ icon: Icon, title, desc, color }) => (
              <motion.div
                key={title}
                variants={fadeUp}
                className="landing-card group"
              >
                <div
                  className={`landing-card-icon bg-gradient-to-br ${color}`}
                >
                  <Icon className="h-6 w-6 text-white" />
                </div>
                <h3 className="landing-card-title">{title}</h3>
                <p className="landing-card-desc">{desc}</p>
              </motion.div>
            ))}
          </motion.div>
        </AnimatedSection>
      </div>
    </section>
  );
}

// ─── CORE FEATURES ───────────────────────────────────────────────────────────
function CoreFeaturesSection() {
  const features = [
    {
      icon: UserCheck,
      title: "Client Onboarding",
      desc: "Create organizations, manage projects, invite stakeholders, and configure consulting engagements with ease.",
      items: [],
      color: "indigo",
    },
    {
      icon: Database,
      title: "Document Management",
      desc: "Upload and organize business documents including:",
      items: ["Business Requirement Documents (BRD)", "Functional Requirement Documents (FRD)", "Standard Operating Procedures (SOP)", "Process Flow Diagrams", "API Documentation", "Excel Files", "PDF Documents", "Images and Screenshots"],
      color: "violet",
    },
    {
      icon: FileSearch,
      title: "AI Requirement Analysis",
      desc: "Automatically analyze uploaded documents to identify:",
      items: ["Missing business information", "Incomplete workflows", "Undefined business rules", "Data gaps", "Process inconsistencies"],
      color: "purple",
    },
    {
      icon: Target,
      title: "AI Readiness Score",
      desc: "Measure project preparedness with AI-generated insights based on:",
      items: ["Business understanding", "Process completeness", "Document coverage", "Requirement quality", "Missing information"],
      color: "cyan",
    },
    {
      icon: PenTool,
      title: "AI Document Generator",
      desc: "Generate professional consulting documents including:",
      items: ["Business Requirements", "Functional Requirements", "Product Requirements", "User Stories", "User Personas", "User Journeys", "Solution Architecture", "API Specifications", "Security Assessments", "Test Cases", "Deployment Guides"],
      color: "emerald",
    },
    {
      icon: MessageSquare,
      title: "Collaboration Workspace",
      desc: "Improve communication between consultants and clients with:",
      items: ["Comments", "Review requests", "Approval workflows", "Version history", "Notifications"],
      color: "orange",
    },
  ];

  const colorMap = {
    indigo: "from-indigo-500 to-indigo-600 border-indigo-500/30 bg-indigo-500/10",
    violet: "from-violet-500 to-violet-600 border-violet-500/30 bg-violet-500/10",
    purple: "from-purple-500 to-purple-600 border-purple-500/30 bg-purple-500/10",
    cyan: "from-cyan-500 to-cyan-600 border-cyan-500/30 bg-cyan-500/10",
    emerald: "from-emerald-500 to-emerald-600 border-emerald-500/30 bg-emerald-500/10",
    orange: "from-orange-500 to-orange-600 border-orange-500/30 bg-orange-500/10",
  };

  return (
    <section id="solutions" className="landing-section-dark">
      <div className="landing-container">
        <AnimatedSection>
          <motion.div variants={fadeUp} className="landing-section-head">
            <p className="landing-eyebrow mb-3">
              Core Features
            </p>
            <h2 className="landing-h2">
              Everything You Need to Deliver{" "}
              <span className="landing-gradient-duo">
                Successful Consulting Projects
              </span>
            </h2>
          </motion.div>

          <motion.div
            variants={staggerContainer}
            className="landing-features-grid"
          >
            {features.map(({ icon: Icon, title, desc, items, color }) => {
              const [gradFrom, gradTo, borderBg, bgColor] = colorMap[color].split(" ");
              return (
                <motion.div
                  key={title}
                  variants={fadeUp}
                  className={`landing-feature-card ${borderBg} ${bgColor}`}
                >
                  <div
                    className={`landing-feature-icon bg-gradient-to-br ${gradFrom} ${gradTo}`}
                  >
                    <Icon className="h-5 w-5 text-white" />
                  </div>
                  <h3 className="landing-card-title">{title}</h3>
                  <p className="landing-card-desc mb-3">{desc}</p>
                  {items.length > 0 && (
                    <ul className="landing-feature-list">
                      {items.map((item) => (
                        <li key={item} className="landing-feature-item">
                          <div className="landing-feature-bullet" />
                          {item}
                        </li>
                      ))}
                    </ul>
                  )}
                </motion.div>
              );
            })}
          </motion.div>
        </AnimatedSection>
      </div>
    </section>
  );
}

// ─── HOW IT WORKS ─────────────────────────────────────────────────────────────
function HowItWorksSection() {
  const steps = [
    {
      num: "01",
      icon: Briefcase,
      title: "Create a New Project",
      desc: "Set up your consulting engagement and invite project stakeholders.",
    },
    {
      num: "02",
      icon: Upload,
      title: "Upload Existing Documentation",
      desc: "Add business documents, process manuals, spreadsheets, diagrams, and supporting materials.",
    },
    {
      num: "03",
      icon: Brain,
      title: "AI Reviews Your Content",
      desc: "The platform analyzes uploaded information and identifies gaps or inconsistencies.",
    },
    {
      num: "04",
      icon: FileSearch,
      title: "Complete Missing Requirements",
      desc: "Answer AI-generated questions or upload additional documents to improve project completeness.",
    },
    {
      num: "05",
      icon: PenTool,
      title: "Generate Consulting Deliverables",
      desc: "Automatically create structured project documentation using AI-assisted generation.",
    },
    {
      num: "06",
      icon: MessageSquare,
      title: "Review and Collaborate",
      desc: "Consultants and clients review documents, leave feedback, and approve deliverables.",
    },
    {
      num: "07",
      icon: Rocket,
      title: "Deliver with Confidence",
      desc: "Export finalized documentation and complete your consulting engagement.",
    },
  ];

  return (
    <section id="how-it-works" className="landing-section-slate">
      <div className="landing-container">
        <AnimatedSection>
          <motion.div variants={fadeUp} className="landing-section-head">
            <p className="landing-eyebrow mb-3">
              How It Works
            </p>
            <h2 className="landing-h2">
              A Simple Process for{" "}
              <span className="landing-gradient-duo">
                Complex Consulting Projects
              </span>
            </h2>
          </motion.div>

          <div className="relative">
            {/* Vertical line */}
            <div className="landing-timeline-line" />

            <motion.div variants={staggerContainer} className="landing-steps">
              {steps.map(({ num, icon: Icon, title, desc }, idx) => (
                <motion.div
                  key={num}
                  variants={fadeUp}
                  className="landing-step group"
                >
                  {/* Step indicator */}
                  <div className="landing-step-indicator-wrap">
                    <div className="landing-step-indicator">
                      <Icon className="h-7 w-7 text-white" />
                    </div>
                  </div>
                  <div className="landing-step-body">
                    <div className="flex items-center gap-3 mb-1">
                      <span className="landing-step-num">
                        Step {num}
                      </span>
                    </div>
                    <h3 className="landing-step-title">{title}</h3>
                    <p className="landing-step-desc">{desc}</p>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </AnimatedSection>
      </div>
    </section>
  );
}

// ─── BENEFITS ─────────────────────────────────────────────────────────────────
function BenefitsSection() {
  const benefits = [
    {
      icon: Clock,
      title: "Faster Project Delivery",
      desc: "Reduce manual documentation effort and accelerate consulting engagements.",
      stat: "60%",
      statLabel: "Faster",
    },
    {
      icon: CheckCircle2,
      title: "Improved Accuracy",
      desc: "AI helps identify missing information and ensures more complete project documentation.",
      stat: "99%",
      statLabel: "Accuracy",
    },
    {
      icon: Users,
      title: "Better Collaboration",
      desc: "Keep consultants and clients aligned with centralized communication and approval workflows.",
      stat: "3x",
      statLabel: "Collaboration",
    },
    {
      icon: RefreshCw,
      title: "Standardized Methodology",
      desc: "Maintain consistent consulting practices across every project.",
      stat: "100%",
      statLabel: "Consistent",
    },
    {
      icon: Zap,
      title: "Increased Productivity",
      desc: "Automate repetitive tasks so teams can focus on solving business problems.",
      stat: "40hrs",
      statLabel: "Saved/Month",
    },
    {
      icon: TrendingUp,
      title: "Scalable for Growth",
      desc: "Support multiple projects, teams, and organizations within a single platform.",
      stat: "∞",
      statLabel: "Scale",
    },
  ];

  return (
    <section className="landing-section-dark">
      <div className="landing-container">
        <AnimatedSection>
          <motion.div variants={fadeUp} className="landing-section-head">
            <p className="landing-eyebrow mb-3">
              Benefits
            </p>
            <h2 className="landing-h2">
              Why Organizations Choose Our Platform
            </h2>
          </motion.div>

          <motion.div
            variants={staggerContainer}
            className="landing-cards-3"
          >
            {benefits.map(({ icon: Icon, title, desc, stat, statLabel }) => (
              <motion.div
                key={title}
                variants={fadeUp}
                className="landing-benefit-card group"
              >
                <div className="landing-benefit-stat">
                  <span className="landing-benefit-stat-value">
                    {stat}
                  </span>
                  <p className="landing-benefit-stat-label">{statLabel}</p>
                </div>
                <div className="landing-benefit-icon-box">
                  <Icon className="h-5 w-5 text-indigo-400" />
                </div>
                <h3 className="landing-benefit-title">{title}</h3>
                <p className="landing-card-desc">{desc}</p>
              </motion.div>
            ))}
          </motion.div>
        </AnimatedSection>
      </div>
    </section>
  );
}

// ─── STATS ────────────────────────────────────────────────────────────────────
function StatsSection() {
  const stats = [
    { value: "100%", label: "Centralized Project Management", icon: Layers },
    { value: "24/7", label: "AI-Assisted Analysis", icon: Brain },
    { value: "Unlimited", label: "Project Documentation", icon: FileText },
    { value: "Enterprise", label: "Designed for organizations of all sizes", icon: Building2 },
  ];

  return (
    <section className="landing-stats-section">
      <div className="landing-container">
        <AnimatedSection>
          <motion.p variants={fadeUp} className="landing-eyebrow text-center mb-10">
            Platform Statistics
          </motion.p>
          <motion.div
            variants={staggerContainer}
            className="landing-stats-grid"
          >
            {stats.map(({ value, label, icon: Icon }) => (
              <motion.div
                key={value}
                variants={fadeUp}
                className="landing-stat-card"
              >
                <div className="landing-stat-icon-box">
                  <Icon className="h-6 w-6 text-indigo-400" />
                </div>
                <div className="landing-stat-value">{value}</div>
                <p className="landing-stat-label">{label}</p>
              </motion.div>
            ))}
          </motion.div>
        </AnimatedSection>
      </div>
    </section>
  );
}

// ─── FAQ ──────────────────────────────────────────────────────────────────────
function FAQSection() {
  const [openIdx, setOpenIdx] = useState(null);

  const faqs = [
    {
      q: "What is the AI Consulting Delivery Platform?",
      a: "It is an enterprise platform that supports the complete consulting lifecycle, from project onboarding and discovery to AI-assisted documentation, collaboration, approvals, and project delivery.",
    },
    {
      q: "Who is this platform designed for?",
      a: "It is built for consulting firms, business analysts, solution architects, project managers, system integrators, and enterprise transformation teams.",
    },
    {
      q: "What types of documents can the platform generate?",
      a: "The platform can assist in generating business requirement documents, functional specifications, product requirements, user stories, architecture documentation, API specifications, security assessments, testing documents, deployment guides, and more.",
    },
    {
      q: "Is my project data secure?",
      a: "Yes. The platform is designed with enterprise security principles, including secure storage, access control, and audit capabilities to help protect project information.",
    },
    {
      q: "Can multiple team members collaborate?",
      a: "Yes. Teams can collaborate through shared workspaces, document reviews, comments, approvals, and version tracking.",
    },
    {
      q: "Can the platform be customized?",
      a: "Yes. The platform is designed to support configurable workflows and project structures to meet different consulting methodologies.",
    },
  ];

  return (
    <section id="resources" className="landing-section-slate">
      <div className="landing-container-narrow">
        <AnimatedSection>
          <motion.div variants={fadeUp} className="landing-section-head-sm">
            <p className="landing-eyebrow mb-3">FAQ</p>
            <h2 className="landing-h2-plain">Frequently Asked Questions</h2>
          </motion.div>

          <motion.div variants={staggerContainer} className="landing-faq-list">
            {faqs.map(({ q, a }, idx) => (
              <motion.div
                key={idx}
                variants={fadeUp}
                className="landing-faq-item"
              >
                <button
                  id={`faq-${idx}`}
                  onClick={() => setOpenIdx(openIdx === idx ? null : idx)}
                  className="landing-faq-btn"
                >
                  <span className="pr-4">{q}</span>
                  {openIdx === idx ? (
                    <ChevronUp className="h-4 w-4 text-indigo-400 flex-shrink-0" />
                  ) : (
                    <ChevronDown className="h-4 w-4 text-slate-400 flex-shrink-0" />
                  )}
                </button>
                {openIdx === idx && (
                  <div className="landing-faq-answer">
                    <p className="pt-4">{a}</p>
                  </div>
                )}
              </motion.div>
            ))}
          </motion.div>
        </AnimatedSection>
      </div>
    </section>
  );
}

// ─── FINAL CTA ────────────────────────────────────────────────────────────────
function FinalCTASection() {
  const navigate = useNavigate();
  return (
    <section id="contact" className="landing-final-cta">
      <div className="landing-final-bg">
        <div className="landing-final-glow" />
        <div className="landing-final-glow-2" />
      </div>
      <div className="landing-final-content">
        <AnimatedSection>
          <motion.div
            variants={fadeUp}
            className="landing-hero-badge"
          >
            <Star className="h-4 w-4" />
            <span>Ready to Transform Your Consulting?</span>
          </motion.div>

          <motion.h2
            variants={fadeUp}
            className="landing-h2-xl"
          >
            Ready to Modernize Your{" "}
            <span className="landing-gradient">
              Consulting Process?
            </span>
          </motion.h2>

          <motion.p variants={fadeUp} className="landing-final-p">
            Deliver consulting projects faster with AI-powered requirement analysis, intelligent
            documentation, and streamlined collaboration.
          </motion.p>

          <motion.div variants={fadeUp} className="landing-hero-cta">
            <button
              onClick={() => navigate("/login")}
              className="landing-btn-primary-lg"
            >
              Get Started <ArrowRight className="h-4 w-4" />
            </button>
            <a
              href="#how-it-works"
              className="landing-btn-demo-lg"
            >
              Request Demo
            </a>
          </motion.div>
        </AnimatedSection>
      </div>
    </section>
  );
}

// ─── MAIN PAGE ────────────────────────────────────────────────────────────────
export default function LandingPage() {
  return (
    <div className="min-h-screen">
      <LandingNavbar />
      <HeroSection />
      <TrustedBySection />
      <PlatformOverviewSection />
      <WhyUpgradeSection />
      <WhyChooseSection />
      <CoreFeaturesSection />
      <HowItWorksSection />
      <BenefitsSection />
      <StatsSection />
      <FAQSection />
      <FinalCTASection />
      <LandingFooter />
    </div>
  );
}
