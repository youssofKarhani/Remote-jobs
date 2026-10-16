import type { Metadata } from "next";
import { FileText, ShieldAlert, CheckCircle2, AlertTriangle, Scale } from "lucide-react";

export const metadata: Metadata = {
  title: "Nutzungsbedingungen (Terms of Service) | RemoteJobs Platform",
  description: "Allgemeine Geschäftsbedingungen und Nutzungsrichtlinien der RemoteJobs Public Platform nach deutschem Recht (BGB).",
};

export default function TermsPage() {
  return (
    <div className="max-w-4xl mx-auto py-10 px-4 space-y-10">
      {/* Header */}
      <div className="space-y-3 border-b border-zinc-800 pb-6">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-mono bg-violet-950/40 text-violet-400 border border-violet-800/40">
          <FileText className="h-3.5 w-3.5" />
          <span>Vertragsbedingungen (AGB)</span>
        </div>
        <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-zinc-100">
          Allgemeine Geschäftsbedingungen (AGB)
        </h1>
        <p className="text-sm text-zinc-400">
          Nutzungsbedingungen für die Inanspruchnahme der Dienste der RemoteJobs Public Platform nach dem Recht der Bundesrepublik Deutschland (§§ 305 ff. BGB).
        </p>
      </div>

      {/* Key Guarantees */}
      <div className="bg-violet-950/20 border border-violet-800/40 rounded-xl p-6 space-y-3">
        <div className="flex items-center gap-2 text-violet-300 font-semibold text-sm">
          <CheckCircle2 className="h-4 w-4 text-violet-400" />
          <span>Kernprinzip: Wahrheit und Verifikation</span>
        </div>
        <p className="text-xs text-zinc-300 leading-relaxed">
          RemoteJobs verpflichtet sich und seine Nutzer dem Grundsatz der Wahrhaftigkeit im Bewerbungsprozess. Das System stellt durch mathematische Schranken (<code className="font-mono text-violet-400">selected_ids ⊆ allowed_ids</code>) sicher, dass keine Qualifikationen oder Erfahrungen frei erfunden werden. Der Nutzer versichert, dass alle in die Evidence Bank eingestellten Daten den Tatsachen entsprechen.
        </p>
      </div>

      {/* Terms Sections */}
      <div className="space-y-8 text-sm text-zinc-300 leading-relaxed">
        
        {/* 1. Geltungsbereich */}
        <section className="space-y-3">
          <h2 className="text-xl font-bold text-zinc-100 flex items-center gap-2">
            1. Geltungsbereich und Vertragsgegenstand
          </h2>
          <p className="text-zinc-400">
            Diese Allgemeinen Geschäftsbedingungen gelten für die Nutzung der Plattform RemoteJobs (nachfolgend &bdquo;Plattform&ldquo; oder &bdquo;wir&ldquo;). Die Plattform stellt Softwarefunktionen zur Aggregation von Stellenangeboten, automatisierten semantischen Eignungsanalyse sowie deterministischen Erstellung maßgeschneiderter Bewerbungsdokumente auf Basis verifizierter Nutzerbelege bereit.
          </p>
        </section>

        {/* 2. Registrierung und Nutzerpflichten */}
        <section className="space-y-3">
          <h2 className="text-xl font-bold text-zinc-100">
            2. Registrierung, Account-Sicherheit und Wahrheitspflicht
          </h2>
          <p className="text-zinc-400">
            (1) Die Nutzung der personalisierten Funktionen erfordert die Erstellung eines Benutzerkontos. Der Nutzer ist verpflichtet, seine Zugangsdaten vertraulich zu behandeln und vor dem Zugriff Dritter zu schützen.
          </p>
          <p className="text-zinc-400">
            (2) <strong className="text-zinc-200">Wahrheitspflicht des Nutzers:</strong> Der Nutzer verpflichtet sich, in seinem Profil und seiner Evidence Bank ausschließlich wahrheitsgemäße, zutreffende und nicht irreführende Angaben über seine Ausbildung, Qualifikationen, Berufserfahrung und bisherigen Arbeitsleistungen zu hinterlegen. Die bewusste Hinterlegung falscher Angaben (insbesondere zur Täuschung potenzieller Arbeitgeber im Sinne von § 123 BGB) ist untersagt.
          </p>
        </section>

        {/* 3. Funktionsweise der KI und Anti-Halluzinations-Architektur */}
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

        {/* 4. Externe Stellenanzeigen & Dritter Erbringer */}
        <section className="space-y-3">
          <h2 className="text-xl font-bold text-zinc-100">
            4. Externe Stellenangebote
          </h2>
          <p className="text-zinc-400">
            Die auf der Plattform angezeigten Stellenangebote stammen aus externen Quellen, öffentlichen Schnittstellen oder Partnernetzwerken. Wir übernehmen keine Gewähr für die Aktualität, Richtigkeit, Vollständigkeit oder fortlaufende Verfügbarkeit der ausgeschriebenen Stellen. Das Zustandekommen eines Bewerbungsverfahrens oder Arbeitsverhältnisses liegt außerhalb unseres Einflussbereichs.
          </p>
        </section>

        {/* 5. Urheberrechte und Nutzungsrechte */}
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

        {/* 6. Haftungsbeschränkung (§§ 276, 280 BGB) */}
        <section className="space-y-3">
          <h2 className="text-xl font-bold text-zinc-100 flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-amber-400" />
            6. Haftungsbeschränkung
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

        {/* 7. Kündigung und Laufzeit */}
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
            (2) Sofern der Nutzer Kaufmann, juristische Person des öffentlichen Rechts oder öffentlich-rechtliches Sondervermögen ist, ist Berlin ausschließlicher Gerichtsstand für alle Streitigkeiten aus dem Vertragsverhältnis.
          </p>
        </section>

      </div>
    </div>
  );
}
