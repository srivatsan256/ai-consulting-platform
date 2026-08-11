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
  Cpu,
  FileSearch,
  PenTool,
  Upload,
  RefreshCw,
  Download,
  Building2,
  Briefcase,
  Code2,
  Database,
  FileBarChart2,
  ScrollText,
  UserCheck,
  Map,
  Server,
  TestTube2,
  Rocket,
} from "lucide-react";
import { AnimatedNavFramer } from "../components/ui/navigation-menu";

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
      className="relative min-h-screen flex flex-col items-center justify-center overflow-hidden bg-[#04060f]"
    >
      {/* Background Grid */}
      <div
        className="absolute inset-0 opacity-25"
        style={{
          backgroundImage:
            "linear-gradient(rgba(99,102,241,0.15) 1px, transparent 1px), linear-gradient(90deg, rgba(99,102,241,0.15) 1px, transparent 1px)",
          backgroundSize: "60px 60px",
        }}
      />
      {/* Radial glows */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[900px] h-[500px] bg-indigo-600/20 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-0 left-1/4 w-[400px] h-[300px] bg-violet-600/15 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute bottom-0 right-1/4 w-[400px] h-[300px] bg-cyan-500/10 rounded-full blur-[100px] pointer-events-none" />

      <div className="relative z-10 max-w-6xl mx-auto px-6 text-center pt-24 pb-16">
        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-indigo-500/40 bg-indigo-500/10 text-indigo-300 text-sm font-medium mb-8 backdrop-blur-sm"
        >
          <span className="text-base">🚀</span>
          <span>AI-Powered Enterprise Consulting Platform</span>
        </motion.div>

        {/* Headline */}
        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.15 }}
          className="text-5xl sm:text-6xl lg:text-7xl font-bold text-white leading-tight tracking-tight mb-6"
        >
          Deliver Better{" "}
          <span className="bg-gradient-to-r from-indigo-400 via-violet-400 to-cyan-400 bg-clip-text text-transparent">
            Consulting Projects
          </span>{" "}
          with AI
        </motion.h1>

        {/* Sub-description */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="max-w-3xl mx-auto text-lg text-slate-400 leading-relaxed mb-4"
        >
          Transform the way consulting teams gather requirements, analyze business processes, generate
          documentation, and collaborate with clients—all from a single intelligent platform.
        </motion.p>
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="max-w-2xl mx-auto text-base text-slate-500 leading-relaxed mb-10"
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
          className="flex flex-wrap items-center justify-center gap-4 mb-16"
        >
          <button
            id="get-started"
            onClick={() => navigate("/login")}
            className="inline-flex items-center gap-2 px-7 py-3.5 rounded-full bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white font-semibold text-base shadow-xl shadow-indigo-900/40 transition-all duration-200 hover:scale-105 hover:shadow-indigo-700/50"
          >
            Get Started <ArrowRight className="h-4 w-4" />
          </button>
          <a
            id="demo"
            href="#how-it-works"
            className="inline-flex items-center gap-2 px-7 py-3.5 rounded-full border border-slate-600 bg-white/5 hover:bg-white/10 text-slate-200 font-semibold text-base backdrop-blur-sm transition-all duration-200 hover:border-slate-400"
          >
            Request Demo
          </a>
        </motion.div>

        {/* Hero Highlights */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.65 }}
          className="flex flex-wrap justify-center gap-6"
        >
          {[
            { icon: Brain, label: "AI-Powered Discovery" },
            { icon: FileText, label: "Intelligent Document Generation" },
            { icon: Target, label: "Project Readiness Assessment" },
            { icon: Shield, label: "Enterprise-Grade Security" },
          ].map(({ icon: Icon, label }) => (
            <div
              key={label}
              className="flex items-center gap-2 text-sm text-slate-400"
            >
              <div className="w-5 h-5 rounded-full bg-indigo-500/20 flex items-center justify-center">
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
        className="relative z-10 w-full max-w-5xl mx-auto px-6 pb-20"
      >
        <div className="relative rounded-2xl overflow-hidden border border-slate-700/60 shadow-2xl shadow-indigo-950/60">
          <div className="bg-slate-900 px-4 py-2.5 flex items-center gap-2 border-b border-slate-700/60">
            <div className="w-3 h-3 rounded-full bg-red-500/70" />
            <div className="w-3 h-3 rounded-full bg-yellow-500/70" />
            <div className="w-3 h-3 rounded-full bg-green-500/70" />
            <div className="flex-1 mx-4 bg-slate-800 rounded px-3 py-1 text-xs text-slate-500">
              app.consultingdeliveryos.com/dashboard
            </div>
          </div>
          <img
            src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200&q=80&auto=format&fit=crop"
            alt="AI Consulting Delivery Platform Dashboard"
            className="w-full object-cover"
            style={{ height: "420px", objectPosition: "top" }}
          />
          <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-transparent to-transparent pointer-events-none" />
          {/* Floating stat cards */}
          <div className="absolute bottom-8 left-8 bg-slate-900/90 backdrop-blur-md border border-slate-700/60 rounded-xl p-4 shadow-xl">
            <p className="text-xs text-slate-400 mb-1">Projects Delivered</p>
            <p className="text-2xl font-bold text-white">2,847</p>
            <p className="text-xs text-emerald-400 flex items-center gap-1 mt-1">
              <TrendingUp className="h-3 w-3" /> +32% this quarter
            </p>
          </div>
          <div className="absolute bottom-8 right-8 bg-slate-900/90 backdrop-blur-md border border-slate-700/60 rounded-xl p-4 shadow-xl">
            <p className="text-xs text-slate-400 mb-1">AI Readiness Score</p>
            <p className="text-2xl font-bold text-indigo-400">94%</p>
            <p className="text-xs text-slate-500 mt-1">Avg. across all projects</p>
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
    <section className="py-20 bg-slate-950 border-y border-slate-800/60">
      <div className="max-w-6xl mx-auto px-6">
        <AnimatedSection>
          <motion.div variants={fadeUp} className="text-center mb-12">
            <h2 className="text-2xl sm:text-3xl font-bold text-white mb-4">
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
            className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4"
          >
            {logos.map(({ name, icon: Icon }) => (
              <motion.div
                key={name}
                variants={fadeUp}
                className="flex flex-col items-center gap-3 p-5 rounded-xl border border-slate-800 bg-slate-900/50 hover:border-indigo-500/40 hover:bg-slate-900 transition-all duration-200 group"
              >
                <div className="w-10 h-10 rounded-lg bg-indigo-500/10 group-hover:bg-indigo-500/20 flex items-center justify-center transition-colors">
                  <Icon className="h-5 w-5 text-indigo-400" />
                </div>
                <span className="text-xs text-slate-400 text-center font-medium leading-tight">
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
    <section id="platform" className="py-24 bg-[#04060f]">
      <div className="max-w-6xl mx-auto px-6">
        <AnimatedSection>
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div>
              <motion.p
                variants={fadeUp}
                className="text-indigo-400 font-semibold text-sm uppercase tracking-widest mb-4"
              >
                Platform Overview
              </motion.p>
              <motion.h2
                variants={fadeUp}
                className="text-3xl sm:text-4xl font-bold text-white mb-6 leading-tight"
              >
                One Platform for the{" "}
                <span className="bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">
                  Entire Consulting Lifecycle
                </span>
              </motion.h2>
              <motion.p variants={fadeUp} className="text-slate-400 mb-4 leading-relaxed">
                Managing consulting projects often requires multiple disconnected tools for
                documentation, collaboration, project tracking, and client communication.
              </motion.p>
              <motion.p variants={fadeUp} className="text-slate-400 mb-8 leading-relaxed">
                Our platform brings everything together into one intelligent workspace, enabling
                consulting teams to manage projects from initial discovery through final delivery.
              </motion.p>
              <motion.div variants={staggerContainer} className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {highlights.map((h) => (
                  <motion.div
                    key={h}
                    variants={fadeUp}
                    className="flex items-center gap-2.5 text-sm text-slate-300"
                  >
                    <CheckCircle2 className="h-4 w-4 text-indigo-400 flex-shrink-0" />
                    {h}
                  </motion.div>
                ))}
              </motion.div>
            </div>

            <motion.div variants={fadeUp} className="relative">
              <div className="rounded-2xl overflow-hidden border border-slate-700/50 shadow-2xl shadow-indigo-950/50">
                <img
                  src="https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&q=80&auto=format&fit=crop"
                  alt="Platform Overview"
                  className="w-full object-cover"
                  style={{ height: "480px", objectPosition: "center" }}
                />
                <div className="absolute inset-0 bg-gradient-to-br from-indigo-900/30 to-transparent pointer-events-none rounded-2xl" />
              </div>
              {/* Floating badge */}
              <div className="absolute -bottom-5 -left-5 bg-slate-900 border border-slate-700/60 rounded-xl p-4 shadow-xl backdrop-blur-md">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center">
                    <Zap className="h-5 w-5 text-emerald-400" />
                  </div>
                  <div>
                    <p className="text-xs text-slate-400">Time Saved</p>
                    <p className="text-lg font-bold text-white">60% Faster</p>
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
    <section id="features" className="py-24 bg-slate-950">
      <div className="max-w-6xl mx-auto px-6">
        <AnimatedSection>
          <motion.div variants={fadeUp} className="text-center mb-16">
            <p className="text-indigo-400 font-semibold text-sm uppercase tracking-widest mb-3">
              Why Choose Our Platform
            </p>
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
              Built Specifically for Consulting Teams
            </h2>
          </motion.div>

          <motion.div
            variants={staggerContainer}
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6"
          >
            {reasons.map(({ icon: Icon, title, desc, color }) => (
              <motion.div
                key={title}
                variants={fadeUp}
                className="group relative p-6 rounded-2xl border border-slate-800 bg-slate-900/60 hover:border-slate-600 transition-all duration-300 hover:-translate-y-1"
              >
                <div
                  className={`w-12 h-12 rounded-xl bg-gradient-to-br ${color} flex items-center justify-center mb-4 shadow-lg`}
                >
                  <Icon className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
                <p className="text-sm text-slate-400 leading-relaxed">{desc}</p>
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
    <section id="solutions" className="py-24 bg-[#04060f]">
      <div className="max-w-6xl mx-auto px-6">
        <AnimatedSection>
          <motion.div variants={fadeUp} className="text-center mb-16">
            <p className="text-indigo-400 font-semibold text-sm uppercase tracking-widest mb-3">
              Core Features
            </p>
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
              Everything You Need to Deliver{" "}
              <span className="bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">
                Successful Consulting Projects
              </span>
            </h2>
          </motion.div>

          <motion.div
            variants={staggerContainer}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
          >
            {features.map(({ icon: Icon, title, desc, items, color }) => {
              const [gradFrom, gradTo, borderBg, bgColor] = colorMap[color].split(" ");
              return (
                <motion.div
                  key={title}
                  variants={fadeUp}
                  className={`p-6 rounded-2xl border ${borderBg} ${bgColor} backdrop-blur-sm hover:scale-[1.02] transition-transform duration-200`}
                >
                  <div
                    className={`w-11 h-11 rounded-xl bg-gradient-to-br ${gradFrom} ${gradTo} flex items-center justify-center mb-4 shadow-lg`}
                  >
                    <Icon className="h-5 w-5 text-white" />
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
                  <p className="text-sm text-slate-400 mb-3 leading-relaxed">{desc}</p>
                  {items.length > 0 && (
                    <ul className="space-y-1.5">
                      {items.map((item) => (
                        <li key={item} className="flex items-center gap-2 text-xs text-slate-400">
                          <div className="w-1.5 h-1.5 rounded-full bg-indigo-500 flex-shrink-0" />
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
    <section id="how-it-works" className="py-24 bg-slate-950">
      <div className="max-w-6xl mx-auto px-6">
        <AnimatedSection>
          <motion.div variants={fadeUp} className="text-center mb-16">
            <p className="text-indigo-400 font-semibold text-sm uppercase tracking-widest mb-3">
              How It Works
            </p>
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
              A Simple Process for{" "}
              <span className="bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">
                Complex Consulting Projects
              </span>
            </h2>
          </motion.div>

          <div className="relative">
            {/* Vertical line */}
            <div className="absolute left-8 top-0 bottom-0 w-px bg-gradient-to-b from-indigo-600 via-violet-600 to-transparent hidden sm:block" />

            <motion.div variants={staggerContainer} className="space-y-6">
              {steps.map(({ num, icon: Icon, title, desc }, idx) => (
                <motion.div
                  key={num}
                  variants={fadeUp}
                  className="flex gap-6 items-start group"
                >
                  {/* Step indicator */}
                  <div className="relative flex-shrink-0">
                    <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-600 to-violet-600 flex items-center justify-center shadow-xl shadow-indigo-900/40 group-hover:scale-110 transition-transform duration-200 z-10 relative">
                      <Icon className="h-7 w-7 text-white" />
                    </div>
                  </div>
                  <div className="flex-1 pt-2 pb-6 border-b border-slate-800/60 last:border-0">
                    <div className="flex items-center gap-3 mb-1">
                      <span className="text-xs font-mono text-indigo-400 font-bold">
                        Step {num}
                      </span>
                    </div>
                    <h3 className="text-lg font-semibold text-white mb-1">{title}</h3>
                    <p className="text-sm text-slate-400 leading-relaxed">{desc}</p>
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
    <section className="py-24 bg-[#04060f]">
      <div className="max-w-6xl mx-auto px-6">
        <AnimatedSection>
          <motion.div variants={fadeUp} className="text-center mb-16">
            <p className="text-indigo-400 font-semibold text-sm uppercase tracking-widest mb-3">
              Benefits
            </p>
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
              Why Organizations Choose Our Platform
            </h2>
          </motion.div>

          <motion.div
            variants={staggerContainer}
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6"
          >
            {benefits.map(({ icon: Icon, title, desc, stat, statLabel }) => (
              <motion.div
                key={title}
                variants={fadeUp}
                className="relative p-6 rounded-2xl border border-slate-800 bg-slate-900/50 hover:border-indigo-500/40 transition-all duration-300 group overflow-hidden"
              >
                <div className="absolute top-0 right-0 p-4 text-right">
                  <span className="text-3xl font-black bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">
                    {stat}
                  </span>
                  <p className="text-xs text-slate-500 font-medium">{statLabel}</p>
                </div>
                <div className="w-10 h-10 rounded-lg bg-indigo-500/15 flex items-center justify-center mb-4">
                  <Icon className="h-5 w-5 text-indigo-400" />
                </div>
                <h3 className="text-base font-semibold text-white mb-2 pr-16">{title}</h3>
                <p className="text-sm text-slate-400 leading-relaxed">{desc}</p>
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
    <section className="py-20 bg-gradient-to-br from-indigo-950 via-slate-950 to-violet-950 border-y border-indigo-900/40">
      <div className="max-w-6xl mx-auto px-6">
        <AnimatedSection>
          <motion.p variants={fadeUp} className="text-center text-indigo-400 font-semibold text-sm uppercase tracking-widest mb-10">
            Platform Statistics
          </motion.p>
          <motion.div
            variants={staggerContainer}
            className="grid grid-cols-2 lg:grid-cols-4 gap-6"
          >
            {stats.map(({ value, label, icon: Icon }) => (
              <motion.div
                key={value}
                variants={fadeUp}
                className="text-center p-6 rounded-2xl border border-indigo-800/40 bg-indigo-900/20 backdrop-blur-sm"
              >
                <div className="w-12 h-12 rounded-xl bg-indigo-500/20 flex items-center justify-center mx-auto mb-4">
                  <Icon className="h-6 w-6 text-indigo-400" />
                </div>
                <div className="text-3xl font-black text-white mb-2">{value}</div>
                <p className="text-xs text-slate-400 leading-tight">{label}</p>
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
    <section id="resources" className="py-24 bg-slate-950">
      <div className="max-w-3xl mx-auto px-6">
        <AnimatedSection>
          <motion.div variants={fadeUp} className="text-center mb-12">
            <p className="text-indigo-400 font-semibold text-sm uppercase tracking-widest mb-3">FAQ</p>
            <h2 className="text-3xl sm:text-4xl font-bold text-white">Frequently Asked Questions</h2>
          </motion.div>

          <motion.div variants={staggerContainer} className="space-y-3">
            {faqs.map(({ q, a }, idx) => (
              <motion.div
                key={idx}
                variants={fadeUp}
                className="border border-slate-800 rounded-xl overflow-hidden bg-slate-900/50"
              >
                <button
                  id={`faq-${idx}`}
                  onClick={() => setOpenIdx(openIdx === idx ? null : idx)}
                  className="w-full flex items-center justify-between px-6 py-4 text-left text-white font-medium hover:bg-slate-800/50 transition-colors"
                >
                  <span className="pr-4">{q}</span>
                  {openIdx === idx ? (
                    <ChevronUp className="h-4 w-4 text-indigo-400 flex-shrink-0" />
                  ) : (
                    <ChevronDown className="h-4 w-4 text-slate-400 flex-shrink-0" />
                  )}
                </button>
                {openIdx === idx && (
                  <div className="px-6 pb-5 text-sm text-slate-400 leading-relaxed border-t border-slate-800">
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
    <section id="contact" className="py-24 bg-[#04060f] relative overflow-hidden">
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[400px] bg-indigo-700/20 rounded-full blur-[100px]" />
        <div className="absolute top-0 right-0 w-[400px] h-[300px] bg-violet-600/10 rounded-full blur-[100px]" />
      </div>
      <div className="relative max-w-4xl mx-auto px-6 text-center">
        <AnimatedSection>
          <motion.div
            variants={fadeUp}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-indigo-500/40 bg-indigo-500/10 text-indigo-300 text-sm font-medium mb-8"
          >
            <Star className="h-4 w-4" />
            <span>Ready to Transform Your Consulting?</span>
          </motion.div>

          <motion.h2
            variants={fadeUp}
            className="text-4xl sm:text-5xl font-bold text-white mb-6 leading-tight"
          >
            Ready to Modernize Your{" "}
            <span className="bg-gradient-to-r from-indigo-400 via-violet-400 to-cyan-400 bg-clip-text text-transparent">
              Consulting Process?
            </span>
          </motion.h2>

          <motion.p variants={fadeUp} className="text-slate-400 text-lg mb-10 max-w-2xl mx-auto">
            Deliver consulting projects faster with AI-powered requirement analysis, intelligent
            documentation, and streamlined collaboration.
          </motion.p>

          <motion.div variants={fadeUp} className="flex flex-wrap items-center justify-center gap-4">
            <button
              onClick={() => navigate("/login")}
              className="inline-flex items-center gap-2 px-8 py-4 rounded-full bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white font-semibold text-base shadow-2xl shadow-indigo-900/50 transition-all duration-200 hover:scale-105"
            >
              Get Started <ArrowRight className="h-4 w-4" />
            </button>
            <a
              href="#how-it-works"
              className="inline-flex items-center gap-2 px-8 py-4 rounded-full border border-slate-600 bg-white/5 hover:bg-white/10 text-slate-200 font-semibold text-base backdrop-blur-sm transition-all duration-200 hover:border-slate-400"
            >
              Request Demo
            </a>
          </motion.div>
        </AnimatedSection>
      </div>
    </section>
  );
}

// ─── FOOTER ───────────────────────────────────────────────────────────────────
function Footer() {
  const footerLinks = {
    Product: ["Platform", "Features", "Solutions", "Pricing"],
    Resources: ["Documentation", "Blog", "FAQs", "Support"],
    Company: ["About Us", "Contact", "Careers"],
    Legal: ["Privacy Policy", "Terms of Service"],
  };

  return (
    <footer className="bg-slate-950 border-t border-slate-800/60">
      <div className="max-w-6xl mx-auto px-6 py-16">
        <div className="grid grid-cols-2 md:grid-cols-6 gap-10 mb-12">
          {/* Brand */}
          <div className="col-span-2">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center">
                <Cpu className="h-4 w-4 text-white" />
              </div>
              <span className="text-white font-bold text-sm">Consulting Delivery OS</span>
            </div>
            <p className="text-sm text-slate-400 leading-relaxed mb-6">
              The intelligent platform for modern consulting teams. Delivering projects faster with AI.
            </p>
            <div className="space-y-2 text-sm text-slate-400">
              <p>
                <span className="text-slate-500">Email:</span>{" "}
                <a href="mailto:info@yourcompany.com" className="hover:text-indigo-400 transition-colors">
                  info@yourcompany.com
                </a>
              </p>
              <p>
                <span className="text-slate-500">Phone:</span> +91 XXXXX XXXXX
              </p>
              <p>
                <span className="text-slate-500">Web:</span>{" "}
                <a href="#" className="hover:text-indigo-400 transition-colors">
                  www.yourcompany.com
                </a>
              </p>
            </div>
          </div>

          {/* Links */}
          {Object.entries(footerLinks).map(([category, links]) => (
            <div key={category}>
              <h4 className="text-white font-semibold text-sm mb-4">{category}</h4>
              <ul className="space-y-2.5">
                {links.map((link) => (
                  <li key={link}>
                    <a
                      href="#"
                      className="text-sm text-slate-400 hover:text-indigo-400 transition-colors"
                    >
                      {link}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-8 border-t border-slate-800/60">
          <p className="text-sm text-slate-500">
            © 2026 Consulting Delivery OS. All rights reserved.
          </p>
          <div className="flex items-center gap-1">
            {[...Array(5)].map((_, i) => (
              <Star key={i} className="h-3.5 w-3.5 text-amber-400 fill-amber-400" />
            ))}
            <span className="text-xs text-slate-500 ml-1.5">Loved by 500+ consulting teams</span>
          </div>
        </div>
      </div>
    </footer>
  );
}

// ─── MAIN PAGE ────────────────────────────────────────────────────────────────
export default function LandingPage() {
  return (
    <div className="min-h-screen">
      <AnimatedNavFramer />
      <HeroSection />
      <TrustedBySection />
      <PlatformOverviewSection />
      <WhyChooseSection />
      <CoreFeaturesSection />
      <HowItWorksSection />
      <BenefitsSection />
      <StatsSection />
      <FAQSection />
      <FinalCTASection />
      <Footer />
    </div>
  );
}
