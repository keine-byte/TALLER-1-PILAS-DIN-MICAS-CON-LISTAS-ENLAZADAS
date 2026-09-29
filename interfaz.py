# -*- coding: utf-8 -*-
"""
interfaz.py
===========
Interfaz gráfica (Tkinter / ttk) del Taller 1: conversión y evaluación de
expresiones con pilas dinámicas implementadas con listas enlazadas.

La ventana incluye los elementos exigidos por el taller:

    * campo de entrada de la expresión,
    * botones: convertir a postfijo, convertir a prefijo, evaluar postfijo,
      evaluar prefijo, limpiar (más un botón de ayuda),
    * área de resultados (postfija, prefija y resultado numérico),
    * área de detalle donde se muestran las trazas de los algoritmos, las
      operaciones realizadas y los mensajes de error.

Toda la lógica matemática vive en `expresiones.py`; este módulo sólo se
encarga de la presentación y de capturar los errores de validación.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText

import expresiones as logica

__all__ = ["VentanaTaller", "TITULO"]

TITULO = "Taller 1 - Pilas dinámicas con listas enlazadas | Notación Polaca"

# Ejemplos útiles para el usuario (incluye los casos del taller y casos de error).
EJEMPLOS = [
    "(A+B)*C",
    "(A+B)*(C-D)",
    "A+B*C-D/E^F",
    "A-B-C",
    "2^3^2",
    "3 + 4 * 2 / (1 - 5)",
    "23+4*",
    "*+234",
    "(A+B*",
    "+A",
]

TEXTO_AYUDA = """AYUDA - CÓMO ESCRIBIR LAS EXPRESIONES
------------------------------------------------------------------
Operadores admitidos:  +  -  *  /  %  ^   (^ = potencia)
Paréntesis: ( ) se usan sólo en notación infija.

1) SIN espacios ("modo compacto"): cada carácter es un token.
      (A+B)*C   ->  tokens  ( A + B ) * C
      23+4*     ->  tokens  2 3 + 4 *
      *+234     ->  tokens  * + 2 3 4
   Es la forma en que el taller plantea los ejemplos numéricos.

2) CON espacios ("modo separado"): cada grupo es un token, por lo que se
   admiten números de varios dígitos y variables de varias letras.
      23 + 4 * 5        ->  tokens  23 + 4 * 5   (INFIJA: convertir)
      23 4 +            ->  tokens  23 4 +      (postfija = 27)
      2.5 4 *           ->  tokens  2.5 4 *     (postfija = 10)
      (total + 2) * 3   ->  variables de varias letras (sólo conversión)

3) El signo negativo se escribe pegado al número: -5, 2*-3.
   El '+' siempre es el operador suma (por eso *+234 es prefija).

FLUJO DE USO
------------------------------------------------------------------
  * "Convertir a postfijo" / "Convertir a prefijo": el campo debe contener
    una expresión INFIJA (por ejemplo (A+B)*C).
  * "Evaluar postfijo" / "Evaluar prefijo": el campo debe contener una
    expresión en esa notación con VALORES NUMÉRICOS (por ejemplo 23+4*).
  * "Limpiar" vacía la entrada, los resultados y el detalle.

El detalle muestra, paso a paso, el estado de la pila dinámica
(la cima aparece siempre a la izquierda) y las operaciones realizadas."""

TEXTO_BIENVENIDA = """TALLER 1: PILAS DINÁMICAS CON LISTAS ENLAZADAS
Conversión y evaluación de expresiones (notación polaca)

Escriba una expresión y use los botones de la parte superior.
Pulse "Ayuda / Sintaxis" para ver las reglas de escritura.

Este panel mostrará:
  * los tokens detectados y las validaciones realizadas,
  * la traza del algoritmo (con el estado de la pila en cada paso),
  * las operaciones realizadas y el resultado final,
  * los mensajes de error cuando la expresión sea inválida."""


class VentanaTaller(tk.Tk):
    """Ventana principal del programa del Taller 1."""

    def __init__(self, usar_dialogos: bool = True) -> None:
        super().__init__()
        # `usar_dialogos=False` permite generar capturas sin ventanas modales.
        self.usar_dialogos = usar_dialogos

        self.title(TITULO)
        self.geometry("1040x740")
        self.minsize(900, 620)

        # Variables enlazadas a los widgets -----------------------------
        self.var_expresion = tk.StringVar()
        self.var_ejemplo = tk.StringVar()
        self.var_postfija = tk.StringVar(value="—")
        self.var_prefija = tk.StringVar(value="—")
        self.var_resultado = tk.StringVar(value="—")
        self.var_estado = tk.StringVar(value="Listo. Escriba una expresión para comenzar.")

        self._configurar_estilos()
        self._construir_interfaz()
        self._escribir_detalle(TEXTO_BIENVENIDA, "titulo")

    # ------------------------------------------------------------------
    # Construcción de la interfaz
    # ------------------------------------------------------------------
    def _configurar_estilos(self) -> None:
        estilo = ttk.Style(self)
        if "clam" in estilo.theme_names():
            estilo.theme_use("clam")
        estilo.configure("Titulo.TLabel", font=("Segoe UI", 15, "bold"),
                         foreground="#12395c")
        estilo.configure("Subtitulo.TLabel", font=("Segoe UI", 10),
                         foreground="#4a4a4a")
        estilo.configure("Resultado.TLabel", font=("Segoe UI", 11, "bold"))
        estilo.configure("Valor.TEntry", font=("Consolas", 12))
        estilo.configure("Accion.TButton", font=("Segoe UI", 10, "bold"))
        estilo.configure("Estado.TLabel", font=("Segoe UI", 9),
                         foreground="#12395c")

    def _construir_interfaz(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(4, weight=1)          # el detalle es el que crece

        self._crear_encabezado()
        self._crear_entrada()
        self._crear_botones()
        self._crear_resultados()
        self._crear_panel_detalle()
        self._crear_barra_estado()

    def _crear_encabezado(self) -> None:
        marco = ttk.Frame(self, padding=(14, 12, 14, 4))
        marco.grid(row=0, column=0, sticky="ew")
        marco.columnconfigure(0, weight=1)
        ttk.Label(marco,
                  text="Conversión y evaluación de expresiones (notación polaca)",
                  style="Titulo.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(marco,
                  text="Pilas dinámicas implementadas con listas enlazadas "
                       "(clases Nodo y Pila) · operadores +  -  *  /  %  ^",
                  style="Subtitulo.TLabel").grid(row=1, column=0, sticky="w")

    def _crear_entrada(self) -> None:
        marco = ttk.LabelFrame(self, text=" Expresión ", padding=(12, 8, 12, 10))
        marco.grid(row=1, column=0, sticky="ew", padx=14, pady=(6, 4))
        marco.columnconfigure(1, weight=1)

        ttk.Label(marco, text="Expresión:").grid(row=0, column=0, sticky="w")
        self.entrada = ttk.Entry(marco, textvariable=self.var_expresion,
                                 font=("Consolas", 14))
        self.entrada.grid(row=0, column=1, sticky="ew", padx=(8, 8))
        self.entrada.bind("<Return>", lambda evento: self._accion_convertir_postfijo())
        self.entrada.focus_set()

        ttk.Label(marco, text="Ejemplos:").grid(row=1, column=0, sticky="w", pady=(8, 0))
        combo = ttk.Combobox(marco, textvariable=self.var_ejemplo, values=EJEMPLOS,
                             state="readonly", width=26)
        combo.grid(row=1, column=1, sticky="w", padx=(8, 8), pady=(8, 0))
        combo.bind("<<ComboboxSelected>>", self._accion_cargar_ejemplo)
        ttk.Label(marco,
                  text="Los ejemplos inválidos sirven para ver los mensajes de error.",
                  style="Subtitulo.TLabel").grid(row=1, column=2, sticky="w", pady=(8, 0))

    def _crear_botones(self) -> None:
        marco = ttk.Frame(self, padding=(14, 0, 14, 6))
        marco.grid(row=2, column=0, sticky="ew")
        botones = (
            ("Convertir a postfijo", self._accion_convertir_postfijo),
            ("Convertir a prefijo", self._accion_convertir_prefijo),
            ("Evaluar postfijo", self._accion_evaluar_postfijo),
            ("Evaluar prefijo", self._accion_evaluar_prefijo),
            ("Limpiar", self._accion_limpiar),
            ("Ayuda / Sintaxis", self._accion_ayuda),
        )
        for indice, (texto, accion) in enumerate(botones):
            ttk.Button(marco, text=texto, command=accion,
                       style="Accion.TButton").grid(row=0, column=indice,
                                                    padx=(0, 8), pady=2, sticky="ew")
            marco.columnconfigure(indice, weight=1)

    def _crear_resultados(self) -> None:
        marco = ttk.LabelFrame(self, text=" Resultados ", padding=(12, 8, 12, 10))
        marco.grid(row=3, column=0, sticky="ew", padx=14, pady=(0, 6))
        marco.columnconfigure(1, weight=1)

        filas = (
            ("Expresión postfija:", self.var_postfija),
            ("Expresión prefija:", self.var_prefija),
            ("Resultado:", self.var_resultado),
        )
        for indice, (etiqueta, variable) in enumerate(filas):
            ttk.Label(marco, text=etiqueta, style="Resultado.TLabel").grid(
                row=indice, column=0, sticky="w", pady=2)
            campo = ttk.Entry(marco, textvariable=variable, state="readonly",
                              style="Valor.TEntry")
            campo.grid(row=indice, column=1, sticky="ew", padx=(8, 0), pady=2)

    def _crear_panel_detalle(self) -> None:
        marco = ttk.LabelFrame(self, text=" Detalle del proceso ", padding=(10, 6, 10, 8))
        marco.grid(row=4, column=0, sticky="nsew", padx=14, pady=(0, 6))
        marco.columnconfigure(0, weight=1)
        marco.rowconfigure(0, weight=1)

        self.detalle = ScrolledText(marco, wrap="word", height=14,
                                    font=("Consolas", 10), background="#fbfcfd")
        self.detalle.grid(row=0, column=0, sticky="nsew")
        self.detalle.configure(state="disabled")

        fondo = self.detalle.cget("background")
        self.detalle.tag_configure("titulo", foreground="#12395c",
                                   font=("Consolas", 11, "bold"),
                                   spacing1=4, spacing3=4)
        self.detalle.tag_configure("subtitulo", foreground="#12395c",
                                   font=("Consolas", 10, "bold"),
                                   spacing1=6, spacing3=2)
        self.detalle.tag_configure("ok", foreground="#0b6623")
        self.detalle.tag_configure("error", foreground="#a3161b",
                                   font=("Consolas", 10, "bold"))
        self.detalle.tag_configure("nota", foreground="#5a5a5a")
        self.detalle.tag_configure("codigo", foreground="#000000",
                                   background=fondo, font=("Consolas", 10, "bold"))
        self.detalle.tag_configure("normal", foreground="#222222")

    def _crear_barra_estado(self) -> None:
        marco = ttk.Frame(self, padding=(14, 0, 14, 8))
        marco.grid(row=5, column=0, sticky="ew")
        marco.columnconfigure(0, weight=1)
        ttk.Label(marco, textvariable=self.var_estado,
                  style="Estado.TLabel").grid(row=0, column=0, sticky="w")

    # ------------------------------------------------------------------
    # Utilidades internas
    # ------------------------------------------------------------------
    def _expresion_actual(self) -> str:
        return self.var_expresion.get().strip()

    def _escribir_detalle(self, texto: str, etiqueta: str = "normal") -> None:
        """Agrega texto al panel de detalle respetando el modo de sólo lectura."""
        self.detalle.configure(state="normal")
        self.detalle.insert("end", texto + "\n", etiqueta)
        self.detalle.see("end")
        self.detalle.configure(state="disabled")

    def _limpiar_detalle(self) -> None:
        self.detalle.configure(state="normal")
        self.detalle.delete("1.0", "end")
        self.detalle.configure(state="disabled")

    def _estado(self, mensaje: str) -> None:
        self.var_estado.set(mensaje)

    def _reiniciar_resultados(self) -> None:
        self.var_postfija.set("—")
        self.var_prefija.set("—")
        self.var_resultado.set("—")

    def _mostrar_informacion(self, titulo: str, mensaje: str) -> None:
        if self.usar_dialogos:
            messagebox.showinfo(titulo, mensaje)

    def _mostrar_error(self, mensaje: str) -> None:
        if self.usar_dialogos:
            messagebox.showerror("Error en la expresión", mensaje)

    def _sin_expresion(self) -> bool:
        """Devuelve True (y avisa) cuando el campo de entrada está vacío."""
        if self._expresion_actual():
            return False
        self._limpiar_detalle()
        self._reiniciar_resultados()
        self._escribir_detalle("ENTRADA VACÍA", "error")
        self._escribir_detalle(
            "Escriba una expresión en el campo superior.\n"
            "  · Infija para convertir:   (A+B)*C\n"
            "  · Postfija para evaluar:   23+4*\n"
            "  · Prefija para evaluar:    *+234", "nota")
        self._estado("No hay ninguna expresión escrita.")
        self._mostrar_error("Escriba una expresión antes de usar los botones.")
        return True

    def _reportar_error(self, error: logica.ErrorExpresion, contexto: str,
                        estructura_correcta: bool = False) -> None:
        """
        Muestra el error en el panel de detalle y en la barra de estado.

        `estructura_correcta=True` indica que la notación de la expresión es
        válida y que el problema está en los valores (por ejemplo 5 0 /: la
        división por cero no es un error de sintaxis).
        """
        self._escribir_detalle(f"ERROR · {contexto}", "error")
        self._escribir_detalle(f"  {error}", "error")
        if estructura_correcta:
            self._escribir_detalle(
                "  La notación de la expresión es CORRECTA: el error está en el\n"
                "  cálculo de los operandos (revise esos valores) o pulse "
                "'Limpiar'.", "nota")
        else:
            self._escribir_detalle(
                "  Revise la sintaxis (botón 'Ayuda / Sintaxis') o pulse 'Limpiar'.",
                "nota")
        self._estado(f"Error: {error}")
        self._mostrar_error(str(error))

    @staticmethod
    def _encabezado(texto: str) -> str:
        return "=" * 66 + "\n" + texto

    def _escribir_traza(self, encabezado: str, lineas: list) -> None:
        self._escribir_detalle(encabezado, "subtitulo")
        for linea in lineas:
            self._escribir_detalle(linea, "normal")

    # ------------------------------------------------------------------
    # Acciones de los botones
    # ------------------------------------------------------------------
    def _accion_cargar_ejemplo(self, _evento=None) -> None:
        ejemplo = self.var_ejemplo.get()
        if not ejemplo:
            return
        self.var_expresion.set(ejemplo)
        self.entrada.icursor("end")
        self.entrada.focus_set()
        self._limpiar_detalle()
        self._reiniciar_resultados()
        self._escribir_detalle(f"Ejemplo cargado: {ejemplo}", "titulo")
        self._escribir_detalle(
            "Elija el botón que corresponda: los ejemplos con paréntesis son infijos "
            "(convertir), los del taller 23+4* / *+234 son polacos (evaluar) y las "
            "entradas (A+B* y +A sirven para ver los errores de validación.", "nota")
        self._estado(f"Ejemplo cargado: {ejemplo}")

    def _accion_ayuda(self) -> None:
        self._limpiar_detalle()
        self._escribir_detalle(TEXTO_AYUDA, "titulo")
        self._estado("Ayuda mostrada en el panel de detalle.")
        self._mostrar_informacion(
            "Ayuda / Sintaxis",
            "La sintaxis y el flujo de uso se muestran en el panel de detalle.\n\n"
            "Resumen: escriba la expresión, convierta (infija -> postfija / prefija) "
            "o evalúe (postfija / prefija).")

    def _accion_limpiar(self) -> None:
        self.var_expresion.set("")
        self.var_ejemplo.set("")
        self._reiniciar_resultados()
        self._limpiar_detalle()
        self._escribir_detalle(TEXTO_BIENVENIDA, "titulo")
        self._estado("Campos limpios. Listo para una nueva expresión.")
        self.entrada.focus_set()

    def _accion_convertir_postfijo(self) -> None:
        self._convertir(destacar="postfija")

    def _accion_convertir_prefijo(self) -> None:
        self._convertir(destacar="prefija")

    def _convertir(self, destacar: str) -> None:
        """Convierte la expresión infija a postfija y prefija mostrando trazas."""
        if self._sin_expresion():
            return
        expresion = self._expresion_actual()
        self._limpiar_detalle()
        self._reiniciar_resultados()

        try:
            tokens = logica.tokenizar(expresion)
            conversion = logica.analizar_infija(expresion)
        except logica.ErrorExpresion as error:
            self._sugerir_desde_error(expresion, error, "conversión infija")
            return

        self.var_postfija.set(conversion.postfija_texto)
        self.var_prefija.set(conversion.prefija_texto)

        self._escribir_detalle(
            self._encabezado(f"CONVERSIÓN DE LA EXPRESIÓN: {expresion}"), "titulo")
        self._escribir_detalle(
            f"Tokens detectados ({len(tokens)}, modo "
            f"{logica.modo_tokenizacion(expresion)}): {conversion.tokens_texto}")
        self._escribir_detalle(
            "Validación de la estructura infija: CORRECTA (paréntesis balanceados "
            "y operandos/operadores alternados).", "ok")
        self._escribir_detalle(
            f"RESULTADO POSTFIJO: {conversion.postfija_texto}\n"
            f"   con espacios: {conversion.postfija_espaciada}", "ok")
        self._escribir_detalle(
            f"RESULTADO PREFIJO: {conversion.prefija_texto}\n"
            f"   con espacios: {conversion.prefija_espaciada}", "ok")

        titulo_post = "--- TRAZA: infija -> POSTFIJA (Shunting Yard de Dijkstra) ---"
        titulo_pre = "--- TRAZA: infija -> PREFIJA (notación polaca directa) ---"
        if destacar == "postfija":
            self._escribir_traza(titulo_post, conversion.traza_postfija)
            self._escribir_traza(titulo_pre, conversion.traza_prefija)
        else:
            self._escribir_traza(titulo_pre, conversion.traza_prefija)
            self._escribir_traza(titulo_post, conversion.traza_postfija)

        self._escribir_detalle(
            "  Los valores mostrados son los que deben reportarse como evidencia.",
            "nota")
        self._estado(
            f"Conversión correcta: postfija = {conversion.postfija_texto} | "
            f"prefija = {conversion.prefija_texto}")

    def _accion_evaluar_postfijo(self) -> None:
        self._evaluar("postfija")

    def _accion_evaluar_prefijo(self) -> None:
        self._evaluar("prefija")

    def _evaluar(self, notacion: str) -> None:
        """Evalúa la expresión escrita en la notación polaca indicada."""
        if self._sin_expresion():
            return
        expresion = self._expresion_actual()
        self._limpiar_detalle()
        self._reiniciar_resultados()

        etiqueta = "Evaluar postfijo" if notacion == "postfija" else "Evaluar prefijo"
        try:
            tokens = logica.tokenizar(expresion)
        except logica.ErrorExpresion as error:
            self._reportar_error(error, etiqueta)
            return

        if logica.es_infija_valida(tokens):
            self._avisar_es_infija(expresion, tokens, notacion)
            return

        try:
            if notacion == "postfija":
                evaluacion = logica.evaluar_tokens_postfijos(tokens, expresion)
            else:
                evaluacion = logica.evaluar_tokens_prefijos(tokens, expresion)
        except logica.ErrorExpresion as error:
            self._sugerir_desde_error(expresion, error,
                                      f"evaluación {notacion}", notacion)
            return

        self.var_resultado.set(evaluacion.valor_texto)
        self._escribir_detalle(
            self._encabezado(f"EVALUACIÓN {notacion.upper()} DE: {expresion}"), "titulo")
        self._escribir_detalle(
            f"Tokens ({len(tokens)}, modo {logica.modo_tokenizacion(expresion)}): "
            f"{logica.unir_tokens(tokens, con_espacios=True)}")
        self._escribir_detalle(
            f"Validación {notacion}: CORRECTA (la expresión se reduce a un valor).",
            "ok")
        self._escribir_traza(f"--- TRAZA: evaluación {notacion} paso a paso ---",
                             evaluacion.traza)
        self._escribir_detalle("--- OPERACIONES REALIZADAS ---", "subtitulo")
        if evaluacion.operaciones:
            for operacion in evaluacion.operaciones:
                self._escribir_detalle(f"   · {operacion}", "ok")
        else:
            self._escribir_detalle(
                "   · (ninguna: la expresión es un único operando)", "nota")
        self._escribir_detalle(
            self._encabezado(f"RESULTADO FINAL: {evaluacion.valor_texto}"), "ok")
        self._estado(f"Resultado ({notacion}) = {evaluacion.valor_texto}")

    def _avisar_es_infija(self, expresion: str, tokens: list, notacion: str) -> None:
        """Avisa cuando el usuario intenta evaluar una expresión infija."""
        self._escribir_detalle(
            self._encabezado(f"LA EXPRESIÓN '{expresion}' ESTÁ EN NOTACIÓN INFIJA"),
            "titulo")
        self._escribir_detalle(
            f"Tokens detectados (modo {logica.modo_tokenizacion(expresion)}): "
            f"{logica.unir_tokens(tokens, con_espacios=True)}")
        self._escribir_detalle(
            "Puede convertirla con 'Convertir a postfijo' / 'Convertir a prefijo' y "
            "evaluar el resultado, o escribir directamente la expresión en notación "
            "polaca (por ejemplo 23+4* para postfija y *+234 para prefija).", "nota")
        self._estado("La expresión es infija: use los botones de conversión.")
        self._mostrar_error(
            f"'{expresion}' es una expresión infija, no {notacion}.\n\n"
            "Use 'Convertir a postfijo' o 'Convertir a prefijo', o escriba la\n"
            "expresión en notación polaca (por ejemplo 23+4* para postfija y\n"
            "*+234 para prefija).")

    def _sugerir_desde_error(self, expresion: str, error: logica.ErrorExpresion,
                             contexto: str,
                             notacion_esperada: str = "") -> None:
        """
        Reporta el error y, si la entrada está en OTRA notación, lo indica.

        `notacion_esperada` es la notación que se estaba procesando ('postfija'
        o 'prefija'). Se usa para no sugerir un cambio de botón cuando la
        expresión ya está en esa misma notación: en ese caso el error es real
        (por ejemplo 5 0 / -> división por cero) y debe mostrarse tal cual.
        """
        try:
            tokens = logica.tokenizar(expresion)
        except logica.ErrorExpresion:
            self._reportar_error(error, contexto)
            return

        otra = logica.notacion_polaca(tokens)
        if not otra or otra == notacion_esperada:
            self._reportar_error(error, contexto,
                                 estructura_correcta=bool(otra))
            return

        etiqueta = "postfijo" if otra == "postfija" else "prefijo"
        self._escribir_detalle(
            self._encabezado(f"LA EXPRESIÓN YA ESTÁ EN NOTACIÓN {otra.upper()}"),
            "titulo")
        self._escribir_detalle(
            f"Tokens detectados (modo {logica.modo_tokenizacion(expresion)}): "
            f"{logica.unir_tokens(tokens, con_espacios=True)}")
        self._escribir_detalle(
            f"Use el botón 'Evaluar {etiqueta}' para obtener su valor (si todos los "
            f"operandos son números) o escriba una expresión infija para convertir.",
            "nota")
        self._estado(f"La expresión ya está en notación {otra}.")
        self._mostrar_error(
            f"'{expresion}' ya está en notación {otra}.\n\n"
            f"Detalle: {error}\n\n"
            f"Use el botón 'Evaluar {etiqueta}' para calcular su valor.")


# ----------------------------------------------------------------------
# Punto de entrada de la interfaz
# ----------------------------------------------------------------------
def iniciar(usar_dialogos: bool = True) -> None:
    """Crea la ventana del taller y entra en el bucle principal de Tkinter."""
    ventana = VentanaTaller(usar_dialogos=usar_dialogos)
    ventana.mainloop()


if __name__ == "__main__":
    iniciar()





