import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion, useInView } from "framer-motion";
import { Check, CheckCircle2, ArrowRight } from "lucide-react";
import LandingNavbar from "../../components/LandingNavbar";
import LandingFooter from "../../components/LandingFooter";
import "./PricingPage.css";

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

const MONTHLY = "monthly";
const ANNUAL = "annual";

function FeatureIcon({ filled = false }) {
  return filled ? (
    <CheckCircle2 className="h-5 w-5 text-emerald-500 dark:text-primary-fixed-dim flex-shrink-0" />
  ) : (
    <Check className="h-5 w-5 text-emerald-500 dark:text-primary-fixed-dim flex-shrink-0" />
  );
}

function BillingToggle({ billing, onChange }) {
  return (
    <div className="pricing-toggle-row">
      <button
        onClick={() => onChange(MONTHLY)}
        className={`pricing-toggle-btn ${
          billing === MONTHLY ? "text-slate-900 dark:text-white font-semibold" : "text-slate-500 dark:text-white/70"
        }`}
      >
        Billed Monthly
      </button>
      <button
        role="switch"
        aria-checked={billing === ANNUAL}
        onClick={() => onChange(billing === ANNUAL ? MONTHLY : ANNUAL)}
        className={`pricing-toggle-switch ${
          billing === ANNUAL ? "bg-indigo-600" : "bg-slate-300 dark:bg-white/10"
        }`}
      >
        <div
          className={`pricing-toggle-knob ${
            billing === ANNUAL
              ? "translate-x-6 bg-white"
              : "translate-x-0 bg-slate-500 dark:bg-white/70"
          }`}
        />
      </button>
      <span className="pricing-toggle-annual">
        Billed Annually{" "}
        <span className="pricing-toggle-save">(Save 20%)</span>
      </span>
    </div>
  );
}

function PlanCard({ plan, highlighted = false }) {
  const navigate = useNavigate();
  const price = plan.annualPrice ?? plan.price;

  return (
    <div
      className={`pricing-card ${
        highlighted
          ? "pricing-card-highlighted"
          : "pricing-card-plain"
      }`}
    >
      {highlighted && (
        <div className="pricing-badge">
          MOST POPULAR
        </div>
      )}
      <h3 className="pricing-plan-name">{plan.name}</h3>
      <p className="pricing-plan-desc">{plan.description}</p>
      <div className="mb-8">
        <span className="pricing-price">{price}</span>
        {price !== "Custom" ? (
          <span className="pricing-price-suffix">/user/mo</span>
        ) : (
          <span className="pricing-price-suffix block mt-2">
            Tailored to your needs
          </span>
        )}
      </div>
      <button
        onClick={() => navigate(plan.cta === "Contact Sales" ? "/contact" : "/signup")}
        className={`pricing-cta-btn ${
          highlighted
            ? "pricing-cta-highlighted"
            : plan.cta === "Contact Sales"
            ? "pricing-cta-sales"
            : "pricing-cta-default"
        }`}
      >
        {plan.cta}
      </button>
      <ul className="pricing-features">
        {plan.features.map((feature) => (
          <li
            key={feature}
            className={`pricing-feature ${
              feature.endsWith("plus:") || feature.includes("plus:")
                ? "pricing-feature-strong"
                : "pricing-feature-normal"
            }`}
          >
            <FeatureIcon filled={highlighted && feature.includes("plus")} />
            {feature}
          </li>
        ))}
      </ul>
    </div>
  );
}

function CompareTable({ billing }) {
  const rows = [
    { feature: "Core AI Models", starter: "Standard", pro: "Advanced", ent: "Custom" },
    { feature: "Data Processing", starter: "10GB/mo", pro: "100GB/mo", ent: "Unlimited" },
    { feature: "API Rate Limit", starter: "60/min", pro: "600/min", ent: "Custom" },
    { feature: "SLA Guarantee", starter: "—", pro: "99.9%", ent: "99.99%" },
    { feature: "Dedicated Server Instance", starter: "—", pro: "—", ent: "✔" },
  ];

  return (
    <div className="overflow-x-auto">
      <table className="pricing-table">
        <thead>
          <tr className="pricing-table-head">
            <th className="pricing-th rounded-tl-2xl w-1/3">
              Features
            </th>
            <th className="pricing-th text-center">
              Starter
            </th>
            <th className="pricing-th-pro">
              Professional
            </th>
            <th className="pricing-th text-center rounded-tr-2xl">
              Enterprise
            </th>
          </tr>
        </thead>
        <tbody className="text-sm">
          {rows.map((row, idx) => (
            <tr
              key={row.feature}
              className={`pricing-tr ${
                idx % 2 === 1 ? "pricing-tr-zebra" : ""
              }`}
            >
              <td className="pricing-td-feature">{row.feature}</td>
              <td className="pricing-td">{row.starter}</td>
              <td className="pricing-td-pro">
                {row.pro}
              </td>
              <td className="pricing-td">{row.ent}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="pricing-note">
        {billing === ANNUAL ? "Annual billing applied" : "Monthly billing applied"}
      </p>
    </div>
  );
}

export default function PricingPage() {
  const [billing, setBilling] = useState(ANNUAL);

  const plans = [
    {
      name: "Starter",
      description: "Perfect for small teams beginning their AI journey.",
      price: billing === ANNUAL ? "$39" : "$49",
      cta: "Start Free Trial",
      features: ["Up to 5 Users", "Basic Generative Models", "Community Support", "100k API Requests/mo"],
    },
    {
      name: "Professional",
      description: "Advanced capabilities for growing organizations.",
      price: billing === ANNUAL ? "$119" : "$149",
      cta: "Get Started",
      highlighted: true,
      features: [
        "Everything in Starter, plus:",
        "Up to 50 Users",
        "Custom Model Fine-tuning",
        "Priority Email Support",
        "1M API Requests/mo",
        "Advanced Analytics Dashboard",
      ],
    },
    {
      name: "Enterprise",
      description: "Custom deployment for large-scale operations.",
      price: "Custom",
      cta: "Contact Sales",
      features: [
        "Unlimited Users",
        "On-Premise Deployment Options",
        "24/7 Dedicated Account Manager",
        "Unlimited API Requests",
        "SSO & Advanced Security",
      ],
    },
  ];

  return (
    <div className="pricing-page">
      <LandingNavbar />

      <main className="pricing-main">
        <section className="pricing-hero">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <p className="pricing-eyebrow">
              Pricing
            </p>
            <h1 className="pricing-h1">
              Scalable Intelligence for{" "}
              <span className="pricing-gradient">
                Modern Enterprises
              </span>
            </h1>
            <p className="pricing-hero-p">
              Choose the right deployment model for your team. From rapid prototyping to full-scale
              infrastructure integration, we provide transparent pricing with no hidden fees.
            </p>
            <BillingToggle billing={billing} onChange={setBilling} />
          </motion.div>
        </section>

        <AnimatedSection>
          <section className="pricing-plans">
            {plans.map((plan) => (
              <motion.div key={plan.name} variants={fadeUp} className="h-full">
                <PlanCard plan={plan} highlighted={plan.highlighted} />
              </motion.div>
            ))}
          </section>
        </AnimatedSection>

        <AnimatedSection>
          <section className="pricing-compare">
            <h2 className="pricing-compare-title">
              Compare Features
            </h2>
            <CompareTable billing={billing} />
          </section>
        </AnimatedSection>
      </main>

      <LandingFooter />
    </div>
  );
}
