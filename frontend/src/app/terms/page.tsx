import type { Metadata } from "next";
import { LegalPageShell } from "@/components/legal/legal-page-shell";

export const metadata: Metadata = {
  title: "Nutzungsbedingungen (Terms of Service) | FindJobFit",
  description: "Allgemeine Geschäftsbedingungen und Nutzungsrichtlinien der Plattform FindJobFit nach deutschem Recht.",
};

export default function TermsPage() {
  return (
    <LegalPageShell
      badgeTextEn="Terms of Service"
      badgeTextDe="Nutzungsbedingungen (AGB)"
      titleEn="Terms of Service"
      titleDe="Allgemeine Geschäftsbedingungen"
      descriptionEn="Terms and conditions governing the use of the FindJobFit software platform under the laws of the Federal Republic of Germany."
      descriptionDe="Bedingungen für die Inanspruchnahme der Dienste von FindJobFit nach dem Recht der Bundesrepublik Deutschland."
      childrenEn={
        <div className="space-y-8 text-sm text-zinc-300 leading-relaxed">
          <section className="space-y-2">
            <h2 className="text-base font-semibold text-zinc-100">1. Scope of Application</h2>
            <p className="text-zinc-400">
              These Terms of Service apply to all users of the FindJobFit platform, operated by Youssof El Karhani, Borngasse 2, 35274 Kirchhain, Germany. By registering or using the platform, you agree to these terms.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-base font-semibold text-zinc-100">2. Description of Services</h2>
            <p className="text-zinc-400">
              FindJobFit provides software tools for job discovery, career qualification structuring, and assisted preparation of application documents. The platform serves as a candidate-side assistive tool. We do not act as an employment agency and do not guarantee the conclusion of an employment contract.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-base font-semibold text-zinc-100">3. User Obligations and Accuracy of Information</h2>
            <p className="text-zinc-400">
              Users are required to provide truthful and accurate information regarding their education, professional experience, and qualifications. Intentionally submitting fraudulent credentials is strictly prohibited. Users remain solely responsible for reviewing and verifying all generated documents prior to transmitting them to potential employers.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-base font-semibold text-zinc-100">4. Third-Party Job Listings</h2>
            <p className="text-zinc-400">
              Job postings displayed on the platform are aggregated from external public sources and partner feeds. We do not assume liability for the correctness, completeness, or ongoing availability of external job postings.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-base font-semibold text-zinc-100">5. Limitation of Liability</h2>
            <p className="text-zinc-400">
              We are liable without limitation for intent, gross negligence, and injury to life, body, or health. In cases of slight negligence, liability is limited to the breach of essential contractual obligations (cardinal obligations) and restricted to the foreseeable, typical damage. We do not guarantee the success of applications or employment outcomes.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-base font-semibold text-zinc-100">6. Termination &amp; Account Deletion</h2>
            <p className="text-zinc-400">
              Users may terminate their contractual relationship at any time by deleting their user account in the profile settings. With account deletion, all stored candidate profiles, resumes, and personal documents are permanently removed from the active system.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-base font-semibold text-zinc-100">7. Applicable Law &amp; Jurisdiction</h2>
            <p className="text-zinc-400">
              The laws of the Federal Republic of Germany apply, excluding the UN Convention on Contracts for the International Sale of Goods (CISG). For merchants and corporate entities, the exclusive place of jurisdiction is the seat of the provider (Kirchhain, Hesse, Germany).
            </p>
          </section>
        </div>
      }
      childrenDe={
        <div className="space-y-8 text-sm text-zinc-300 leading-relaxed">
          <section className="space-y-2">
            <h2 className="text-base font-semibold text-zinc-100">1. Geltungsbereich und Vertragspartner</h2>
            <p className="text-zinc-400">
              Diese Allgemeinen Geschäftsbedingungen gelten für die Nutzung der Plattform FindJobFit, betrieben von Youssof El Karhani, Borngasse 2, 35274 Kirchhain, Deutschland. Mit der Registrierung oder Nutzung der Plattform erklärt sich der Nutzer mit diesen Bedingungen einverstanden.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-base font-semibold text-zinc-100">2. Leistungsbeschreibung</h2>
            <p className="text-zinc-400">
              FindJobFit stellt Softwarewerkzeuge zur Erfassung und Strukturierung von Qualifikationen, zur Aggregation von Stellenanzeigen und zur passgenauen Aufbereitung von Bewerbungsunterlagen bereit. Die Plattform fungiert als technisches Assistenzsystem für Bewerber. Eine Arbeitsvermittlung oder ein Erfolg von Bewerbungen wird nicht geschuldet.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-base font-semibold text-zinc-100">3. Nutzerpflichten und Wahrheitspflicht</h2>
            <p className="text-zinc-400">
              Der Nutzer verpflichtet sich, in seinem Profil und seinen Unterlagen ausschließlich wahrheitsgemäße Angaben zu hinterlegen. Die bewusste Angabe falscher Qualifikationen oder gefälschter Nachweise ist unzulässig. Der Nutzer ist verpflichtet, alle generierten Dokumente vor einem Versand sorgfältig eigenverantwortlich zu prüfen.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-base font-semibold text-zinc-100">4. Externe Stellenanzeigen</h2>
            <p className="text-zinc-400">
              Die auf der Plattform dargestellten Stellenangebote beruhen auf öffentlich zugänglichen Datenquellen und Schnittstellen Dritter. Wir übernehmen keine Gewähr für die Aktualität, Richtigkeit oder Verfügbarkeit der externen Stellenanzeigen.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-base font-semibold text-zinc-100">5. Haftung</h2>
            <p className="text-zinc-400">
              Wir haften unbeschränkt für Vorsatz, grobe Fahrlässigkeit sowie bei Verletzung von Leben, Körper oder Gesundheit. Bei leicht fahrlässiger Verletzung wesentlicher Vertragspflichten ist die Haftung auf den vertragstypischen, vorhersehbaren Schaden begrenzt. Eine Haftung für den Erfolg von Bewerbungen oder das Zustandekommen von Arbeitsverträgen ist ausgeschlossen.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-base font-semibold text-zinc-100">6. Kündigung und Kontolöschung</h2>
            <p className="text-zinc-400">
              Der Nutzer kann sein Konto jederzeit über die Kontoeinstellungen löschen. Mit der Löschung werden alle gespeicherten Profildaten, Lebensläufe und Dokumente unwiderruflich aus der aktiven Datenbank gelöscht.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-base font-semibold text-zinc-100">7. Anwendbares Recht und Gerichtsstand</h2>
            <p className="text-zinc-400">
              Es gilt das Recht der Bundesrepublik Deutschland unter Ausschluss des UN-Kaufrechts. Sofern der Nutzer Kaufmann, juristische Person des öffentlichen Rechts oder ein öffentlich-rechtliches Sondervermögen ist, ist der Sitz des Diensteanbieters (Kirchhain, Hessen, Deutschland) ausschließlicher Gerichtsstand.
            </p>
          </section>
        </div>
      }
    />
  );
}
