import type { Metadata } from "next";
import { ShieldCheck, CheckCircle2, HeartHandshake, Scale, Lock, Eye, Sparkles } from "lucide-react";

export const metadata: Metadata = {
  title: "Ethik & Rechtliche Konformität (Ethics & Compliance) | RemoteJobs Platform",
  description: "Warum RemoteJobs ethisch ist und deutschen sowie europäischen Gesetzen entspricht: EU AI Act, DSGVO, BDSG § 26 und AGG.",
};

export default function EthicsPage() {
  return (
    <div className="max-w-4xl mx-auto py-10 px-4 space-y-12">
      {/* Header */}
      <div className="space-y-4 border-b border-zinc-800 pb-8">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-mono bg-emerald-950/40 text-emerald-400 border border-emerald-800/40">
          <ShieldCheck className="h-3.5 w-3.5" />
          <span>Ethische Leitlinien &amp; Rechtskonformität</span>
        </div>
        <h1 className="text-3xl md:text-5xl font-bold tracking-tight text-zinc-100">
          Ethisches Manifest &amp; Deutsches Gesetzeskonzept
        </h1>
        <p className="text-base text-zinc-400 max-w-3xl leading-relaxed">
          Warum der Einsatz der RemoteJobs-Plattform ethisch geboten ist, wie unsere Architektur Kandidaten vor Fälschungen schützt und warum das System in vollem Einklang mit deutschen und europäischen Gesetzen steht.
        </p>
      </div>

      {/* Core Principle Banner */}
      <div className="bg-gradient-to-r from-violet-950/40 via-zinc-900 to-indigo-950/40 border border-violet-800/40 rounded-2xl p-6 md:p-8 space-y-3 shadow-xl">
        <div className="flex items-center gap-2 text-violet-400 font-mono text-xs uppercase tracking-wider">
          <Sparkles className="h-4 w-4" />
          <span>Das Ethische Grundaxiom</span>
        </div>
        <blockquote className="text-xl md:text-2xl font-serif italic text-zinc-100">
          &bdquo;Künstliche Intelligenz darf entscheiden, welche verifizierten Belege für eine Stelle relevant sind. Sie darf jedoch niemals entscheiden, welche Belege existieren.&ldquo;
        </blockquote>
        <p className="text-xs text-zinc-400 font-sans">
          Herkömmliche generative KI neigt dazu, Lebensläufe zu &bdquo;halluzinieren&ldquo; &mdash; Erfindungen, die sowohl Arbeitgeber täuschen als auch Bewerber rechtlich angreifbar machen. RemoteJobs verhindert dies auf Code-Ebene durch mathematische Invarianten.
        </p>
      </div>

      {/* Section 1: Warum ist das System ethisch? */}
      <section className="space-y-6">
        <div className="space-y-2">
          <h2 className="text-2xl font-bold text-zinc-100 flex items-center gap-2.5">
            <HeartHandshake className="h-6 w-6 text-violet-400" />
            1. Warum ist RemoteJobs ethisch?
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
              Unternehmen nutzen seit Jahren intransparente ATS-Filter. RemoteJobs gibt Kandidaten die technologische Augenhöhe zurück &mdash; ohne unlautere Tricks, sondern durch präzise Strukturierung.
            </p>
          </div>
        </div>
      </section>

      {/* Section 2: Warum verstößt es NICHT gegen deutsches und europäisches Recht? */}
      <section className="space-y-6">
        <div className="space-y-2">
          <h2 className="text-2xl font-bold text-zinc-100 flex items-center gap-2.5">
            <Scale className="h-6 w-6 text-emerald-400" />
            2. Rechtliche Konformität in Deutschland und der EU
          </h2>
          <p className="text-sm text-zinc-400">
            Detaillierte juristische Einordnung gegenüber zentralen Gesetzen:
          </p>
        </div>

        <div className="space-y-4 text-sm text-zinc-300 leading-relaxed">
          
          {/* EU AI Act */}
          <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-xl p-6 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-zinc-100 text-base">
                A. EU AI Act (KI-Verordnung - Verordnung (EU) 2024/1689)
              </h3>
              <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-emerald-950/40 text-emerald-400 border border-emerald-800/40">
                Voll Konform
              </span>
            </div>
            <p className="text-zinc-400 text-xs leading-relaxed">
              Gemäß Anhang III der KI-Verordnung gelten KI-Systeme im Bereich Beschäftigung und Personalmanagement als &bdquo;Hochrisiko-KI&ldquo;, wenn sie von <em>Arbeitgebern</em> zur automatisierten Bewerberauslese oder Entscheidung über Beförderungen eingesetzt werden.
            </p>
            <ul className="list-disc pl-5 space-y-1.5 text-xs text-zinc-400">
              <li>
                <strong className="text-zinc-200">Kandidatenseitige Assistenz:</strong> RemoteJobs ist ein Hilfsmittel für den Bewerber, kein Arbeitgeber-Filter.
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
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-zinc-100 text-base">
                B. DSGVO (GDPR) &amp; § 26 BDSG (Beschäftigtendatenschutz)
              </h3>
              <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-emerald-950/40 text-emerald-400 border border-emerald-800/40">
                DSGVO-Konform
              </span>
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

          {/* AGG (Allgemeines Gleichbehandlungsgesetz) */}
          <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-xl p-6 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-zinc-100 text-base">
                C. AGG (Allgemeines Gleichbehandlungsgesetz) &amp; Antidiskriminierung
              </h3>
              <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-emerald-950/40 text-emerald-400 border border-emerald-800/40">
                Diskriminierungsfrei
              </span>
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

          {/* BGB / StGB (Schutz vor Täuschung) */}
          <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-xl p-6 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-zinc-100 text-base">
                D. BGB &amp; StGB (Schutz vor Täuschung und Arbeitsrecht)
              </h3>
              <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-emerald-950/40 text-emerald-400 border border-emerald-800/40">
                Rechtssicher
              </span>
            </div>
            <p className="text-zinc-400 text-xs leading-relaxed">
              Im deutschen Arbeitsrecht kann eine Fälschung im Lebenslauf eine <strong>arglistige Täuschung (§ 123 BGB)</strong> darstellen oder eine fristlose Kündigung aus wichtigem Grund (§ 626 BGB) rechtfertigen.
            </p>
            <p className="text-zinc-400 text-xs leading-relaxed">
              <strong className="text-zinc-200">Der rechtliche Schutzschild von RemoteJobs:</strong> Da unser System mathematisch ausschließt, dass unbestätigte oder erfundene Stationen in den exportierten Lebenslauf gelangen, bewahrt RemoteJobs den Bewerber aktiv davor, sich unabsichtlich strafbar oder arbeitsrechtlich angreifbar zu machen.
            </p>
          </div>

          {/* § 5 DDG & TDDDG */}
          <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-xl p-6 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-zinc-100 text-base">
                E. § 5 DDG (Digitale-Dienste-Gesetz) &amp; TDDDG
              </h3>
              <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-emerald-950/40 text-emerald-400 border border-emerald-800/40">
                Aktualisiert Mai 2024
              </span>
            </div>
            <p className="text-zinc-400 text-xs leading-relaxed">
              Die Plattform erfüllt alle Vorgaben des am 14. Mai 2024 in Kraft getretenen Digitalen-Dienste-Gesetzes (DDG, Nachfolger des TMG) sowie des TDDDG (vormals TTDSG). Ein vollständiges, leicht auffindbares Impressum und datenschutzkonforme technische Token sichern den gesetzeskonformen Betrieb in Deutschland.
            </p>
          </div>

        </div>
      </section>

      {/* Summary Box */}
      <div className="border border-zinc-800 bg-zinc-900/60 rounded-xl p-6 text-center space-y-3">
        <h3 className="font-bold text-zinc-100 text-base">
          Verlässlichkeit durch Code statt Versprechen
        </h3>
        <p className="text-xs text-zinc-400 max-w-2xl mx-auto leading-relaxed">
          Ethisches Handeln entsteht bei uns nicht durch Marketingtexte, sondern durch strikte Programmiergrenzen, datenschutzfreundliche Architektur (Privacy by Design) und den unbedingten Respekt vor der menschlichen Wahrheit.
        </p>
      </div>
    </div>
  );
}
