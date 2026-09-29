# -*- coding: utf-8 -*-
"""
expresiones.py
==============
Lógica pura (independiente de la interfaz gráfica) del Taller 1:

    * tokenización y validación de expresiones infijas
    * conversión infija -> postfija  (algoritmo Shunting Yard de Dijkstra)
    * conversión infija -> prefija
    * evaluación de expresiones postfijas y prefijas
    * trazas paso a paso: operaciones realizadas y estado de la pila

Todas las pilas que usan los algoritmos son instancias de `pila.Pila`, es
decir pilas dinámicas construidas con listas enlazadas (no listas de Python).

Formas de escribir la expresión
-------------------------------
1. **Sin espacios (modo compacto)**: cada carácter es un token, por lo que
   "23+4*" se interpreta como los tokens  2 3 + 4 *  (es la forma en que el
   taller plantea los ejemplos: 23+4* = 20 y *+234 = 20).
2. **Con espacios (modo separado)**: cada grupo separado por espacios es un
   token, de modo que se admiten números de varios dígitos o nombres de
   varias letras:  "23 4 +" -> tokens 23 4 +  (23 + 4 = 27).

Los paréntesis siempre se separan del resto. El signo `-` que actúa como
signo (por ejemplo `-5` o `2*-3`) se absorbe dentro del número; no se admite
el menos unario delante de paréntesis o variables. El `+` siempre se
interpreta como el operador suma (por eso `*+234` sigue siendo prefija).

Complejidad global: cada algoritmo recorre los tokens una sola vez, por lo
que todos son O(n) en tiempo y O(n) en memoria (n = número de tokens).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional, Sequence

from pila import Pila, PilaVaciaError

__all__ = [
    "ErrorExpresion",
    "Conversion",
    "Evaluacion",
    "PRECEDENCIA",
    "ASOCIATIVIDAD",
    "OPERADORES",
    "tokenizar",
    "validar_estructura",
    "infijo_a_postfijo",
    "infijo_a_prefijo",
    "analizar_infija",
    "convertir_a_postfija",
    "convertir_a_prefija",
    "evaluar_postfija",
    "evaluar_prefija",
    "evaluar_tokens_postfijos",
    "evaluar_tokens_prefijos",
    "es_numero",
    "es_identificador",
    "formatear_numero",
    "unir_tokens",
]

# ----------------------------------------------------------------------
# Configuración de los operadores
# ----------------------------------------------------------------------
# Precedencia: a mayor número, mayor prioridad de evaluación.
PRECEDENCIA = {
    "+": 1,
    "-": 1,
    "*": 2,
    "/": 2,
    "%": 2,
    "^": 3,
}

# Asociatividad: 'izq' = evaluado de izquierda a derecha, 'der' = al revés.
# La potencia es la única asociativa por la derecha (2^3^2 = 2^(3^2)).
ASOCIATIVIDAD = {
    "+": "izq",
    "-": "izq",
    "*": "izq",
    "/": "izq",
    "%": "izq",
    "^": "der",
}

OPERADORES = tuple(PRECEDENCIA.keys())
PARENTESIS = ("(", ")")


class ErrorExpresion(Exception):
    """Error de validación de una expresión matemática."""


# ----------------------------------------------------------------------
# Estructuras de resultado (dataclasses)
# ----------------------------------------------------------------------
@dataclass
class Conversion:
    """Resultado completo del análisis de una expresión infija."""

    expresion: str
    tokens: List[str]
    postfija: List[str]
    prefija: List[str]
    traza_postfija: List[str] = field(default_factory=list)
    traza_prefija: List[str] = field(default_factory=list)

    # Propiedades de presentación -------------------------------------
    @property
    def postfija_texto(self) -> str:
        """Notación postfija compacta, por ejemplo 'AB+C*'."""
        return unir_tokens(self.postfija)

    @property
    def prefija_texto(self) -> str:
        """Notación prefija compacta, por ejemplo '*+ABC'."""
        return unir_tokens(self.prefija)

    @property
    def postfija_espaciada(self) -> str:
        """Notación postfija con espacios, por ejemplo 'A B + C *'."""
        return unir_tokens(self.postfija, con_espacios=True)

    @property
    def prefija_espaciada(self) -> str:
        """Notación prefija con espacios, por ejemplo '* + A B C'."""
        return unir_tokens(self.prefija, con_espacios=True)

    @property
    def tokens_texto(self) -> str:
        """Tokens detectados, separados por un espacio."""
        return unir_tokens(self.tokens, con_espacios=True)


@dataclass
class Evaluacion:
    """Resultado de evaluar una expresión postfija o prefija."""

    expresion: str
    notacion: str                 # "postfija" o "prefija"
    tokens: List[str]
    operaciones: List[str]        # ["2 + 3 = 5", "5 * 4 = 20"]
    traza: List[str]              # pasos con el estado de la pila
    valor: float | int

    @property
    def valor_texto(self) -> str:
        """Valor final formateado (sin decimales innecesarios)."""
        return formatear_numero(self.valor)

    @property
    def resultado_texto(self) -> str:
        """Texto listo para mostrar como resultado."""
        return f"Resultado final: {self.valor_texto}"


# ----------------------------------------------------------------------
# Funciones auxiliares
# ----------------------------------------------------------------------
def unir_tokens(tokens: Sequence[Any], con_espacios: bool = False) -> str:
    """Une una secuencia de tokens en una cadena, con o sin espacios."""
    separador = " " if con_espacios else ""
    return separador.join(str(token) for token in tokens)


def es_numero(token: Any) -> bool:
    """Indica si el token es un número (entero o decimal)."""
    try:
        float(token)
        return True
    except (TypeError, ValueError):
        return False


def es_identificador(token: Any) -> bool:
    """
    Indica si el token es un identificador válido:
    empieza con letra o guion bajo y continúa con letras, dígitos o '_'.
    """
    if not isinstance(token, str) or not token:
        return False
    if not (token[0].isalpha() or token[0] == "_"):
        return False
    return all(caracter.isalnum() or caracter == "_" for caracter in token)


def formatear_numero(valor: Any) -> str:
    """
    Convierte un número a texto legible: sin `.0` innecesario y con máximo
    10 decimales para evitar el ruido de la aritmética de punto flotante.
    """
    if isinstance(valor, bool):
        return str(valor)
    if isinstance(valor, int):
        return str(valor)
    numero = float(valor)
    if numero != numero:                      # NaN
        return "NaN"
    if numero in (float("inf"), float("-inf")):
        return "infinito" if numero > 0 else "-infinito"
    if numero == int(numero) and abs(numero) < 1e16:
        return str(int(numero))
    texto = f"{numero:.10f}".rstrip("0").rstrip(".")
    return texto if texto else "0"


def _separar_parentesis(pieza: str) -> List[str]:
    """Separa los paréntesis de una pieza, sin romper números ni variables."""
    partes: List[str] = []
    buffer = ""
    for caracter in pieza:
        if caracter in PARENTESIS:
            if buffer:
                partes.append(buffer)
                buffer = ""
            partes.append(caracter)
        elif caracter.isspace():
            if buffer:
                partes.append(buffer)
                buffer = ""
        else:
            buffer += caracter
    if buffer:
        partes.append(buffer)
    return partes


# ----------------------------------------------------------------------
# Tokenización
# ----------------------------------------------------------------------
def tokenizar(expresion: str) -> List[str]:
    """
    Divide la expresión en tokens, valida los caracteres y resuelve los
    signos unarios que preceden a un número.

    Devuelve la lista de tokens (números normalizados, identificadores,
    operadores y paréntesis). Lanza `ErrorExpresion` si encuentra basura.

    Complejidad O(n) en tiempo y O(n) en memoria.
    """
    if not isinstance(expresion, str) or not expresion.strip():
        raise ErrorExpresion(
            "La expresión está vacía. Escriba una expresión para procesar."
        )

    texto = expresion.strip()
    tiene_espacios = any(caracter.isspace() for caracter in texto)

    if tiene_espacios:
        # Modo separado: cada grupo con espacios es un token.
        crudos: List[str] = []
        for pieza in texto.split():
            crudos.extend(_separar_parentesis(pieza))
    else:
        # Modo compacto: cada carácter es un token independiente.
        if "." in texto:
            raise ErrorExpresion(
                "En modo sin espacios cada carácter es un token independiente. "
                "Para usar números decimales sepárelos con espacios "
                "(ejemplo: 2.5 + 3.5)."
            )
        crudos = list(texto)

    tokens: List[str] = []
    for crudo in crudos:
        pieza = crudo.strip()
        if not pieza:
            continue
        if pieza in PARENTESIS:
            tokens.append(pieza)
        elif pieza in PRECEDENCIA:
            tokens.append(pieza)
        elif es_numero(pieza):
            # Normaliza el número (por ejemplo '2.50' -> '2.5', '+7' -> '7').
            tokens.append(formatear_numero(float(pieza)))
        elif es_identificador(pieza):
            tokens.append(pieza)
        else:
            raise ErrorExpresion(
                f"Token inválido: '{pieza}'. Sólo se admiten números, "
                f"variables, paréntesis y los operadores {', '.join(OPERADORES)}."
            )

    return _resolver_signos_unarios(tokens)


def _resolver_signos_unarios(tokens: List[str]) -> List[str]:
    """
    Convierte el signo `-` que actúa como signo (no como resta) en parte del
    número que le sigue:  - 5  ->  -5   (también `2 * - 3` -> 2 * -3).

    El `+` nunca se absorbe porque siempre se interpreta como el operador
    suma: así la expresión prefija '*+234' se lee como * + 2 3 4.

    Si el `-` no está delante de un número literal se deja tal cual para que
    `validar_estructura()` informe el error con precisión.
    """
    resultado: List[str] = []
    indice = 0
    while indice < len(tokens):
        token = tokens[indice]
        if token == "-":
            esperando_operando = (
                not resultado
                or resultado[-1] in PRECEDENCIA
                or resultado[-1] == "("
            )
            if (esperando_operando and indice + 1 < len(tokens)
                    and es_numero(tokens[indice + 1])):
                resultado.append(
                    formatear_numero(-float(tokens[indice + 1]))
                )
                indice += 2
                continue
        resultado.append(token)
        indice += 1
    return resultado


# ----------------------------------------------------------------------
# Validaciones
# ----------------------------------------------------------------------
def validar_estructura(tokens: List[str]) -> None:
    """
    Verifica la sintaxis de una expresión infija con una máquina de estados:
    alternancia operando/operador, grupos vacíos y paréntesis balanceados.

    Lanza `ErrorExpresion` con un mensaje explicativo si algo está mal.
    Complejidad O(n) en tiempo y O(n) en memoria (pila de paréntesis).
    """
    if not tokens:
        raise ErrorExpresion("La expresión no contiene tokens para procesar.")

    esperando_operando = True          # al inicio se espera un operando
    pila_parentesis = Pila()           # pila dinámica con las posiciones de '('

    for posicion, token in enumerate(tokens, start=1):
        if token == "(":
            if not esperando_operando:
                raise ErrorExpresion(
                    f"Falta un operador antes del paréntesis '(' "
                    f"de la posición {posicion}."
                )
            pila_parentesis.push(posicion)

        elif token == ")":
            if esperando_operando:
                raise ErrorExpresion(
                    f"El paréntesis ')' de la posición {posicion} no tiene "
                    "operando que cerrar (paréntesis vacío o mal ubicado)."
                )
            if pila_parentesis.esta_vacia():
                raise ErrorExpresion(
                    f"Paréntesis desbalanceados: ')' en la posición {posicion} "
                    "sin un '(' que lo abra."
                )
            pila_parentesis.pop()
            esperando_operando = False   # tras ')' se espera un operador

        elif token in PRECEDENCIA:
            if esperando_operando:
                raise ErrorExpresion(
                    f"El operador '{token}' (posición {posicion}) no tiene "
                    "operando a su izquierda."
                )
            esperando_operando = True

        else:                            # operando (número o variable)
            if not esperando_operando:
                raise ErrorExpresion(
                    f"Faltan operadores entre '{tokens[posicion - 2]}' y "
                    f"'{token}' (posición {posicion})."
                )
            esperando_operando = False

    if not pila_parentesis.esta_vacia():
        abiertos = ", ".join(str(valor) for valor in pila_parentesis)
        raise ErrorExpresion(
            f"Paréntesis desbalanceados: falta cerrar {pila_parentesis.tamanio} "
            f"paréntesis de apertura (posiciones: {abiertos})."
        )

    if esperando_operando:
        raise ErrorExpresion(
            f"Expresión incompleta: termina en '{tokens[-1]}' y falta un operando."
        )


def _sugerencia_notacion(tokens: List[str], notacion: str) -> str:
    """Sugiere cambiar de notación cuando la expresión parece ser la otra."""
    if notacion == "postfija" and tokens and tokens[0] in PRECEDENCIA:
        return (" La expresión parece estar en notación PREFIJA: "
                "pruebe con el botón 'Evaluar prefijo'.")
    if notacion == "prefija" and tokens and tokens[-1] in PRECEDENCIA:
        return (" La expresión parece estar en notación POSTFIJA: "
                "pruebe con el botón 'Evaluar postfijo'.")
    return ""


def _validar_expresion_polaca(tokens: List[str], notacion: str) -> None:
    """
    Valida la estructura de una expresión en notación polaca.

    Regla: recorriendo la expresión en el orden en que se consumen los
    operandos (izquierda a derecha para postfija, derecha a izquierda para
    prefija), cada operador necesita 2 operandos y al final debe quedar
    exactamente 1 valor. Complejidad O(n).
    """
    if not tokens:
        raise ErrorExpresion("La expresión está vacía.")

    secuencia = tokens if notacion == "postfija" else list(reversed(tokens))
    disponibles = 0
    for posicion, token in enumerate(secuencia, start=1):
        if token in PRECEDENCIA:
            if disponibles < 2:
                raise ErrorExpresion(
                    f"Expresión {notacion} inválida: el operador '{token}' "
                    f"(posición {posicion} de la secuencia) necesita 2 operandos "
                    f"y sólo hay {disponibles} disponible(s)."
                    + _sugerencia_notacion(tokens, notacion)
                )
            disponibles -= 1
        elif token in PARENTESIS:
            raise ErrorExpresion(
                f"Una expresión en notación {notacion} no debe contener "
                f"paréntesis (posición {posicion})."
            )
        elif es_numero(token) or es_identificador(token):
            disponibles += 1
        else:
            raise ErrorExpresion(
                f"Token inválido en la expresión {notacion}: '{token}'."
            )

    if disponibles != 1:
        raise ErrorExpresion(
            f"Expresión {notacion} incompleta: quedan {disponibles} operandos "
            "sin operador que los consuma."
        )


def _verificar_operandos_numericos(tokens: List[str]) -> None:
    """Comprueba que todos los operandos sean números para poder evaluar."""
    for token in tokens:
        if token in PRECEDENCIA:
            continue
        if not es_numero(token):
            raise ErrorExpresion(
                f"No se puede evaluar: el elemento '{token}' no es un número. "
                "Las variables sólo se pueden convertir "
                "(infija -> postfija / prefija)."
            )


# ----------------------------------------------------------------------
# Conversiones
# ----------------------------------------------------------------------
def _mayor_precedencia(en_pila: str, actual: str,
                       asociatividad_invertida: bool = False) -> bool:
    """
    Indica si el operador que está en la pila debe salir antes de apilar
    el operador actual (regla del Shunting Yard):

      * mayor precedencia -> sale
      * igual precedencia y operador asociativo por izquierda -> sale
      * igual precedencia y operador asociativo por derecha (^) -> no sale

    `asociatividad_invertida` se usa en la conversión a prefijo: al trabajar
    sobre la expresión invertida la asociatividad se comporta al revés
    (por eso 2^3^2 -> prefijo '^2^32', que es 2^(3^2)).
    """
    precedencia_pila = PRECEDENCIA[en_pila]
    precedencia_actual = PRECEDENCIA[actual]
    if precedencia_pila > precedencia_actual:
        return True
    if precedencia_pila == precedencia_actual:
        asociatividad = ASOCIATIVIDAD[actual]
        if asociatividad_invertida:
            asociatividad = "izq" if asociatividad == "der" else "der"
        return asociatividad == "izq"
    return False


def infijo_a_postfijo(tokens: List[str],
                      traza: Optional[List[str]] = None,
                      asociatividad_invertida: bool = False) -> List[str]:
    """
    Convierte una expresión infija (ya tokenizada) a notación postfija
    mediante el algoritmo Shunting Yard de Dijkstra.

    `traza` es una lista opcional donde se registran los pasos del
    algoritmo con el estado de la pila dinámica de operadores.
    `asociatividad_invertida` sólo lo usa la conversión a prefijo.

    Complejidad O(n) en tiempo y O(n) en memoria.
    """
    salida: List[str] = []
    operadores = Pila()                # pila dinámica de operadores
    # `anotar` registra los pasos sólo si el llamador pidió la traza.
    anotar = (lambda linea: None) if traza is None else traza.append

    anotar("-" * 66)
    anotar("CONVERSIÓN INFIJA -> POSTFIJA (Shunting Yard de Dijkstra)")
    anotar(f"Tokens de entrada: {unir_tokens(tokens, con_espacios=True)}")
    anotar("Nota: en las pilas se muestra primero la cima (izquierda).")

    for posicion, token in enumerate(tokens, start=1):
        prefijo = f"{posicion:>3}. "
        if token == "(":
            operadores.push(token)
            anotar(f"{prefijo}token '('      -> push('(')                          | Pila operadores: {operadores}")

        elif token == ")":
            anotar(f"{prefijo}token ')'      -> desapilar hasta encontrar '('      | Pila operadores: {operadores}")
            while not operadores.esta_vacia() and operadores.peek() != "(":
                desapilado = operadores.pop()
                salida.append(desapilado)
                anotar(f"      operador '{desapilado}' sale a la salida            | Salida: {unir_tokens(salida, True)}")
            if operadores.esta_vacia():
                raise ErrorExpresion("Paréntesis desbalanceados: ')' sin '(' que lo abra.")
            operadores.pop()           # se descarta el '('
            anotar(f"      se descarta '('                                | Pila operadores: {operadores}")

        elif token in PRECEDENCIA:
            while (not operadores.esta_vacia()
                   and operadores.peek() in PRECEDENCIA
                   and _mayor_precedencia(operadores.peek(), token,
                                          asociatividad_invertida)):
                desapilado = operadores.pop()
                salida.append(desapilado)
                anotar(f"      '{desapilado}' tiene prioridad y sale a la salida | Salida: {unir_tokens(salida, True)}")
            operadores.push(token)
            anotar(f"{prefijo}operador '{token}' -> push('{token}')                        | Pila operadores: {operadores}")

        else:
            salida.append(token)
            anotar(f"{prefijo}operando '{token}' -> salida directa                 | Salida: {unir_tokens(salida, True)}")

    while not operadores.esta_vacia():
        desapilado = operadores.pop()
        if desapilado in PARENTESIS:
            raise ErrorExpresion("Paréntesis desbalanceados en la expresión.")
        salida.append(desapilado)
        anotar(f"      fin de tokens: '{desapilado}' sale a la salida         | Salida: {unir_tokens(salida, True)}")

    anotar(f"RESULTADO POSTFIJO: {unir_tokens(salida)}   (con espacios: {unir_tokens(salida, True)})")
    return salida


def infijo_a_prefijo(tokens: List[str],
                     traza: Optional[List[str]] = None) -> List[str]:
    """
    Convierte una expresión infija a notación prefija (notación polaca
    directa) reutilizando el Shunting Yard:

        1. se invierte la lista de tokens,
        2. se intercambian los paréntesis de apertura por los de cierre,
        3. se aplica la conversión a postfija,
        4. se invierte el resultado.

    Complejidad O(n) en tiempo y O(n) en memoria.
    """
    anotar = (lambda linea: traza.append(linea)) if traza is not None else (lambda linea: None)
    traza_interna: Optional[List[str]] = [] if traza is not None else None

    anotar("=" * 66)
    anotar("CONVERSIÓN INFIJA -> PREFIJA (notación polaca directa)")
    anotar(f"Tokens de entrada: {unir_tokens(tokens, con_espacios=True)}")

    invertidos = list(reversed(tokens))
    anotar(f"1) Se invierten los tokens:            {unir_tokens(invertidos, True)}")

    intercambiados = [
        ")" if elemento == "(" else ("(" if elemento == ")" else elemento)
        for elemento in invertidos
    ]
    anotar(f"2) Se intercambian '(' y ')':          {unir_tokens(intercambiados, True)}")
    anotar("   (en esta pasada la asociatividad se invierte: los operadores")
    anotar("    asociativos por la izquierda se comportan por la derecha y viceversa)")
    anotar("3) Se aplica el algoritmo postfijo a esa secuencia:")

    intermedia = infijo_a_postfijo(intercambiados, traza_interna,
                                   asociatividad_invertida=True)
    if traza is not None and traza_interna is not None:
        traza.extend("   " + linea for linea in traza_interna)

    prefija = list(reversed(intermedia))
    anotar(f"4) Se invierte el resultado intermedio: {unir_tokens(intermedia, True)}")
    anotar(f"RESULTADO PREFIJO: {unir_tokens(prefija)}   (con espacios: {unir_tokens(prefija, True)})")
    return prefija


# ----------------------------------------------------------------------
# Evaluación de expresiones en notación polaca
# ----------------------------------------------------------------------
def _pop_seguro(pila: Pila, contexto: str) -> Any:
    """
    Hace pop() comprobando antes que la pila no esté vacía (requisito del
    taller) y traduce el error a un mensaje entendible.
    """
    if pila.esta_vacia():                     # verificación previa obligatoria
        raise ErrorExpresion(
            f"Pila vacía: no se puede hacer pop() al procesar '{contexto}'. "
            "La expresión está incompleta."
        )
    try:
        return pila.pop()
    except PilaVaciaError as error:           # red de seguridad de la pila
        raise ErrorExpresion(
            f"No se pudo hacer pop() al procesar '{contexto}': {error}"
        ) from error


def _aplicar_operador(operador: str, a: float, b: float) -> float:
    """
    Aplica el operador a los operandos a (izquierdo) y b (derecho).
    Controla división/módulo por cero y resultados no reales.
    """
    if operador == "+":
        resultado = a + b
    elif operador == "-":
        resultado = a - b
    elif operador == "*":
        resultado = a * b
    elif operador == "/":
        if b == 0:
            raise ErrorExpresion("Error aritmético: división por cero.")
        resultado = a / b
    elif operador == "%":
        if b == 0:
            raise ErrorExpresion("Error aritmético: módulo por cero.")
        if not (float(a).is_integer() and float(b).is_integer()):
            raise ErrorExpresion(
                "El operador '%' (módulo) sólo admite operandos enteros."
            )
        resultado = float(a) % float(b)
    elif operador == "^":
        if a < 0 and not float(b).is_integer():
            raise ErrorExpresion(
                "Potencia no real: no se puede elevar una base negativa "
                "a un exponente fraccionario."
            )
        resultado = a ** b
    else:
        raise ErrorExpresion(f"Operador no soportado: '{operador}'.")

    if isinstance(resultado, complex):
        raise ErrorExpresion("El resultado no es un número real.")
    return round(float(resultado), 10)   # evita el ruido del punto flotante


def resultado_texto(operaciones: List[str], valor: Any) -> str:
    """Frase final con las operaciones realizadas y el resultado."""
    detalle = " ; ".join(operaciones) if operaciones else "sin operaciones"
    return f"Resultado final = {formatear_numero(valor)}  (operaciones: {detalle})"


def evaluar_postfija(expresion: str) -> Evaluacion:
    """
    Evalúa una expresión escrita en notación postfija (por ejemplo '23+4*').

    Devuelve una `Evaluacion` con el valor, la lista de operaciones
    realizadas y la traza paso a paso con el estado de la pila.
    Complejidad O(n) en tiempo y O(n) en memoria.
    """
    return evaluar_tokens_postfijos(tokenizar(expresion), expresion)


def evaluar_prefija(expresion: str) -> Evaluacion:
    """
    Evalúa una expresión escrita en notación prefija (por ejemplo '*+234').

    Devuelve una `Evaluacion` con el valor, la lista de operaciones
    realizadas y la traza paso a paso con el estado de la pila.
    Complejidad O(n) en tiempo y O(n) en memoria.
    """
    return evaluar_tokens_prefijos(tokenizar(expresion), expresion)


def evaluar_tokens_postfijos(tokens: List[str],
                             expresion_original: str = "") -> Evaluacion:
    """Evalúa tokens postfijos ya separados y genera la traza completa."""
    _validar_expresion_polaca(tokens, "postfija")
    _verificar_operandos_numericos(tokens)
    if not expresion_original:
        expresion_original = unir_tokens(tokens)

    pila = Pila()
    traza: List[str] = [
        "-" * 66,
        f"EVALUACIÓN POSTFIJA de: {unir_tokens(tokens, con_espacios=True)}",
        "Se recorre la expresión de izquierda a derecha.",
        "Nota: en las pilas se muestra primero la cima (izquierda).",
    ]
    operaciones: List[str] = []

    for posicion, token in enumerate(tokens, start=1):
        if token in PRECEDENCIA:
            derecho = _pop_seguro(pila, token)
            izquierdo = _pop_seguro(pila, token)
            valor = _aplicar_operador(token, izquierdo, derecho)
            operaciones.append(
                f"{formatear_numero(izquierdo)} {token} "
                f"{formatear_numero(derecho)} = {formatear_numero(valor)}"
            )
            pila.push(valor)
            traza.append(
                f"{posicion:>3}. operador '{token}' -> pop()={formatear_numero(derecho)}, "
                f"pop()={formatear_numero(izquierdo)} | operación: "
                f"{formatear_numero(izquierdo)} {token} {formatear_numero(derecho)}"
                f" = {formatear_numero(valor)} | push() | Pila: {pila}"
            )
        else:
            pila.push(float(token))
            traza.append(
                f"{posicion:>3}. operando '{token}' -> push({token}) | Pila: {pila}"
            )

    if pila.tamanio != 1:
        raise ErrorExpresion(
            "La expresión postfija no se reduce a un único valor "
            f"(quedan {pila.tamanio} elementos en la pila)."
        )
    valor_final = pila.pop()
    traza.append(f"Pila final: {pila}  ->  {resultado_texto(operaciones, valor_final)}")
    return Evaluacion(
        expresion=expresion_original,
        notacion="postfija",
        tokens=tokens,
        operaciones=operaciones,
        traza=traza,
        valor=valor_final,
    )


def evaluar_tokens_prefijos(tokens: List[str],
                            expresion_original: str = "") -> Evaluacion:
    """Evalúa tokens prefijos ya separados y genera la traza completa."""
    _validar_expresion_polaca(tokens, "prefija")
    _verificar_operandos_numericos(tokens)
    if not expresion_original:
        expresion_original = unir_tokens(tokens)

    pila = Pila()
    traza: List[str] = [
        "-" * 66,
        f"EVALUACIÓN PREFIJA de: {unir_tokens(tokens, con_espacios=True)}",
        "Se recorre la expresión de derecha a izquierda.",
        "Nota: en las pilas se muestra primero la cima (izquierda).",
    ]
    operaciones: List[str] = []

    for posicion, token in enumerate(reversed(tokens), start=1):
        if token in PRECEDENCIA:
            izquierdo = _pop_seguro(pila, token)
            derecho = _pop_seguro(pila, token)
            valor = _aplicar_operador(token, izquierdo, derecho)
            operaciones.append(
                f"{formatear_numero(izquierdo)} {token} "
                f"{formatear_numero(derecho)} = {formatear_numero(valor)}"
            )
            pila.push(valor)
            traza.append(
                f"{posicion:>3}. operador '{token}' -> pop()={formatear_numero(izquierdo)}"
                f" (izquierdo), pop()={formatear_numero(derecho)} (derecho) | operación: "
                f"{formatear_numero(izquierdo)} {token} {formatear_numero(derecho)}"
                f" = {formatear_numero(valor)} | push() | Pila: {pila}"
            )
        else:
            pila.push(float(token))
            traza.append(
                f"{posicion:>3}. operando '{token}' -> push({token}) | Pila: {pila}"
            )

    if pila.tamanio != 1:
        raise ErrorExpresion(
            "La expresión prefija no se reduce a un único valor "
            f"(quedan {pila.tamanio} elementos en la pila)."
        )
    valor_final = pila.pop()
    traza.append(f"Pila final: {pila}  ->  {resultado_texto(operaciones, valor_final)}")
    return Evaluacion(
        expresion=expresion_original,
        notacion="prefija",
        tokens=tokens,
        operaciones=operaciones,
        traza=traza,
        valor=valor_final,
    )


# ----------------------------------------------------------------------
# API de alto nivel usada por la interfaz gráfica y por las pruebas
# ----------------------------------------------------------------------
def modo_tokenizacion(expresion: str) -> str:
    """
    Describe cómo se tokenizó una expresión:
    'con espacios' (números y variables de varios caracteres) o
    'sin espacios' (cada carácter es un token).
    """
    return "con espacios" if any(caracter.isspace() for caracter in expresion.strip()) else "sin espacios"


def es_infija_valida(tokens: List[str]) -> bool:
    """
    Indica si los tokens forman una expresión infija estructuralmente válida
    (operandos y operadores alternados, paréntesis balanceados).
    """
    try:
        validar_estructura(tokens)
    except ErrorExpresion:
        return False
    return True


def notacion_polaca(tokens: List[str]) -> Optional[str]:
    """
    Devuelve 'postfija', 'prefija' o None según la notación polaca en la que
    los tokens forman una expresión válida (se usa para sugerir al usuario
    el botón correcto).
    """
    for notacion in ("postfija", "prefija"):
        try:
            _validar_expresion_polaca(tokens, notacion)
        except ErrorExpresion:
            continue
        return notacion
    return None


def analizar_infija(expresion: str) -> Conversion:
    """
    Tokeniza, valida y convierte una expresión infija a postfija y prefija,
    devolviendo además las trazas completas de ambos algoritmos.
    """
    tokens = tokenizar(expresion)
    validar_estructura(tokens)
    traza_postfija: List[str] = []
    traza_prefija: List[str] = []
    postfija = infijo_a_postfijo(tokens, traza_postfija)
    prefija = infijo_a_prefijo(tokens, traza_prefija)
    return Conversion(
        expresion=expresion,
        tokens=tokens,
        postfija=postfija,
        prefija=prefija,
        traza_postfija=traza_postfija,
        traza_prefija=traza_prefija,
    )


def convertir_a_postfija(expresion: str) -> str:
    """Devuelve la notación postfija compacta, por ejemplo 'AB+C*'."""
    return analizar_infija(expresion).postfija_texto


def convertir_a_prefija(expresion: str) -> str:
    """Devuelve la notación prefija compacta, por ejemplo '*+ABC'."""
    return analizar_infija(expresion).prefija_texto






