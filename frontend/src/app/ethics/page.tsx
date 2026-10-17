import type { Metadata } from "next";
import { LegalPageShell } from "@/components/legal/legal-page-shell";
import { ShieldCheck, CheckCircle2, HeartHandshake, Scale, Lock, Eye, Sparkles, ExternalLink, ShieldAlert, Cpu } from "lucide-react";

export const metadata: Metadata = {
  title: "Ethics & AI Compliance | FindJobFit",
  description: "Comprehensive ethical framework and European statutory compliance: EU AI Act (Regulation (EU) 2024/1689), GDPR, BDSG § 26, and AGG.",
};

const LAW_REFS = [
  {
    code: "EU AI Act (2024/1689)",
    url: "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689",
    title: "Regulation (EU) 2024/1689 (Harmonised Rules on AI)",
  },
  {
    code: "AGG (Antidiskriminierung)",
    url: "https://www.gesetze-im-internet.de/agg/",
    title: "General Equal Treatment Act (Allgemeines Gleichbehandlungsgesetz)",
  },
  {
    code: "Antidiskriminierungsstelle",
    url: "https://www.antidiskriminierungsstelle.de",
    title: "Federal Anti-Discrimination Agency of Germany",
  },
  {
    code: "§ 123 & § 626 BGB",
    url: "https://www.gesetze-im-internet.de/bgb/__123.html",
    title: "German Civil Code: Protection Against Deception & Termination for Cause",
  },
  {
    code: "§ 44b UrhG",
    url: "https://www.gesetze-im-internet.de/urhg/__44b.html",
    title: "German Copyright Act: Text and Data Mining",
  },
];

export default function EthicsPage() {
  return (
    <LegalPageShell
      badgeTextEn="Ethical Charter &amp; Regulatory Alignment"
      badgeTextDe="Ethische Leitlinien &amp; Rechtskonformität"
      titleEn="Ethical Manifest &amp; EU Legal Concept"
      titleDe="Ethisches Manifest &amp; Deutsches Gesetzeskonzept"
      descriptionEn="Why deploying the FindJobFit platform is ethically responsible, how our architecture shields candidates from fraudulent credential hallucinations, and why the system stands in strict alignment with German and European statutes."
      descriptionDe="Warum der Einsatz der FindJobFit-Plattform ethisch geboten ist, wie unsere Architektur Kandidaten vor Fälschungen schützt und warum das System in vollem Einklang mit deutschen und europäischen Gesetzen steht."
      lawReferences={LAW_REFS}
      childrenEn={
        <div className="space-y-12 text-sm text-zinc-300 leading-relaxed">
          {/* Core Principle Banner */}
          <div className="bg-gradient-to-r from-violet-950/40 via-zinc-900 to-indigo-950/40 border border-violet-800/40 rounded-2xl p-6 md:p-8 space-y-3 shadow-xl">
            <div className="flex items-center gap-2 text-violet-400 font-mono text-xs uppercase tracking-wider">
              <Sparkles className="h-4 w-4" />
              <span>The Foundational Ethical Axiom</span>
            </div>
            <blockquote className="text-xl md:text-2xl font-serif italic text-zinc-100">
              &ldquo;Artificial intelligence may select which verified credentials are relevant for a job opening. It must never invent which credentials exist.&rdquo;
            </blockquote>
            <p className="text-xs text-zinc-400 font-sans">
              Conventional generative AI tools frequently &ldquo;hallucinate&rdquo; resume milestones &mdash; fabrications that deceive employers and expose applicants to civil liabilities and criminal fraud charges under German law. FindJobFit precludes this by mathematical design.
            </p>
          </div>

          {/* Section 1: Ethical Pillars */}
          <section className="space-y-6">
            <div className="space-y-2">
              <h2 className="text-2xl font-bold text-zinc-100 flex items-center gap-2.5">
                <HeartHandshake className="h-6 w-6 text-violet-400" />
                <span>1. Why FindJobFit is Built for Ethical Responsibility</span>
              </h2>
              <p className="text-sm text-zinc-400">
                Three foundational principles govern our algorithmic and architectural choices:
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-zinc-900/60 border border-zinc-800/80 rounded-xl p-5 space-y-3">
                <CheckCircle2 className="h-5 w-5 text-emerald-400" />
                <h3 className="font-semibold text-zinc-100 text-sm">Truthfulness (Veritas)</h3>
                <p className="text-xs text-zinc-400 leading-relaxed">
                  Zero fabricated competencies or inflated metrics. The platform preserves the integrity of the employment market by only synthesizing verifiable career evidence (<code className="font-mono text-violet-400">selected_ids ⊆ allowed_ids</code>).
                </p>
              </div>

              <div className="bg-zinc-900/60 border border-zinc-800/80 rounded-xl p-5 space-y-3">
                <Eye className="h-5 w-5 text-indigo-400" />
                <h3 className="font-semibold text-zinc-100 text-sm">Candidate Sovereignty</h3>
                <p className="text-xs text-zinc-400 leading-relaxed">
                  Applicants retain absolute sovereignty (<strong className="text-zinc-200">Human-in-the-Loop</strong>). Every extracted experience milestone must be verified in the Evidence Bank before activation.
                </p>
              </div>

              <div className="bg-zinc-900/60 border border-zinc-800/80 rounded-xl p-5 space-y-3">
                <Scale className="h-5 w-5 text-purple-400" />
                <h3 className="font-semibold text-zinc-100 text-sm">Level Playing Field</h3>
                <p className="text-xs text-zinc-400 leading-relaxed">
                  Corporate recruiters have used opaque ATS keyword screening algorithms for decades. FindJobFit restores parity for candidates &mdash; not through illicit hacks, but through precise, merit-based semantic matching.
                </p>
              </div>
            </div>
          </section>

          {/* Section 2: Legal Alignment */}
          <section className="space-y-6">
            <div className="space-y-2">
              <h2 className="text-2xl font-bold text-zinc-100 flex items-center gap-2.5">
                <Scale className="h-6 w-6 text-emerald-400" />
                <span>2. Comprehensive Statutory Compliance in Germany &amp; the EU</span>
              </h2>
              <p className="text-sm text-zinc-400">
                Detailed legal analysis against governing European and German frameworks:
              </p>
            </div>

            <div className="space-y-4">
              {/* EU AI Act */}
              <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-xl p-6 space-y-3">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <h3 className="font-bold text-zinc-100 text-base">
                    A. EU AI Act (Regulation (EU) 2024/1689)
                  </h3>
                  <a
                    href="https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[11px] font-mono px-2.5 py-1 rounded bg-emerald-950/40 text-emerald-400 border border-emerald-800/40 inline-flex items-center gap-1 w-fit hover:bg-emerald-900/40 transition-colors"
                  >
                    <span>EUR-Lex Gazette</span>
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
                <p className="text-zinc-400 text-xs leading-relaxed">
                  Pursuant to Annex III Section 4 of Regulation (EU) 2024/1689, AI systems in employment and human resources management are classified as &ldquo;High-Risk AI&rdquo; when deployed by <em>employers or recruiters</em> for the automated recruitment, screening, or evaluation of candidates.
                </p>
                <ul className="list-disc pl-5 space-y-1.5 text-xs text-zinc-400">
                  <li>
                    <strong className="text-zinc-200">Candidate-Facing Assistance:</strong> FindJobFit is an empowerment tool for candidates, not an employer-side screening filter.
                  </li>
                  <li>
                    <strong className="text-zinc-200">Human Oversight (Article 14 AI Act):</strong> No automated application submission occurs without prior explicit human verification. The candidate exercises final authority.
                  </li>
                  <li>
                    <strong className="text-zinc-200">Transparency and Accuracy (Articles 13 &amp; 15 AI Act):</strong> Semantic fit breakdowns clearly expose match reasoning, missing requirements, and evidence citations rather than producing unexplainable black-box scores.
                  </li>
                </ul>
              </div>

              {/* GDPR & BDSG § 26 */}
              <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-xl p-6 space-y-3">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <h3 className="font-bold text-zinc-100 text-base">
                    B. GDPR (DSGVO) &amp; § 26 BDSG (Employment Data Protection)
                  </h3>
                  <a
                    href="https://www.gesetze-im-internet.de/bdsg_2018/__26.html"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[11px] font-mono px-2.5 py-1 rounded bg-emerald-950/40 text-emerald-400 border border-emerald-800/40 inline-flex items-center gap-1 w-fit hover:bg-emerald-900/40 transition-colors"
                  >
                    <span>§ 26 BDSG Law</span>
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
                <p className="text-zinc-400 text-xs leading-relaxed">
                  The handling of candidate career records meets all European privacy benchmarks:
                </p>
                <ul className="list-disc pl-5 space-y-1.5 text-xs text-zinc-400">
                  <li>
                    <strong className="text-zinc-200">No Violation of Art. 22 GDPR:</strong> No automated profiling producing legal effects is performed without candidate intervention.
                  </li>
                  <li>
                    <strong className="text-zinc-200">Data Minimization (Art. 5 (1)(c) GDPR):</strong> Contact identities (name, address, date of birth) are decoupled and never transmitted to generative reasoning prompts.
                  </li>
                  <li>
                    <strong className="text-zinc-200">Candidate Sovereign Erasure (Art. 17 GDPR):</strong> Candidates may export or irrevocably destroy their Evidence Bank at any moment with a single click.
                  </li>
                </ul>
              </div>

              {/* AGG Anti-Discrimination */}
              <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-xl p-6 space-y-3">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <h3 className="font-bold text-zinc-100 text-base">
                    C. AGG (General Equal Treatment Act) &amp; Anti-Discrimination
                  </h3>
                  <a
                    href="https://www.antidiskriminierungsstelle.de"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[11px] font-mono px-2.5 py-1 rounded bg-emerald-950/40 text-emerald-400 border border-emerald-800/40 inline-flex items-center gap-1 w-fit hover:bg-emerald-900/40 transition-colors"
                  >
                    <span>Federal Agency (ADS)</span>
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
                <p className="text-zinc-400 text-xs leading-relaxed">
                  To eliminate discrimination proscribed by §§ 1, 7, and 11 of the German AGG:
                </p>
                <ul className="list-disc pl-5 space-y-1.5 text-xs text-zinc-400">
                  <li>
                    <strong className="text-zinc-200">Automatic Title Neutralization:</strong> Gender suffixes (e.g. <code className="font-mono text-violet-400">(m/w/d)</code>, <code className="font-mono text-violet-400">(gn)</code>) are automatically stripped from job queries.
                  </li>
                  <li>
                    <strong className="text-zinc-200">Strictly Objective Criteria:</strong> Algorithmic scoring evaluates exclusively verified skills, technical deliverables, and candidate-configured preferences &mdash; disregarding age, gender, ethnic origin, religious beliefs, or marital status.
                  </li>
                </ul>
              </div>

              {/* BGB & StGB Legal Shield */}
              <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-xl p-6 space-y-3">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <h3 className="font-bold text-zinc-100 text-base">
                    D. Civil &amp; Criminal Safeguards (§ 123 BGB, § 267 StGB)
                  </h3>
                  <a
                    href="https://www.gesetze-im-internet.de/bgb/__123.html"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[11px] font-mono px-2.5 py-1 rounded bg-emerald-950/40 text-emerald-400 border border-emerald-800/40 inline-flex items-center gap-1 w-fit hover:bg-emerald-900/40 transition-colors"
                  >
                    <span>§ 123 BGB Law</span>
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
                <p className="text-zinc-400 text-xs leading-relaxed">
                  Under German labor and contract law, misrepresentations on CVs can constitute fraudulent deception (<strong className="text-zinc-200">arglistige Täuschung, § 123 BGB</strong>) or justify immediate summary dismissal for cause (<strong className="text-zinc-200">§ 626 BGB</strong>).
                </p>
                <p className="text-zinc-400 text-xs leading-relaxed">
                  <strong className="text-zinc-200">FindJobFit&rsquo;s Legal Shield:</strong> Because our architecture mathematically forbids unverified credentials from entering tailored CVs, FindJobFit actively protects the candidate from inadvertently committing employment fraud or becoming subject to legal sanctions.
                </p>
              </div>

              {/* DDG & TDDDG May 2024 */}
              <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-xl p-6 space-y-3">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <h3 className="font-bold text-zinc-100 text-base">
                    E. § 5 DDG (Digital Services Act Germany) &amp; § 25 TDDDG
                  </h3>
                  <a
                    href="https://www.gesetze-im-internet.de/ddg/__5.html"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[11px] font-mono px-2.5 py-1 rounded bg-emerald-950/40 text-emerald-400 border border-emerald-800/40 inline-flex items-center gap-1 w-fit hover:bg-emerald-900/40 transition-colors"
                  >
                    <span>§ 5 DDG Law</span>
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
                <p className="text-zinc-400 text-xs leading-relaxed">
                  The platform complies with the German Digitale-Dienste-Gesetz (DDG, effective May 14, 2024, superseding the TMG) and the TDDDG (formerly TTDSG). A complete statutory Impressum and consent-free necessary session token storage guarantee legal operation in Germany.
                </p>
              </div>
            </div>
          </section>

          {/* Code Guarantee Summary */}
          <div className="border border-zinc-800 bg-zinc-900/60 rounded-xl p-6 text-center space-y-3">
            <h3 className="font-bold text-zinc-100 text-base">
              Integrity via Code Instead of Empty Marketing
            </h3>
            <p className="text-xs text-zinc-400 max-w-2xl mx-auto leading-relaxed">
              Ethical behavior is not established through declarations, but through strict architectural constraints, privacy-by-design engineering, and uncompromising respect for human truth.
            </p>
          </div>
        </div>
      }
      childrenDe={
        <div className="space-y-12 text-sm text-zinc-300 leading-relaxed">
          {/* Grundsatz Banner */}
          <div className="bg-gradient-to-r from-violet-950/40 via-zinc-900 to-indigo-950/40 border border-violet-800/40 rounded-2xl p-6 md:p-8 space-y-3 shadow-xl">
            <div className="flex items-center gap-2 text-violet-400 font-mono text-xs uppercase tracking-wider">
              <Sparkles className="h-4 w-4" />
              <span>Das Ethische Grundaxiom</span>
            </div>
            <blockquote className="text-xl md:text-2xl font-serif italic text-zinc-100">
              &bdquo;Künstliche Intelligenz darf entscheiden, welche verifizierten Belege für eine Stelle relevant sind. Sie darf jedoch niemals entscheiden, welche Belege existieren.&ldquo;
            </blockquote>
            <p className="text-xs text-zinc-400 font-sans">
              Herkömmliche generative KI neigt dazu, Lebensläufe zu &bdquo;halluzinieren&ldquo; &mdash; Erfindungen, die sowohl Arbeitgeber täuschen als auch Bewerber rechtlich angreifbar machen. FindJobFit verhindert dies auf Code-Ebene durch mathematische Invarianten.
            </p>
          </div>

          {/* Abschnitt 1: Warum ist das System ethisch? */}
          <section className="space-y-6">
            <div className="space-y-2">
              <h2 className="text-2xl font-bold text-zinc-100 flex items-center gap-2.5">
                <HeartHandshake className="h-6 w-6 text-violet-400" />
                <span>1. Warum ist FindJobFit ethisch?</span>
              </h2>
              <p className="text-sm text-zinc-400">
                Drei fundamentale ethische Säulen definieren unsere Architektur:
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-zinc-900/60 border border-zinc-800/80 rounded-xl p-5 space-y-3">
                <CheckCircle2 className="h-5 w-5 text-emerald-400" />
                <h3 className="font-semibold text-zinc-100 text-sm">Wahrhaftigkeit (Veritas)</h3>
                <p className="text-xs text-zinc-400 leading-relaxed">
                  Keine erfundenen Technologien oder gefälschten Kennzahlen. Das System schützt die Integrität des Arbeitsmarktes, indem es nur nachweisbare Erfahrungen präsentiert (<code className="font-mono text-violet-400">selected_ids ⊆ allowed_ids</code>).
                </p>
              </div>

              <div className="bg-zinc-900/60 border border-zinc-800/80 rounded-xl p-5 space-y-3">
                <Eye className="h-5 w-5 text-indigo-400" />
                <h3 className="font-semibold text-zinc-100 text-sm">Transparenz &amp; Selbstbestimmung</h3>
                <p className="text-xs text-zinc-400 leading-relaxed">
                  Bewerber behalten stets die volle Hoheit (Human-in-the-Loop). Sie verifizieren jeden extrahierten Baustein in der Evidence Bank und lösen jede Generierung bewusst aus.
                </p>
              </div>

              <div className="bg-zinc-900/60 border border-zinc-800/80 rounded-xl p-5 space-y-3">
                <Scale className="h-5 w-5 text-purple-400" />
                <h3 className="font-semibold text-zinc-100 text-sm">Chancengleichheit</h3>
                <p className="text-xs text-zinc-400 leading-relaxed">
                  Unternehmen nutzen seit Jahren intransparente ATS-Filter. FindJobFit gibt Kandidaten die technologische Augenhöhe zurück &mdash; ohne unlautere Tricks, sondern durch präzise Strukturierung.
                </p>
              </div>
            </div>
          </section>

          {/* Abschnitt 2: Rechtliche Konformität */}
          <section className="space-y-6">
            <div className="space-y-2">
              <h2 className="text-2xl font-bold text-zinc-100 flex items-center gap-2.5">
                <Scale className="h-6 w-6 text-emerald-400" />
                <span>2. Rechtliche Konformität in Deutschland und der EU</span>
              </h2>
              <p className="text-sm text-zinc-400">
                Detaillierte juristische Einordnung gegenüber zentralen Gesetzen:
              </p>
            </div>

            <div className="space-y-4">
              {/* EU AI Act */}
              <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-xl p-6 space-y-3">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <h3 className="font-bold text-zinc-100 text-base">
                    A. EU AI Act (KI-Verordnung - Verordnung (EU) 2024/1689)
                  </h3>
                  <a
                    href="https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[11px] font-mono px-2.5 py-1 rounded bg-emerald-950/40 text-emerald-400 border border-emerald-800/40 inline-flex items-center gap-1 w-fit hover:bg-emerald-900/40 transition-colors"
                  >
                    <span>EUR-Lex Verordnung</span>
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
                <p className="text-zinc-400 text-xs leading-relaxed">
                  Gemäß Anhang III der KI-Verordnung gelten KI-Systeme im Bereich Beschäftigung und Personalmanagement als &bdquo;Hochrisiko-KI&ldquo;, wenn sie von <em>Arbeitgebern</em> zur automatisierten Bewerberauslese oder Entscheidung über Beförderungen eingesetzt werden.
                </p>
                <ul className="list-disc pl-5 space-y-1.5 text-xs text-zinc-400">
                  <li>
                    <strong className="text-zinc-200">Kandidatenseitige Assistenz:</strong> FindJobFit ist ein Hilfsmittel für den Bewerber, kein Arbeitgeber-Filter.
                  </li>
                  <li>
                    <strong className="text-zinc-200">Menschliche Aufsicht (Art. 14 AI Act):</strong> Kein Schritt wird vollautomatisch ohne menschliche Kontrolle ausgeführt. Der Bewerber hat das letzte Wort vor jedem Versand.
                  </li>
                  <li>
                    <strong className="text-zinc-200">Transparenz und Genauigkeit (Art. 13 &amp; 15 AI Act):</strong> Die Eignungsbewertungen schlüsseln Stärken, Schwächen und fehlende Anforderungen transparent auf, statt undurchsichtige Punktzahlen zu vergeben.
                  </li>
                </ul>
              </div>

              {/* DSGVO / BDSG */}
              <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-xl p-6 space-y-3">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <h3 className="font-bold text-zinc-100 text-base">
                    B. DSGVO (GDPR) &amp; § 26 BDSG (Beschäftigtendatenschutz)
                  </h3>
                  <a
                    href="https://www.gesetze-im-internet.de/bdsg_2018/__26.html"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[11px] font-mono px-2.5 py-1 rounded bg-emerald-950/40 text-emerald-400 border border-emerald-800/40 inline-flex items-center gap-1 w-fit hover:bg-emerald-900/40 transition-colors"
                  >
                    <span>§ 26 BDSG Gesetz</span>
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
                <p className="text-zinc-400 text-xs leading-relaxed">
                  Die Verarbeitung von Lebensläufen unterliegt strengen Anforderungen:
                </p>
                <ul className="list-disc pl-5 space-y-1.5 text-xs text-zinc-400">
                  <li>
                    <strong className="text-zinc-200">Kein Verstoß gegen Art. 22 DSGVO:</strong> Es gibt kein automatisches Profiling mit rechtlicher Wirkung gegenüber dem Nutzer.
                  </li>
                  <li>
                    <strong className="text-zinc-200">Datensparsamkeit (Art. 5 Abs. 1 lit. c DSGVO):</strong> Personenbezogene Identitätsdaten (Name, Adresse, Geburtsdatum) werden strikt in der privaten Datenbank gehalten und nicht an LLM-Reasoning-Prompts übertragen.
                  </li>
                  <li>
                    <strong className="text-zinc-200">Souveränität &amp; Löschanspruch (Art. 17 DSGVO):</strong> Nutzer können ihre Daten jederzeit exportieren oder auf Knopfdruck spurlos vernichten.
                  </li>
                </ul>
              </div>

              {/* AGG */}
              <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-xl p-6 space-y-3">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <h3 className="font-bold text-zinc-100 text-base">
                    C. AGG (Allgemeines Gleichbehandlungsgesetz) &amp; Antidiskriminierung
                  </h3>
                  <a
                    href="https://www.antidiskriminierungsstelle.de"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[11px] font-mono px-2.5 py-1 rounded bg-emerald-950/40 text-emerald-400 border border-emerald-800/40 inline-flex items-center gap-1 w-fit hover:bg-emerald-900/40 transition-colors"
                  >
                    <span>Antidiskriminierungsstelle</span>
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
                <p className="text-zinc-400 text-xs leading-relaxed">
                  Um Diskriminierung nach dem AGG vorzubeugen:
                </p>
                <ul className="list-disc pl-5 space-y-1.5 text-xs text-zinc-400">
                  <li>
                    <strong className="text-zinc-200">Automatische Titelbereinigung:</strong> Geschlechtsmarkierungen (z. B. <code className="font-mono text-violet-400">(m/w/d)</code>, <code className="font-mono text-violet-400">(gn)</code>) werden neutralisiert.
                  </li>
                  <li>
                    <strong className="text-zinc-200">Objektive Kriterien:</strong> Das Matching bewertet ausschließlich verifizierte fachliche Fähigkeiten, Technologie-Stacks, Erfahrungswerte und vom Nutzer definierte Arbeitsort-Präferenzen &mdash; ohne Rücksicht auf Alter, Geschlecht, Herkunft oder persönliche Schutzmerkmale.
                  </li>
                </ul>
              </div>

              {/* BGB / StGB */}
              <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-xl p-6 space-y-3">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <h3 className="font-bold text-zinc-100 text-base">
                    D. BGB &amp; StGB (Schutz vor Täuschung und Arbeitsrecht)
                  </h3>
                  <a
                    href="https://www.gesetze-im-internet.de/bgb/__123.html"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[11px] font-mono px-2.5 py-1 rounded bg-emerald-950/40 text-emerald-400 border border-emerald-800/40 inline-flex items-center gap-1 w-fit hover:bg-emerald-900/40 transition-colors"
                  >
                    <span>§ 123 BGB Gesetz</span>
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
                <p className="text-zinc-400 text-xs leading-relaxed">
                  Im deutschen Arbeitsrecht kann eine Fälschung im Lebenslauf eine <strong>arglistige Täuschung (§ 123 BGB)</strong> darstellen oder eine fristlose Kündigung aus wichtigem Grund (§ 626 BGB) rechtfertigen.
                </p>
                <p className="text-zinc-400 text-xs leading-relaxed">
                  <strong className="text-zinc-200">Der rechtliche Schutzschild von FindJobFit:</strong> Da unser System mathematisch ausschließt, dass unbestätigte oder erfundene Stationen in den exportierten Lebenslauf gelangen, bewahrt FindJobFit den Bewerber aktiv davor, sich unabsichtlich strafbar oder arbeitsrechtlich angreifbar zu machen.
                </p>
              </div>

              {/* § 5 DDG & TDDDG */}
              <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-xl p-6 space-y-3">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <h3 className="font-bold text-zinc-100 text-base">
                    E. § 5 DDG (Digitale-Dienste-Gesetz) &amp; TDDDG
                  </h3>
                  <a
                    href="https://www.gesetze-im-internet.de/ddg/__5.html"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[11px] font-mono px-2.5 py-1 rounded bg-emerald-950/40 text-emerald-400 border border-emerald-800/40 inline-flex items-center gap-1 w-fit hover:bg-emerald-900/40 transition-colors"
                  >
                    <span>§ 5 DDG Gesetz</span>
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
                <p className="text-zinc-400 text-xs leading-relaxed">
                  Die Plattform erfüllt alle Vorgaben des am 14. Mai 2024 in Kraft getretenen Digitalen-Dienste-Gesetzes (DDG, Nachfolger des TMG) sowie des TDDDG (vormals TTDSG). Ein vollständiges, leicht auffindbares Impressum und datenschutzkonforme technische Token sichern den gesetzeskonformen Betrieb in Deutschland.
                </p>
              </div>
            </div>
          </section>

          {/* Zusammenfassung */}
          <div className="border border-zinc-800 bg-zinc-900/60 rounded-xl p-6 text-center space-y-3">
            <h3 className="font-bold text-zinc-100 text-base">
              Verlässlichkeit durch Code statt Versprechen
            </h3>
            <p className="text-xs text-zinc-400 max-w-2xl mx-auto leading-relaxed">
              Ethisches Handeln entsteht bei uns nicht durch Marketingtexte, sondern durch strikte Programmiergrenzen, datenschutzfreundliche Architektur (Privacy by Design) und den unbedingten Respekt vor der menschlichen Wahrheit.
            </p>
          </div>
        </div>
      }
    />
  );
}
