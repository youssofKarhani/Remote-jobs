import type { Metadata } from "next";
import { LegalPageShell } from "@/components/legal/legal-page-shell";

export const metadata: Metadata = {
  title: "Impressum (Legal Notice) | FindJobFit",
  description: "Gesetzliche Anbieterkennzeichnung gemäß § 5 Digitale-Dienste-Gesetz (DDG) und § 18 Abs. 2 MStV.",
};

export default function ImpressumPage() {
  return (
    <LegalPageShell
      badgeTextEn="Legal Notice (Impressum)"
      badgeTextDe="Rechtliche Anbieterkennzeichnung"
      titleEn="Legal Notice"
      titleDe="Impressum"
      descriptionEn="Information pursuant to § 5 of the German Digital Services Act (DDG) and § 18 para. 2 of the State Media Treaty (MStV)."
      descriptionDe="Angaben gemäß § 5 Digitale-Dienste-Gesetz (DDG) und § 18 Abs. 2 Medienstaatsvertrag (MStV)."
      childrenEn={
        <div className="space-y-8 text-sm text-zinc-300 leading-relaxed">
          {/* Provider & Contact */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-zinc-900/40 border border-zinc-800 rounded-lg p-5 space-y-2">
              <h2 className="text-xs uppercase font-mono tracking-wider text-zinc-400 font-semibold">
                Service Provider
              </h2>
              <div className="text-zinc-200 space-y-1">
                <p className="font-semibold text-base text-zinc-100">Youssof El Karhani</p>
                <p>Borngasse 2</p>
                <p>35274 Kirchhain</p>
                <p>Germany</p>
              </div>
            </div>

            <div className="bg-zinc-900/40 border border-zinc-800 rounded-lg p-5 space-y-2">
              <h2 className="text-xs uppercase font-mono tracking-wider text-zinc-400 font-semibold">
                Contact
              </h2>
              <div className="text-zinc-300 space-y-1.5 font-mono text-xs">
                <p>
                  Email:{" "}
                  <a href="mailto:support@findjobfit.de" className="text-violet-400 hover:underline">
                    support@findjobfit.de
                  </a>
                </p>
                <p>
                  Website:{" "}
                  <a href="https://findjobfit.de" className="text-violet-400 hover:underline">
                    https://findjobfit.de
                  </a>
                </p>
              </div>
            </div>
          </div>

          {/* Editorial Responsibility */}
          <section className="space-y-2 bg-zinc-900/30 border border-zinc-800 rounded-lg p-5">
            <h2 className="text-sm font-semibold text-zinc-100">
              Responsible for Content (§ 18 para. 2 MStV)
            </h2>
            <p className="text-zinc-400 text-xs leading-relaxed">
              Youssof El Karhani<br />
              Borngasse 2, 35274 Kirchhain, Germany<br />
              Email: support@findjobfit.de
            </p>
          </section>

          {/* Legal Disclaimers */}
          <div className="space-y-6 pt-2">
            <section className="space-y-2">
              <h2 className="text-base font-semibold text-zinc-100">Liability for Content</h2>
              <p className="text-zinc-400">
                As a service provider, we are responsible for our own content on these pages under general law pursuant to § 7 para. 1 of the German Digital Services Act (DDG). However, according to §§ 8 to 10 DDG, we are not obligated to monitor transmitted or stored third-party information or to investigate circumstances that indicate unlawful activity. Obligations to remove or block the use of information in accordance with general statutory provisions remain unaffected.
              </p>
            </section>

            <section className="space-y-2">
              <h2 className="text-base font-semibold text-zinc-100">Liability for External Links</h2>
              <p className="text-zinc-400">
                Our platform contains links to external websites of third parties over whose content we have no influence. Therefore, we cannot assume any liability for these external contents. The respective provider or operator of the pages is always responsible for the contents of the linked pages. If we become aware of any infringements, we will remove such links immediately.
              </p>
            </section>

            <section className="space-y-2">
              <h2 className="text-base font-semibold text-zinc-100">Copyright &amp; Automated Analysis (§ 44b UrhG)</h2>
              <p className="text-zinc-400">
                The content and works created by the site operator on these pages are subject to German copyright law. The analysis and indexing of publicly accessible job offers are conducted in accordance with statutory copyright exceptions, particularly § 44b UrhG (Text and Data Mining), and in compliance with public interfaces.
              </p>
            </section>

            <section className="space-y-2">
              <h2 className="text-base font-semibold text-zinc-100">Dispute Resolution (§ 36 VSBG)</h2>
              <p className="text-zinc-400">
                The European Commission provides a platform for online dispute resolution (ODR):{" "}
                <a
                  href="https://ec.europa.eu/consumers/odr"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-violet-400 hover:underline font-mono text-xs"
                >
                  https://ec.europa.eu/consumers/odr
                </a>.
                We are neither willing nor obligated to participate in dispute resolution proceedings before a consumer arbitration board.
              </p>
            </section>
          </div>
        </div>
      }
      childrenDe={
        <div className="space-y-8 text-sm text-zinc-300 leading-relaxed">
          {/* Provider & Contact */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-zinc-900/40 border border-zinc-800 rounded-lg p-5 space-y-2">
              <h2 className="text-xs uppercase font-mono tracking-wider text-zinc-400 font-semibold">
                Dienstanbieter
              </h2>
              <div className="text-zinc-200 space-y-1">
                <p className="font-semibold text-base text-zinc-100">Youssof El Karhani</p>
                <p>Borngasse 2</p>
                <p>35274 Kirchhain</p>
                <p>Deutschland</p>
              </div>
            </div>

            <div className="bg-zinc-900/40 border border-zinc-800 rounded-lg p-5 space-y-2">
              <h2 className="text-xs uppercase font-mono tracking-wider text-zinc-400 font-semibold">
                Kontakt
              </h2>
              <div className="text-zinc-300 space-y-1.5 font-mono text-xs">
                <p>
                  E-Mail:{" "}
                  <a href="mailto:support@findjobfit.de" className="text-violet-400 hover:underline">
                    support@findjobfit.de
                  </a>
                </p>
                <p>
                  Website:{" "}
                  <a href="https://findjobfit.de" className="text-violet-400 hover:underline">
                    https://findjobfit.de
                  </a>
                </p>
              </div>
            </div>
          </div>

          {/* Verantwortlicher nach § 18 MStV */}
          <section className="space-y-2 bg-zinc-900/30 border border-zinc-800 rounded-lg p-5">
            <h2 className="text-sm font-semibold text-zinc-100">
              Verantwortlich für den Inhalt nach § 18 Abs. 2 MStV
            </h2>
            <p className="text-zinc-400 text-xs leading-relaxed">
              Youssof El Karhani<br />
              Borngasse 2, 35274 Kirchhain, Deutschland<br />
              E-Mail: support@findjobfit.de
            </p>
          </section>

          {/* Rechtliche Hinweise */}
          <div className="space-y-6 pt-2">
            <section className="space-y-2">
              <h2 className="text-base font-semibold text-zinc-100">Haftung für Inhalte</h2>
              <p className="text-zinc-400">
                Als Diensteanbieter sind wir gemäß § 7 Abs. 1 DDG für eigene Inhalte auf diesen Seiten nach den allgemeinen Gesetzen verantwortlich. Nach §§ 8 bis 10 DDG sind wir als Diensteanbieter jedoch nicht verpflichtet, übermittelte oder gespeicherte fremde Informationen zu überwachen oder nach Umständen zu forschen, die auf eine rechtswidrige Tätigkeit hinweisen. Verpflichtungen zur Entfernung oder Sperrung der Nutzung von Informationen nach den allgemeinen Gesetzen bleiben hiervon unberührt.
              </p>
            </section>

            <section className="space-y-2">
              <h2 className="text-base font-semibold text-zinc-100">Haftung für Links</h2>
              <p className="text-zinc-400">
                Unser Angebot enthält Links zu externen Websites Dritter, auf deren Inhalte wir keinen Einfluss haben. Deshalb können wir für diese fremden Inhalte auch keine Gewähr übernehmen. Für die Inhalte der verlinkten Seiten ist stets der jeweilige Anbieter oder Betreiber der Seiten verantwortlich. Bei Bekanntwerden von Rechtsverletzungen werden wir derartige Links umgehend entfernen.
              </p>
            </section>

            <section className="space-y-2">
              <h2 className="text-base font-semibold text-zinc-100">Urheberrecht und Text- und Data-Mining (§ 44b UrhG)</h2>
              <p className="text-zinc-400">
                Die durch den Seitenbetreiber erstellten Inhalte und Werke auf diesen Seiten unterliegen dem deutschen Urheberrecht. Die Vervielfältigung, Bearbeitung, Verbreitung und jede Art der Verwertung außerhalb der Grenzen des Urheberrechtes bedürfen der schriftlichen Zustimmung des Betreibers. Die automatisierte Auswertung und Aggregation öffentlich zugänglicher Stellenanzeigen erfolgt im Rahmen der gesetzlichen Schrankenregelungen gemäß § 44b UrhG sowie öffentlicher Programmierschnittstellen.
              </p>
            </section>

            <section className="space-y-2">
              <h2 className="text-base font-semibold text-zinc-100">Verbraucherstreitbeilegung (§ 36 VSBG)</h2>
              <p className="text-zinc-400">
                Die Europäische Kommission stellt eine Plattform zur Online-Streitbeilegung (OS) bereit:{" "}
                <a
                  href="https://ec.europa.eu/consumers/odr"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-violet-400 hover:underline font-mono text-xs"
                >
                  https://ec.europa.eu/consumers/odr
                </a>.
                Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.
              </p>
            </section>
          </div>
        </div>
      }
    />
  );
}
