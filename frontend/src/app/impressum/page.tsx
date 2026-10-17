import type { Metadata } from "next";
import { LegalPageShell } from "@/components/legal/legal-page-shell";
import { MapPin, Mail, Globe, FileText, ShieldAlert, Scale, ExternalLink } from "lucide-react";

export const metadata: Metadata = {
  title: "Legal Notice (Impressum) | FindJobFit",
  description: "Statutory provider identification pursuant to § 5 German Digital Services Act (Digitale-Dienste-Gesetz - DDG) and § 18 MStV.",
};

const LAW_REFS = [
  {
    code: "§ 5 DDG",
    url: "https://www.gesetze-im-internet.de/ddg/__5.html",
    title: "Digitale-Dienste-Gesetz § 5 (Provider Identification)",
  },
  {
    code: "§ 18 Abs. 2 MStV",
    url: "https://www.die-medienanstalten.de/service/rechtsgrundlagen/medienstaatsvertrag-mstv",
    title: "Medienstaatsvertrag § 18 (Editorial Responsibility)",
  },
  {
    code: "EU DSA (2022/2065)",
    url: "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R2065",
    title: "EU Digital Services Act (Intermediary Liability)",
  },
  {
    code: "§ 44b UrhG",
    url: "https://www.gesetze-im-internet.de/urhg/__44b.html",
    title: "Urheberrechtsgesetz § 44b (Text & Data Mining)",
  },
  {
    code: "§ 36 VSBG & ODR",
    url: "https://ec.europa.eu/consumers/odr",
    title: "EU Online Dispute Resolution Platform",
  },
];

export default function ImpressumPage() {
  return (
    <LegalPageShell
      badgeTextEn="Statutory Provider Disclosure"
      badgeTextDe="Rechtliche Anbieterkennzeichnung"
      titleEn="Legal Notice (Impressum)"
      titleDe="Impressum"
      descriptionEn="Statutory provider identification in accordance with § 5 of the German Digital Services Act (Digitale-Dienste-Gesetz - DDG, formerly TMG) and § 18 para. 2 of the German State Media Treaty (MStV)."
      descriptionDe="Angaben gemäß § 5 Digitale-Dienste-Gesetz (DDG) (vormals Telemediengesetz - TMG) sowie § 18 Abs. 2 Medienstaatsvertrag (MStV)."
      lawReferences={LAW_REFS}
      childrenEn={
        <div className="space-y-10 text-sm text-zinc-300 leading-relaxed">
          {/* Main Provider & Contact Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Service Provider */}
            <div className="bg-zinc-900/60 border border-zinc-800/80 rounded-xl p-6 space-y-4">
              <div className="flex items-center gap-2 text-violet-400 font-mono text-sm font-semibold">
                <MapPin className="h-4 w-4" />
                <span>Service Provider</span>
              </div>
              <div className="text-sm text-zinc-300 space-y-1.5 leading-relaxed">
                <p className="font-semibold text-zinc-100 text-base">FindJobFit</p>
                <p className="text-zinc-400 text-xs italic">[Operator Full Legal Name / Registered Summonable Address]</p>
                <p>State of Hesse, Federal Republic of Germany</p>
                <div className="pt-2 text-xs text-zinc-400 font-mono">
                  <span>EU Jurisdiction: Germany</span>
                </div>
              </div>
            </div>

            {/* Direct Contact */}
            <div className="bg-zinc-900/60 border border-zinc-800/80 rounded-xl p-6 space-y-4">
              <div className="flex items-center gap-2 text-violet-400 font-mono text-sm font-semibold">
                <Mail className="h-4 w-4" />
                <span>Contact Channels (§ 5 (1) No. 2 DDG)</span>
              </div>
              <div className="text-sm text-zinc-300 space-y-2 leading-relaxed font-mono">
                <p>
                  E-Mail:{" "}
                  <a href="mailto:support@findjobfit.de" className="text-violet-400 hover:underline">
                    support@findjobfit.de
                  </a>
                </p>
                <p>
                  Web:{" "}
                  <a href="https://findjobfit.de" className="text-violet-400 hover:underline">
                    https://findjobfit.de
                  </a>
                </p>
                <p className="text-xs text-zinc-400 font-sans pt-1">
                  Rapid electronic communication and direct dialogue are guaranteed pursuant to § 5 para. 1 no. 2 DDG.
                </p>
              </div>
            </div>
          </div>

          {/* Editorial Responsibility */}
          <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-xl p-6 space-y-3">
            <div className="flex items-center gap-2 text-zinc-200 font-semibold text-sm">
              <FileText className="h-4 w-4 text-violet-400" />
              <span>Person Responsible for Editorial Content (§ 18 para. 2 MStV)</span>
            </div>
            <p className="text-sm text-zinc-400 leading-relaxed">
              FindJobFit Editorial Team<br />
              Hesse, Germany<br />
              E-Mail:{" "}
              <a href="mailto:support@findjobfit.de" className="text-violet-400 hover:underline">
                support@findjobfit.de
              </a>
            </p>
            <p className="text-xs text-zinc-500">
              Statutory reference: Interstate Media Treaty (Medienstaatsvertrag - MStV).
            </p>
          </div>

          {/* Legal Disclaimers */}
          <div className="space-y-6">
            <section className="space-y-2.5">
              <h2 className="text-lg font-semibold text-zinc-100 flex items-center gap-2">
                <ShieldAlert className="h-4 w-4 text-violet-400" />
                <span>Liability for Platform Content (§ 7 DDG &amp; EU DSA)</span>
              </h2>
              <p className="text-zinc-400">
                As a service provider, we are responsible for our own content on these web pages under general statutory laws pursuant to § 7 para. 1 of the German Digital Services Act (DDG) and the EU Digital Services Act (DSA, Regulation (EU) 2022/2065). Pursuant to §§ 8 to 10 DDG and Article 14 DSA, we as an intermediary host provider are not obligated to monitor transmitted or stored external information (such as syndicated third-party job postings or user-entered CV experience tokens) or to investigate circumstances that indicate unlawful activity. Obligations to remove or block the use of information in accordance with general statutory laws upon substantiated notice remain unaffected.
              </p>
            </section>

            <section className="space-y-2.5">
              <h2 className="text-lg font-semibold text-zinc-100 flex items-center gap-2">
                <Globe className="h-4 w-4 text-violet-400" />
                <span>Liability for External Hyperlinks</span>
              </h2>
              <p className="text-zinc-400">
                Our platform contains links to external websites operated by third parties (e.g. external applicant tracking systems, employer career portals, public job boards, and statutory gazettes), over whose content we have no influence. Therefore, we cannot assume any liability for these external contents. The respective provider or operator of the pages is always responsible for the contents of linked pages. The linked pages were checked for potential legal infringements at the time of linking. Should any infringement become known to us, we will remove such external links immediately.
              </p>
            </section>

            <section className="space-y-2.5">
              <h2 className="text-lg font-semibold text-zinc-100 flex items-center gap-2">
                <Scale className="h-4 w-4 text-violet-400" />
                <span>Copyright &amp; Text and Data Mining (§ 44b UrhG)</span>
              </h2>
              <p className="text-zinc-400">
                The content and software compiled on these pages by FindJobFit are governed by German copyright law (Urheberrechtsgesetz - UrhG). The automated retrieval and aggregation of publicly accessible job listings is carried out strictly within statutory boundaries, particularly the text and data mining exception under{" "}
                <a
                  href="https://www.gesetze-im-internet.de/urhg/__44b.html"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-violet-400 hover:underline inline-flex items-center gap-1 font-mono text-xs"
                >
                  § 44b UrhG
                  <ExternalLink className="h-3 w-3" />
                </a>{" "}
                and Directive (EU) 2019/790, respecting machine-readable opt-outs (robots.txt reservations pursuant to § 44b para. 3 UrhG) and authorized public application programming interfaces (APIs).
              </p>
            </section>

            <section className="space-y-2.5">
              <h2 className="text-lg font-semibold text-zinc-100 flex items-center gap-2">
                <FileText className="h-4 w-4 text-violet-400" />
                <span>Consumer Dispute Resolution (§ 36 VSBG &amp; EU ODR Platform)</span>
              </h2>
              <p className="text-zinc-400">
                The European Commission provides a platform for out-of-court Online Dispute Resolution (ODR), accessible via the mandatory statutory link:{" "}
                <a
                  href="https://ec.europa.eu/consumers/odr"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-violet-400 hover:underline inline-flex items-center gap-1 font-mono text-xs"
                >
                  https://ec.europa.eu/consumers/odr
                  <ExternalLink className="h-3 w-3" />
                </a>.
                Our contact email address is:{" "}
                <a href="mailto:support@findjobfit.de" className="text-violet-400 hover:underline">
                  support@findjobfit.de
                </a>.
              </p>
              <p className="text-zinc-400">
                In accordance with § 36 of the German Consumer Dispute Resolution Act (VSBG), we state that FindJobFit is neither obligated nor willing to participate in dispute resolution proceedings before a consumer arbitration board (Verbraucherschlichtungsstelle). Competent body: Universalschlichtungsstelle des Bundes am Zentrum für Schlichtung e.V. (
                <a
                  href="https://www.verbraucher-schlichter.de"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-violet-400 hover:underline inline-flex items-center gap-1 font-mono text-xs"
                >
                  www.verbraucher-schlichter.de
                  <ExternalLink className="h-3 w-3" />
                </a>).
              </p>
            </section>
          </div>
        </div>
      }
      childrenDe={
        <div className="space-y-10 text-sm text-zinc-300 leading-relaxed">
          {/* Main Provider & Contact Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Diensteanbieter */}
            <div className="bg-zinc-900/60 border border-zinc-800/80 rounded-xl p-6 space-y-4">
              <div className="flex items-center gap-2 text-violet-400 font-mono text-sm font-semibold">
                <MapPin className="h-4 w-4" />
                <span>Diensteanbieter</span>
              </div>
              <div className="text-sm text-zinc-300 space-y-1.5 leading-relaxed">
                <p className="font-semibold text-zinc-100 text-base">FindJobFit</p>
                <p className="text-zinc-400 text-xs italic">[Vor- und Nachname des Betreibers / Ladungsfähige Anschrift]</p>
                <p>Hessen, Bundesrepublik Deutschland</p>
                <div className="pt-2 text-xs text-zinc-400 font-mono">
                  <span>EU-Rechtsraum: Deutschland</span>
                </div>
              </div>
            </div>

            {/* Kontakt */}
            <div className="bg-zinc-900/60 border border-zinc-800/80 rounded-xl p-6 space-y-4">
              <div className="flex items-center gap-2 text-violet-400 font-mono text-sm font-semibold">
                <Mail className="h-4 w-4" />
                <span>Kontaktmöglichkeiten (§ 5 Abs. 1 Nr. 2 DDG)</span>
              </div>
              <div className="text-sm text-zinc-300 space-y-2 leading-relaxed font-mono">
                <p>
                  E-Mail:{" "}
                  <a href="mailto:support@findjobfit.de" className="text-violet-400 hover:underline">
                    support@findjobfit.de
                  </a>
                </p>
                <p>
                  Internet:{" "}
                  <a href="https://findjobfit.de" className="text-violet-400 hover:underline">
                    https://findjobfit.de
                  </a>
                </p>
                <p className="text-xs text-zinc-400 font-sans pt-1">
                  Schnelle elektronische Kontaktaufnahme und unmittelbare Kommunikation sind gemäß § 5 Abs. 1 Nr. 2 DDG gewährleistet.
                </p>
              </div>
            </div>
          </div>

          {/* Verantwortlich für den Inhalt */}
          <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-xl p-6 space-y-3">
            <div className="flex items-center gap-2 text-zinc-200 font-semibold text-sm">
              <FileText className="h-4 w-4 text-violet-400" />
              <span>Verantwortlich für den Inhalt nach § 18 Abs. 2 MStV</span>
            </div>
            <p className="text-sm text-zinc-400 leading-relaxed">
              FindJobFit Redaktion<br />
              Hessen, Deutschland<br />
              E-Mail:{" "}
              <a href="mailto:support@findjobfit.de" className="text-violet-400 hover:underline">
                support@findjobfit.de
              </a>
            </p>
            <p className="text-xs text-zinc-500">
              Gesetzliche Grundlage: Medienstaatsvertrag (MStV).
            </p>
          </div>

          {/* Rechtliche Hinweise */}
          <div className="space-y-6">
            <section className="space-y-2.5">
              <h2 className="text-lg font-semibold text-zinc-100 flex items-center gap-2">
                <ShieldAlert className="h-4 w-4 text-violet-400" />
                <span>Haftung für Inhalte (§ 7 DDG &amp; EU DSA)</span>
              </h2>
              <p className="text-zinc-400">
                Als Diensteanbieter sind wir gemäß § 7 Abs. 1 Digitale-Dienste-Gesetz (DDG) sowie der Verordnung (EU) 2022/2065 (Digital Services Act - DSA) für eigene Inhalte auf diesen Seiten nach den allgemeinen Gesetzen verantwortlich. Nach §§ 8 bis 10 DDG und Art. 14 DSA sind wir als Host-Provider jedoch nicht verpflichtet, übermittelte oder gespeicherte fremde Informationen (wie externe Stellenangebote oder von Nutzern hinterlegte Bewerbungsbelege) aktiv zu überwachen oder nach Umständen zu forschen, die auf eine rechtswidrige Tätigkeit hinweisen. Verpflichtungen zur Entfernung oder Sperrung der Nutzung von Informationen nach den allgemeinen Gesetzen bleiben hiervon unberührt.
              </p>
            </section>

            <section className="space-y-2.5">
              <h2 className="text-lg font-semibold text-zinc-100 flex items-center gap-2">
                <Globe className="h-4 w-4 text-violet-400" />
                <span>Haftung für externe Links</span>
              </h2>
              <p className="text-zinc-400">
                Unser Angebot enthält Links zu externen Websites Dritter (z. B. externe Stellenportale, Arbeitgeber-Websites und amtliche Gesetzesseiten), auf deren Inhalte wir keinen Einfluss haben. Deshalb können wir für diese fremden Inhalte auch keine Gewähr übernehmen. Für die Inhalte der verlinkten Seiten ist stets der jeweilige Anbieter oder Betreiber der Seiten verantwortlich. Die verlinkten Seiten wurden zum Zeitpunkt der Verlinkung auf mögliche Rechtsverstöße überprüft. Bei Bekanntwerden von Rechtsverletzungen werden wir derartige Links umgehend entfernen.
              </p>
            </section>

            <section className="space-y-2.5">
              <h2 className="text-lg font-semibold text-zinc-100 flex items-center gap-2">
                <Scale className="h-4 w-4 text-violet-400" />
                <span>Urheberrecht und Text- und Data-Mining (§ 44b UrhG)</span>
              </h2>
              <p className="text-zinc-400">
                Die durch die Seitenbetreiber erstellten Inhalte und Werke auf diesen Seiten unterliegen dem deutschen Urheberrecht. Die Erfassung und Aggregation öffentlich zugänglicher Stellenangebote erfolgt unter Wahrung der gesetzlichen Bestimmungen, insbesondere der Schrankenregelungen für Text- und Data-Mining gemäß{" "}
                <a
                  href="https://www.gesetze-im-internet.de/urhg/__44b.html"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-violet-400 hover:underline inline-flex items-center gap-1 font-mono text-xs"
                >
                  § 44b UrhG
                  <ExternalLink className="h-3 w-3" />
                </a>{" "}
                sowie der EU-Richtlinie 2019/790, unter Beachtung von maschinenlesbaren Nutzungsvorbehalten (robots.txt nach § 44b Abs. 3 UrhG) und im Rahmen öffentlicher Programmierschnittstellen (APIs).
              </p>
            </section>

            <section className="space-y-2.5">
              <h2 className="text-lg font-semibold text-zinc-100 flex items-center gap-2">
                <FileText className="h-4 w-4 text-violet-400" />
                <span>Verbraucherstreitbeilegung (§ 36 VSBG &amp; OS-Plattform)</span>
              </h2>
              <p className="text-zinc-400">
                Die Europäische Kommission stellt eine Plattform zur Online-Streitbeilegung (OS) bereit:{" "}
                <a
                  href="https://ec.europa.eu/consumers/odr"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-violet-400 hover:underline inline-flex items-center gap-1 font-mono text-xs"
                >
                  https://ec.europa.eu/consumers/odr
                  <ExternalLink className="h-3 w-3" />
                </a>.
                Unsere E-Mail-Adresse lautet:{" "}
                <a href="mailto:support@findjobfit.de" className="text-violet-400 hover:underline">
                  support@findjobfit.de
                </a>.
              </p>
              <p className="text-zinc-400">
                Gemäß § 36 VSBG weisen wir darauf hin, dass wir nicht bereit oder verpflichtet sind, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen. Zuständige Schlichtungsstelle: Universalschlichtungsstelle des Bundes am Zentrum für Schlichtung e.V. (
                <a
                  href="https://www.verbraucher-schlichter.de"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-violet-400 hover:underline inline-flex items-center gap-1 font-mono text-xs"
                >
                  www.verbraucher-schlichter.de
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
