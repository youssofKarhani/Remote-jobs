import type { Metadata } from "next";
import { Scale, Mail, MapPin, ShieldAlert, FileText } from "lucide-react";

export const metadata: Metadata = {
  title: "Impressum | RemoteJobs Platform",
  description: "Gesetzliche Anbieterkennzeichnung gemäß § 5 Digitale-Dienste-Gesetz (DDG).",
};

export default function ImpressumPage() {
  return (
    <div className="max-w-4xl mx-auto py-10 px-4 space-y-10">
      {/* Header */}
      <div className="space-y-3 border-b border-zinc-800 pb-6">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-mono bg-violet-950/40 text-violet-400 border border-violet-800/40">
          <Scale className="h-3.5 w-3.5" />
          <span>Rechtliche Anbieterkennzeichnung</span>
        </div>
        <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-zinc-100">
          Impressum
        </h1>
        <p className="text-sm text-zinc-400">
          Angaben gemäß § 5 Digitale-Dienste-Gesetz (DDG) (vormals Telemediengesetz - TMG)
        </p>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Angaben zum Betreiber */}
        <div className="bg-zinc-900/60 border border-zinc-800/80 rounded-xl p-6 space-y-4">
          <div className="flex items-center gap-2 text-violet-400 font-mono text-sm font-semibold">
            <MapPin className="h-4 w-4" />
            <span>Dienstanbieter</span>
          </div>
          <div className="text-sm text-zinc-300 space-y-1 leading-relaxed">
            <p className="font-semibold text-zinc-100">RemoteJobs Public Platform</p>
            <p>Musterstraße 42</p>
            <p>10115 Berlin</p>
            <p>Deutschland / Germany</p>
          </div>
        </div>

        {/* Kontakt */}
        <div className="bg-zinc-900/60 border border-zinc-800/80 rounded-xl p-6 space-y-4">
          <div className="flex items-center gap-2 text-violet-400 font-mono text-sm font-semibold">
            <Mail className="h-4 w-4" />
            <span>Kontaktmöglichkeiten</span>
          </div>
          <div className="text-sm text-zinc-300 space-y-2 leading-relaxed font-mono">
            <p>E-Mail: <span className="text-zinc-100">legal@remotejobs-platform.com</span></p>
            <p>Support: <span className="text-zinc-100">support@remotejobs-platform.com</span></p>
            <p className="text-xs text-zinc-400 font-sans">
              Schnelle elektronische Kontaktaufnahme gemäß § 5 Abs. 1 Nr. 2 DDG gewährleistet.
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
          RemoteJobs Public Platform Team<br />
          Musterstraße 42, 10115 Berlin, Deutschland
        </p>
      </div>

      {/* Rechtliche Hinweise */}
      <div className="space-y-6 text-sm text-zinc-300 leading-relaxed">
        <section className="space-y-2">
          <h2 className="text-lg font-semibold text-zinc-100 flex items-center gap-2">
            <ShieldAlert className="h-4 w-4 text-violet-400" />
            Haftung für Inhalte
          </h2>
          <p className="text-zinc-400">
            Als Diensteanbieter sind wir gemäß § 7 Abs. 1 DDG für eigene Inhalte auf diesen Seiten nach den allgemeinen Gesetzen verantwortlich. Nach §§ 8 bis 10 DDG sind wir als Diensteanbieter jedoch nicht verpflichtet, übermittelte oder gespeicherte fremde Informationen (wie externe Stellenanzeigen oder von Nutzern bereitgestellte Bewerbungsdaten) zu überwachen oder nach Umständen zu forschen, die auf eine rechtswidrige Tätigkeit hinweisen. Verpflichtungen zur Entfernung oder Sperrung der Nutzung von Informationen nach den allgemeinen Gesetzen bleiben hiervon unberührt.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-lg font-semibold text-zinc-100">Haftung für externe Links</h2>
          <p className="text-zinc-400">
            Unser Angebot enthält Links zu externen Websites Dritter (z. B. externe Stellenportale und Arbeitgeber-Websites), auf deren Inhalte wir keinen Einfluss haben. Deshalb können wir für diese fremden Inhalte auch keine Gewähr übernehmen. Für die Inhalte der verlinkten Seiten ist stets der jeweilige Anbieter oder Betreiber der Seiten verantwortlich. Bei Bekanntwerden von Rechtsverletzungen werden wir derartige Links umgehend entfernen.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-lg font-semibold text-zinc-100">Urheberrecht und Text- und Data-Mining (§ 44b UrhG)</h2>
          <p className="text-zinc-400">
            Die durch die Seitenbetreiber erstellten Inhalte und Werke auf diesen Seiten unterliegen dem deutschen Urheberrecht. Die Erfassung und Aggregation öffentlich zugänglicher Stellenangebote erfolgt unter Wahrung der gesetzlichen Bestimmungen, insbesondere der Schrankenregelungen für Text- und Data-Mining gemäß § 44b UrhG sowie im Rahmen öffentlicher Programmierschnittstellen (APIs).
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-lg font-semibold text-zinc-100">Verbraucherstreitbeilegung (§ 36 VSBG)</h2>
          <p className="text-zinc-400">
            Die Europäische Kommission stellt eine Plattform zur Online-Streitbeilegung (OS) bereit:{" "}
            <a
              href="https://ec.europa.eu/consumers/odr"
              target="_blank"
              rel="noopener noreferrer"
              className="text-violet-400 hover:underline"
            >
              https://ec.europa.eu/consumers/odr
            </a>.
            Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.
          </p>
        </section>
      </div>
    </div>
  );
}
