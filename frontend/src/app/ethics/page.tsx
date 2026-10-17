import type { Metadata } from "next";
import { LegalPageShell } from "@/components/legal/legal-page-shell";

export const metadata: Metadata = {
  title: "Ethik & EU AI Act Konformität | FindJobFit",
  description: "Erklärung zur ethischen Ausrichtung und Konformität mit der EU-KI-Verordnung (EU AI Act).",
};

export default function EthicsPage() {
  return (
    <LegalPageShell
      badgeTextEn="Compliance & Standards"
      badgeTextDe="Konformität & Standards"
      titleEn="AI Ethics & Regulatory Compliance"
      titleDe="KI-Ethik & Gesetzliche Konformität"
      descriptionEn="Statement on the responsible use of artificial intelligence and alignment with the European Union AI Act (Regulation (EU) 2024/1689)."
      descriptionDe="Grundsätze zum verantwortungsvollen Einsatz von Künstlicher Intelligenz und Konformität mit dem EU AI Act (Verordnung (EU) 2024/1689)."
      childrenEn={
        <div className="space-y-8 text-sm text-zinc-300 leading-relaxed">
          <section className="space-y-2">
            <h2 className="text-base font-semibold text-zinc-100">
              1. Classification under the EU AI Act (Regulation (EU) 2024/1689)
            </h2>
            <p className="text-zinc-400">
              Under Annex III of the EU AI Act, AI systems used in employment and recruitment are classified as high-risk when utilized by employers for applicant screening, candidate ranking, or employment decisions. FindJobFit operates strictly on the candidate side as an individual productivity and drafting assistant. It does not perform automated hiring rejections or binding employment evaluations.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-base font-semibold text-zinc-100">
              2. Human Oversight (Human-in-the-Loop)
            </h2>
            <p className="text-zinc-400">
              In accordance with Article 14 of the EU AI Act, our platform enforces full human oversight at every stage. The platform suggests document tailoring and identifies matching criteria, but the candidate retains sole discretion and final authority over whether to accept, edit, or submit any generated application materials.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-base font-semibold text-zinc-100">
              3. Data Integrity &amp; Factual Grounding
            </h2>
            <p className="text-zinc-400">
              FindJobFit enforces strict factual boundaries. Tailored resumes and cover letters are constructed solely from verified evidence and career history explicitly provided by the user. The platform does not invent credentials, fabricate dates, or generate fictitious claims.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-base font-semibold text-zinc-100">
              4. Non-Discrimination &amp; Objective Evaluation
            </h2>
            <p className="text-zinc-400">
              The matching algorithm evaluates jobs exclusively against objective parameters, such as documented technical skills, verified work experience, and user-defined location preferences. Characteristics protected under the German General Equal Treatment Act (AGG)&mdash;including gender, age, origin, and religion&mdash;are strictly excluded from the matching logic.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-base font-semibold text-zinc-100">
              5. Transparency &amp; Explainability
            </h2>
            <p className="text-zinc-400">
              Users are provided with transparent explanations of match ratings, highlighting specific skill overlaps and missing prerequisites rather than opaque, unexplainable scores.
            </p>
          </section>
        </div>
      }
      childrenDe={
        <div className="space-y-8 text-sm text-zinc-300 leading-relaxed">
          <section className="space-y-2">
            <h2 className="text-base font-semibold text-zinc-100">
              1. Einstufung nach der EU-KI-Verordnung (EU AI Act &ndash; VO (EU) 2024/1689)
            </h2>
            <p className="text-zinc-400">
              Gemäß Anhang III der KI-Verordnung gelten KI-Systeme im Bereich Beschäftigung als Hochrisiko-Systeme, wenn sie von Arbeitgebern zur automatisierten Auswahl, Filterung oder Bewertung von Bewerbern eingesetzt werden. FindJobFit agiert ausschließlich auf Seiten des Bewerbers als persönliches Assistenzwerkzeug zur Erstellung und Organisation von Unterlagen. Das System trifft keine automatisierten Einstellungsentscheidungen und filtert keine Kandidaten im Auftrag von Arbeitgebern aus.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-base font-semibold text-zinc-100">
              2. Menschliche Aufsicht (Human-in-the-Loop)
            </h2>
            <p className="text-zinc-400">
              Gemäß Art. 14 der KI-Verordnung bleibt die volle menschliche Kontrolle in jedem Prozessschritt gewahrt. Die Plattform generiert Vorschläge zur Formulierung und Anpassung; die finale Entscheidung über die Übernahme, Bearbeitung und Absendung von Dokumenten liegt stets vollumfänglich beim Nutzer.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-base font-semibold text-zinc-100">
              3. Wahrhaftigkeit und Belegbindung
            </h2>
            <p className="text-zinc-400">
              FindJobFit arbeitet mit einer strikten Belegbindung. Alle generierten Lebensläufe und Anschreiben stützen sich ausschließlich auf die vom Nutzer zuvor hinterlegten und freigegebenen Qualifikationen. Das System erfindet keine Berufsstationen, Abschlüsse oder Fähigkeiten.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-base font-semibold text-zinc-100">
              4. Antidiskriminierung und Objektivität
            </h2>
            <p className="text-zinc-400">
              Das Matching erfolgt ausschließlich anhand sachbezogener Kriterien (wie nachgewiesene Fachkenntnisse, Programmiersprachen und vom Nutzer gewählte Arbeitsort-Präferenzen). Kriterien im Sinne des Allgemeinen Gleichbehandlungsgesetzes (AGG)&mdash;wie Geschlecht, Herkunft, Alter oder Religionszugehörigkeit&mdash;fließen zu keinem Zeitpunkt in die Bewertung ein.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-base font-semibold text-zinc-100">
              5. Transparenz und Nachvollziehbarkeit
            </h2>
            <p className="text-zinc-400">
              Bewerber erhalten eine transparente Aufschlüsselung der Passgenauigkeit von Stellen, einschließlich übereinstimmender und fehlender Anforderungen, anstelle undurchsichtiger automatisierter Kennzahlen.
            </p>
          </section>
        </div>
      }
    />
  );
}
