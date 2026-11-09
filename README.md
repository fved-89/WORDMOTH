# WORDMOTH---Generador-de-diccionarios

Generador inteligente de diccionarios y reglas de mutación para auditorías de seguridad WiFi (WPA/WPA2).

Diseñado para ser utilizado en conjunto con herramientas como **Hashcat** o **Aircrack-ng** (comúnmente presentes en distribuciones como Wifislax o Kali Linux).

> **Aviso:** Esta herramienta ha sido creada exclusivamente para auditorías de seguridad, pruebas de penetración autorizadas y laboratorios personales. El uso de este software contra redes sin permiso explícito es ilegal.

## Características

- **Generación dirigida:** Utiliza el SSID, nombres, fechas y datos del objetivo para crear contraseñas altamente probables.
- **Anclas numéricas:** Extrae fechas, números de teléfono y números del SSID, combinándolos de formas en que un humano lo haría.
- **Soporte para Hashcat:** Genera un archivo `.rule` optimizado con mutaciones (capitalización, leetspeak, sufijos).
- **Modo interactivo y Batch:** Puedes ingresar los datos a mano o cargarlos desde un archivo `.json`.
- **Multiplataforma:** Funciona sin problemas en Windows y Linux.

## Instalación

No requiere dependencias externas, solo Python 3.8 o superior.

```bash
git clone https://github.com/fved-89/wordmoth.git
cd wordmoth
