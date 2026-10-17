import type { Metadata } from "next";
import { LegalPageShell } from "@/components/legal/legal-page-shell";
import { Lock, ShieldCheck, Database, Cpu, UserCheck, Eye, ExternalLink, ShieldAlert, Server } from "lucide-react";

export const metadata: Metadata = {
  title: "Privacy Policy (Datenschutz) | FindJobFit",
  description: "Privacy policy pursuant to EU GDPR (DSGVO), German Federal Data Protection Act (§ 26 BDSG), and § 25 TDDDG.",
};

const LAW_REFS = [
  {
    code: "EU GDPR (2016/679)",
    url: "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32016R0679",
    title: "General Data Protection Regulation (Official EU Text)",
  },
  {
    code: "§ 26 BDSG",
    url: "https://www.gesetze-im-internet.de/bdsg_2018/__26.html",
    title: "Federal Data Protection Act § 26 (Employment & Applicant Data)",
  },
  {
    code: "§ 25 TDDDG",
    url: "https://www.gesetze-im-internet.de/tdddg/__25.html",
    title: "Telecommunications Digital Services Data Protection Act (Terminal Privacy)",
  },
  {
    code: "HBDI Hessen",
    url: "https://datenschutz.hessen.de",
    title: "State Commissioner for Data Protection and Freedom of Information (Hesse)",
  },
  {
    code: "EU-US DPF",
    url: "https://www.dataprivacyframework.gov",
    title: "EU-U.S. Data Privacy Framework Program",
  },
];

export default function PrivacyPage() {
  return (
    <LegalPageShell
      badgeTextEn="GDPR, BDSG &amp; TDDDG Compliance"
      badgeTextDe="DSGVO, BDSG &amp; TDDDG Konformität"
      titleEn="Privacy Policy"
      titleDe="Datenschutzerklärung"
      descriptionEn="Transparent information regarding the processing of personal candidate data under Articles 13 and 14 of the General Data Protection Regulation (GDPR / DSGVO), § 26 of the German Federal Data Protection Act (BDSG), and § 25 of the TDDDG."
      descriptionDe="Transparente Information über die Verarbeitung personenbezogener Daten nach Art. 13 und 14 der Datenschutz-Grundverordnung (DSGVO), § 26 Bundesdatenschutzgesetz (BDSG) sowie § 25 TDDDG."
      lawReferences={LAW_REFS}
      childrenEn={
        <div className="space-y-10 text-sm text-zinc-300 leading-relaxed">
          {/* Architecture Privacy Pillars */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-zinc-900/60 border border-zinc-800/80 rounded-xl p-5 space-y-2">
              <Database className="h-5 w-5 text-violet-400" />
              <h3 className="font-semibold text-zinc-200 text-sm">Evidence Bank Isolation</h3>
              <p className="text-xs text-zinc-400 leading-relaxed">
                Personal identity data (full legal name, street address, private phone) is stored in encrypted database partitions and excluded from LLM reasoning prompts (Data Minimization under Art. 5 (1)(c) GDPR).
              </p>
            </div>

            <div className="bg-zinc-900/60 border border-zinc-800/80 rounded-xl p-5 space-y-2">
              <Cpu className="h-5 w-5 text-indigo-400" />
              <h3 className="font-semibold text-zinc-200 text-sm">Anti-Hallucination Gate</h3>
              <p className="text-xs text-zinc-400 leading-relaxed">
                AI models operate strictly as subset selectors (<code className="font-mono text-violet-400">selected_ids ⊆ allowed_ids</code>). They cannot invent biometric or biographical career credentials.
              </p>
            </div>

            <div className="bg-zinc-900/60 border border-zinc-800/80 rounded-xl p-5 space-y-2">
              <UserCheck className="h-5 w-5 text-emerald-400" />
              <h3 className="font-semibold text-zinc-200 text-sm">Human-in-the-Loop</h3>
              <p className="text-xs text-zinc-400 leading-relaxed">
                No automated decisions with legal effect under Art. 22 GDPR. The candidate retains full authority, manually reviewing each evidence token and confirming every application export.
              </p>
            </div>
          </div>

          {/* Privacy Articles */}
          <div className="space-y-8">
            {/* 1. Controller */}
            <section className="space-y-3">
              <h2 className="text-xl font-bold text-zinc-100 flex items-center gap-2">
                1. Data Controller Name and Address
              </h2>
              <p className="text-zinc-400">
                The Data Controller within the meaning of Article 4 No. 7 of the General Data Protection Regulation (GDPR), other data protection laws applicable in the Member States of the European Union, and other statutory data protection provisions is:
              </p>
              <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-lg p-4 font-mono text-xs text-zinc-300 space-y-1">
                <p className="text-zinc-100 font-semibold">FindJobFit</p>
                <p className="text-zinc-400 italic">[Operator Full Legal Name / Summonable Address]</p>
                <p>State of Hesse, Federal Republic of Germany</p>
                <p>
                  E-Mail:{" "}
                  <a href="mailto:support@findjobfit.de" className="text-violet-400 hover:underline">
                    support@findjobfit.de
                  </a>
                </p>
              </div>
            </section>

            {/* 2. Legal Bases */}
            <section className="space-y-3">
              <h2 className="text-xl font-bold text-zinc-100">
                2. Legal Bases for Processing Personal Data
              </h2>
              <p className="text-zinc-400">
                Candidate personal data is processed strictly in compliance with the provisions of the GDPR and the German Federal Data Protection Act (BDSG):
              </p>
              <ul className="list-disc pl-5 space-y-2 text-zinc-400">
                <li>
                  <strong className="text-zinc-200">Art. 6 (1)(b) GDPR (Performance of Contract):</strong> For the provision of our core software services (ingestion of CVs, structuring into the verifiable Evidence Bank, semantic matching with jobs, and generating tailored application documents).
                </li>
                <li>
                  <strong className="text-zinc-200">§ 26 BDSG (Employment-Related Data Processing in Germany):</strong> For storing, cataloging, and targeting applicant professional qualifications, certifications, career milestones, and work history.{" "}
                  <a
                    href="https://www.gesetze-im-internet.de/bdsg_2018/__26.html"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-violet-400 hover:underline inline-flex items-center gap-1 font-mono text-xs"
                  >
                    (Statutory Text)
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </li>
                <li>
                  <strong className="text-zinc-200">Art. 6 (1)(a) GDPR (Explicit Consent):</strong> For optional experimental AI reasoning features or personalized job alert digests where affirmative consent was granted.
                </li>
                <li>
                  <strong className="text-zinc-200">Art. 6 (1)(f) GDPR (Legitimate Interests):</strong> For cybersecurity preservation, prevention of automated abuse or scrapers, server load balancing, and lawful aggregation of publicly accessible job offers under § 44b UrhG.
                </li>
              </ul>
            </section>

            {/* 3. CV Ingestion & Evidence Bank */}
            <section className="space-y-3">
              <h2 className="text-xl font-bold text-zinc-100">
                3. CV Ingestion &amp; Evidence Bank Processing
              </h2>
              <p className="text-zinc-400">
                When you upload a CV or resume (PDF, DOCX, or text), our pipeline decomposes the document into discrete, atomic units of verifiable career evidence:
              </p>
              <ul className="list-disc pl-5 space-y-1 text-zinc-400">
                <li>Professional roles, achievements, project deliverables, and academic degrees</li>
                <li>Technical competencies and categorized skill hierarchies</li>
                <li>Immutable identifier assignments (e.g., <code className="font-mono text-violet-400">EXP_001</code>)</li>
              </ul>
              <p className="text-zinc-400">
                <strong className="text-zinc-200">Verification Principle:</strong> All extracted evidence tokens initially remain in an unverified draft state (<code className="font-mono text-violet-400">is_verified = False</code>). They are only activated for job matching and document generation once you have personally reviewed and confirmed their accuracy.
              </p>
            </section>

            {/* 4. AI Gateways & Zero Training */}
            <section className="space-y-3">
              <h2 className="text-xl font-bold text-zinc-100">
                4. AI Processing &amp; Privacy Shield (No LLM Model Training)
              </h2>
              <p className="text-zinc-400">
                To safeguard candidate privacy and prevent hallucinated fabrications, FindJobFit implements strict architectural firewalls:
              </p>
              <div className="space-y-2 text-zinc-400">
                <p>
                  &bull; <strong className="text-zinc-200">Subset Selection vs Generative Fabrication:</strong> During CV tailoring, the AI does not write new biographical facts. It receives only verified IDs (<code className="font-mono text-violet-400">allowed_ids</code>) and selects matching IDs. Text resolution occurs deterministically from our PostgreSQL database.
                </p>
                <p>
                  &bull; <strong className="text-zinc-200">Zero Model Training:</strong> Under our commercial API terms and local model pipelines (e.g. Ollama / Llama 3), neither FindJobFit nor external gateway providers use your uploaded resumes, career tokens, or generated cover letters to train foundation models.
                </p>
                <p>
                  &bull; <strong className="text-zinc-200">Local LLM Execution:</strong> The platform architecture supports fully local inference. When running with local models, candidate career data never exits your secured infrastructure.
                </p>
              </div>
            </section>

            {/* 5. Human-in-the-Loop & Art. 22 GDPR */}
            <section className="space-y-3">
              <h2 className="text-xl font-bold text-zinc-100 flex items-center gap-2">
                <Eye className="h-5 w-5 text-violet-400" />
                5. Absence of Solely Automated Decisions (Art. 22 GDPR)
              </h2>
              <p className="text-zinc-400">
                FindJobFit does <strong>not</strong> perform automated decision-making or profiling having legal effect concerning the candidate pursuant to Article 22 of the GDPR. FindJobFit operates strictly as a decision-support and drafting tool for candidates (<strong className="text-zinc-200">Human-in-the-Loop</strong>). The user retains sole and unrestricted control over whether to apply for any job and can edit all tailored application documents prior to submission.
              </p>
            </section>

            {/* 6. Data Subject Rights */}
            <section className="space-y-3">
              <h2 className="text-xl font-bold text-zinc-100 flex items-center gap-2">
                <ShieldCheck className="h-5 w-5 text-emerald-400" />
                6. Your Rights as a Data Subject
              </h2>
              <p className="text-zinc-400">
                Under the European GDPR, you have the following enforceable statutory rights:
              </p>
              <ul className="list-disc pl-5 space-y-1.5 text-zinc-400">
                <li>
                  <strong className="text-zinc-200">Art. 15 GDPR (Right of Access):</strong> Obtain confirmation as to whether your personal data is being processed, and access your full Evidence Bank record.
                </li>
                <li>
                  <strong className="text-zinc-200">Art. 16 GDPR (Right to Rectification):</strong> Rectify inaccurate personal data or complete incomplete career milestones without undue delay.
                </li>
                <li>
                  <strong className="text-zinc-200">Art. 17 GDPR (Right to Erasure / &ldquo;Right to be Forgotten&rdquo;):</strong> Request immediate erasure of all your candidate data, uploaded files, and generated documents.
                </li>
                <li>
                  <strong className="text-zinc-200">Art. 18 GDPR (Right to Restriction):</strong> Restrict the processing of your data under statutory conditions.
                </li>
                <li>
                  <strong className="text-zinc-200">Art. 20 GDPR (Right to Data Portability):</strong> Receive your personal data in a structured, commonly used, and machine-readable format (JSON / PDF / DOCX).
                </li>
                <li>
                  <strong className="text-zinc-200">Art. 21 GDPR (Right to Object):</strong> Object at any time to processing based on Art. 6 (1)(f) GDPR.
                </li>
                <li>
                  <strong className="text-zinc-200">Art. 77 GDPR (Right to Lodge a Complaint):</strong> You have the statutory right to lodge a complaint with a supervisory authority. The competent authority for our seat in Hesse is:{" "}
                  <span className="text-zinc-200 font-medium">Der Hessische Beauftragte für Datenschutz und Informationsfreiheit (HBDI)</span>, Gustav-Stresemann-Ring 1, 65189 Wiesbaden, Germany (
                  <a
                    href="https://datenschutz.hessen.de"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-violet-400 hover:underline inline-flex items-center gap-1 font-mono text-xs"
                  >
                    https://datenschutz.hessen.de
                    <ExternalLink className="h-3 w-3" />
                  </a>).
                </li>
              </ul>
            </section>

            {/* 7. Retention & Account Deletion */}
            <section className="space-y-3">
              <h2 className="text-xl font-bold text-zinc-100">
                7. Data Retention &amp; One-Click Deletion
              </h2>
              <p className="text-zinc-400">
                Personal data is retained only for the duration required to achieve the processing purposes or until you delete your candidate account. Upon account deletion in your profile settings, all Evidence Bank records, preferences, tailored documents, and activity histories are permanently purged from our primary databases and backups.
              </p>
            </section>

            {/* 8. Cookies & Terminal Privacy (§ 25 TDDDG) */}
            <section className="space-y-3">
              <h2 className="text-xl font-bold text-zinc-100">
                8. Cookies &amp; Local Storage (§ 25 para. 2 no. 2 TDDDG)
              </h2>
              <p className="text-zinc-400">
                Our application uses strictly necessary authentication session tokens (JWT - JSON Web Tokens) stored in localStorage and secure HTTP cookies to maintain your login session. In accordance with § 25 para. 2 no. 2 of the German Telecommunications Digital Services Data Protection Act (
                <a
                  href="https://www.gesetze-im-internet.de/tdddg/__25.html"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-violet-400 hover:underline inline-flex items-center gap-1 font-mono text-xs"
                >
                  § 25 TDDDG
                  <ExternalLink className="h-3 w-3" />
                </a>), prior consent is not required for storage accesses that are technically essential to deliver the requested service. We do not use third-party behavioral advertising or tracking scripts.
              </p>
            </section>

            {/* 9. Cloud Infrastructure & Hosting */}
            <section className="space-y-3">
              <h2 className="text-xl font-bold text-zinc-100 flex items-center gap-2">
                <Server className="h-5 w-5 text-violet-400" />
                9. Cloud Infrastructure &amp; International Transfers
              </h2>
              <p className="text-zinc-400">
                The platform is hosted via the cloud provider <strong className="text-zinc-200">Railway</strong> (Railway Corp., 548 Market St, Suite 63441, San Francisco, CA 94104, USA). Core application servers and database clusters are situated in European data centers (Region EU-West). Processing is based on our legitimate interest under Art. 6 (1)(f) GDPR in providing a reliable, performant, and secure application. Any transatlantic data transfer is governed by Standard Contractual Clauses (SCCs) and the EU-US Data Privacy Framework (
                <a
                  href="https://www.dataprivacyframework.gov"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-violet-400 hover:underline inline-flex items-center gap-1 font-mono text-xs"
                >
                  www.dataprivacyframework.gov
                  <ExternalLink className="h-3 w-3" />
                </a>).
              </p>
            </section>
          </div>
        </div>
      }
      childrenDe={
        <div className="space-y-10 text-sm text-zinc-300 leading-relaxed">
          {/* Übersichtskarten */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-zinc-900/60 border border-zinc-800/80 rounded-xl p-5 space-y-2">
              <Database className="h-5 w-5 text-violet-400" />
              <h3 className="font-semibold text-zinc-200 text-sm">Evidence Bank Trennung</h3>
              <p className="text-xs text-zinc-400 leading-relaxed">
                Persönliche Kontaktdaten werden strikt isoliert und nicht unverschlüsselt in KI-Reasoning-Prompts übertragen (Datensparsamkeit nach Art. 5 Abs. 1 lit. c DSGVO).
              </p>
            </div>

            <div className="bg-zinc-900/60 border border-zinc-800/80 rounded-xl p-5 space-y-2">
              <Cpu className="h-5 w-5 text-indigo-400" />
              <h3 className="font-semibold text-zinc-200 text-sm">Anti-Halluzination Gate</h3>
              <p className="text-xs text-zinc-400 leading-relaxed">
                KI-Modelle fungieren ausschließlich als Indexierungshelfer (<code className="font-mono text-violet-400">selected_ids ⊆ allowed_ids</code>). Sie erzeugen keine unüberprüften biometrischen oder biografischen Daten.
              </p>
            </div>

            <div className="bg-zinc-900/60 border border-zinc-800/80 rounded-xl p-5 space-y-2">
              <UserCheck className="h-5 w-5 text-emerald-400" />
              <h3 className="font-semibold text-zinc-200 text-sm">Human-in-the-Loop</h3>
              <p className="text-xs text-zinc-400 leading-relaxed">
                Keine vollautomatisierte Entscheidung nach Art. 22 DSGVO. Der Nutzer verifiziert jeden Beleg manuell und entscheidet über jede Bewerbung.
              </p>
            </div>
          </div>

          {/* DSGVO Abschnitte */}
          <div className="space-y-8">
            {/* 1. Verantwortlicher */}
            <section className="space-y-3">
              <h2 className="text-xl font-bold text-zinc-100 flex items-center gap-2">
                1. Name und Anschrift des Verantwortlichen
              </h2>
              <p className="text-zinc-400">
                Verantwortlicher im Sinne der Datenschutz-Grundverordnung (DSGVO), sonstiger in den Mitgliedstaaten der Europäischen Union geltenden Datenschutzgesetze und anderer Bestimmungen mit datenschutzrechtlichem Charakter ist:
              </p>
              <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-lg p-4 font-mono text-xs text-zinc-300 space-y-1">
                <p className="text-zinc-100 font-semibold">FindJobFit</p>
                <p className="text-zinc-400 italic">[Vor- und Nachname des Betreibers / Ladungsfähige Anschrift]</p>
                <p>Hessen, Bundesrepublik Deutschland</p>
                <p>
                  E-Mail:{" "}
                  <a href="mailto:support@findjobfit.de" className="text-violet-400 hover:underline">
                    support@findjobfit.de
                  </a>
                </p>
              </div>
            </section>

            {/* 2. Rechtsgrundlagen */}
            <section className="space-y-3">
              <h2 className="text-xl font-bold text-zinc-100">
                2. Rechtsgrundlagen der Verarbeitung
              </h2>
              <p className="text-zinc-400">
                Die Verarbeitung personenbezogener Daten erfolgt im Einklang mit den Bestimmungen der DSGVO und des BDSG:
              </p>
              <ul className="list-disc pl-5 space-y-2 text-zinc-400">
                <li>
                  <strong className="text-zinc-200">Art. 6 Abs. 1 lit. b DSGVO (Vertragserfüllung):</strong> Zur Erbringung unseres Dienstes (Ingestion von Lebensläufen, Strukturierung in die Evidence Bank, Filterung passender Stellen und Generierung von Bewerbungsunterlagen).
                </li>
                <li>
                  <strong className="text-zinc-200">§ 26 BDSG (Bewerberdatenverarbeitung):</strong> Zur Speicherung und zielgerichteten Aufbereitung beruflicher Qualifikationen, Werdegänge und Zeugnisse des Bewerbers.{" "}
                  <a
                    href="https://www.gesetze-im-internet.de/bdsg_2018/__26.html"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-violet-400 hover:underline inline-flex items-center gap-1 font-mono text-xs"
                  >
                    (Gesetzestext)
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </li>
                <li>
                  <strong className="text-zinc-200">Art. 6 Abs. 1 lit. a DSGVO (Einwilligung):</strong> Für optionale experimentelle KI-Funktionen und personalisierte Benachrichtigungen, sofern eine ausdrückliche Einwilligung erteilt wurde.
                </li>
                <li>
                  <strong className="text-zinc-200">Art. 6 Abs. 1 lit. f DSGVO (Berechtigtes Interesse):</strong> Für die Gewährleistung der IT-Sicherheit, Missbrauchsbekämpfung und die Aggregation öffentlich zugänglicher Stellenanzeigen (§ 44b UrhG).
                </li>
              </ul>
            </section>

            {/* 3. CV Ingestion */}
            <section className="space-y-3">
              <h2 className="text-xl font-bold text-zinc-100">
                3. Datenverarbeitung: CV-Ingestion &amp; Evidence Bank
              </h2>
              <p className="text-zinc-400">
                Wenn Sie Ihren Lebenslauf (PDF, DOCX oder Text) hochladen, wird das Dokument in diskrete, atomare Informationseinheiten zerlegt:
              </p>
              <ul className="list-disc pl-5 space-y-1 text-zinc-400">
                <li>Berufliche Erfahrungen, Projekte, Bildungsabschlüsse und Zertifikate</li>
                <li>Kategorisierte Fähigkeiten und Kenntnisse</li>
                <li>Verbindliche Zuweisung unveränderlicher Beleg-IDs (z. B. <code className="font-mono text-violet-400">EXP_001</code>)</li>
              </ul>
              <p className="text-zinc-400">
                <strong className="text-zinc-200">Verifikationsprinzip:</strong> Alle extrahierten Daten verbleiben zunächst im unbestätigten Entwurfsstatus (<code className="font-mono text-violet-400">is_verified = False</code>). Sie werden erst nach Ihrer manuellen Freigabe für Matching- und Bewerbungsprozesse aktiviert.
              </p>
            </section>

            {/* 4. KI-Verarbeitung */}
            <section className="space-y-3">
              <h2 className="text-xl font-bold text-zinc-100">
                4. KI-Verarbeitung &amp; Datenschutz-Schutzwall (Privacy Gate)
              </h2>
              <p className="text-zinc-400">
                Um Ihre Privatsphäre zu schützen und Halluzinationen auszuschließen, folgt die Plattform strengen Grundsätzen:
              </p>
              <div className="space-y-2 text-zinc-400">
                <p>
                  &bull; <strong className="text-zinc-200">Selektionsprinzip statt Generierung:</strong> Bei der Anpassung von Lebensläufen formuliert die KI keine neuen Fakten. Sie erhält lediglich eine Liste erlaubter IDs (<code className="font-mono text-violet-400">allowed_ids</code>) und wählt die passenden IDs aus. Die Textauflösung erfolgt ausschließlich deterministisch aus unserer gesicherten Datenbank.
                </p>
                <p>
                  &bull; <strong className="text-zinc-200">Lokale Ausführung (Offline-LLM):</strong> Unsere Architektur unterstützt den Betrieb mit lokalen Modellen (z. B. Ollama / Llama 3). Bei Nutzung lokaler Modelle verlassen Ihre Bewerbungsdaten zu keinem Zeitpunkt Ihre eigene Infrastruktur bzw. unseren gesicherten Server.
                </p>
                <p>
                  &bull; <strong className="text-zinc-200">Kein KI-Training mit Nutzerdaten:</strong> Weder wir noch unsere angebundenen API-Endpunkte nutzen Ihre Lebensläufe, Belege oder Anschreiben zum Trainieren von Basismodellen.
                </p>
              </div>
            </section>

            {/* 5. Art. 22 DSGVO */}
            <section className="space-y-3">
              <h2 className="text-xl font-bold text-zinc-100 flex items-center gap-2">
                <Eye className="h-5 w-5 text-violet-400" />
                5. Keine vollautomatisierte Entscheidungsfindung (Art. 22 DSGVO)
              </h2>
              <p className="text-zinc-400">
                Die Plattform führt <strong>keine</strong> vollautomatisierte Entscheidungsfindung oder Profiling im Sinne von Art. 22 DSGVO durch, die Ihnen gegenüber rechtliche Wirkung entfaltet. FindJobFit dient als Assistenzwerkzeug (Decision Support). Das System schlägt Übereinstimmungen und Entwürfe vor; die finale Entscheidung über die Einreichung einer Bewerbung liegt stets vollumfänglich beim Nutzer (<strong className="text-zinc-200">Human-in-the-Loop</strong>).
              </p>
            </section>

            {/* 6. Rechte der betroffenen Person */}
            <section className="space-y-3">
              <h2 className="text-xl font-bold text-zinc-100 flex items-center gap-2">
                <ShieldCheck className="h-5 w-5 text-emerald-400" />
                6. Ihre Rechte als betroffene Person
              </h2>
              <p className="text-zinc-400">
                Sie haben jederzeit das Recht:
              </p>
              <ul className="list-disc pl-5 space-y-1.5 text-zinc-400">
                <li><strong className="text-zinc-200">Art. 15 DSGVO:</strong> Auskunft über Ihre von uns verarbeiteten personenbezogenen Daten zu verlangen.</li>
                <li><strong className="text-zinc-200">Art. 16 DSGVO:</strong> Unverzüglich die Berichtigung unrichtiger Daten oder Vervollständigung zu verlangen.</li>
                <li><strong className="text-zinc-200">Art. 17 DSGVO:</strong> Die unverzügliche Löschung Ihrer Daten zu verlangen (&bdquo;Recht auf Vergessenwerden&ldquo;).</li>
                <li><strong className="text-zinc-200">Art. 18 DSGVO:</strong> Die Einschränkung der Verarbeitung Ihrer Daten zu verlangen.</li>
                <li><strong className="text-zinc-200">Art. 20 DSGVO:</strong> Ihre Daten in einem strukturierten, gängigen und maschinenlesbaren Format zu erhalten (Datenübertragbarkeit).</li>
                <li><strong className="text-zinc-200">Art. 21 DSGVO:</strong> Widerspruch gegen die Verarbeitung einzulegen.</li>
                <li>
                  <strong className="text-zinc-200">Art. 77 DSGVO:</strong> Beschwerderecht bei der zuständigen Aufsichtsbehörde:{" "}
                  <span className="text-zinc-200 font-medium">Der Hessische Beauftragte für Datenschutz und Informationsfreiheit (HBDI)</span>, Gustav-Stresemann-Ring 1, 65189 Wiesbaden (
                  <a
                    href="https://datenschutz.hessen.de"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-violet-400 hover:underline inline-flex items-center gap-1 font-mono text-xs"
                  >
                    https://datenschutz.hessen.de
                    <ExternalLink className="h-3 w-3" />
                  </a>).
                </li>
              </ul>
            </section>

            {/* 7. Speicherdauer */}
            <section className="space-y-3">
              <h2 className="text-xl font-bold text-zinc-100">
                7. Speicherdauer und Kontolöschung
              </h2>
              <p className="text-zinc-400">
                Personenbezogene Daten werden gelöscht, sobald der Zweck ihrer Speicherung entfällt oder Sie Ihr Nutzerkonto löschen. Bei Löschung des Kontos werden sämtliche Einträge der Evidence Bank, Präferenzen, generierte Dokumente und Bewerbungshistorien unwiderruflich aus der Datenbank entfernt.
              </p>
            </section>

            {/* 8. TDDDG */}
            <section className="space-y-3">
              <h2 className="text-xl font-bold text-zinc-100">
                8. Lokale Speicherung und Token (§ 25 TDDDG)
              </h2>
              <p className="text-zinc-400">
                Unsere Anwendung verwendet technisch notwendige Sitzungstoken (JWT - JSON Web Tokens) im LocalStorage bzw. in HTTP-Only Cookies, um Ihren Authentifizierungsstatus aufrechtzuerhalten. Gemäß § 25 Abs. 2 Nr. 2 TDDDG ist für diese technisch zwingend erforderlichen Speicherzugriffe keine gesonderte Cookie-Einwilligung erforderlich. Wir setzen keine Werbe- oder Drittanbieter-Tracking-Cookies ein.
              </p>
            </section>

            {/* 9. Hosting */}
            <section className="space-y-3">
              <h2 className="text-xl font-bold text-zinc-100 flex items-center gap-2">
                <Server className="h-5 w-5 text-violet-400" />
                9. Hosting &amp; Server-Infrastruktur
              </h2>
              <p className="text-zinc-400">
                Wir hosten die Plattform über den Cloud-Hosting-Dienst <strong className="text-zinc-200">Railway</strong> (Railway Corp., 548 Market St, Suite 63441, San Francisco, CA 94104, USA). Die Server für Frontend und Backend befinden sich in europäischen Rechenzentren (Region EU-West). Rechtsgrundlage für den Einsatz dieses Hosting-Dienstleisters ist Art. 6 Abs. 1 lit. f DSGVO. Soweit Daten in die USA übertragen werden, erfolgt dies auf Grundlage von Standardvertragsklauseln der EU-Kommission bzw. des EU-US Data Privacy Frameworks (
                <a
                  href="https://www.dataprivacyframework.gov"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-violet-400 hover:underline inline-flex items-center gap-1 font-mono text-xs"
                >
                  www.dataprivacyframework.gov
                  <ExternalLink className="h-3 w-3" />
                </a>).
              </p>
            </section>
          </div>
        </div>
      }
    />
  );
}
