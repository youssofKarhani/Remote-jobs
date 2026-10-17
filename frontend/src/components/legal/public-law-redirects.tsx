"use client";

import React, { useState } from "react";
import { BookOpen, ExternalLink, ChevronDown, ChevronUp, Scale, Shield, FileCheck } from "lucide-react";
import { useLegalLanguage } from "./legal-context";
import { cn } from "@/lib/utils";

interface LawEntry {
  categoryEn: string;
  categoryDe: string;
  items: Array<{
    code: string;
    nameEn: string;
    nameDe: string;
    authority: string;
    url: string;
    purposeEn: string;
    purposeDe: string;
  }>;
}

const PUBLIC_LAWS: LawEntry[] = [
  {
    categoryEn: "Digital Services & Provider Transparency",
    categoryDe: "Digitale Dienste & Anbieterkennzeichnung",
    items: [
      {
        code: "§ 5 DDG",
        nameEn: "Digital Services Act Germany (Digitale-Dienste-Gesetz)",
        nameDe: "Digitale-Dienste-Gesetz (ehemals § 5 TMG)",
        authority: "Federal Ministry of Justice (BMJ)",
        url: "https://www.gesetze-im-internet.de/ddg/__5.html",
        purposeEn: "Statutory provider identification, physical address, and rapid electronic contact requirements.",
        purposeDe: "Gesetzliche Anbieterkennzeichnung, ladungsfähige Anschrift und Pflichtangaben zur schnellen Kontaktaufnahme.",
      },
      {
        code: "§ 18 Abs. 2 MStV",
        nameEn: "State Media Treaty (Medienstaatsvertrag)",
        nameDe: "Medienstaatsvertrag",
        authority: "Die Medienanstalten (DLM)",
        url: "https://www.die-medienanstalten.de/service/rechtsgrundlagen/medienstaatsvertrag-mstv",
        purposeEn: "Designation of an editorially responsible person for platform-provided informational texts.",
        purposeDe: "Benennung der inhaltlich und redaktionell verantwortlichen Person für redaktionelle Inhalte.",
      },
      {
        code: "EU Regulation 2022/2065 (DSA)",
        nameEn: "EU Digital Services Act",
        nameDe: "EU-Gesetz über digitale Dienste (Digital Services Act)",
        authority: "EUR-Lex (Official Journal of the European Union)",
        url: "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R2065",
        purposeEn: "Harmonized EU rules on intermediary service provider liability, notice-and-action, and illegal content.",
        purposeDe: "Harmonisierte EU-Haftungsregeln für Vermittlungsdienste, Host-Provider-Privileg und Notice-and-Action-Verfahren.",
      },
      {
        code: "§ 44b UrhG & Directive (EU) 2019/790",
        nameEn: "German Copyright Act: Text & Data Mining",
        nameDe: "Urheberrechtsgesetz: Text und Data Mining (§ 44b UrhG)",
        authority: "Federal Ministry of Justice (BMJ)",
        url: "https://www.gesetze-im-internet.de/urhg/__44b.html",
        purposeEn: "Statutory authorization for algorithmic analysis and indexing of publicly accessible job openings.",
        purposeDe: "Gesetzliche Schrankenregelung zur automatisierten Erfassung öffentlich zugänglicher Stellenangebote.",
      },
    ],
  },
  {
    categoryEn: "Data Privacy & Telecommunications",
    categoryDe: "Datenschutz & Telekommunikation",
    items: [
      {
        code: "Regulation (EU) 2016/679 (GDPR / DSGVO)",
        nameEn: "General Data Protection Regulation",
        nameDe: "Datenschutz-Grundverordnung (DSGVO)",
        authority: "EUR-Lex (European Union)",
        url: "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32016R0679",
        purposeEn: "Articles 5, 6, 12-23, and 77 regulating candidate personal data, access, rectification, and erasure.",
        purposeDe: "Art. 5, 6, 12-23 und 77 zur transparenten Verarbeitung, Löschung und Betroffenenrechten bei Nutzerdaten.",
      },
      {
        code: "§ 26 BDSG",
        nameEn: "Federal Data Protection Act (Applicant Data)",
        nameDe: "Bundesdatenschutzgesetz: Beschäftigtendatenschutz",
        authority: "Federal Ministry of the Interior (BMI)",
        url: "https://www.gesetze-im-internet.de/bdsg_2018/__26.html",
        purposeEn: "Processing of employment and qualification data exclusively for the purpose of candidate job matching.",
        purposeDe: "Rechtliche Grundlage für die Verarbeitung von Qualifikations- und Bewerberdaten zur Arbeitsvermittlung.",
      },
      {
        code: "§ 25 TDDDG",
        nameEn: "Telecommunications Digital Services Data Protection Act",
        nameDe: "Telekommunikation-Digitale-Dienste-Datenschutz-Gesetz",
        authority: "Federal Ministry of Justice (BMJ)",
        url: "https://www.gesetze-im-internet.de/tdddg/__25.html",
        purposeEn: "Privacy exception for strictly necessary terminal storage (JWT session tokens, no tracking cookies).",
        purposeDe: "Schutz der Privatsphäre bei Endeinrichtungen: Technisch notwendige Speicherung ohne Tracking-Cookies.",
      },
      {
        code: "HBDI Hessen",
        nameEn: "Hesse Commissioner for Data Protection & FOI",
        nameDe: "Der Hessische Beauftragte für Datenschutz und Informationsfreiheit",
        authority: "State of Hesse Data Protection Authority",
        url: "https://datenschutz.hessen.de",
        purposeEn: "Direct statutory supervisory authority for lodging complaints under Article 77 GDPR.",
        purposeDe: "Zuständige Landesaufsichtsbehörde für das Beschwerderecht der Nutzer gemäß Art. 77 DSGVO.",
      },
      {
        code: "EU-US Data Privacy Framework",
        nameEn: "Data Privacy Framework (DPF Program)",
        nameDe: "EU-US Data Privacy Framework",
        authority: "U.S. Department of Commerce & European Commission",
        url: "https://www.dataprivacyframework.gov",
        purposeEn: "Adequacy framework governing international cloud hosting providers (Railway / AWS infrastructure).",
        purposeDe: "Angemessenheitsbeschluss für transatlantische Datenübermittlungen an US-Cloudanbieter.",
      },
    ],
  },
  {
    categoryEn: "AI Governance, Consumer Rights & Contract Law",
    categoryDe: "KI-Verordnung, Verbraucherschutz & Vertragsrecht",
    items: [
      {
        code: "Regulation (EU) 2024/1689 (EU AI Act)",
        nameEn: "EU Artificial Intelligence Act",
        nameDe: "EU-Verordnung über Künstliche Intelligenz (AI Act)",
        authority: "EUR-Lex (European Union)",
        url: "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689",
        purposeEn: "Annex III high-risk boundaries, Article 13 transparency, Article 14 human oversight, and Article 50 GPAI.",
        purposeDe: "Einstufung nach Anhang III, menschliche Aufsicht (Art. 14), Transparenz (Art. 13) und Zero-Hallucination-Invariante.",
      },
      {
        code: "AGG (Antidiskriminierungsgesetz)",
        nameEn: "General Equal Treatment Act (AGG)",
        nameDe: "Allgemeines Gleichbehandlungsgesetz",
        authority: "Federal Anti-Discrimination Agency (ADS)",
        url: "https://www.antidiskriminierungsstelle.de",
        purposeEn: "Objective merit-based matching and neutral filtering avoiding protected category discrimination.",
        purposeDe: "Schutz vor Benachteiligung: Geschlechtsneutrales Titel-Sanitizing und objektive Kompetenzbewertung.",
      },
      {
        code: "§§ 305 ff. & § 312i BGB",
        nameEn: "German Civil Code (Standard Terms & E-Commerce)",
        nameDe: "Bürgerliches Gesetzbuch: AGB-Recht & E-Commerce",
        authority: "Federal Ministry of Justice (BMJ)",
        url: "https://www.gesetze-im-internet.de/bgb/__305.html",
        purposeEn: "Consumer contract formation, electronic communication duties, and statutory limitation of liability.",
        purposeDe: "Transparente AGB-Regelungen, Pflichten im elektronischen Geschäftsverkehr und gesetzliche Haftungsordnung.",
      },
      {
        code: "§ 123 BGB & § 267 StGB",
        nameEn: "Civil & Criminal Truth Invariants",
        nameDe: "Schutz vor Täuschung (§ 123 BGB) & Urkundenfälschung",
        authority: "Federal Ministry of Justice (BMJ)",
        url: "https://www.gesetze-im-internet.de/bgb/__123.html",
        purposeEn: "Platform mathematical guarantees ensuring users cannot inadvertently submit fraudulent qualifications.",
        purposeDe: "Mathematische Garantie gegen Bewerbungsbetrug, arglistige Täuschung und Arbeitsrechtsfolgen.",
      },
      {
        code: "§ 36 VSBG & EU ODR Platform",
        nameEn: "Consumer Dispute Resolution / EU ODR",
        nameDe: "Verbraucherstreitbeilegung & OS-Plattform",
        authority: "European Commission & BfJ",
        url: "https://ec.europa.eu/consumers/odr",
        purposeEn: "Mandatory statutory link to the EU Online Dispute Resolution platform and national arbitration board.",
        purposeDe: "Gesetzlich vorgeschriebener Link zur europäischen Plattform zur Online-Streitbeilegung.",
      },
    ],
  },
];

export function PublicLawRedirects({ className }: { className?: string }) {
  const { language } = useLegalLanguage();
  const [isOpen, setIsOpen] = useState(false);
  const isEn = language === "en";

  return (
    <div
      className={cn(
        "rounded-2xl border border-zinc-800 bg-zinc-900/40 p-6 md:p-8 space-y-6 backdrop-blur-sm",
        className
      )}
    >
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2 text-violet-400 font-mono text-xs uppercase tracking-wider">
            <BookOpen className="h-4 w-4" />
            <span>{isEn ? "Statutory Public Law Directory" : "Gesetzliches Normen- & Linkverzeichnis"}</span>
          </div>
          <h3 className="text-lg md:text-xl font-bold text-zinc-100 flex items-center gap-2">
            <Scale className="h-5 w-5 text-violet-400" />
            <span>
              {isEn ? "Direct Redirects to Official German & EU Statutes" : "Direktverweise zu amtlichen deutschen & EU-Gesetzestexten"}
            </span>
          </h3>
          <p className="text-xs md:text-sm text-zinc-400 max-w-2xl">
            {isEn
              ? "All statutory authorities, directives, and dispute bodies cited across our platform are linked directly below to official government gazettes."
              : "Alle zitierten Bundesgesetze, EU-Verordnungen und Aufsichtsbehörden sind hier mit ihren amtlichen Gesetzesblättern verknüpft."}
          </p>
        </div>

        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          className="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-zinc-800/80 hover:bg-zinc-800 text-zinc-200 border border-zinc-700/60 transition-colors shrink-0"
        >
          <span>{isOpen ? (isEn ? "Collapse Directory" : "Verzeichnis einklappen") : (isEn ? "Explore Official Statutes" : "Amtliche Gesetzestexte einsehen")}</span>
          {isOpen ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
        </button>
      </div>

      {isOpen && (
        <div className="space-y-6 pt-4 border-t border-zinc-800/80 animate-in fade-in duration-200">
          {PUBLIC_LAWS.map((category) => (
            <div key={category.categoryEn} className="space-y-3">
              <h4 className="text-xs font-bold font-mono uppercase tracking-wider text-violet-400/90 flex items-center gap-2">
                <FileCheck className="h-3.5 w-3.5" />
                <span>{isEn ? category.categoryEn : category.categoryDe}</span>
              </h4>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {category.items.map((item) => (
                  <a
                    key={item.code}
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="group block p-3.5 rounded-xl bg-zinc-950/60 border border-zinc-800/80 hover:border-violet-500/50 hover:bg-zinc-900/70 transition-all duration-200 space-y-1.5"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-mono text-xs font-bold text-violet-300 group-hover:text-violet-200">
                        {item.code}
                      </span>
                      <ExternalLink className="h-3.5 w-3.5 text-zinc-500 group-hover:text-violet-400 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-all" />
                    </div>

                    <p className="text-xs font-semibold text-zinc-200 leading-snug">
                      {isEn ? item.nameEn : item.nameDe}
                    </p>

                    <div className="flex items-center gap-1.5 text-[10px] font-mono text-emerald-400/90">
                      <Shield className="h-2.5 w-2.5" />
                      <span>{item.authority}</span>
                    </div>

                    <p className="text-[11px] text-zinc-400 leading-relaxed pt-0.5">
                      {isEn ? item.purposeEn : item.purposeDe}
                    </p>
                  </a>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
