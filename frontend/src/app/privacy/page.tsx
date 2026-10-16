import type { Metadata } from "next";
import { Lock, ShieldCheck, Database, Cpu, UserCheck, Eye } from "lucide-react";

export const metadata: Metadata = {
  title: "Datenschutzerklärung (Privacy Policy) | RemoteJobs Platform",
  description: "Datenschutzerklärung gemäß DSGVO, BDSG und TDDDG. Transparenz über Evidence Bank, KI-Verarbeitung und Betroffenenrechte.",
};

export default function PrivacyPage() {
  return (
    <div className="max-w-4xl mx-auto py-10 px-4 space-y-10">
      {/* Header */}
      <div className="space-y-3 border-b border-zinc-800 pb-6">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-mono bg-violet-950/40 text-violet-400 border border-violet-800/40">
          <Lock className="h-3.5 w-3.5" />
          <span>DSGVO &amp; BDSG Konformität</span>
        </div>
        <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-zinc-100">
          Datenschutzerklärung
        </h1>
        <p className="text-sm text-zinc-400">
          Transparente Information über die Verarbeitung personenbezogener Daten nach Art. 13 und 14 der Datenschutz-Grundverordnung (DSGVO) sowie § 26 Bundesdatenschutzgesetz (BDSG).
        </p>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-zinc-900/60 border border-zinc-800/80 rounded-xl p-5 space-y-2">
          <Database className="h-5 w-5 text-violet-400" />
          <h3 className="font-semibold text-zinc-200 text-sm">Evidence Bank Trennung</h3>
          <p className="text-xs text-zinc-400 leading-relaxed">
            Persönliche Kontaktdaten werden strikt isoliert und nicht unverschlüsselt in KI-Reasoning-Prompts übertragen (Data Minimization nach Art. 5 DSGVO).
          </p>
        </div>

        <div className="bg-zinc-900/60 border border-zinc-800/80 rounded-xl p-5 space-y-2">
          <Cpu className="h-5 w-5 text-indigo-400" />
          <h3 className="font-semibold text-zinc-200 text-sm">Anti-Halluzination Gate</h3>
          <p className="text-xs text-zinc-400 leading-relaxed">
            KI-Modelle fungieren ausschließlich als Indexierungshelfer. Sie erhalten IDs und wählen diese aus, erzeugen jedoch keine unüberprüften biometrischen oder biografischen Daten.
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

      {/* Legal Articles */}
      <div className="space-y-8 text-sm text-zinc-300 leading-relaxed">
        
        {/* 1. Verantwortlicher */}
        <section className="space-y-3">
          <h2 className="text-xl font-bold text-zinc-100 flex items-center gap-2">
            1. Name und Anschrift des Verantwortlichen
          </h2>
          <p className="text-zinc-400">
            Verantwortlicher im Sinne der Datenschutz-Grundverordnung (DSGVO), sonstiger in den Mitgliedstaaten der Europäischen Union geltenden Datenschutzgesetze und anderer Bestimmungen mit datenschutzrechtlichem Charakter ist:
          </p>
          <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-lg p-4 font-mono text-xs text-zinc-300 space-y-1">
            <p className="text-zinc-100 font-semibold">RemoteJobs Public Platform</p>
            <p>Musterstraße 42, 10115 Berlin, Deutschland</p>
            <p>E-Mail: privacy@remotejobs-platform.com</p>
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
              <strong className="text-zinc-200">§ 26 BDSG (Bewerberdatenverarbeitung):</strong> Zur Speicherung und zielgerichteten Aufbereitung beruflicher Qualifikationen, Werdegänge und Zeugnisse des Bewerbers.
            </li>
            <li>
              <strong className="text-zinc-200">Art. 6 Abs. 1 lit. a DSGVO (Einwilligung):</strong> Für optionale experimentelle KI-Funktionen und personalisierte Benachrichtigungen, sofern eine ausdrückliche Einwilligung erteilt wurde.
            </li>
            <li>
              <strong className="text-zinc-200">Art. 6 Abs. 1 lit. f DSGVO (Berechtigtes Interesse):</strong> Für die Gewährleistung der IT-Sicherheit, Missbrauchsbekämpfung und die Aggregation öffentlich zugänglicher Stellenanzeigen (§ 44b UrhG).
            </li>
          </ul>
        </section>

        {/* 3. Datenverarbeitung bei CV-Ingestion und Evidence Bank */}
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

        {/* 4. Nutzung von Künstlicher Intelligenz und LLM-Gateways */}
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
              &bull; <strong className="text-zinc-200">Lokale Ausführung (Offline-LLM):</strong> Unsere Architektur unterstützt den Betrieb mit lokalen Open-Source-Modellen (z. B. Ollama / Llama 3). Bei Nutzung lokaler Modelle verlassen Ihre Bewerbungsdaten zu keinem Zeitpunkt Ihre eigene Infrastruktur bzw. unseren gesicherten Server.
            </p>
            <p>
              &bull; <strong className="text-zinc-200">Kein KI-Training mit Nutzerdaten:</strong> Weder wir noch unsere angebundenen API-Endpunkte nutzen Ihre Lebensläufe, Belege oder Anschreiben zum Trainieren von Basismodellen.
            </p>
          </div>
        </section>

        {/* 5. Keine vollautomatisierte Entscheidungsfindung (Art. 22 DSGVO) */}
        <section className="space-y-3">
          <h2 className="text-xl font-bold text-zinc-100 flex items-center gap-2">
            <Eye className="h-5 w-5 text-violet-400" />
            5. Keine vollautomatisierte Entscheidungsfindung (Art. 22 DSGVO)
          </h2>
          <p className="text-zinc-400">
            Die Plattform führt <strong>keine</strong> vollautomatisierte Entscheidungsfindung oder Profiling im Sinne von Art. 22 DSGVO durch, die Ihnen gegenüber rechtliche Wirkung entfaltet. RemoteJobs dient als Assistenzwerkzeug (Decision Support). Das System schlägt Übereinstimmungen und Entwürfe vor; die finale Entscheidung über die Einreichung einer Bewerbung liegt stets vollumfänglich beim Nutzer (<strong className="text-zinc-200">Human-in-the-Loop</strong>).
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
            <li><strong className="text-zinc-200">Art. 77 DSGVO:</strong> Sich bei einer zuständigen Datenschutz-Aufsichtsbehörde zu beschweren (z. B. Berliner Beauftragte für Datenschutz und Informationsfreiheit).</li>
          </ul>
        </section>

        {/* 7. Speicherdauer und Löschung */}
        <section className="space-y-3">
          <h2 className="text-xl font-bold text-zinc-100">
            7. Speicherdauer und Kontolöschung
          </h2>
          <p className="text-zinc-400">
            Personenbezogene Daten werden gelöscht, sobald der Zweck ihrer Speicherung entfällt oder Sie Ihr Nutzerkonto löschen. Bei Löschung des Kontos werden sämtliche Einträge der Evidence Bank, Präferenzen, generierte Dokumente und Bewerbungshistorien unwiderruflich aus der Datenbank entfernt.
          </p>
        </section>

        {/* 8. Cookies & Lokaler Speicher (TDDDG) */}
        <section className="space-y-3">
          <h2 className="text-xl font-bold text-zinc-100">
            8. Lokale Speicherung und Token (TDDDG)
          </h2>
          <p className="text-zinc-400">
            Unsere Anwendung verwendet technisch notwendige Sitzungstoken (JWT - JSON Web Tokens) im LocalStorage bzw. in HTTP-Only Cookies, um Ihren Authentifizierungsstatus aufrechtzuerhalten. Gemäß § 25 Abs. 2 Nr. 2 TDDDG ist für diese technisch zwingend erforderlichen Speicherzugriffe keine gesonderte Cookie-Einwilligung erforderlich. Wir setzen keine Werbe- oder Drittanbieter-Tracking-Cookies ein.
          </p>
        </section>

      </div>
    </div>
  );
}
