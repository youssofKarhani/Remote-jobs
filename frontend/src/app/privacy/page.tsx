import type { Metadata } from "next";
import { LegalPageShell } from "@/components/legal/legal-page-shell";
import { vcopy } from "@/lib/verification-copy";

export const metadata: Metadata = {
  title: "Datenschutzerklärung (Privacy Policy) | FindJobFit",
  description: "Informationen über die Verarbeitung personenbezogener Daten nach Art. 13 und 14 DSGVO sowie dem BDSG.",
};

export default function PrivacyPage() {
  return (
    <LegalPageShell
      badgeTextEn="Data Protection"
      badgeTextDe="Datenschutz"
      titleEn="Privacy Policy"
      titleDe="Datenschutzerklärung"
      descriptionEn="Information on the processing of personal data in accordance with Articles 13 and 14 of the General Data Protection Regulation (GDPR)."
      descriptionDe="Informationen über die Verarbeitung personenbezogener Daten nach Art. 13 und 14 der Datenschutz-Grundverordnung (DSGVO)."
      childrenEn={
        <div className="space-y-8 text-sm text-zinc-300 leading-relaxed">
          {/* 1. Controller */}
          <section className="space-y-3 bg-zinc-900/40 border border-zinc-800 rounded-lg p-5">
            <h2 className="text-base font-semibold text-zinc-100">
              1. Data Controller
            </h2>
            <p className="text-zinc-400">
              The controller responsible for data processing on this platform pursuant to Article 4 No. 7 GDPR is:
            </p>
            <div className="text-zinc-200 text-xs font-mono space-y-1">
              <p className="font-semibold text-sm text-zinc-100 font-sans">Youssof El Karhani</p>
              <p>Borngasse 2</p>
              <p>35274 Kirchhain, Germany</p>
              <p>
                Email:{" "}
                <a href="mailto:support@findjobfit.de" className="text-violet-400 hover:underline">
                  support@findjobfit.de
                </a>
              </p>
            </div>
          </section>

          {/* 2. Collection & Purposes */}
          <section className="space-y-3">
            <h2 className="text-base font-semibold text-zinc-100">
              2. Data Processing on This Platform
            </h2>
            <p className="text-zinc-400">
              We process personal data only to the extent necessary to provide an operational website and deliver our services:
            </p>
            <ul className="list-disc pl-5 space-y-1.5 text-zinc-400">
              <li>
                <strong className="text-zinc-200">Account Registration:</strong> When you register, we collect your email address and authentication credentials to secure your account.
              </li>
              <li>
                <strong className="text-zinc-200">Resume &amp; Career Information:</strong> {vcopy("privacy.careerInfo")}
              </li>
              <li>
                <strong className="text-zinc-200">Candidate Preferences:</strong> Defined search criteria (e.g. target roles, locations, remote options) are stored to filter job listings.
              </li>
            </ul>
          </section>

          {/* 3. Legal Bases */}
          <section className="space-y-3">
            <h2 className="text-base font-semibold text-zinc-100">
              3. Legal Bases for Processing
            </h2>
            <ul className="list-disc pl-5 space-y-2 text-zinc-400">
              <li>
                <strong className="text-zinc-200">Art. 6 para. 1 lit. b GDPR (Contract Fulfillment):</strong> Processing is required to perform the services requested by the user.
              </li>
              <li>
                <strong className="text-zinc-200">Art. 6 para. 1 lit. f GDPR (Legitimate Interests):</strong> Processing necessary to maintain system security, defend against unauthorized access, and ensure server stability.
              </li>
              <li>
                <strong className="text-zinc-200">Art. 6 para. 1 lit. a GDPR (Consent):</strong> Applicable where you have granted explicit consent for specific features.
              </li>
            </ul>
          </section>

          {/* 4. AI-Assisted Processing */}
          <section className="space-y-3">
            <h2 className="text-base font-semibold text-zinc-100">
              4. AI-Assisted Processing &amp; Control
            </h2>
            <p className="text-zinc-400">
              {vcopy("privacy.mlModels")}
            </p>
            <ul className="list-disc pl-5 space-y-1.5 text-zinc-400">
              <li>
                <strong className="text-zinc-200">No Automated Decisions (Art. 22 GDPR):</strong> No fully automated decisions or profiling with legal effect are carried out. The user retains full control and manually decides whether to use or submit any generated application materials.
              </li>
              <li>
                <strong className="text-zinc-200">No Model Training on User Data:</strong> Personal resume details are not used to train public baseline AI models.
              </li>
            </ul>
          </section>

          {/* 5. Hosting & Infrastructure */}
          <section className="space-y-3">
            <h2 className="text-base font-semibold text-zinc-100">
              5. Hosting &amp; Infrastructure
            </h2>
            <p className="text-zinc-400">
              Our website is hosted with the cloud provider Railway (Railway Corp., 548 Market St, Suite 63441, San Francisco, CA 94104, USA). The servers processing application traffic are deployed in European data centers (EU-West region). Processing is based on our legitimate interest in providing a reliable, secure service (Art. 6 para. 1 lit. f GDPR) in compliance with EU Standard Contractual Clauses.
            </p>
          </section>

          {/* 6. Retention and Deletion */}
          <section className="space-y-3">
            <h2 className="text-base font-semibold text-zinc-100">
              6. Storage Duration &amp; Account Deletion
            </h2>
            <p className="text-zinc-400">
              We process and store personal data only for as long as required to achieve the purpose of storage. If you delete your account via the platform settings, your account credentials, uploaded resumes, and saved profile data are removed from active databases.
            </p>
          </section>

          {/* 7. Data Subject Rights */}
          <section className="space-y-3">
            <h2 className="text-base font-semibold text-zinc-100">
              7. Your Rights under the GDPR
            </h2>
            <p className="text-zinc-400">
              You have the statutory right under the GDPR to:
            </p>
            <ul className="list-disc pl-5 space-y-1 text-zinc-400">
              <li>Request information about your processed personal data (Art. 15 GDPR).</li>
              <li>Request correction of inaccurate personal data (Art. 16 GDPR).</li>
              <li>Request erasure of your data (&ldquo;right to be forgotten&rdquo;) (Art. 17 GDPR).</li>
              <li>Request restriction of processing (Art. 18 GDPR).</li>
              <li>Receive your data in a structured, commonly used format (Art. 20 GDPR).</li>
              <li>Object to processing based on legitimate interests (Art. 21 GDPR).</li>
            </ul>
          </section>

          {/* 8. Supervisory Authority */}
          <section className="space-y-3">
            <h2 className="text-base font-semibold text-zinc-100">
              8. Competent Supervisory Authority
            </h2>
            <p className="text-zinc-400">
              Under Article 77 GDPR, you have the right to lodge a complaint with a data protection supervisory authority. The competent authority for the state of Hesse is:
            </p>
            <div className="bg-zinc-900/40 border border-zinc-800 rounded-lg p-4 text-xs font-mono text-zinc-300 space-y-1">
              <p className="font-semibold text-zinc-200">Der Hessische Beauftragte für Datenschutz und Informationsfreiheit (HBDI)</p>
              <p>Gustav-Stresemann-Ring 1, 65189 Wiesbaden</p>
              <p>
                Website:{" "}
                <a href="https://datenschutz.hessen.de" target="_blank" rel="noopener noreferrer" className="text-violet-400 hover:underline">
                  https://datenschutz.hessen.de
                </a>
              </p>
            </div>
          </section>
        </div>
      }
      childrenDe={
        <div className="space-y-8 text-sm text-zinc-300 leading-relaxed">
          {/* 1. Verantwortlicher */}
          <section className="space-y-3 bg-zinc-900/40 border border-zinc-800 rounded-lg p-5">
            <h2 className="text-base font-semibold text-zinc-100">
              1. Name und Anschrift des Verantwortlichen
            </h2>
            <p className="text-zinc-400">
              Verantwortlicher im Sinne der Datenschutz-Grundverordnung (DSGVO) und des Bundesdatenschutzgesetzes (BDSG) ist:
            </p>
            <div className="text-zinc-200 text-xs font-mono space-y-1">
              <p className="font-semibold text-sm text-zinc-100 font-sans">Youssof El Karhani</p>
              <p>Borngasse 2</p>
              <p>35274 Kirchhain, Deutschland</p>
              <p>
                E-Mail:{" "}
                <a href="mailto:support@findjobfit.de" className="text-violet-400 hover:underline">
                  support@findjobfit.de
                </a>
              </p>
            </div>
          </section>

          {/* 2. Datenverarbeitung */}
          <section className="space-y-3">
            <h2 className="text-base font-semibold text-zinc-100">
              2. Erhebung und Verarbeitung personenbezogener Daten
            </h2>
            <p className="text-zinc-400">
              Wir verarbeiten personenbezogene Daten ausschließlich im Rahmen der gesetzlichen Vorschriften und für den Betrieb unseres Dienstes:
            </p>
            <ul className="list-disc pl-5 space-y-1.5 text-zinc-400">
              <li>
                <strong className="text-zinc-200">Registrierung und Konto:</strong> Bei der Erstellung eines Nutzerkontos erfassen wir Ihre E-Mail-Adresse und Zugangsdaten zur Bereitstellung des Zugangs.
              </li>
              <li>
                <strong className="text-zinc-200">Lebenslauf- und Berufsdaten:</strong> Von Ihnen hochgeladene Lebensläufe und Qualifikationen werden strukturiert, um einen Abgleich mit passenden Stellenangeboten zu ermöglichen.
              </li>
              <li>
                <strong className="text-zinc-200">Nutzungspräferenzen:</strong> Ihre Angaben zu bevorzugten Tätigkeiten, Arbeitsorten und Arbeitszeitmodellen dienen der Filterung passender Angebote.
              </li>
            </ul>
          </section>

          {/* 3. Rechtsgrundlagen */}
          <section className="space-y-3">
            <h2 className="text-base font-semibold text-zinc-100">
              3. Rechtsgrundlagen der Verarbeitung
            </h2>
            <ul className="list-disc pl-5 space-y-2 text-zinc-400">
              <li>
                <strong className="text-zinc-200">Art. 6 Abs. 1 lit. b DSGVO (Vertragserfüllung):</strong> Die Verarbeitung ist zur Erbringung unserer vertraglichen Leistungen erforderlich.
              </li>
              <li>
                <strong className="text-zinc-200">Art. 6 Abs. 1 lit. f DSGVO (Berechtigtes Interesse):</strong> Zur Gewährleistung der IT-Sicherheit, Abwehr von Missbrauch und Stabilität der Systeme.
              </li>
              <li>
                <strong className="text-zinc-200">Art. 6 Abs. 1 lit. a DSGVO (Einwilligung):</strong> Sofern Sie uns eine ausdrückliche Einwilligung für spezifische Funktionen erteilt haben.
              </li>
            </ul>
          </section>

          {/* 4. KI-Verarbeitung */}
          <section className="space-y-3">
            <h2 className="text-base font-semibold text-zinc-100">
              4. KI-gestützte Datenverarbeitung
            </h2>
            <p className="text-zinc-400">
              Die Plattform nutzt Algorithmen zur Analyse von Stellenanzeigen und zum Abgleich mit den vom Nutzer hinterlegten Qualifikationen:
            </p>
            <ul className="list-disc pl-5 space-y-1.5 text-zinc-400">
              <li>
                <strong className="text-zinc-200">Keine automatisierten Entscheidungen (Art. 22 DSGVO):</strong> Es erfolgt keine vollautomatisierte Entscheidung mit Rechtswirkung gegenüber dem Nutzer. Das System dient als Assistenzwerkzeug; jede Übernahme oder Absendung von Unterlagen erfolgt manuell durch den Nutzer.
              </li>
              <li>
                <strong className="text-zinc-200">Kein Modelltraining mit Nutzerdaten:</strong> Persönliche Daten und Lebensläufe werden nicht zum Training allgemeiner KI-Modelle verwendet.
              </li>
            </ul>
          </section>

          {/* 5. Hosting */}
          <section className="space-y-3">
            <h2 className="text-base font-semibold text-zinc-100">
              5. Hosting und Infrastruktur
            </h2>
            <p className="text-zinc-400">
              Die Anwendung wird über den Cloud-Hosting-Dienst Railway (Railway Corp., 548 Market St, Suite 63441, San Francisco, CA 94104, USA) in europäischen Rechenzentren (Region EU-West) gehostet. Grundlage ist unser berechtigtes Interesse an einem stabilen und sicheren Betrieb (Art. 6 Abs. 1 lit. f DSGVO). Soweit Daten in Drittstaaten übermittelt werden, erfolgt dies auf Grundlage von Standardvertragsklauseln der EU-Kommission.
            </p>
          </section>

          {/* 6. Speicherdauer */}
          <section className="space-y-3">
            <h2 className="text-base font-semibold text-zinc-100">
              6. Speicherdauer und Löschung
            </h2>
            <p className="text-zinc-400">
              Personenbezogene Daten werden gelöscht, sobald der Zweck ihrer Speicherung entfällt oder Sie Ihr Benutzerkonto löschen. Gesetzliche Aufbewahrungspflichten bleiben unberührt.
            </p>
          </section>

          {/* 7. Betroffenenrechte */}
          <section className="space-y-3">
            <h2 className="text-base font-semibold text-zinc-100">
              7. Ihre Rechte als betroffene Person
            </h2>
            <p className="text-zinc-400">
              Nach der DSGVO stehen Ihnen folgende Rechte zu:
            </p>
            <ul className="list-disc pl-5 space-y-1 text-zinc-400">
              <li>Auskunft über Ihre von uns verarbeiteten Daten (Art. 15 DSGVO).</li>
              <li>Berichtigung unrichtiger Daten (Art. 16 DSGVO).</li>
              <li>Löschung Ihrer Daten (Art. 17 DSGVO).</li>
              <li>Einschränkung der Verarbeitung (Art. 18 DSGVO).</li>
              <li>Datenübertragbarkeit in einem maschinenlesbaren Format (Art. 20 DSGVO).</li>
              <li>Widerspruch gegen die Verarbeitung (Art. 21 DSGVO).</li>
            </ul>
          </section>

          {/* 8. Aufsichtsbehörde */}
          <section className="space-y-3">
            <h2 className="text-base font-semibold text-zinc-100">
              8. Zuständige Datenschutz-Aufsichtsbehörde
            </h2>
            <p className="text-zinc-400">
              Sie haben gemäß Art. 77 DSGVO das Recht auf Beschwerde bei einer Aufsichtsbehörde. Die für unseren Standort zuständige Behörde ist:
            </p>
            <div className="bg-zinc-900/40 border border-zinc-800 rounded-lg p-4 text-xs font-mono text-zinc-300 space-y-1">
              <p className="font-semibold text-zinc-200">Der Hessische Beauftragte für Datenschutz und Informationsfreiheit (HBDI)</p>
              <p>Gustav-Stresemann-Ring 1, 65189 Wiesbaden</p>
              <p>
                Website:{" "}
                <a href="https://datenschutz.hessen.de" target="_blank" rel="noopener noreferrer" className="text-violet-400 hover:underline">
                  https://datenschutz.hessen.de
                </a>
              </p>
            </div>
          </section>
        </div>
      }
    />
  );
}
