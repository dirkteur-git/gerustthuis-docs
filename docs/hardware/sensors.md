# Sensor Specificaties

## Overzicht

GerustThuis gebruikt Zigbee sensoren voor betrouwbare, privacy-vriendelijke monitoring.

## Sensor Hardware

| Sensor | Protocol | Prijs | Gebruik |
|--------|----------|-------|---------|
| Aqara Presence Sensor FP2 | WiFi mmWave | €73,95 | Aanwezigheidsdetectie met zones |
| Aqara Presence Sensor FP1E | Zigbee | €40,95 | Aanwezigheidsdetectie kamers |
| Aqara Presence Multi-Sensor FP300 | Zigbee/Thread | €49,95 | 5-in-1: presence, lux, temp, humidity, motion |
| Aqara Motion Sensor P1 | Zigbee | €21,95 | Bewegingsdetectie |
| Aqara Motion And Light Sensor P2 | Zigbee | €28,95 | Beweging + lichtsterkte |
| Aqara Door Sensor P2 | Zigbee | €25,95 | Deuren, koelkast, medicijnkastje |
| Aqara Temperature Sensor T1 | Zigbee | €19,95 | Temperatuur en luchtvochtigheid |
| FIBARO Flood Sensor | Z-Wave Plus | €49,95 | Waterlekkage detectie |

**Totaal starter kit:** ~€311,60

## Protocol Notities

- **FP2 (WiFi):** Vereist Aqara Hub of directe WiFi-koppeling, niet via Zigbee2MQTT
- **FIBARO (Z-Wave):** Vereist Z-Wave dongle naast Zigbee dongle
- **FP300/FP1E (Zigbee/Thread):** Werkt direct met Zigbee2MQTT

## Plaatsing Aanbevelingen

### Woonkamer
- Presence sensor (FP1E of FP300)
- Optioneel: Motion sensor voor extra dekking

### Slaapkamer
- Presence sensor
- Deur sensor (optioneel)

### Keuken
- Motion sensor
- Deur sensor op koelkast
- Temperatuur sensor (optioneel)

### Badkamer
- Motion sensor (waterbestendig model aanbevolen)
- Flood sensor bij douche/bad

### Voordeur
- Deur sensor

## Batterij Levensduur

| Sensor Type | Verwachte levensduur |
|-------------|---------------------|
| Motion Sensor | 2-3 jaar |
| Door Sensor | 2-3 jaar |
| Presence Sensor | USB powered / 1-2 jaar |
| Temperature Sensor | 2 jaar |

## Zigbee2MQTT Compatibiliteit

Alle Aqara sensoren zijn volledig ondersteund door Zigbee2MQTT. Zie de [Zigbee2MQTT device database](https://www.zigbee2mqtt.io/supported-devices/) voor specifieke device pagina's.
