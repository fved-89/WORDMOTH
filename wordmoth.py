#!/usr/bin/env python3

import argparse
import json
import os
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path


titulo = r"""
__        __  ___  ____  ____  __  __  ___  _____  _   _
\ \      / / / _ \|  _ \|  _ \|  \/  |/ _ \|_   _|| | | |
 \ \ /\ / / | | | | |_) | | | | |\/| | | | | | |  | |_| |
  \ V  V /  | |_| |  _ <| |_| | |  | | |_| | | |  |  _  |
   \_/\_/    \___/|_| \_\____/|_|  |_|\___/  |_|  |_| |_|
""".strip("\n").splitlines()

polilla = r"""
                                  __,--'""`-.
                               _,'   ,::'-.  \
                            _,'  ,::::; ,. )  |
                          ,'  ,::"' ,::::' )  |
                        ,'  ,;" ,:;" '     \  |
                       ; ,;' ,'_,-"`._    .'  |
                     ,':'.. _,':',$'  `.   )  |
                   ,', .::,'    `',$$   ^.;_,'
                  /,'!!!,d.      $"'    /"|
                 /,!!!,' Y8P     ;$"'  ,','
                /,!!,',' d8'   ,$$$' ,','
          ,' , /!!!/,'  , `8b  `$' ,;'
        ,',-' /!!,'   ,'  ,8F    ,;/
      _(_;___/::/::,------------',-.
   ,-'__  .:. .:  : "".,-"".,'"-" /
   \ :`-': `:.`:  ;    )    |   ;'
    )\_"'(\   ,-.'    /_   ;   /
  ,:'  `-| \  | |    ,\_\  ;--'
 (/    ,'_;-`-; ;___,\__\\'
    ,::''    /,'        | \
           ,;'          ", \
          `'              "`'
-hrr-
""".strip("\n").splitlines()

polilla = [linea.replace("|", " ") for linea in polilla]


def mostrar_banner():
    ancho = max(len(linea) for linea in titulo) + 5
    inicio = (len(polilla) - len(titulo)) // 2

    print()
    for i, linea_polilla in enumerate(polilla):
        posicion = i - inicio
        linea_titulo = titulo[posicion] if 0 <= posicion < len(titulo) else ""
        print(linea_titulo.ljust(ancho) + linea_polilla)
    print()


class PerfilWiFi:
    def __init__(self):
        self.ssid = ""
        self.nombres = []
        self.apellidos = []
        self.fecha_nacimiento = ""
        self.ciudad = ""
        self.empresa = ""
        self.telefono = ""
        self.otros = []


def normalizar(texto):
    if not texto:
        return ""
    texto = unicodedata.normalize("NFKD", str(texto))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.strip().lower()


def partes_ssid(ssid):
    completo = normalizar(ssid)
    partes = re.split(r"[_\-.\s]+", completo)
    return [p for p in [completo, *partes] if p]


def validar_fecha(texto):
    formatos = ["%Y-%m-%d", "%d/%m/%Y", "%Y%m%d", "%d-%m-%Y"]
    for fmt in formatos:
        try:
            return datetime.strptime(texto, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def validar_telefono(texto):
    digitos = re.sub(r"\D", "", texto or "")
    return digitos if len(digitos) >= 4 else ""


def pedir(prompt, multiple=False, opcional=True, validador=None, aviso=None):
    sufijo = " (separados por coma, Enter para omitir)" if multiple else " (Enter para omitir)"
    while True:
        entrada = input(f"{prompt}{sufijo}: ").strip()
        if not entrada:
            if opcional:
                return None
            print("Obligatorio.")
            continue
        if validador:
            resultado = validador(entrada)
            if not resultado:
                print(aviso or "Valor no valido.")
                continue
            return resultado
        if multiple:
            return [x.strip() for x in entrada.split(",") if x.strip()]
        return entrada


def recolectar_perfil():
    print()

    p = PerfilWiFi()

    while not p.ssid:
        p.ssid = input("SSID (obligatorio): ").strip()

    p.nombres = pedir("Nombres", multiple=True) or []
    p.apellidos = pedir("Apellidos", multiple=True) or []

    fecha = pedir(
        "Fecha de nacimiento (YYYY-MM-DD, DD/MM/YYYY o YYYYMMDD)",
        validador=validar_fecha,
        aviso="Fecha no valida.",
    )
    p.fecha_nacimiento = fecha or ""

    p.ciudad = pedir("Ciudad") or ""
    p.empresa = pedir("Empresa / operador") or ""

    telefono = pedir(
        "Telefono (ultimos 4 digitos)",
        validador=validar_telefono,
        aviso="Minimo 4 digitos.",
    )
    p.telefono = telefono or ""

    while True:
        entrada = input("Otro dato (Enter para terminar): ").strip()
        if not entrada:
            break
        p.otros.append(entrada)

    return p


def cargar_perfil_json(ruta):
    datos = json.loads(Path(ruta).read_text(encoding="utf-8"))
    p = PerfilWiFi()
    p.ssid = datos.get("ssid", "")
    p.nombres = datos.get("nombres", [])
    p.apellidos = datos.get("apellidos", [])
    p.fecha_nacimiento = validar_fecha(datos.get("fecha_nacimiento", "")) or ""
    p.ciudad = datos.get("ciudad", "")
    p.empresa = datos.get("empresa", "")
    p.telefono = validar_telefono(datos.get("telefono", ""))
    p.otros = datos.get("otros", [])
    if not p.ssid:
        raise ValueError("Falta el campo 'ssid'.")
    return p


def extraer_anclas(perfil):
    anclas = set()

    for m in re.findall(r"\d+", perfil.ssid):
        if len(m) >= 3:
            anclas.add(m)

    if perfil.fecha_nacimiento:
        partes = perfil.fecha_nacimiento.split("-")
        if len(partes) == 3:
            año, mes, dia = partes
            anclas.add(año)
            anclas.add(dia + mes)
            anclas.add(dia.lstrip("0") + mes)
            anclas.add(mes + dia)

    if perfil.telefono:
        anclas.add(perfil.telefono[-4:])

    if not perfil.empresa:
        for op in ["movistar", "vodafone", "orange", "jazztel", "yoigo", "masmovil"]:
            anclas.add(op)

    return anclas


def generar_candidatos(perfil):
    ssid_partes = partes_ssid(perfil.ssid)

    nombres = [normalizar(n) for n in perfil.nombres if normalizar(n)]
    apellidos = [normalizar(a) for a in perfil.apellidos if normalizar(a)]
    otros = [normalizar(o) for o in perfil.otros if normalizar(o)]

    palabras = list(dict.fromkeys(ssid_partes + nombres + apellidos + otros))

    if perfil.ciudad:
        palabras.append(normalizar(perfil.ciudad))
    if perfil.empresa:
        palabras.append(normalizar(perfil.empresa))

    palabras = [p for p in palabras if p]
    if not palabras:
        return []

    anclas = extraer_anclas(perfil)

    candidatas = {}

    def añadir(valor, prioridad):
        valor = valor.strip()
        if not valor or len(valor) < 6:
            return
        clave = valor.lower()
        if clave not in candidatas or candidatas[clave][0] > prioridad:
            candidatas[clave] = (prioridad, valor)

    for s in ssid_partes:
        añadir(s, 2)
        for num in anclas:
            añadir(f"{s}{num}", 0)
            añadir(f"{num}{s}", 1)

    for n in nombres:
        añadir(n, 4)
        for num in anclas:
            añadir(f"{n}{num}", 2)
            añadir(f"{num}{n}", 3)

    if nombres and apellidos:
        inicial = nombres[0][0]
        for ap in apellidos:
            base = f"{inicial}{ap}"
            añadir(base, 3)
            for num in anclas:
                añadir(f"{base}{num}", 2)

    for n in nombres:
        for ap in apellidos:
            base = f"{n}{ap}"
            añadir(base, 3)
            añadir(f"{n}_{ap}", 4)
            for num in anclas:
                añadir(f"{base}{num}", 2)

    for i, p1 in enumerate(palabras):
        for p2 in palabras[i + 1:]:
            añadir(f"{p1}{p2}", 5)
            añadir(f"{p1}_{p2}", 6)

    def clave(item):
        prioridad, valor = item
        ideal = 0 if 8 <= len(valor) <= 12 else 1
        return (prioridad, ideal, len(valor))

    resultado = sorted(candidatas.values(), key=clave)
    return [valor for _prioridad, valor in resultado]


def generar_reglas(anclas):
    reglas = set()

    reglas.add("c")
    reglas.add("t")
    reglas.add("u")
    reglas.add("l")

    for r in ["sa4", "se3", "si1", "so0", "ss5", "sa@"]:
        reglas.add(r)

    for num in anclas:
        if num.isdigit() and len(num) <= 6:
            reglas.add("".join(f"${ch}" for ch in num))
            reglas.add("c" + "".join(f"${ch}" for ch in num))

    for num in ["1", "12", "123", "1234", "12345", "2024", "2025", "2026"]:
        reglas.add("".join(f"${ch}" for ch in num))

    for num in ["1", "12", "123"]:
        reglas.add("".join(f"^{ch}" for ch in num))

    reglas.add("$!")
    reglas.add("c$!")
    reglas.add("$.")
    reglas.add("$@")

    for num in ["1", "123", "2024"]:
        base = "c" + "".join(f"${ch}" for ch in num)
        reglas.add(base)
        reglas.add(base + "$!")

    return sorted(reglas)


def escribir_archivo(ruta, lineas):
    try:
        ruta.parent.mkdir(parents=True, exist_ok=True)
        with ruta.open("w", encoding="utf-8", newline="\n") as f:
            for linea in lineas:
                f.write(linea + "\n")
    except OSError as e:
        print(f"Error al escribir {ruta}: {e}")
        sys.exit(1)


def ejecutar(perfil, salida_dict, salida_rules):
    candidatos = generar_candidatos(perfil)

    if not candidatos:
        print("\nSin candidatas. Faltan datos utiles.")
        return 1

    anclas = extraer_anclas(perfil)
    reglas = generar_reglas(anclas)

    escribir_archivo(salida_dict, candidatos)
    escribir_archivo(salida_rules, reglas)

    print(f"\nSSID: {perfil.ssid}")
    print(f"Candidatas: {len(candidatos)}")
    print(f"Reglas:     {len(reglas)}")
    print(f"Salida:     {salida_dict}")
    print(f"Reglas:     {salida_rules}")

    print("\nPrimeras 15:")
    for c in candidatos[:15]:
        print(f"  {c}")

    print(f"\naircrack-ng -w {salida_dict.name} captura.cap")
    print(f"hashcat -m 22000 -a 0 hash.hc22000 {salida_dict.name} -r {salida_rules.name}")
    return 0


def main():
    parser = argparse.ArgumentParser(prog="wordmoth", add_help=True)
    parser.add_argument("--batch", metavar="JSON", help="Perfil en JSON.")
    parser.add_argument("-o", "--salida", default="diccionario_wifi.txt")
    parser.add_argument("-r", "--reglas", default=None)
    args = parser.parse_args()

    mostrar_banner()

    salida_dict = Path(os.path.expanduser(args.salida)).resolve()
    salida_rules = (
        Path(os.path.expanduser(args.reglas)).resolve()
        if args.reglas
        else salida_dict.with_suffix(".rule")
    )

    if args.batch:
        try:
            perfil = cargar_perfil_json(args.batch)
        except (OSError, ValueError, json.JSONDecodeError) as e:
            print(f"Error al cargar el perfil: {e}")
            return 1
    else:
        perfil = recolectar_perfil()

    return ejecutar(perfil, salida_dict, salida_rules)


if __name__ == "__main__":
    sys.exit(main())