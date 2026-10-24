import Link from "next/link";
import { ShieldCheck, Scale, FileText, Lock } from "lucide-react";
import { BrandIcon } from "@/components/layout/brand-icon";
import { vcopy } from "@/lib/verification-copy";

export function Footer() {
  return (
    <footer className="border-t border-zinc-800/80 bg-zinc-950/80 backdrop-blur-xl mt-auto">
      <div className="container max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-16">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 lg:gap-12">
          {/* Brand & Mission */}
          <div className="space-y-4 md:col-span-1">
            <Link href="/" className="flex items-center space-x-2.5 group">
              <div className="h-9 w-9 rounded-lg bg-gradient-to-br from-violet-500 via-indigo-600 to-sky-500 p-0.5 shadow-lg shadow-violet-500/20 group-hover:shadow-violet-500/40 transition-all duration-300">
                <div className="h-full w-full bg-zinc-950 rounded-[6px] flex items-center justify-center p-1.5">
                  <BrandIcon className="w-full h-full group-hover:scale-110 transition-transform duration-300" />
                </div>
              </div>
              <div className="flex flex-col">
                <span className="font-bold text-sm tracking-tight text-zinc-100 flex items-center gap-1.5">
                  FindJobFit
                  <span className="text-[10px] font-mono font-medium px-1.5 py-0.5 rounded bg-violet-500/10 text-violet-400 border border-violet-500/20">
                    PLATFORM
                  </span>
                </span>
                <span className="text-[10px] text-zinc-400 font-sans">Deterministic AI Pipeline</span>
              </div>
            </Link>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Enterprise-grade job discovery and CV engineering with a strict mathematical anti-hallucination gate. Grounded in German and EU compliance.
            </p>
            <div className="flex items-center gap-2 text-[11px] font-mono text-emerald-400 bg-emerald-950/30 border border-emerald-800/30 px-2.5 py-1 rounded-md w-fit">
              <ShieldCheck className="h-3.5 w-3.5" />
              <span>EU AI Act &amp; DSGVO Compliant</span>
            </div>
          </div>

          {/* Navigation Links */}
          <div className="space-y-3">
            <h4 className="text-xs font-semibold text-zinc-200 uppercase tracking-wider font-mono">Platform</h4>
            <ul className="space-y-2 text-xs text-zinc-400">
              <li>
                <Link href="/onboarding" className="hover:text-zinc-200 transition-colors">
                  Getting Started
                </Link>
              </li>
              <li>
                <Link href="/cv-upload" className="hover:text-zinc-200 transition-colors">
                  CV Ingestion
                </Link>
              </li>
              <li>
                <Link href="/profile" className="hover:text-zinc-200 transition-colors">
                  {vcopy("bank.name")}
                </Link>
              </li>
              <li>
                <Link href="/preferences" className="hover:text-zinc-200 transition-colors">
                  Candidate Preferences
                </Link>
              </li>
              <li>
                <Link href="/jobs" className="hover:text-zinc-200 transition-colors">
                  Jobs Feed
                </Link>
              </li>
            </ul>
          </div>

          {/* Legal & Governance */}
          <div className="space-y-3">
            <h4 className="text-xs font-semibold text-zinc-200 uppercase tracking-wider font-mono">Legal &amp; Compliance</h4>
            <ul className="space-y-2 text-xs text-zinc-400">
              <li>
                <Link href="/impressum" className="hover:text-zinc-200 transition-colors flex items-center gap-1.5">
                  <Scale className="h-3 w-3 text-violet-400" />
                  <span>Legal Notice (Imprint / § 5 DDG)</span>
                </Link>
              </li>
              <li>
                <Link href="/privacy" className="hover:text-zinc-200 transition-colors flex items-center gap-1.5">
                  <Lock className="h-3 w-3 text-violet-400" />
                  <span>Privacy Policy (GDPR / BDSG)</span>
                </Link>
              </li>
              <li>
                <Link href="/terms" className="hover:text-zinc-200 transition-colors flex items-center gap-1.5">
                  <FileText className="h-3 w-3 text-violet-400" />
                  <span>Terms of Service (AGB)</span>
                </Link>
              </li>
              <li>
                <Link href="/ethics" className="hover:text-zinc-200 transition-colors flex items-center gap-1.5">
                  <ShieldCheck className="h-3 w-3 text-emerald-400" />
                  <span>Ethics &amp; AI Compliance</span>
                </Link>
              </li>
            </ul>
          </div>

          {/* Ethics & Guarantee */}
          <div className="space-y-3">
            <h4 className="text-xs font-semibold text-zinc-200 uppercase tracking-wider font-mono">Guarantee</h4>
            <p className="text-xs text-zinc-400 leading-relaxed">
              <strong className="text-zinc-300">Zero-Hallucination Guarantee:</strong> {vcopy("footer.guarantee")}
            </p>
            <div className="text-[11px] text-zinc-500 font-mono pt-1">
              Location: Hesse, Germany / EU
            </div>
          </div>
        </div>

        <div className="mt-12 pt-6 border-t border-zinc-800/60 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-zinc-500 font-mono">
          <p>&copy; {new Date().getFullYear()} FindJobFit. All rights reserved.</p>
          <div className="flex items-center space-x-6 text-zinc-400">
            <Link href="/impressum" className="hover:text-zinc-200 transition-colors">
              Legal Notice (Imprint)
            </Link>
            <Link href="/privacy" className="hover:text-zinc-200 transition-colors">
              Privacy Policy
            </Link>
            <Link href="/terms" className="hover:text-zinc-200 transition-colors">
              Terms of Service
            </Link>
            <Link href="/ethics" className="hover:text-zinc-200 transition-colors">
              Ethics Manifest
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
