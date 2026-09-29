# -*- coding: utf-8 -*-
"""
pruebas.py
==========
Evidencia de pruebas del TALLER 1. Contiene la batería de pruebas unitarias
(unittest) que valida:

    1. la pila dinámica `Pila` construida con listas enlazadas (`Nodo`),
    2. la tokenización de los dos modos de entrada (con y sin espacios),
    3. las validaciones de expresiones incorrectas,
    4. las conversiones infija -> postfija y infija -> prefija,
    5. la evaluación postfija y prefija,
    6. la consistencia entre ambas evaluaciones y `eval()` de Python,
    7. los casos exactos exigidos por el taller:
       válidas (A+B)*C y (A+B)*(C-D); inválidas (A+B* y +A;
       numéricas 23+4* y *+234,
    8. la interfaz gráfica (Tkinter) pulsando sus botones sin abrir el bucle de
       eventos: conversiones, evaluaciones, mensajes de error y "Limpiar".

Ejecución:
    py pruebas.py            (informe por consola)
    py main.py --pruebas
"""

from __future__ import annotations

import io
import sys
import unittest
from contextlib import redirect_stdout

import expresiones as logica
from pila import Nodo, Pila, PilaVaciaError

__all__ = ["ejecutar_pruebas", "cargar_suite"]


# ----------------------------------------------------------------------
# 1. Pila dinámica con listas enlazadas
# ----------------------------------------------------------------------
class TestPilaDinamica(unittest.TestCase):
    """Verifica la clase Nodo y la Pila LIFO (push, pop, pila vacía)."""

    def test_pila_nueva_esta_vacia(self):
        pila = Pila()
        self.assertTrue(pila.esta_vacia())
        self.assertEqual(pila.tamanio, 0)
        self.assertIsNone(pila.cima)
        self.assertFalse(pila)

    def test_push_apila_en_la_cima(self):
        pila = Pila()
        pila.push("A")
        pila.push("B")
        pila.push("C")
        self.assertFalse(pila.esta_vacia())
        self.assertEqual(pila.tamanio, 3)
        self.assertEqual(pila.peek(), "C")
        self.assertEqual(pila.a_lista(), ["C", "B", "A"])   # cima -> base
        self.assertIsInstance(pila.cima, Nodo)
        self.assertEqual(pila.cima.dato, "C")

    def test_pop_respeta_orden_lifo(self):
        pila = Pila()
        for valor in (1, 2, 3, 4):
            pila.push(valor)
        desapilados = [pila.pop() for _ in range(4)]
        self.assertEqual(desapilados, [4, 3, 2, 1])
        self.assertTrue(pila.esta_vacia())
        self.assertEqual(pila.tamanio, 0)

    def test_pop_en_pila_vacia_lanza_error(self):
        pila = Pila()
        with self.assertRaises(PilaVaciaError):
            pila.pop()
        with self.assertRaises(PilaVaciaError):
            pila.peek()

    def test_peek_no_modifica_la_pila(self):
        pila = Pila()
        pila.push(10)
        pila.push(20)
        self.assertEqual(pila.peek(), 20)
        self.assertEqual(pila.peek(), 20)
        self.assertEqual(pila.tamanio, 2)

    def test_limpiar_vacia_la_pila(self):
        pila = Pila()
        pila.push("x")
        pila.push("y")
        pila.limpiar()
        self.assertTrue(pila.esta_vacia())
        self.assertEqual(pila.tamanio, 0)
        self.assertIsNone(pila.cima)

    def test_iteracion_y_representacion(self):
        pila = Pila()
        for valor in ("+", "*", "("):
            pila.push(valor)
        self.assertEqual(list(pila), ["(", "*", "+"])      # de la cima a la base
        self.assertEqual(str(pila), "[(, *, +]")
        self.assertIn("*", pila)
        self.assertEqual(len(pila), 3)

    def test_nodo_guarda_dato_y_enlace(self):
        nodo = Nodo("A")
        self.assertEqual(nodo.dato, "A")
        self.assertIsNone(nodo.siguiente)
        otro = Nodo("B", nodo)
        self.assertIs(otro.siguiente, nodo)

    def test_pila_crece_dinamicamente(self):
        """La pila no tiene tamaño fijo: se valida con 1000 elementos."""
        pila = Pila()
        for numero in range(1000):
            pila.push(numero)
        self.assertEqual(pila.tamanio, 1000)
        self.assertEqual(pila.pop(), 999)
        self.assertNotEqual(pila.cima, pila.cima.siguiente)  # nodos distintos


# ----------------------------------------------------------------------
# 2. Tokenización
# ----------------------------------------------------------------------
class TestTokenizacion(unittest.TestCase):
    """Modo compacto (cada carácter es un token) y modo con espacios."""

    def test_modo_compacto_cada_caracter_es_token(self):
        self.assertEqual(logica.tokenizar("(A+B)*C"),
                         ["(", "A", "+", "B", ")", "*", "C"])
        self.assertEqual(logica.tokenizar("23+4*"), ["2", "3", "+", "4", "*"])
        self.assertEqual(logica.tokenizar("*+234"), ["*", "+", "2", "3", "4"])

    def test_modo_con_espacios_admite_varios_caracteres(self):
        self.assertEqual(logica.tokenizar("23 + 4 * 5"),
                         ["23", "+", "4", "*", "5"])
        self.assertEqual(logica.tokenizar("2.5 * total"), ["2.5", "*", "total"])
        self.assertEqual(logica.tokenizar("(total + 2) * 3"),
                         ["(", "total", "+", "2", ")", "*", "3"])

    def test_minus_unario_se_une_al_numero(self):
        self.assertEqual(logica.tokenizar("-5"), ["-5"])
        self.assertEqual(logica.tokenizar("2*-3"), ["2", "*", "-3"])
        self.assertEqual(logica.tokenizar("2 - -3"), ["2", "-", "-3"])

    def test_el_mas_siempre_es_operador(self):
        # Necesario para que '*+234' se lea como prefijo: * (2+3) 4
        self.assertEqual(logica.tokenizar("*+234"), ["*", "+", "2", "3", "4"])
        self.assertEqual(logica.tokenizar("+A"), ["+", "A"])

    def test_decimal_en_modo_compacto_no_es_valido(self):
        with self.assertRaises(logica.ErrorExpresion) as contexto:
            logica.tokenizar("2.5*3")
        self.assertIn("decimales", str(contexto.exception))

    def test_caracter_invalido(self):
        with self.assertRaises(logica.ErrorExpresion) as contexto:
            logica.tokenizar("A & B")
        self.assertIn("Token inválido", str(contexto.exception))

    def test_expresion_vacia(self):
        for entrada in ("", "   "):
            with self.assertRaises(logica.ErrorExpresion):
                logica.tokenizar(entrada)

    def test_numeros_se_normalizan(self):
        self.assertEqual(logica.tokenizar("2.50 + 3"), ["2.5", "+", "3"])

    def test_modo_tokenizacion(self):
        self.assertEqual(logica.modo_tokenizacion("(A+B)*C"), "sin espacios")
        self.assertEqual(logica.modo_tokenizacion("23 + 4"), "con espacios")


# ----------------------------------------------------------------------
# 3. Validaciones de expresiones incorrectas
# ----------------------------------------------------------------------
class TestValidacion(unittest.TestCase):
    """Paréntesis, operadores inválidos y expresiones incompletas."""

    def _mensaje_de_error(self, expresion: str) -> str:
        with self.assertRaises(logica.ErrorExpresion) as contexto:
            logica.analizar_infija(expresion)
        return str(contexto.exception)

    def test_falta_cerrar_parentesis(self):
        self.assertIn("desbalanceados", self._mensaje_de_error("(A+B*"))

    def test_parentesis_de_cierre_sin_apertura(self):
        self.assertIn("desbalanceados", self._mensaje_de_error("A+B)"))

    def test_operador_sin_operando_izquierdo(self):
        self.assertIn("no tiene operando a su izquierda",
                      self._mensaje_de_error("+A"))
        self.assertIn("no tiene operando a su izquierda",
                      self._mensaje_de_error("2+*3"))

    def test_falta_operador_entre_operandos(self):
        self.assertIn("Faltan operadores", self._mensaje_de_error("A B"))

    def test_parentesis_vacio(self):
        self.assertIn("paréntesis", self._mensaje_de_error("()").lower())

    def test_falta_operador_antes_del_parentesis(self):
        self.assertIn("Falta un operador", self._mensaje_de_error("A(B+C)"))

    def test_expresion_incompleta(self):
        self.assertIn("incompleta", self._mensaje_de_error("2+"))

    def test_expresiones_validas_no_lanzan_error(self):
        for expresion in ("(A+B)*C", "(A+B)*(C-D)", "A-B-C", "-5+3", "A/B/C",
                          "2^3^2", "A%(B+C)"):
            with self.subTest(expresion=expresion):
                logica.analizar_infija(expresion)     # no debe lanzar

    def test_division_por_cero(self):
        with self.assertRaises(logica.ErrorExpresion) as contexto:
            logica.evaluar_postfija("5 0 /")
        self.assertIn("división por cero", str(contexto.exception))

    def test_modulo_por_cero(self):
        with self.assertRaises(logica.ErrorExpresion):
            logica.evaluar_postfija("5 0 %")

    def test_simbolos_no_numericos_no_se_pueden_evaluar(self):
        with self.assertRaises(logica.ErrorExpresion) as contexto:
            logica.evaluar_postfija("AB+")
        self.assertIn("no es un número", str(contexto.exception))

    def test_parentesis_en_notacion_polaca(self):
        with self.assertRaises(logica.ErrorExpresion) as contexto:
            logica.evaluar_postfija("(2+3)")
        self.assertIn("paréntesis", str(contexto.exception))

    def test_expresion_postfija_incompleta(self):
        with self.assertRaises(logica.ErrorExpresion) as contexto:
            logica.evaluar_postfija("2 3 + 4")
        self.assertIn("incompleta", str(contexto.exception))

    def test_expresion_postfija_con_falta_de_operandos(self):
        with self.assertRaises(logica.ErrorExpresion) as contexto:
            logica.evaluar_postfija("23+*")
        self.assertIn("necesita 2 operandos", str(contexto.exception))

    def test_expresion_prefija_incompleta(self):
        with self.assertRaises(logica.ErrorExpresion):
            logica.evaluar_prefija("*+23")

    def test_sugerencia_cuando_la_notacion_esta_cambiada(self):
        with self.assertRaises(logica.ErrorExpresion) as contexto:
            logica.evaluar_postfija("*+234")
        self.assertIn("PREFIJA", str(contexto.exception))


# ----------------------------------------------------------------------
# 4. Conversiones
# ----------------------------------------------------------------------
class TestConversiones(unittest.TestCase):
    """Casos del taller y casos con precedencia/asociatividad."""

    def test_ejemplos_del_taller(self):
        conversion = logica.analizar_infija("(A+B)*C")
        self.assertEqual(conversion.postfija_texto, "AB+C*")
        self.assertEqual(conversion.prefija_texto, "*+ABC")

        otra = logica.analizar_infija("(A+B)*(C-D)")
        self.assertEqual(otra.postfija_texto, "AB+CD-*")
        self.assertEqual(otra.prefija_texto, "*+AB-CD")

    def test_precedencia_y_parentesis(self):
        casos = {
            "A+B*C": "ABC*+",
            "(A+B)*C": "AB+C*",
            "A*B+C/D": "AB*CD/+",
            "A+B-C*D/E": "AB+CD*E/-",
            "(A+B)*(C-D)": "AB+CD-*",
            "A%(B+C)": "ABC+%",
        }
        for infija, esperado in casos.items():
            with self.subTest(infija=infija):
                self.assertEqual(logica.convertir_a_postfija(infija), esperado)

    def test_prefijos(self):
        casos = {
            "A+B*C": "+A*BC",
            "(A+B)*C": "*+ABC",
            "A*B+C/D": "+*AB/CD",
            "A+B-C*D/E": "-+AB/*CDE",
            "(A+B)*(C-D)": "*+AB-CD",
        }
        for infija, esperado in casos.items():
            with self.subTest(infija=infija):
                self.assertEqual(logica.convertir_a_prefija(infija), esperado)

    def test_asociatividad_izquierda(self):
        for infija, postfija, prefija in (("A-B-C", "AB-C-", "--ABC"),
                                          ("A/B/C", "AB/C/", "//ABC"),
                                          ("A%B%C", "AB%C%", "%%ABC")):
            with self.subTest(infija=infija):
                self.assertEqual(logica.convertir_a_postfija(infija), postfija)
                self.assertEqual(logica.convertir_a_prefija(infija), prefija)

    def test_asociatividad_derecha_de_la_potencia(self):
        self.assertEqual(logica.convertir_a_postfija("2^3^2"), "232^^")
        self.assertEqual(logica.convertir_a_prefija("2^3^2"), "^2^32")
        self.assertEqual(logica.convertir_a_postfija("(A^B)^C"), "AB^C^")
        self.assertEqual(logica.convertir_a_prefija("(A^B)^C"), "^^ABC")
        self.assertEqual(logica.convertir_a_postfija("A^(B^C)"), "ABC^^")
        self.assertEqual(logica.convertir_a_prefija("A^(B^C)"), "^A^BC")

    def test_la_traza_documenta_el_uso_de_la_pila(self):
        conversion = logica.analizar_infija("(A+B)*C")
        self.assertTrue(any("Pila operadores" in linea
                            for linea in conversion.traza_postfija))
        self.assertTrue(any("RESULTADO POSTFIJO" in linea
                            for linea in conversion.traza_postfija))
        self.assertTrue(any("RESULTADO PREFIJO" in linea
                            for linea in conversion.traza_prefija))

    def test_tokens_y_presentacion(self):
        conversion = logica.analizar_infija("(A+B)*C")
        self.assertEqual(conversion.tokens, ["(", "A", "+", "B", ")", "*", "C"])
        self.assertEqual(conversion.tokens_texto, "( A + B ) * C")
        self.assertEqual(conversion.postfija_espaciada, "A B + C *")
        self.assertEqual(conversion.prefija_espaciada, "* + A B C")
        self.assertEqual(conversion.expresion, "(A+B)*C")


# ----------------------------------------------------------------------
# 5. Evaluación en notación polaca
# ----------------------------------------------------------------------
class TestEvaluacionPostfija(unittest.TestCase):
    """Evaluación postfija con operaciones realizadas y resultado."""

    def test_ejemplo_del_taller(self):
        """23+4* se lee dígito a dígito: (2+3)*4 = 20."""
        evaluacion = logica.evaluar_postfija("23+4*")
        self.assertEqual(evaluacion.valor_texto, "20")
        self.assertEqual(evaluacion.operaciones, ["2 + 3 = 5", "5 * 4 = 20"])
        self.assertEqual(evaluacion.notacion, "postfija")
        self.assertEqual(evaluacion.tokens, ["2", "3", "+", "4", "*"])

    def test_expresiones_con_espacios(self):
        casos = {
            "3 4 + 2 *": "14",          # (3+4)*2
            "3 4 2 * +": "11",          # 3 + 4*2
            "2 3 ^": "8",
            "2 3 2 ^ ^": "512",
            "8 2 / 2 /": "2",           # 8 / 2 / 2 (notación postfija real)
            "2.5 2 *": "5",
            "7 3 %": "1",
            "10 4 -": "6",
        }
        for expresion, esperado in casos.items():
            with self.subTest(expresion=expresion):
                self.assertEqual(logica.evaluar_postfija(expresion).valor_texto,
                                 esperado)

    def test_operandos_negativos(self):
        self.assertEqual(logica.evaluar_postfija("2 -3 *").valor_texto, "-6")
        self.assertEqual(logica.evaluar_postfija("2 -3 +").valor_texto, "-1")

    def test_un_solo_operando(self):
        evaluacion = logica.evaluar_postfija("7")
        self.assertEqual(evaluacion.valor_texto, "7")
        self.assertEqual(evaluacion.operaciones, [])

    def test_la_traza_muestra_la_pila(self):
        evaluacion = logica.evaluar_postfija("23+4*")
        self.assertTrue(any("Pila:" in linea for linea in evaluacion.traza))
        self.assertTrue(any("pop()" in linea for linea in evaluacion.traza))


class TestEvaluacionPrefija(unittest.TestCase):
    """Evaluación prefija con operaciones realizadas y resultado."""

    def test_ejemplo_del_taller(self):
        evaluacion = logica.evaluar_prefija("*+234")
        self.assertEqual(evaluacion.valor_texto, "20")
        self.assertEqual(evaluacion.operaciones, ["2 + 3 = 5", "5 * 4 = 20"])

    def test_expresiones_con_espacios(self):
        casos = {
            "+ 6 * 3 2": "12",          # 6 + 3*2
            "* + 3 4 2": "14",          # (3+4)*2
            "^ 2 3": "8",
            "^ 2 ^ 3 2": "512",
            "/ / 8 2 2": "2",
            "* 2.5 2": "5",
        }
        for expresion, esperado in casos.items():
            with self.subTest(expresion=expresion):
                self.assertEqual(logica.evaluar_prefija(expresion).valor_texto,
                                 esperado)

    def test_un_solo_operando(self):
        self.assertEqual(logica.evaluar_prefija("7").valor_texto, "7")


# ----------------------------------------------------------------------
# 6. Consistencia: conversión -> evaluación y comparación con eval()
# ----------------------------------------------------------------------
class TestConsistencia(unittest.TestCase):
    """Las dos notaciones deben dar el mismo valor que eval() de Python."""

    EXPRESIONES = [
        ("2+3", 5),
        ("(2+3)*4", 20),
        ("2*3+4*5", 26),
        ("2+3*4-6/3", 12),
        ("(1+2)*(3+4)", 21),
        ("5-3-1", 1),
        ("8/2/2", 2),
        ("2^3^2", 512),
        ("(2+3)*(4+5)-6", 39),
    ]

    def test_conversion_y_evaluacion_coinciden_con_eval(self):
        for infija, esperado in self.EXPRESIONES:
            with self.subTest(infija=infija):
                referencia = eval(infija.replace("^", "**"))   # noqa: S307
                self.assertEqual(referencia, esperado)
                conversion = logica.analizar_infija(infija)
                valor_post = logica.evaluar_tokens_postfijos(
                    conversion.postfija, infija).valor
                valor_pre = logica.evaluar_tokens_prefijos(
                    conversion.prefija, infija).valor
                self.assertEqual(valor_post, esperado)
                self.assertEqual(valor_pre, esperado)

    def test_evaluar_la_conversion_de_un_ejemplo_del_taller(self):
        conversion = logica.analizar_infija("(2+3)*4")
        self.assertEqual(conversion.postfija_texto, "23+4*")
        self.assertEqual(conversion.prefija_texto, "*+234")
        self.assertEqual(logica.evaluar_postfija("23+4*").valor_texto, "20")
        self.assertEqual(logica.evaluar_prefija("*+234").valor_texto, "20")

    def test_notacion_polaca_detecta_la_notacion(self):
        self.assertEqual(logica.notacion_polaca(["2", "3", "+"]), "postfija")
        self.assertEqual(logica.notacion_polaca(["+", "2", "3"]), "prefija")
        self.assertIsNone(logica.notacion_polaca(["(", "2", "+", "3", ")"]))

    def test_es_infija_valida(self):
        self.assertTrue(logica.es_infija_valida(["2", "+", "3"]))
        self.assertFalse(logica.es_infija_valida(["2", "3", "+"]))


# ----------------------------------------------------------------------
# 7. Interfaz gráfica (Tkinter) sin abrir el bucle de eventos
# ----------------------------------------------------------------------
def _tkinter_disponible() -> bool:
    """True si el entorno puede crear una ventana de Tkinter (hay pantalla)."""
    try:
        import tkinter
        raiz = tkinter.Tk()
    except Exception:                # ImportError o TclError (sin pantalla)
        return False
    raiz.withdraw()
    raiz.destroy()
    return True


TKINTER_DISPONIBLE = _tkinter_disponible()


@unittest.skipUnless(TKINTER_DISPONIBLE,
                     "Tkinter no está disponible en este entorno")
class TestInterfazGrafica(unittest.TestCase):
    """
    Pruebas de la interfaz: se crea la ventana real pero NO se entra en
    `mainloop()`, y cada botón se pulsa llamando a su acción.

    Se usa `VentanaTaller(usar_dialogos=False)` para que los avisos no abran
    ventanas modales durante las pruebas.
    """

    def setUp(self):
        import interfaz

        self.ventana = interfaz.VentanaTaller(usar_dialogos=False)
        self.ventana.withdraw()                       # no se muestra al usuario
        self.addCleanup(self.ventana.destroy)         # se cierra aunque falle

    # Utilidades -------------------------------------------------------
    def _escribir(self, expresion: str) -> None:
        """Escribe la expresión en el campo de entrada de la ventana."""
        self.ventana.var_expresion.set(expresion)

    def _detalle(self) -> str:
        """Devuelve todo el texto del panel 'Detalle del proceso'."""
        return self.ventana.detalle.get("1.0", "end")

    # Pruebas ----------------------------------------------------------
    def test_conversion_actualiza_los_resultados(self):
        self._escribir("(A+B)*C")
        self.ventana._accion_convertir_postfijo()
        self.assertEqual(self.ventana.var_postfija.get(), "AB+C*")
        self.assertEqual(self.ventana.var_prefija.get(), "*+ABC")
        detalle = self._detalle()
        self.assertIn("RESULTADO POSTFIJO: AB+C*", detalle)
        self.assertIn("Shunting Yard", detalle)

    def test_evaluacion_postfija_del_taller(self):
        self._escribir("23+4*")
        self.ventana._accion_evaluar_postfijo()
        self.assertEqual(self.ventana.var_resultado.get(), "20")
        detalle = self._detalle()
        self.assertIn("2 + 3 = 5", detalle)
        self.assertIn("5 * 4 = 20", detalle)
        self.assertIn("RESULTADO FINAL: 20", detalle)

    def test_evaluacion_prefija_del_taller(self):
        self._escribir("*+234")
        self.ventana._accion_evaluar_prefijo()
        self.assertEqual(self.ventana.var_resultado.get(), "20")
        self.assertIn("RESULTADO FINAL: 20", self._detalle())

    def test_error_de_sintaxis_se_reporta_como_sintaxis(self):
        self._escribir("(A+B*")
        self.ventana._accion_convertir_postfijo()
        detalle = self._detalle()
        self.assertEqual(self.ventana.var_postfija.get(), "—")
        self.assertIn("desbalanceados", detalle)
        self.assertIn("Revise la sintaxis", detalle)

    def test_error_de_calculo_no_sugiere_cambiar_de_notacion(self):
        """Regresión: '5 0 /' YA está en postfija; el error es la división."""
        self._escribir("5 0 /")
        self.ventana._accion_evaluar_postfijo()
        detalle = self._detalle()
        self.assertEqual(self.ventana.var_resultado.get(), "—")
        self.assertIn("división por cero", detalle)
        self.assertIn("CORRECTA", detalle)
        self.assertNotIn("YA ESTÁ EN NOTACIÓN POSTFIJA", detalle)

    def test_limpiar_deja_la_ventana_en_estado_inicial(self):
        self._escribir("(A+B)*C")
        self.ventana._accion_convertir_postfijo()
        self.ventana._accion_limpiar()
        self.assertEqual(self.ventana.var_expresion.get(), "")
        self.assertEqual(self.ventana.var_postfija.get(), "—")
        self.assertEqual(self.ventana.var_prefija.get(), "—")
        self.assertEqual(self.ventana.var_resultado.get(), "—")
        self.assertIn("TALLER 1", self._detalle())


# ----------------------------------------------------------------------
# 8. Informe de ejecución
# ----------------------------------------------------------------------
def cargar_suite() -> unittest.TestSuite:
    """Agrupa todas las clases de prueba en una única suite."""
    cargador = unittest.TestLoader()
    clases = (
        TestPilaDinamica,
        TestTokenizacion,
        TestValidacion,
        TestConversiones,
        TestEvaluacionPostfija,
        TestEvaluacionPrefija,
        TestConsistencia,
        TestInterfazGrafica,
    )
    suite = unittest.TestSuite()
    for clase in clases:
        suite.addTests(cargador.loadTestsFromTestCase(clase))
    return suite


def ejecutar_pruebas(verboso: bool = True) -> int:
    """Ejecuta la suite y devuelve 0 si todo pasa (código de salida)."""
    print("=" * 70)
    print("EVIDENCIA DE PRUEBAS - TALLER 1: PILAS DINÁMICAS CON LISTAS ENLAZADAS")
    print("=" * 70)
    corredor = unittest.TextTestRunner(stream=sys.stdout,
                                       verbosity=2 if verboso else 1)
    resultado = corredor.run(cargar_suite())
    print("-" * 70)
    print(f"Pruebas ejecutadas : {resultado.testsRun}")
    print(f"Errores            : {len(resultado.errors)}")
    print(f"Fallos             : {len(resultado.failures)}")
    print(f"Omitidas           : {len(resultado.skipped)}")
    estado = "TODAS LAS PRUEBAS PASARON" if resultado.wasSuccessful() else "HAY FALLOS"
    print(f"Resultado          : {estado}")
    print("=" * 70)
    return 0 if resultado.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(ejecutar_pruebas())





