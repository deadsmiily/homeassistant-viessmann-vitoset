# Vitoset Aqua für Home Assistant

Version 1.0.0 · Für die vorhandene Viessmann-ViCare-Integration

Diese zusätzliche Integration zeigt den Wasserverbrauch einer Vitoset Aqua in
Home Assistant an. Sie verwendet die bereits eingerichtete ViCare-Verbindung.
Die Anmeldung und die Erneuerung des Zugangstokens übernimmt weiterhin ViCare.

## Installation

1. Das ZIP auf dem Computer entpacken.
2. Den enthaltenen Ordner " custom_components/vitoset_aqua " in den
   Home-Assistant-Konfigurationsordner kopieren. Der Zielpfad lautet:

   **`/config/custom_components/vitoset_aqua/`**

   Falls `custom_components` schon existiert, nur den Unterordner `vitoset_aqua`
   hinzufügen.

3. Home Assistant neu starten.
4. Unter **Einstellungen → Geräte & Dienste → Integration hinzufügen** nach
   **Vitoset Aqua** suchen. Falls der Eintrag nicht sofort erscheint, den Browser
   vollständig neu laden.
5. Die bereits verbundene Aqua auswählen und bestätigen.

Die  Integration **Viessmann ViCare muss eingerichtet und geladen
bleiben**. Es werden keine neuen Zugangsdaten benötigt. Dies ist eine manuell
installierte Custom Integration; sie wird nicht automatisch über HACS aktualisiert.

## Wasserverbrauch im Energie-Dashboard

1. Unter **Einstellungen → Dashboards → Energie** die Energiekonfiguration öffnen.
2. Im Bereich **Wasserverbrauch** den Sensor **Vitoset Aqua Wasserverbrauch gesamt**
   hinzufügen. Die Sprache und ein bereits vergebener Gerätename können den
   angezeigten Namen verändern.
3. Einige Minuten bis zur ersten Statistikberechnung warten. Die Integration
   aktualisiert alle **fünf Minuten**.

Für diese Auswertung den **Gesamtverbrauch** verwenden. Der Sensor für heute
ist eine zusätzliche Tagesanzeige. Werden beide als Wasserquelle hinzugefügt,
würde derselbe Verbrauch doppelt erfasst.

Der bestehende Zählerstand wird beim Start als Ausgangspunkt übernommen.
Home Assistant zeichnet anschließend die Zuwächse auf. Die bis zur Installation
verbrauchten Liter werden dadurch nicht rückwirkend als historische Tageswerte
importiert. Die Gesamtsumme kann auch Wasserentnahmen während einer zeitweisen
Verbindungsunterbrechung nachholen; deren genaue zeitliche Verteilung ist dann
nicht bekannt.

## Sensoren

| Sensor | Einheit | Zweck |
| --- | --- | --- |
| Wasserverbrauch gesamt | L | Fortlaufender Verbrauchszähler für das Energie-Dashboard |
| Wasserverbrauch heute | L | Laufender Tag laut Viessmann; Tagesrücksetzung durch die Anlage |
| Aktueller Durchfluss | L/min | Momentaufnahme bei der letzten Cloud-Abfrage |
| Salzreichweite | Tage | Von der Anlage gemeldete verbleibende Reichweite |
| Maximaler Durchfluss | L/min | Optionaler Diagnosewert; standardmäßig deaktiviert |

Der Durchfluss wird nicht sekündlich übertragen. Kurze Wasserentnahmen können
zwischen zwei Abfragen liegen; sie bleiben im Gesamtverbrauch enthalten.
Der optionale Maximalwert hat keinen hier bestätigten Bezugszeitraum.

Die API liefert außerdem `lastSevenDays`. Ob dies bei dieser Anlage eine
Wochensumme oder der in der App angezeigte Tagesdurchschnitt ist, ist aus der
Diagnose allein nicht eindeutig. Deshalb wird dieser Wert nicht als Sensor
ausgegeben. Für die Verbrauchserfassung ist er nicht erforderlich.

## Verbindung und Verhalten bei Fehlern

- Alle Sensoren teilen sich eine Abfrage alle fünf Minuten: bei einer Anlage
  normalerweise etwa 288 Abrufe pro Tag, zuzüglich Einrichtung und manueller
  Aktualisierungen. Zusätzliche Viessmann-Anbindungen teilen das API-Kontingent.
- Die Erweiterung liest ausschließlich Wasserwerte. Sie enthält keine Befehle
  für Ventile, Regeneration oder Geräteeinstellungen.
- Bei einer fehlenden Messung erscheint der betroffene Sensor als nicht
  verfügbar. Fehler werden nicht durch künstliche Nullwerte ersetzt.
- Wird die ViCare-Verbindung neu geladen, verwendet die Erweiterung danach
  automatisch deren neue Laufzeitinstanz. Währenddessen sind die Sensoren
  vorübergehend nicht verfügbar.
- Fordert ViCare eine erneute Anmeldung, diese in **Viessmann ViCare** durchführen.
- Wird der gewählte ViCare-Eintrag ganz gelöscht und neu angelegt, die
  Vitoset-Aqua-Integration ebenfalls entfernen und mit der neuen Verbindung
  erneut hinzufügen. Die Geräte- und Sensor-IDs basieren auf der Anlagenidentität.