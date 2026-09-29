# -*- coding: utf-8 -*-
"""
main.py
=======
Punto de entrada del TALLER 1: Pilas dinámicas con listas enlazadas
(conversión y evaluación de expresiones en notación polaca).

Uso:
    py main.py               -> abre la interfaz gráfica (Tkinter)
    py main.py --pruebas     -> ejecuta la batería de pruebas (unittest)
    py main.py --capturas    -> genera las capturas de evidencia en /evidencias
    py main.py --demo        -> demostración por consola con los casos del taller
    py main.py --ayuda       -> muestra esta ayuda

También se puede ejecutar directamente cada módulo:
    py interfaz.py    py pruebas.py    py capturas.py
"""

from __future__ import annotations

import sys

AYUDA = __doc__


def _demo_consola() -> int:
    """Muestra por consola los casos exigidos por el taller (evidencia rápida)."""
    import expresiones as logica

    print("=" * 70)
    print("DEMOSTRACIÓN POR CONSOLA - CASOS DEL TALLER 1")
    print("=" * 70)

    print("\n[1] Conversiones infija -> postfija / prefija")
    for infija in ("(A+B)*C", "(A+B)*(C-D)", "A+B*C-D/E^F", "2^3^2", "(A+B)^C"):
        conversion = logica.analizar_infija(infija)
        print(f"    {infija:>14}  ->  postfija: {conversion.postfija_texto:<12} "
              f"prefija: {conversion.prefija_texto}")

    print("\n[2] Evaluación postfija")
    for expression in ("23+4*", "3 4 + 2 *", "82/2/", "23*45*+", "2 10 ^"):
        evaluacion = logica.evaluar_postfija(expression)
        print(f"    {expression:>10}  ->  {evaluacion.valor_texto:<8} "
              f"operaciones: {' ; '.join(evaluacion.operaciones)}")

    print("\n[3] Evaluación prefija")
    for expression in ("*+234", "+ 6 * 3 2", "//822", "+*23*45", "^ 2 10"):
        evaluacion = logica.evaluar_prefija(expression)
        print(f"    {expression:>10}  ->  {evaluacion.valor_texto:<8} "
              f"operaciones: {' ; '.join(evaluacion.operaciones)}")

    print("\n[4] Expresiones inválidas (validación y mensajes de error)")
    pruebas_invalidas = [
        ("(A+B*", "convertir"),
        ("+A", "convertir"),
        ("A B", "convertir"),
        ("2 3 + 4", "postfija"),
        ("*+23", "prefija"),
        ("5 0 /", "postfija"),
    ]
    for expresion, tipo in pruebas_invalidas:
        try:
            if tipo == "convertir":
                logica.analizar_infija(expresion)
            elif tipo == "postfija":
                logica.evaluar_postfija(expresion)
            else:
                logica.evaluar_prefija(expresion)
            print(f"    {expresion:>10}  ->  (no se detectó error: revise)")
        except logica.ErrorExpresion as error:
            print(f"    {expresion:>10}  ->  ERROR: {error}")

    print("\nDemostración terminada correctamente.")
    return 0


def main(argv: list | None = None) -> int:
    """Despacha la ejecución según los argumentos recibidos."""
    argumentos = list(sys.argv[1:] if argv is None else argv)
    bandera = argumentos[0].lower() if argumentos else ""

    if bandera in ("--ayuda", "-h", "--help", "ayuda"):
        print(AYUDA)
        return 0

    if bandera in ("--pruebas", "pruebas", "-t", "--test"):
        import pruebas
        return pruebas.ejecutar_pruebas()

    if bandera in ("--capturas", "capturas"):
        import capturas
        return capturas.generar_capturas()

    if bandera in ("--demo", "demo"):
        return _demo_consola()

    if bandera in ("--consola", "consola"):
        print("Use 'py main.py --demo' para la demostración por consola.")
        return 0

    if bandera:
        print(f"Opción no reconocida: {bandera}\n")
        print(AYUDA)
        return 2

    # Sin argumentos: se abre la interfaz gráfica.
    try:
        import interfaz
    except ImportError as error:                # Tkinter no disponible
        print("No se pudo cargar la interfaz gráfica (Tkinter):", error)
        print("Puede usar 'py main.py --demo' o 'py main.py --pruebas'.")
        return 1

    print("Iniciando la interfaz gráfica del Taller 1...")
    interfaz.iniciar()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
