import React, { useState } from "react";
import { motion, useInView } from "framer-motion";
import { Mail, Headset, Phone, MapPin, ArrowRight, Clock, Loader2, AlertCircle } from "lucide-react";
import LandingNavbar from "../../components/LandingNavbar";
import LandingFooter from "../../components/LandingFooter";
import { contactService, getApiError } from "../../services/api";
import "../../styles/pages/marketing/ContactPage.css";

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

const inputClass = "contact-input";

const labelClass = "contact-label";

const INQUIRY_TYPE_MAP = {
  "Sales & Integration": "sales",
  "Technical Support": "support",
  Partnership: "partnership",
  Other: "other",
};

function ContactForm() {
  const [form, setForm] = useState({
    firstName: "",
    lastName: "",
    email: "",
    type: "Sales & Integration",
    message: "",
  });
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      await contactService.submit({
        first_name: form.firstName,
        last_name: form.lastName,
        email: form.email,
        inquiry_type: INQUIRY_TYPE_MAP[form.type] || "other",
        message: form.message,
      });
      setSubmitted(true);
    } catch (err) {
      setError(getApiError(err, "Unable to send your message. Please try again."));
    } finally {
      setSubmitting(false);
    }
  };

  const reset = () => {
    setSubmitted(false);
    setError("");
    setForm({ firstName: "", lastName: "", email: "", type: "Sales & Integration", message: "" });
  };

  return (
    <div className="contact-form-card">
      <div className="contact-form-bar" />
      <h2 className="contact-form-title">Send a Message</h2>

      {submitted ? (
        <div className="contact-success">
          <div className="contact-success-icon">
            <Mail className="h-7 w-7 text-emerald-500 dark:text-emerald-400" />
          </div>
          <h3 className="contact-success-title">Thank you!</h3>
          <p className="contact-success-text">
            Your message has been received. Our team will get back to you within one business day.
          </p>
          <button
            onClick={reset}
            className="contact-reset-btn"
          >
            Send another message
          </button>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="contact-form">
          <div>
            <label className={labelClass}>First Name</label>
            <input
              name="firstName"
              value={form.firstName}
              onChange={handleChange}
              required
              className={inputClass}
              placeholder="Jane"
              type="text"
            />
          </div>
          <div>
            <label className={labelClass}>Last Name</label>
            <input
              name="lastName"
              value={form.lastName}
              onChange={handleChange}
              required
              className={inputClass}
              placeholder="Doe"
              type="text"
            />
          </div>
          <div className="md:col-span-2">
            <label className={labelClass}>Work Email</label>
            <input
              name="email"
              value={form.email}
              onChange={handleChange}
              required
              className={inputClass}
              placeholder="jane@company.com"
              type="email"
            />
          </div>
          <div className="md:col-span-2">
            <label className={labelClass}>Inquiry Type</label>
            <select
              name="type"
              value={form.type}
              onChange={handleChange}
              className="contact-select"
            >
              <option>Sales & Integration</option>
              <option>Technical Support</option>
              <option>Partnership</option>
              <option>Other</option>
            </select>
          </div>
          <div className="md:col-span-2">
            <label className={labelClass}>Message</label>
            <textarea
              name="message"
              value={form.message}
              onChange={handleChange}
              required
              className={inputClass + " h-32 resize-none"}
              placeholder="How can we help you accelerate your AI initiatives?"
            />
          </div>
          <div className="md:col-span-2 pt-2">
            {error && (
              <div className="contact-error">
                <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                <span>{error}</span>
              </div>
            )}
            <button
              type="submit"
              disabled={submitting}
              className="contact-submit-btn"
            >
              {submitting ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" /> Sending...
                </>
              ) : (
                <>
                  Submit Request <ArrowRight className="h-4 w-4" />
                </>
              )}
            </button>
          </div>
        </form>
      )}
    </div>
  );
}

export default function ContactPage() {
  return (
    <div className="contact-page">
      <LandingNavbar />

      <main className="contact-main">
        <section className="contact-hero">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
            <p className="contact-eyebrow">
              Contact
            </p>
            <h1 className="contact-h1">
              Get in touch
            </h1>
            <p className="contact-hero-p">
              Whether you're looking to integrate our AI solutions, need technical support, or want to
              explore partnership opportunities, our expert team is ready to assist you.
            </p>
          </motion.div>
        </section>

        <AnimatedSection>
          <div className="contact-grid">
            <motion.div variants={fadeUp} className="lg:col-span-8">
              <ContactForm />
            </motion.div>

            <div className="contact-side">
              <motion.div
                variants={fadeUp}
                className="contact-card"
              >
                <h3 className="contact-card-h3">
                  Direct Channels
                </h3>
                <div className="contact-channel mb-5 mt-3">
                  <div className="contact-channel-icon">
                    <Mail className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="contact-channel-title">Sales Inquiry</p>
                    <p className="contact-channel-value">sales@synthetix.ai</p>
                  </div>
                </div>
                <div className="contact-channel mb-5">
                  <div className="contact-channel-icon">
                    <Headset className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="contact-channel-title">Technical Support</p>
                    <p className="contact-channel-value">support@synthetix.ai</p>
                  </div>
                </div>
                <div className="contact-channel">
                  <div className="contact-channel-icon">
                    <Phone className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="contact-channel-title">Phone</p>
                    <p className="contact-channel-value">+1 (800) 555-0199</p>
                  </div>
                </div>
              </motion.div>

              <motion.div
                variants={fadeUp}
                className="contact-card flex-grow"
              >
                <h3 className="contact-card-h3">
                  Global HQ
                </h3>
                <div className="flex items-start gap-4 mt-3">
                  <div className="contact-channel-icon">
                    <MapPin className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="contact-address">
                      100 Innovation Drive
                      <br />
                      Suite 400
                      <br />
                      San Francisco, CA 94105
                      <br />
                      United States
                    </p>
                  </div>
                </div>
                <div className="contact-hours">
                  <p className="contact-hours-title">
                    <Clock className="h-4 w-4 text-indigo-600 dark:text-primary-fixed-dim" />
                    Operating Hours
                  </p>
                  <p className="contact-hours-text">Mon - Fri: 9:00 AM - 6:00 PM PST</p>
                </div>
              </motion.div>
            </div>

            <motion.div
              variants={fadeUp}
              className="contact-cta-banner"
            >
              <div className="contact-cta-glow" />
              <div className="contact-cta-text">
                <h2 className="contact-cta-title">Ready to see the platform in action?</h2>
                <p className="contact-cta-desc">
                  Schedule a personalized 1-on-1 demo with an AI solution architect to explore how our
                  platform can optimize your specific workflows.
                </p>
              </div>
              <button className="contact-demo-btn">
                Request a Demo
              </button>
            </motion.div>
          </div>
        </AnimatedSection>
      </main>

      <LandingFooter />
    </div>
  );
}
