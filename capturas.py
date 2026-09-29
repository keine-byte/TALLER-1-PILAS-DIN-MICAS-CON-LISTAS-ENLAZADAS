# -*- coding: utf-8 -*-
"""
capturas.py
===========
Genera la **evidencia de ejecución** del TALLER 1 dentro de la carpeta
`evidencias/`:

    * capturas PNG de la interfaz gráfica en cada situación del taller
      (conversión postfija/prefija, evaluación postfija/prefija, errores de
      validación y ayuda),
    * archivos de texto con la salida de la demostración por consola y el
      informe completo de las pruebas unitarias.

La captura de imágenes usa Pillow (`ImageGrab`). Si Pillow no estuviera
instalado, las evidencias de texto se generan igualmente y se informa por
consola.

Ejecución:
    py capturas.py
    py main.py --capturas
"""

from __future__ import annotations

import io
import os
import sys
import time
import unittest
from contextlib import redirect_stdout

import expresiones as logica

__all__ = ["generar_capturas", "DIRECTORIO_EVIDENCIAS"]

DIRECTORIO_EVIDENCIAS = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "evidencias")

# Guion de capturas: (nombre de archivo, expresión, acción sobre la ventana)
GUION_CAPTURAS = (
    ("01_interfaz_inicial.png", "", None),
    ("02_conversion_postfija.png", "(A+B)*C", "_accion_convertir_postfijo"),
    ("03_conversion_prefija.png", "(A+B)*(C-D)", "_accion_convertir_prefijo"),
    ("04_precedencia_y_asociatividad.png", "A+B*C-D/E^F",
     "_accion_convertir_postfijo"),
    ("05_evaluacion_postfija.png", "23+4*", "_accion_evaluar_postfijo"),
    ("06_evaluacion_prefija.png", "*+234", "_accion_evaluar_prefijo"),
    ("07_evaluacion_postfija_compleja.png", "23*45*+",
     "_accion_evaluar_postfijo"),
    ("08_error_parentesis.png", "(A+B*", "_accion_convertir_postfijo"),
    ("09_error_operador.png", "+A", "_accion_convertir_postfijo"),
    ("10_error_expresion_incompleta.png", "2 3 + 4",
     "_accion_evaluar_postfijo"),
    ("11_error_division_por_cero.png", "5 0 /", "_accion_evaluar_postfijo"),
    ("12_ayuda_sintaxis.png", "", "_accion_ayuda"),
)


def _asegurar_directorio() -> str:
    """Crea (si hace falta) la carpeta de evidencias y devuelve su ruta."""
    os.makedirs(DIRECTORIO_EVIDENCIAS, exist_ok=True)
    return DIRECTORIO_EVIDENCIAS


def _capturar_ventana(ventana, ruta: str) -> bool:
    """
    Guarda una imagen PNG del área que ocupa la ventana.
    Devuelve True si la captura se realizó correctamente.
    """
    try:
        from PIL import ImageGrab                   # importación diferida
    except ImportError:
        print("  (aviso) Pillow no está instalado: no se generan capturas PNG.")
        return False

    ventana.update_idletasks()
    ventana.update()
    time.sleep(0.15)                                # deja que Windows dibuje
    x = ventana.winfo_rootx()
    y = ventana.winfo_rooty()
    ancho = ventana.winfo_width()
    alto = ventana.winfo_height()
    try:
        imagen = ImageGrab.grab(bbox=(x, y, x + ancho, y + alto))
        imagen.save(ruta)
        print(f"  captura: {os.path.basename(ruta)}  ({ancho}x{alto})")
        return True
    except Exception as error:                      # pragma: no cover
        print(f"  (aviso) no se pudo capturar '{os.path.basename(ruta)}': {error}")
        return False


def _guardar_texto(nombre: str, contenido: str) -> str:
    """Guarda un archivo de evidencia de texto y devuelve su ruta."""
    ruta = os.path.join(_asegurar_directorio(), nombre)
    with open(ruta, "w", encoding="utf-8") as archivo:
        archivo.write(contenido)
    print(f"  evidencia de texto: {nombre}")
    return ruta


def _evidencia_demostracion() -> str:
    """Captura la salida de la demostración por consola del taller."""
    import main

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        main._demo_consola()
    return _guardar_texto("demostracion_consola.txt", buffer.getvalue())


def _evidencia_pruebas() -> str:
    """Captura el informe completo de las pruebas unitarias."""
    import pruebas

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        codigo = pruebas.ejecutar_pruebas(verboso=True)
    contenido = buffer.getvalue()
    contenido += (f"\nCódigo de salida de las pruebas: {codigo} "
                  f"({'éxito' if codigo == 0 else 'con fallos'})\n")
    return _guardar_texto("informe_pruebas.txt", contenido)


def _evidencia_conversiones() -> str:
    """Tabla de conversiones y evaluaciones generada por la lógica pura."""
    lineas = [
        "=" * 78,
        "EVIDENCIA DE CONVERSIONES Y EVALUACIONES (generada por capturas.py)",
        "=" * 78,
        "",
        f"{'Expresión infija':>20} | {'Postfija':>12} | {'Prefija':>12} | "
        f"{'Valor':>8} | Operaciones",
        "-" * 78,
    ]
    ejemplos = ("(A+B)*C", "(A+B)*(C-D)", "2+3*4", "(2+3)*4", "2^3^2")
    for infija in ejemplos:
        conversion = logica.analizar_infija(infija)
        try:
            evaluacion = logica.evaluar_tokens_postfijos(conversion.postfija, infija)
            valor = evaluacion.valor_texto
            operaciones = " ; ".join(evaluacion.operaciones)
        except logica.ErrorExpresion:
            # Con variables no hay valor numérico: sólo tiene sentido convertir.
            valor = "n/a"
            operaciones = "no evaluable (sólo variables): sólo conversión"
        lineas.append(
            f"{infija:>20} | {conversion.postfija_texto:>12} | "
            f"{conversion.prefija_texto:>12} | {valor:>8} | {operaciones}")
    lineas.append("-" * 78)
    return _guardar_texto("tabla_conversiones.txt", "\n".join(lineas) + "\n")


def _evidencia_trazas() -> str:
    """Traza paso a paso (con el estado de la pila) de los casos del taller."""
    lineas: list = []
    for infija in ("(A+B)*C", "(2+3)*4"):
        lineas.append(f"\n### TOKENS: {infija}\n")
        conversion = logica.analizar_infija(infija)
        lineas.extend(conversion.traza_postfija)
        lineas.extend(conversion.traza_prefija)
    lineas.append("\n### EVALUACIÓN POSTFIJA DE 23+4* (caso del taller)\n")
    lineas.extend(logica.evaluar_postfija("23+4*").traza)
    lineas.append("\n### EVALUACIÓN PREFIJA DE *+234 (caso del taller)\n")
    lineas.extend(logica.evaluar_prefija("*+234").traza)
    return _guardar_texto("trazas_paso_a_paso.txt", "\n".join(lineas) + "\n")


def generar_capturas(mostrar_ventana: bool = True) -> int:
    """
    Genera todas las evidencias del taller y devuelve el código de salida.
    Las capturas PNG requieren Tkinter + Pillow; las evidencias de texto
    (pruebas, demostración, tablas y trazas) siempre se generan.
    """
    print("=" * 70)
    print("GENERACIÓN DE EVIDENCIAS - TALLER 1 (PILAS DINÁMICAS)")
    print("=" * 70)
    print(f"Carpeta de evidencias: {_asegurar_directorio()}")

    print("\n[1] Evidencias de texto (pruebas, demostración, tablas y trazas)")
    _evidencia_pruebas()
    _evidencia_demostracion()
    _evidencia_conversiones()
    _evidencia_trazas()

    print("\n[2] Capturas de la interfaz gráfica")
    try:
        import interfaz
    except ImportError as error:
        print(f"  (aviso) Tkinter no está disponible: {error}")
        print("  Las evidencias de texto se generaron correctamente.")
        print("=" * 70)
        return 0

    total = 0
    try:
        ventana = interfaz.VentanaTaller(usar_dialogos=False)
    except Exception as error:                      # pragma: no cover
        print(f"  (aviso) no se pudo abrir la ventana: {error}")
        print("  Las evidencias de texto se generaron correctamente.")
        print("=" * 70)
        return 0

    try:
        ventana.title(f"{interfaz.TITULO} - evidencia de ejecución")
        ventana.geometry("1060x760+30+20")
        ventana.update()
        if mostrar_ventana:
            ventana.lift()
            ventana.focus_force()
        ventana.update()

        for nombre, expresion, accion in GUION_CAPTURAS:
            ventana.var_expresion.set(expresion)
            ventana.var_ejemplo.set("")
            if accion is not None:
                getattr(ventana, accion)()
            # La captura se toma con el detalle al inicio, para que se vea el
            # comienzo de la traza (o de la ayuda) y no el final del texto.
            try:
                ventana.detalle.yview_moveto(0.0)
            except Exception:                       # pragma: no cover
                pass
            ventana.update_idletasks()
            ventana.update()
            ruta = os.path.join(DIRECTORIO_EVIDENCIAS, nombre)
            if _capturar_ventana(ventana, ruta):
                total += 1
    finally:
        try:
            ventana.destroy()
        except Exception:                           # pragma: no cover
            pass

    print("-" * 70)
    print(f"Capturas PNG generadas: {total} de {len(GUION_CAPTURAS)}")
    print("Evidencias de texto    : 4 archivos (pruebas, demo, tablas, trazas)")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    raise SystemExit(generar_capturas())

