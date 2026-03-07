<template>
  <div class="max-w-2xl mx-auto py-4 space-y-8 text-sm text-gray-300 leading-relaxed">
    <h1 class="text-2xl font-bold text-gray-100">Datenschutzerklärung</h1>

    <section class="space-y-3">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium mb-3">1. Verantwortlicher</h2>
      <p class="font-medium text-gray-100">Lorik Bajrami</p>
      <p>[Straße und Hausnummer], [PLZ] [Stadt]</p>
      <p>E-Mail: <a href="mailto:[ihre-email@example.com]" class="text-emerald-400 hover:text-emerald-300">[ihre-email@example.com]</a></p>
    </section>

    <section class="space-y-3">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium mb-3">2. Erhebung und Verarbeitung personenbezogener Daten</h2>
      <p>
        Wir erheben und verarbeiten personenbezogene Daten nur soweit dies zur Bereitstellung einer
        funktionsfähigen Anwendung sowie unserer Inhalte und Leistungen erforderlich ist.
      </p>
      <p>
        <span class="text-gray-100 font-medium">Registrierungsdaten:</span> Beim Erstellen eines Kontos
        werden Ihre E-Mail-Adresse und ein Passwort erhoben. Diese Daten werden über Amazon Cognito
        (AWS) verarbeitet und gespeichert.
      </p>
      <p>
        <span class="text-gray-100 font-medium">Finanzdaten:</span> Von Ihnen eingetragene Dividenden-
        und Zinsdaten werden in Ihrem persönlichen Bereich gespeichert und sind nur für Sie einsehbar.
      </p>
      <p>
        <span class="text-gray-100 font-medium">Einstellungen:</span> Sprachpräferenz und Währungseinstellung
        werden lokal in Ihrem Browser (localStorage) gespeichert und nicht an Server übermittelt.
      </p>
    </section>

    <section class="space-y-3">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium mb-3">3. Rechtsgrundlage der Verarbeitung</h2>
      <p>
        Die Verarbeitung Ihrer Daten erfolgt auf Basis von Art. 6 Abs. 1 lit. b DSGVO
        (Vertragserfüllung) sowie Art. 6 Abs. 1 lit. f DSGVO (berechtigtes Interesse an einem
        sicheren und funktionsfähigen Betrieb der Anwendung).
      </p>
    </section>

    <section class="space-y-3">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium mb-3">4. Drittanbieter / Hosting</h2>
      <p>
        <span class="text-gray-100 font-medium">IONOS SE (Anwendungsserver):</span> Der Anwendungsserver
        wird von IONOS SE, Elgendorfer Str. 57, 56410 Montabaur, Deutschland betrieben. Der Server
        befindet sich in Deutschland und unterliegt damit dem deutschen und europäischen Datenschutzrecht.
        Weitere Informationen finden Sie unter
        <a href="https://www.ionos.de/terms-gtc/datenschutzerklaerung/" target="_blank" rel="noopener noreferrer" class="text-emerald-400 hover:text-emerald-300">ionos.de/terms-gtc/datenschutzerklaerung</a>.
      </p>
      <p>
        <span class="text-gray-100 font-medium">Amazon Web Services (AWS):</span> Authentifizierung
        und Datenspeicherung erfolgen über AWS-Dienste (Amazon Cognito, Amazon S3). AWS ist gemäß
        Art. 46 DSGVO zertifiziert. Weitere Informationen finden Sie unter
        <a href="https://aws.amazon.com/de/privacy/" target="_blank" rel="noopener noreferrer" class="text-emerald-400 hover:text-emerald-300">aws.amazon.com/de/privacy</a>.
      </p>
      <p>
        <span class="text-gray-100 font-medium">Server-Logfiles:</span> Der Hosting-Anbieter erhebt
        automatisch Server-Logdaten (IP-Adresse, Browsertyp, Betriebssystem, Zeitpunkt des Zugriffs).
        Diese Daten sind nicht bestimmten Personen zuordenbar und werden nicht mit anderen Datenquellen
        zusammengeführt.
      </p>
    </section>

    <section class="space-y-3">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium mb-3">5. Keine Nutzungsanalyse / kein Tracking</h2>
      <p>
        Diese Anwendung verwendet <span class="text-gray-100 font-medium">kein Google Analytics</span>
        und keine vergleichbaren Analyse- oder Tracking-Dienste. Es wird kein nutzerspezifisches
        Verhalten aufgezeichnet, keine Sitzungsaufzeichnung durchgeführt und keine Daten an
        Werbenetzwerke übermittelt.
      </p>
      <p>
        Es werden ausschließlich die technisch notwendigen Daten verarbeitet, die zur Bereitstellung
        der Anwendungsfunktionen unbedingt erforderlich sind (Authentifizierungstoken, eingegebene
        Finanzdaten, Spracheinstellung).
      </p>
    </section>

    <section class="space-y-3">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium mb-3">6. Speicherdauer</h2>
      <p>
        Personenbezogene Daten werden nur so lange gespeichert, wie es für die jeweiligen Zwecke
        erforderlich ist oder gesetzliche Aufbewahrungsfristen bestehen. Nach Löschung Ihres Kontos
        werden Ihre Daten innerhalb von 30 Tagen gelöscht.
      </p>
    </section>

    <section class="space-y-3">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium mb-3">7. Ihre Rechte (DSGVO)</h2>
      <ul class="space-y-2">
        <li class="flex gap-2">
          <span class="text-emerald-400 shrink-0">→</span>
          <span><span class="text-gray-100">Auskunft</span> über Ihre gespeicherten Daten (Art. 15 DSGVO)</span>
        </li>
        <li class="flex gap-2">
          <span class="text-emerald-400 shrink-0">→</span>
          <span><span class="text-gray-100">Berichtigung</span> unrichtiger Daten (Art. 16 DSGVO)</span>
        </li>
        <li class="flex gap-2">
          <span class="text-emerald-400 shrink-0">→</span>
          <span><span class="text-gray-100">Löschung</span> Ihrer Daten (Art. 17 DSGVO)</span>
        </li>
        <li class="flex gap-2">
          <span class="text-emerald-400 shrink-0">→</span>
          <span><span class="text-gray-100">Einschränkung</span> der Verarbeitung (Art. 18 DSGVO)</span>
        </li>
        <li class="flex gap-2">
          <span class="text-emerald-400 shrink-0">→</span>
          <span><span class="text-gray-100">Datenübertragbarkeit</span> (Art. 20 DSGVO)</span>
        </li>
        <li class="flex gap-2">
          <span class="text-emerald-400 shrink-0">→</span>
          <span><span class="text-gray-100">Widerspruch</span> gegen die Verarbeitung (Art. 21 DSGVO)</span>
        </li>
        <li class="flex gap-2">
          <span class="text-emerald-400 shrink-0">→</span>
          <span><span class="text-gray-100">Beschwerde</span> bei einer Aufsichtsbehörde (Art. 77 DSGVO)</span>
        </li>
      </ul>
      <p class="text-gray-400">
        Zur Ausübung Ihrer Rechte wenden Sie sich bitte per E-Mail an den oben genannten Verantwortlichen.
      </p>
    </section>

    <section class="space-y-3">
      <h2 class="text-xs uppercase tracking-wider text-gray-500 font-medium mb-3">8. Cookies und lokaler Speicher</h2>
      <p>
        Diese Anwendung setzt keine Tracking-Cookies ein. Es werden ausschließlich technisch
        notwendige Session-Tokens (zur Authentifizierung) sowie Einstellungen (Sprache, Währung)
        im lokalen Speicher Ihres Browsers (localStorage / sessionStorage) abgelegt.
      </p>
      <p>
        Diese Daten verlassen Ihren Browser nicht und dienen ausschließlich dem Betrieb der Anwendung.
      </p>
    </section>

    <p class="text-xs text-gray-600 pt-4 border-t border-gray-800">Stand: {{ new Date().getFullYear() }}</p>
  </div>
</template>
