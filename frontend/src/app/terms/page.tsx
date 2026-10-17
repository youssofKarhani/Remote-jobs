import type { Metadata } from "next";
import { LegalPageShell } from "@/components/legal/legal-page-shell";
import { FileText, ShieldAlert, CheckCircle2, AlertTriangle, Scale, ExternalLink } from "lucide-react";

export const metadata: Metadata = {
  title: "Terms of Service (AGB) | FindJobFit",
  description: "General terms of service and acceptable use policy for FindJobFit governed by the laws of the Federal Republic of Germany (§§ 305 ff. BGB).",
};

const LAW_REFS = [
  {
    code: "§§ 305 ff. BGB",
    url: "https://www.gesetze-im-internet.de/bgb/__305.html",
    title: "German Civil Code: Law of Standard Terms and Conditions",
  },
  {
    code: "§ 312i BGB",
    url: "https://www.gesetze-im-internet.de/bgb/__312i.html",
    title: "German Civil Code: General Duties in E-Commerce",
  },
  {
    code: "§ 123 BGB",
    url: "https://www.gesetze-im-internet.de/bgb/__123.html",
    title: "German Civil Code: Avoidance for Fraudulent Deception",
  },
  {
    code: "§ 626 BGB",
    url: "https://www.gesetze-im-internet.de/bgb/__626.html",
    title: "German Civil Code: Termination Without Notice for Cause",
  },
  {
    code: "§ 36 VSBG",
    url: "https://www.gesetze-im-internet.de/vsbg/__36.html",
    title: "Consumer Dispute Resolution Act",
  },
];

export default function TermsPage() {
  return (
    <LegalPageShell
      badgeTextEn="Standard Contractual Terms (AGB)"
      badgeTextDe="Vertragsbedingungen (AGB)"
      titleEn="Terms of Service"
      titleDe="Allgemeine Geschäftsbedingungen (AGB)"
      descriptionEn="General terms and conditions for utilizing the software services and algorithmic job engineering tools provided by FindJobFit under the laws of the Federal Republic of Germany (§§ 305 ff. BGB)."
      descriptionDe="Nutzungsbedingungen für die Inanspruchnahme der Dienste der FindJobFit-Plattform nach dem Recht der Bundesrepublik Deutschland (§§ 305 ff. BGB)."
      lawReferences={LAW_REFS}
      childrenEn={
        <div className="space-y-10 text-sm text-zinc-300 leading-relaxed">
          {/* Core Guarantees Callout */}
          <div className="bg-violet-950/20 border border-violet-800/40 rounded-xl p-6 space-y-3">
            <div className="flex items-center gap-2 text-violet-300 font-semibold text-sm">
              <CheckCircle2 className="h-4 w-4 text-violet-400" />
              <span>Core Principle: Truthfulness and Mathematical Verification</span>
            </div>
            <p className="text-xs text-zinc-300 leading-relaxed">
              FindJobFit commits itself and its candidate users to the highest standards of veracity in the employment market. Our software architecture enforces mathematical invariants (<code className="font-mono text-violet-400">selected_ids ⊆ allowed_ids</code>) ensuring that AI cannot invent credentials. In reciprocal obligation, the user covenants that all career evidence entered into the Evidence Bank is factually authentic.
            </p>
          </div>

          {/* Terms Articles */}
          <div className="space-y-8">
            {/* 1. Scope & Subject */}
            <section className="space-y-3">
              <h2 className="text-xl font-bold text-zinc-100 flex items-center gap-2">
                1. Scope of Applicability &amp; Subject of the Contract
              </h2>
              <p className="text-zinc-400">
                These General Terms and Conditions (AGB) govern the relationship between FindJobFit (hereinafter &ldquo;we&rdquo;, &ldquo;us&rdquo;, or &ldquo;Platform&rdquo;) and registered users or visitors (hereinafter &ldquo;User&rdquo; or &ldquo;Candidate&rdquo;). FindJobFit provides deterministic software tools for job discovery, semantic fit analysis, and tailoring verifiable application documents strictly derived from the candidate&rsquo;s authenticated Evidence Bank.
              </p>
            </section>

            {/* 2. Registration & Truth Invariant */}
            <section className="space-y-3">
              <h2 className="text-xl font-bold text-zinc-100">
                2. User Account &amp; Duty of Truthfulness (§ 123 BGB)
              </h2>
              <p className="text-zinc-400">
                (1) Access to personalized features requires the creation of a user account. The candidate is obligated to keep login credentials confidential and protect them against unauthorized third-party access.
              </p>
              <p className="text-zinc-400">
                (2) <strong className="text-zinc-200">Affirmative Duty of Truthfulness:</strong> The candidate warrants that all statements, dates, project accomplishments, employment titles, and academic degrees entered into their profile or Evidence Bank are truthful, accurate, and not misleading.
              </p>
              <div className="p-3.5 rounded-lg bg-zinc-900/60 border border-zinc-800 text-xs text-zinc-400 space-y-1">
                <p className="font-semibold text-amber-300">Statutory Notice under German Employment &amp; Civil Law:</p>
                <p>
                  Submitting deliberately falsified qualifications in job applications constitutes fraudulent misrepresentation (
                  <a
                    href="https://www.gesetze-im-internet.de/bgb/__123.html"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-violet-400 hover:underline font-mono inline-flex items-center gap-0.5"
                  >
                    § 123 BGB
                    <ExternalLink className="h-2.5 w-2.5" />
                  </a>
                  ) and may justify summary dismissal without notice under{" "}
                  <a
                    href="https://www.gesetze-im-internet.de/bgb/__626.html"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-violet-400 hover:underline font-mono inline-flex items-center gap-0.5"
                  >
                    § 626 BGB
                  </a>
                  , as well as criminal prosecution for document forgery under § 267 StGB.
                </p>
              </div>
            </section>

            {/* 3. AI Service Operation & Anti-Hallucination Gate */}
            <section className="space-y-3">
              <h2 className="text-xl font-bold text-zinc-100 flex items-center gap-2">
                <Scale className="h-4 w-4 text-violet-400" />
                3. Algorithmic Processing &amp; Pre-Submission Inspection Duty
              </h2>
              <p className="text-zinc-400">
                (1) The platform employs artificial intelligence models to parse job postings and filter matching evidence tokens from the user&rsquo;s verified Evidence Bank.
              </p>
              <p className="text-zinc-400">
                (2) <strong className="text-zinc-200">Zero Generative Fabrication:</strong> By mathematical design, the software will not insert qualifications that lack corresponding verified identifiers. However, FindJobFit provides no warranty that prospective employers will react favorably to tailored wording or specific candidate profiles.
              </p>
              <p className="text-zinc-400">
                (3) <strong className="text-zinc-200">Mandatory Candidate Review Duty:</strong> Prior to any external submission to an employer, the candidate is required to thoroughly review all generated documents (CV, cover letter, synthesis summaries) and provide autonomous personal approval (<strong className="text-zinc-200">Human-in-the-Loop</strong>).
              </p>
            </section>

            {/* 4. External Job Listings */}
            <section className="space-y-3">
              <h2 className="text-xl font-bold text-zinc-100">
                4. Syndicated Job Postings &amp; Third-Party Services
              </h2>
              <p className="text-zinc-400">
                Job vacancies displayed on the platform are aggregated from external APIs, employer careers portals, and public employment registers under § 44b UrhG. FindJobFit does not act as an employment agency and assumes no warranty for the currency, completeness, or ongoing availability of external openings. The conclusion of an employment contract remains entirely between the candidate and the respective employer.
              </p>
            </section>

            {/* 5. Intellectual Property & Export Rights */}
            <section className="space-y-3">
              <h2 className="text-xl font-bold text-zinc-100">
                5. Intellectual Property Rights &amp; Document Ownership
              </h2>
              <p className="text-zinc-400">
                (1) The candidate retains full ownership of all uploaded CV files, raw career milestones, and personal intellectual property. The user grants FindJobFit a non-exclusive, royalty-free, revocable license strictly limited to storing and processing these assets to provide the requested software services.
              </p>
              <p className="text-zinc-400">
                (2) All documents generated and exported by the platform (PDF, DOCX) become the unrestricted property of the user for private and professional employment applications.
              </p>
            </section>

            {/* 6. Limitation of Liability */}
            <section className="space-y-3">
              <h2 className="text-xl font-bold text-zinc-100 flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-amber-400" />
                6. Limitation of Liability (§§ 276, 280 BGB)
              </h2>
              <p className="text-zinc-400">
                (1) FindJobFit is liable without limitation in cases of intent (Vorsatz), gross negligence (grobe Fahrlässigkeit), or culpable injury to life, body, or health.
              </p>
              <p className="text-zinc-400">
                (2) In cases of slight negligence, liability is limited exclusively to breaches of material contractual obligations (cardinal obligations / Kardinalpflichten), whose fulfillment is essential to the proper performance of the contract and on whose observance the user regularly relies. In such cases, liability is capped at typical, foreseeable contractual damages.
              </p>
              <p className="text-zinc-400">
                (3) FindJobFit expressly assumes no liability for the success of job applications, interview invitations, or the conclusion of employment agreements.
              </p>
            </section>

            {/* 7. Termination & Account Purge */}
            <section className="space-y-3">
              <h2 className="text-xl font-bold text-zinc-100">
                7. Term, Termination &amp; One-Click Purge
              </h2>
              <p className="text-zinc-400">
                The user may terminate the usage relationship at any time without notice by deleting their account in the candidate profile settings. Upon account deletion, all personal data, Evidence Bank tokens, tailored applications, and preferences are irrevocably destroyed.
              </p>
            </section>

            {/* 8. Governing Law & Jurisdiction */}
            <section className="space-y-3">
              <h2 className="text-xl font-bold text-zinc-100">
                8. Governing Law, Consumer Rights &amp; Place of Jurisdiction
              </h2>
              <p className="text-zinc-400">
                (1) Contracts between FindJobFit and the candidate shall be governed by the laws of the Federal Republic of Germany, to the exclusion of the UN Convention on Contracts for the International Sale of Goods (CISG). For consumers habitually resident in an EU member state, mandatory consumer protection provisions of the state of residence remain unaffected pursuant to Article 6 para. 2 of Regulation (EC) No. 593/2008 (Rome I).
              </p>
              <p className="text-zinc-400">
                (2) If the user is a merchant (Kaufmann), a legal entity under public law, or a special fund under public law, the exclusive place of jurisdiction for all disputes arising from this contractual relationship shall be Hesse, Germany.
              </p>
            </section>
          </div>
        </div>
      }
      childrenDe={
        <div className="space-y-10 text-sm text-zinc-300 leading-relaxed">
          {/* Kernprinzip */}
          <div className="bg-violet-950/20 border border-violet-800/40 rounded-xl p-6 space-y-3">
            <div className="flex items-center gap-2 text-violet-300 font-semibold text-sm">
              <CheckCircle2 className="h-4 w-4 text-violet-400" />
              <span>Kernprinzip: Wahrheit und Verifikation</span>
            </div>
            <p className="text-xs text-zinc-300 leading-relaxed">
              FindJobFit verpflichtet sich und seine Nutzer dem Grundsatz der Wahrhaftigkeit im Bewerbungsprozess. Das System stellt durch mathematische Schranken (<code className="font-mono text-violet-400">selected_ids ⊆ allowed_ids</code>) sicher, dass keine Qualifikationen oder Erfahrungen frei erfunden werden. Der Nutzer versichert, dass alle in die Evidence Bank eingestellten Daten den Tatsachen entsprechen.
            </p>
          </div>

          {/* Abschnitte */}
          <div className="space-y-8">
            {/* 1. Geltungsbereich */}
            <section className="space-y-3">
              <h2 className="text-xl font-bold text-zinc-100 flex items-center gap-2">
                1. Geltungsbereich und Vertragsgegenstand
              </h2>
              <p className="text-zinc-400">
                Diese Allgemeinen Geschäftsbedingungen gelten für die Nutzung der Plattform FindJobFit (nachfolgend &bdquo;Plattform&ldquo; oder &bdquo;wir&ldquo;). Die Plattform stellt Softwarefunktionen zur Aggregation von Stellenangeboten, automatisierten semantischen Eignungsanalyse sowie deterministischen Erstellung maßgeschneiderter Bewerbungsdokumente auf Basis verifizierter Nutzerbelege bereit.
              </p>
            </section>

            {/* 2. Registrierung */}
            <section className="space-y-3">
              <h2 className="text-xl font-bold text-zinc-100">
                2. Registrierung, Account-Sicherheit und Wahrheitspflicht (§ 123 BGB)
              </h2>
              <p className="text-zinc-400">
                (1) Die Nutzung der personalisierten Funktionen erfordert die Erstellung eines Benutzerkontos. Der Nutzer ist verpflichtet, seine Zugangsdaten vertraulich zu behandeln und vor dem Zugriff Dritter zu schützen.
              </p>
              <p className="text-zinc-400">
                (2) <strong className="text-zinc-200">Wahrheitspflicht des Nutzers:</strong> Der Nutzer verpflichtet sich, in seinem Profil und seiner Evidence Bank ausschließlich wahrheitsgemäße, zutreffende und nicht irreführende Angaben über seine Ausbildung, Qualifikationen, Berufserfahrung und bisherigen Arbeitsleistungen zu hinterlegen.
              </p>
              <div className="p-3.5 rounded-lg bg-zinc-900/60 border border-zinc-800 text-xs text-zinc-400 space-y-1">
                <p className="font-semibold text-amber-300">Rechtlicher Hinweis nach BGB und Arbeitsrecht:</p>
                <p>
                  Die bewusste Hinterlegung falscher Angaben zur Täuschung potenzieller Arbeitgeber stellt eine arglistige Täuschung im Sinne von{" "}
                  <a
                    href="https://www.gesetze-im-internet.de/bgb/__123.html"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-violet-400 hover:underline font-mono inline-flex items-center gap-0.5"
                  >
                    § 123 BGB
                    <ExternalLink className="h-2.5 w-2.5" />
                  </a>{" "}
                  dar und berechtigt Arbeitgeber zur Anfechtung des Arbeitsvertrages sowie zur fristlosen Kündigung nach{" "}
                  <a
                    href="https://www.gesetze-im-internet.de/bgb/__626.html"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-violet-400 hover:underline font-mono inline-flex items-center gap-0.5"
                  >
                    § 626 BGB
                  </a>
                  . Urkundenfälschungen werden nach § 267 StGB strafrechtlich verfolgt.
                </p>
              </div>
            </section>

            {/* 3. Funktionsweise der KI */}
            <section className="space-y-3">
              <h2 className="text-xl font-bold text-zinc-100 flex items-center gap-2">
                <Scale className="h-4 w-4 text-violet-400" />
                3. Bereitstellung der KI-Dienste &amp; Anti-Halluzinations-Gate
              </h2>
              <p className="text-zinc-400">
                (1) Die Plattform verwendet Algorithmen und Sprachmodelle (LLMs), um Stellenangebote zu analysieren und relevante Belege aus der persönlichen Evidence Bank des Nutzers auszuwählen.
              </p>
              <p className="text-zinc-400">
                (2) <strong className="text-zinc-200">Keine generative Neuerfindung von Fakten:</strong> Das System ist so programmiert, dass es in generierten Lebensläufen ausschließlich Belege verwendet, die der Nutzer zuvor freigegeben hat. Die Plattform übernimmt jedoch keine Garantie dafür, dass potenzielle Arbeitgeber die generierten Formulierungen oder den Zuschnitt positiv bewerten.
              </p>
              <p className="text-zinc-400">
                (3) <strong className="text-zinc-200">Prüfpflicht vor Versand:</strong> Der Nutzer ist vor jeder tatsächlichen Absendung einer Bewerbung verpflichtet, die generierten Dokumente (Lebenslauf und Anschreiben) sorgfältig zu prüfen und eigenverantwortlich freizugeben.
              </p>
            </section>

            {/* 4. Externe Stellenanzeigen */}
            <section className="space-y-3">
              <h2 className="text-xl font-bold text-zinc-100">
                4. Externe Stellenangebote
              </h2>
              <p className="text-zinc-400">
                Die auf der Plattform angezeigten Stellenangebote stammen aus externen Quellen, öffentlichen Schnittstellen oder Partnernetzwerken. Wir übernehmen keine Gewähr für die Aktualität, Richtigkeit, Vollständigkeit oder fortlaufende Verfügbarkeit der ausgeschriebenen Stellen. Das Zustandekommen eines Bewerbungsverfahrens oder Arbeitsverhältnisses liegt außerhalb unseres Einflussbereichs.
              </p>
            </section>

            {/* 5. Urheberrechte */}
            <section className="space-y-3">
              <h2 className="text-xl font-bold text-zinc-100">
                5. Urheber- und Nutzungsrechte
              </h2>
              <p className="text-zinc-400">
                (1) Der Nutzer behält alle Rechte an den von ihm hochgeladenen Dokumenten und Erfahrungswerten. Er räumt der Plattform das einfache, unentgeltliche, auf die Vertragslaufzeit beschränkte Recht ein, diese Daten zur Erbringung der vereinbarten Funktionen zu speichern und zu verarbeiten.
              </p>
              <p className="text-zinc-400">
                (2) Die durch die Plattform exportierten Dokumente (DOCX, PDF) stehen dem Nutzer zur uneingeschränkten privaten und beruflichen Nutzung zur Verfügung.
              </p>
            </section>

            {/* 6. Haftungsbeschränkung */}
            <section className="space-y-3">
              <h2 className="text-xl font-bold text-zinc-100 flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-amber-400" />
                6. Haftungsbeschränkung (§§ 276, 280 BGB)
              </h2>
              <p className="text-zinc-400">
                (1) Wir haften unbeschränkt bei Vorsatz und grober Fahrlässigkeit sowie bei Verletzung von Leben, Körper oder Gesundheit.
              </p>
              <p className="text-zinc-400">
                (2) Bei leichter Fahrlässigkeit haften wir nur bei Verletzung wesentlicher Vertragspflichten (Kardinalpflichten), deren Erfüllung die ordnungsgemäße Durchführung des Vertrages überhaupt erst ermöglicht und auf deren Einhaltung der Nutzer regelmäßig vertrauen darf. In diesem Fall ist die Haftung auf den vertragstypischen, vorhersehbaren Schaden begrenzt.
              </p>
              <p className="text-zinc-400">
                (3) Wir haften nicht für den Erfolg von Bewerbungen oder das Zustandekommen von Arbeitsverträgen.
              </p>
            </section>

            {/* 7. Kündigung */}
            <section className="space-y-3">
              <h2 className="text-xl font-bold text-zinc-100">
                7. Beendigung des Vertrages &amp; Kontolöschung
              </h2>
              <p className="text-zinc-400">
                Der Nutzer kann sein Benutzerkonto jederzeit ohne Angabe von Gründen über die Profileinstellungen löschen. Mit der Kontolöschung werden alle gespeicherten Daten der Evidence Bank und Dokumente unwiederbringlich gelöscht. Das Recht zur außerordentlichen Kündigung aus wichtigem Grund bleibt unberührt.
              </p>
            </section>

            {/* 8. Schlussbestimmungen */}
            <section className="space-y-3">
              <h2 className="text-xl font-bold text-zinc-100">
                8. Anwendbares Recht und Gerichtsstand
              </h2>
              <p className="text-zinc-400">
                (1) Auf Verträge zwischen uns und dem Nutzer findet das Recht der Bundesrepublik Deutschland unter Ausschluss des UN-Kaufrechts Anwendung. Bei Verbrauchern gilt diese Rechtswahl nur insoweit, als nicht der durch zwingende Bestimmungen des Rechts des Staates des gewöhnlichen Aufenthalts des Verbrauchers gewährte Schutz entzogen wird.
              </p>
              <p className="text-zinc-400">
                (2) Sofern der Nutzer Kaufmann, juristische Person des öffentlichen Rechts oder öffentlich-rechtliches Sondervermögen ist, ist der Sitz des Diensteanbieters (Hessen, Deutschland) ausschließlicher Gerichtsstand für alle Streitigkeiten aus dem Vertragsverhältnis.
              </p>
            </section>
          </div>
        </div>
      }
    />
  );
}
