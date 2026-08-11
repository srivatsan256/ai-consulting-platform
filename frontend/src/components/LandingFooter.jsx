import React from "react";
import { Cpu, Star } from "lucide-react";

const footerLinks = {
  Product: ["Platform", "Features", "Solutions", "Pricing"],
  Resources: ["Documentation", "Blog", "FAQs", "Support"],
  Company: ["About Us", "Contact", "Careers"],
  Legal: ["Privacy Policy", "Terms of Service"],
};

export default function LandingFooter() {
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
