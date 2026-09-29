# TALLER 1 — Pilas dinámicas con listas enlazadas

## Portada de la entrega

| Dato                       | Información                                                                                          |
| -------------------------- | ----------------------------------------------------------------------------------------------------- |
| **Asignatura**       | «completar: p. ej. Estructura de Datos / Análisis de Algoritmos»                                   |
| **Tema**             | Conversión y evaluación de expresiones en notación polaca con pilas dinámicas                     |
| **Modalidad**        | Trabajo en grupos de tres (3) estudiantes                                                             |
| **Integrantes**      | 1. Keiner Elias Beltran Vergara<br />2. Samuel Gueovo Payares <br />3. Alex Chica Lloreda            |
| **Docente**          | Jairo Enrique Martinez Banda                                                                          |
| **Institución**     | Cecar                                                                                                 |
| **Fecha de entrega** | 01/10/2026                                                                                            |
| **Entregables**      | Código fuente completo · Capturas de ejecución · Evidencia de pruebas · Análisis de complejidad |

> **Antes de entregar:** reemplace los textos entre `« »` por los datos reales
> del grupo (asignatura, integrantes, docente, institución y fecha).

---

Conversión y evaluación de expresiones aritméticas en **notación infija, postfija
(notación polaca inversa) y prefija (notación polaca)**, implementadas con una
**pila dinámica LIFO construida con listas enlazadas simples** (clases `Nodo` y
`Pila` estudiadas en clase) y una interfaz gráfica en **Tkinter**.

El proyecto **no usa listas de Python como pila** en los algoritmos: toda la
conversión y toda la evaluación trabajan con instancias de `pila.Pila`.

---

## 1. Contenido del proyecto

| Archivo                             | Descripción                                                                                                                                                                                                                                                             |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `pila.py`                         | Estructura de datos:`Nodo` (lista enlazada simple) y `Pila` LIFO dinámica (`push`, `pop`, `peek`/`cima`, `esta_vacia`, `limpiar`, `a_lista`, `tamano`).                                                                                             |
| `expresiones.py`                  | Lógica pura (sin Tkinter): tokenización, validación, conversión infija→postfija/prefija y evaluación postfija/prefija, con**trazas paso a paso** y registro de operaciones.                                                                                  |
| `interfaz.py`                     | Interfaz gráfica (Tkinter/ttk): campo de entrada, combobox de ejemplos, botones*Convertir a postfijo*, *Convertir a prefijo*, *Evaluar postfijo*, *Evaluar prefijo*, *Limpiar* y *Ayuda / Sintaxis*; área de resultados y panel de detalle con las trazas. |
| `pruebas.py`                      | Batería de**59 pruebas unitarias** (`unittest`) e informe de ejecución: 53 de lógica pura (pila, expresiones) y 6 de la interfaz gráfica.                                                                                                                    |
| `capturas.py`                     | Genera las**evidencias** en `evidencias/`: 12 capturas PNG de la interfaz y 4 archivos de texto.                                                                                                                                                                 |
| `main.py`                         | Punto de entrada por línea de comandos (abre la GUI si no recibe argumentos).                                                                                                                                                                                           |
| `evidencias/`                     | Evidencias de ejecución (capturas y textos) que se entregan con el taller.                                                                                                                                                                                              |
| `TALLER 1 de Pilas Dinamicas.pdf` | Enunciado original del taller.                                                                                                                                                                                                                                           |

---

## 2. Requisitos e instalación

* **Python 3.10 o superior** (se probó con Python 3.14.4 en Windows).
* **Tkinter**: viene incluido en el instalador oficial de Python para Windows.
* **Pillow** (opcional, sólo para generar las capturas PNG de evidencia):

```powershell
py -m pip install pillow        # opcional: sólo para py capturas.py
```

La lógica matemática (`expresiones.py`, `pila.py`) y las pruebas (`pruebas.py`)
no necesitan ninguna dependencia externa.

---

## 3. Cómo ejecutar

```powershell
py main.py                # abre la interfaz gráfica (Tkinter)
py main.py --demo         # demostración por consola con los casos del taller
py main.py --pruebas      # ejecuta las 59 pruebas unitarias (informe completo)
py main.py --capturas     # genera las evidencias en la carpeta evidencias/
py main.py --ayuda        # muestra la ayuda de opciones
```

También se puede ejecutar cada módulo directamente:

```powershell
py interfaz.py            # interfaz gráfica
py pruebas.py             # pruebas unitarias
py capturas.py            # evidencias
```

---

## 4. Formas de escribir las expresiones

El programa acepta **dos modos de tokenización**, elegidos automáticamente según
la entrada:

1. **Sin espacios (modo compacto):** cada carácter es un token. Es la forma en
   que el taller plantea los ejemplos numéricos.
   * `23+4*` → tokens `2 3 + 4 *` → `(2+3)*4 = 20`
   * `*+234` → tokens `* + 2 3 4` → `2+3=5, 5*4=20`
2. **Con espacios (modo separado):** cada grupo separado por espacios es un
   token, por lo que se admiten números de varios dígitos, decimales y nombres
   de varias letras.
   * `23 4 +` → tokens `23 4 +` → postfija → `23 + 4 = 27` (número de 2 dígitos)
   * `2.5 4 *` → tokens `2.5 4 *` → postfija → `2.5 * 4 = 10` (decimales)
   * `23 + 4 * 5` → tokens `23 + 4 * 5` → es **infija**: se convierte a
     postfija `23 4 5 * +` y ya entonces se puede evaluar (43)
   * `(total + 2) * 3` → variables de varias letras: sólo conversión (postfija
     `total2+3*`), no hay valor numérico

> Nota: evaluar una expresión infija con los botones *Evaluar postfijo/
> prefijo* produce un error de validación; para eso están los botones
> *Convertir*, que además muestran la traza de la pila.

Los paréntesis siempre se separan del resto (`(A+B)*C` ≡ `( A + B ) * C`).

### Operadores

| Operador | Significado     | Precedencia | Asociatividad     |
| -------- | --------------- | ----------- | ----------------- |
| `+`    | suma            | 1           | izquierda         |
| `-`    | resta           | 1           | izquierda         |
| `*`    | multiplicación | 2           | izquierda         |
| `/`    | división       | 2           | izquierda         |
| `%`    | módulo         | 2           | izquierda         |
| `^`    | potencia        | 3           | **derecha** |

Reglas especiales:

* El **signo negativo se escribe pegado al número** (`-5`, `2*-3`); no se admite
  el menos unario delante de variables o paréntesis.
* El `+` **siempre** es el operador suma (por eso `*+234` se interpreta como
  expresión prefija y no como un número `+234`).

---

## 5. Casos del taller y resultados obtenidos

### 5.1 Conversiones pedidas por el taller (infija → postfija / prefija)

| Expresión infija | Postfija        | Prefija         |
| ----------------- | --------------- | --------------- |
| `(A+B)*C`       | `AB+C*`       | `*+ABC`       |
| `(A+B)*(C-D)`   | `AB+CD-*`     | `*+AB-CD`     |
| `A+B*C-D/E^F`   | `ABC*+DEF^/-` | `-+A*BC/D^EF` |
| `2^3^2`         | `232^^`       | `^2^32`       |
| `(A+B)^C`       | `AB+C^`       | `^+ABC`       |

### 5.2 Evaluaciones pedidas por el taller (notación polaca)

| Expresión postfija | Resultado | Operaciones registradas                          |
| ------------------- | --------- | ------------------------------------------------ |
| `23+4*`           | `20`    | `2 + 3 = 5` ; `5 * 4 = 20`                   |
| `3 4 + 2 *`       | `14`    | `3 + 4 = 7` ; `7 * 2 = 14`                   |
| `8 2 / 2 /`       | `2`     | `8 / 2 = 4` ; `4 / 2 = 2`                    |
| `23*45*+`         | `26`    | `2 * 3 = 6` ; `4 * 5 = 20` ; `6 + 20 = 26` |
| `2 10 ^`          | `1024`  | `2 ^ 10 = 1024`                                |

| Expresión prefija | Resultado | Operaciones registradas                          |
| ------------------ | --------- | ------------------------------------------------ |
| `*+234`          | `20`    | `2 + 3 = 5` ; `5 * 4 = 20`                   |
| `+ 6 * 3 2`      | `12`    | `3 * 2 = 6` ; `6 + 6 = 12`                   |
| `//822`          | `2`     | `8 / 2 = 4` ; `4 / 2 = 2`                    |
| `+*23*45`        | `26`    | `4 * 5 = 20` ; `2 * 3 = 6` ; `6 + 20 = 26` |
| `^ 2 10`         | `1024`  | `2 ^ 10 = 1024`                                |

### 5.3 Expresiones inválidas (validación exigida por el taller)

| Entrada     | Mensaje del programa                                                                                                              |
| ----------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `(A+B*`   | `Paréntesis desbalanceados: falta cerrar 1 paréntesis de apertura (posiciones: 1).`                                           |
| `+A`      | `El operador '+' (posición 1) no tiene operando a su izquierda.`                                                               |
| `A B`     | `Faltan operadores entre 'A' y 'B' (posición 2).`                                                                              |
| `2 3 + 4` | `Expresión postfija incompleta: quedan 2 operandos sin operador que los consuma.`                                              |
| `*+23`    | `Expresión prefija inválida: el operador '*' (posición 4 de la secuencia) necesita 2 operandos y sólo hay 1 disponible(s).` |
| `5 0 /`   | `Error aritmético: división por cero.`                                                                                        |

También se validan: paréntesis vacíos `()`, paréntesis de cierre sin apertura,
operandos consecutivos sin operador, operador al final, expresiones incompletas
en notación polaca, símbolos no numéricos al evaluar, y se avisa cuando la
expresión está escrita en **otra notación** de la que se pidió (por ejemplo, al
pulsar *Evaluar postfijo* con `+23` se sugiere *Evaluar prefijo*).

Además, la interfaz distingue dos tipos de fallo en el panel *Detalle del proceso*
y no confunde uno con otro:

* **Error de sintaxis:** la expresión no está bien formada (`(A+B*`, `+A`,
  `2 3 + 4`) → se sugiere revisar la sintaxis con el botón *Ayuda / Sintaxis*.
* **Error de cálculo:** la notación es correcta, pero la operación no se puede
  realizar (`5 0 /` → división por cero, `AB+` → operandos no numéricos) → se
  indica que el error está en los **valores de los operandos**; nunca se sugiere
  cambiar de notación, porque la expresión ya está en la notación correcta.

---

## 6. Algoritmos y complejidad

### 6.1 Operaciones de la pila dinámica (`pila.py`)

| Operación                     | Tiempo         | Memoria adicional | Comentario                                                      |
| ------------------------------ | -------------- | ----------------- | --------------------------------------------------------------- |
| `push(dato)`                 | **O(1)** | O(1)              | Inserta un nodo al inicio de la lista enlazada.                 |
| `pop()`                      | **O(1)** | O(1)              | Extrae el primer nodo; lanza`PilaVaciaError` si está vacía. |
| `peek()` / `cima_dato()`   | **O(1)** | O(1)              | Devuelve el dato de la cima sin modificar la pila.              |
| `esta_vacia()`               | **O(1)** | O(1)              | Comparación de la referencia`cima` con `None`.             |
| `tamano()`                   | **O(1)** | O(1)              | Contador de nodos actualizado en`push`/`pop`.               |
| `limpiar()`                  | O(n)           | O(1)              | Recorre los nodos liberándolos.                                |
| `a_lista()` / `__iter__()` | O(n)           | O(1)*             | Recorre de la cima a la base sin modificar la pila.             |

\* `a_lista()` construye una lista de n elementos, por lo que ocupa O(n) memoria
adicional (el recorrido con `for` sí es O(1)).

El crecimiento es **dinámico**: la pila no tiene tamaño fijo (las pruebas crean
una pila con 1000 elementos) y el espacio total es O(n) para n elementos.

### 6.2 Algoritmos de expresiones (`expresiones.py`)

| Etapa                | Algoritmo                                                                                                     | Tiempo | Memoria |
| -------------------- | ------------------------------------------------------------------------------------------------------------- | ------ | ------- |
| Tokenización        | recorrido lineal de la expresión                                                                             | O(n)   | O(n)    |
| Validación          | autómata de un solo paso (balance de paréntesis y de operandos)                                             | O(n)   | O(1)    |
| Infija → postfija   | **Shunting Yard de Dijkstra** (pila de operadores)                                                      | O(n)   | O(n)    |
| Infija → prefija    | inversión de tokens +`('(' ↔ ')')` + Shunting Yard con asociatividad invertida + inversión del resultado | O(n)   | O(n)    |
| Evaluación postfija | pila de operandos, un solo recorrido izquierda→derecha                                                       | O(n)   | O(n)    |
| Evaluación prefija  | pila de operandos, un solo recorrido derecha→izquierda                                                       | O(n)   | O(n)    |
| Trazas paso a paso   | se acumulan cadenas por cada token                                                                            | O(n)   | O(n)    |

donde **n = número de tokens**. En todos los casos cada token se procesa una sola
vez y cada elemento entra y sale de la pila a lo sumo una vez (cada operación de
pila es O(1)), por lo que el costo total es lineal.

### 6.3 Idea de cada algoritmo

* **Shunting Yard (infija → postfija):** se apilan operadores y paréntesis de
  apertura; un operador nuevo desapila los que tengan mayor precedencia (o igual,
  si son asociativos por la izquierda) y todo lo que quede en la pila se vacía al
  final. Los operandos salen en el orden en que aparecen.
* **Infija → prefija:** se invierten los tokens, se intercambian `(` y `)`, se
  aplica el mismo Shunting Yard (con la asociatividad invertida) y se invierte el
  resultado intermedio.
* **Evaluación postfija:** se recorre de izquierda a derecha; los operandos se
  apilan y cada operador desapila dos valores (`pop` es el operando derecho,
  el siguiente `pop` es el izquierdo), calcula y vuelve a apilar el resultado.
* **Evaluación prefija:** igual, pero de derecha a izquierda; en este caso el
  primer `pop` es el operando **izquierdo** y el segundo el **derecho**.
* **Trazas:** cada paso registra el token procesado, la operación realizada, el
  valor calculado y el contenido de la pila (con la **cima a la izquierda**), lo
  que se muestra en el panel *Detalle del proceso* de la interfaz y se archiva en
  las evidencias.

---

## 7. Pruebas unitarias

`py pruebas.py` (o `py main.py --pruebas`) ejecuta **59 pruebas** distribuidas en
8 clases:

| Clase                      | Qué valida                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `TestPilaDinamica`       | La clase`Nodo` y la pila LIFO: pila nueva vacía, `push` en la cima, orden LIFO en `pop`, `pop`/`peek` sobre pila vacía, `peek` no modifica, `limpiar`, iteración/representación y crecimiento dinámico (1000 elementos).                                                                                                                                                                                                           |
| `TestTokenizacion`       | Modo compacto (un carácter = un token), modo con espacios (números y variables de varios caracteres), normalización de números,`-` unario, el `+` siempre operador, expresión vacía y caracteres inválidos.                                                                                                                                                                                                                                |
| `TestValidacion`         | Paréntesis desbalanceados/vacíos/de cierre sin apertura, falta de operador entre operandos, operador sin operando izquierdo, expresión incompleta (infija, postfija y prefija), operandos sobrantes, división y módulo por cero, símbolos no numéricos y sugerencia cuando la notación está cambiada.                                                                                                                                        |
| `TestConversiones`       | Ejemplos del taller, precedencia y paréntesis, asociatividad izquierda y derecha de`^` (2^3^2), tokens y presentación (compacta/espaciada) y que la traza documente el uso de la pila.                                                                                                                                                                                                                                                            |
| `TestEvaluacionPostfija` | Casos del taller (23+4*), expresiones con espacios, un solo operando, operandos negativos y presencia del estado de la pila en la traza.                                                                                                                                                                                                                                                                                                              |
| `TestEvaluacionPrefija`  | Casos del taller (*+234), expresiones con espacios y un solo operando.                                                                                                                                                                                                                                                                                                                                                                                |
| `TestConsistencia`       | Contraste de los resultados con`eval()` de Python, `es_infija_valida`, `notacion_polaca` y evaluación de la conversión de un ejemplo del taller.                                                                                                                                                                                                                                                                                              |
| `TestInterfazGrafica`    | La ventana de Tkinter**sin abrir `mainloop()`** (`VentanaTaller(usar_dialogos=False)`): *Convertir a postfijo* (`(A+B)*C` → `AB+C*` / `*+ABC`), *Evaluar postfijo* (`23+4*` = `20` con sus operaciones), *Evaluar prefijo* (`*+234` = `20`), error de sintaxis (`(A+B*` → "desbalanceados"), error de cálculo sin sugerir cambio de notación (`5 0 /` → división por cero, notación correcta) y *Limpiar*. |

> Las 6 pruebas de la interfaz se **omiten automáticamente** (`skipUnless`) en
> entornos sin pantalla (por ejemplo un servidor sin escritorio); en Windows se
> ejecutan las 59.

Resultado esperado (y obtenido):

```
Ran 59 tests in 1.681s
OK
Pruebas ejecutadas : 59
Errores            : 0
Fallos             : 0
Omitidas           : 0
Resultado          : TODAS LAS PRUEBAS PASARON
```

---

## 8. Evidencias (`evidencias/`)

Se generan con `py main.py --capturas` (o `py capturas.py`).

### Capturas de la interfaz gráfica (PNG)

| Archivo                                 | Situación que documenta                                                                                                                                                                         |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `01_interfaz_inicial.png`             | Ventana recién abierta, con el mensaje de bienvenida.                                                                                                                                           |
| `02_conversion_postfija.png`          | Conversión de`(A+B)*C` → `AB+C*` con la traza del Shunting Yard.                                                                                                                           |
| `03_conversion_prefija.png`           | Conversión de`(A+B)*(C-D)` → `*+AB-CD` con la traza completa.                                                                                                                              |
| `04_precedencia_y_asociatividad.png`  | `A+B*C-D/E^F` → `ABC*+DEF^/-` (precedencia de `*`, `/` y `^`).                                                                                                                        |
| `05_evaluacion_postfija.png`          | Evaluación de`23+4*` = `20` con las operaciones paso a paso.                                                                                                                                |
| `06_evaluacion_prefija.png`           | Evaluación de`*+234` = `20` con la pila de operandos.                                                                                                                                       |
| `07_evaluacion_postfija_compleja.png` | Evaluación de`23*45*+` = `26` (tres operaciones).                                                                                                                                           |
| `08_error_parentesis.png`             | Error`(A+B*`: paréntesis sin cerrar.                                                                                                                                                          |
| `09_error_operador.png`               | Error`+A`: operador sin operando izquierdo.                                                                                                                                                    |
| `10_error_expresion_incompleta.png`   | Error`2 3 + 4`: operandos sobrantes en postfija.                                                                                                                                               |
| `11_error_division_por_cero.png`      | Error de cálculo al pulsar*Evaluar postfijo* con `5 0 /`: `Error aritmético: división por cero.`, aclarando que la notación postfija es correcta y el problema está en los operandos. |
| `12_ayuda_sintaxis.png`               | Ventana con la ayuda de sintaxis de operadores y modos de escritura.                                                                                                                             |

### Evidencias de texto

| Archivo                      | Contenido                                                                                                              |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `informe_pruebas.txt`      | Informe completo de`unittest` con las 59 pruebas y el resumen (0 errores, 0 fallos, 0 omitidas).                     |
| `demostracion_consola.txt` | Salida de`py main.py --demo`: conversiones, evaluaciones postfija/prefija y expresiones inválidas con sus mensajes. |
| `tabla_conversiones.txt`   | Tabla infija → postfija/prefija → valor → operaciones de 5 ejemplos.                                                |
| `trazas_paso_a_paso.txt`   | Trazas completas (estado de la pila en cada paso) de`(A+B)*C`, `(2+3)*4`, `23+4*` y `*+234`.                   |

---

## 9. Decisiones de diseño y limitaciones

* **Separación lógica / interfaz:** `expresiones.py` y `pila.py` no dependen de
  Tkinter, por lo que se pueden probar y usar por consola (lo hace `--demo`).
  `interfaz.py` sólo presenta resultados y captura `ErrorExpresion`.
* **Pilas reales, no listas:** los algoritmos sólo usan `Pila.push/pop/peek/ esta_vacia`; las listas de Python se emplean únicamente para guardar la
  secuencia de salida y las cadenas de la traza.
* **Dos modos de tokenización:** el modo compacto permite reproducir literalmente
  los ejemplos del taller (`23+4*` = 20), mientras que el modo con espacios cubre
  el caso general (números de varios dígitos y variables multiletra).
* **Limitaciones conocidas:**
  * La evaluación numérica requiere que **todos** los operandos sean números
    (`int`, `float` o notación exponencial); las variables sólo se pueden
    convertir, no evaluar.
  * No se admite el menos unario delante de paréntesis ni de variables
    (`-(A+B)`), sólo pegado a un número.
  * La división y el módulo usan la semántica de Python (`%` y `//`-estilo de
    signo); la potencia `^` se implementa con `**`.
  * Las capturas PNG requieren Pillow y un entorno con escritorio (Windows);
    sin Pillow, el programa genera igualmente las cuatro evidencias de texto.
  * Las 6 pruebas de `TestInterfazGrafica` necesitan una pantalla; en un entorno
    sin escritorio `unittest` las marca como **omitidas** y las otras 53 pruebas
    siguen ejecutándose con normalidad.

---

## 10. Verificación rápida

```powershell
py main.py --pruebas     # debe terminar con "TODAS LAS PRUEBAS PASARON"
py main.py --demo        # debe mostrar las tablas de conversión y evaluación
py main.py               # abre la interfaz; pruebe con (A+B)*C y con 23+4*
```

---

## 11. Cumplimiento de la rúbrica del taller

La rúbrica del enunciado (*TALLER 1 de Pilas Dinamicas.pdf*, páginas 4–5) evalúa
7 criterios sobre 100 %: **Funcionalidad del programa (25 %)**,
**Implementación de pilas dinámicas (20 %)**, **Conversión de expresiones (15 %)**,
**Evaluación de expresiones (15 %)**, **Estructura y organización del código
(10 %)**, **Interfaz gráfica de usuario (10 %)** y **Pruebas y validaciones (5 %)**.

| Criterio (peso)                               | Nivel alcanzado                                                                                                                                    | Evidencia en el proyecto                                                                                                                                                                                                                                              |
| --------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Funcionalidad del programa (25 %)             | **Superior**: convierte y evalúa correctamente los casos del taller y casos complejos, con resultados precisos y consistentes.              | `(A+B)*C` → `AB+C*` / `*+ABC` (§5.1), `23+4*` = `20` y `*+234` = `20` (§5.2), `py main.py --demo`, capturas `02`–`07`.                                                                                                                        |
| Implementación de pilas dinámicas (20 %)    | **Superior**: pila dinámica robusta, modular y eficiente con listas enlazadas, usando correctamente la clase `Nodo`.                      | `pila.py` (`Nodo`, `Pila`, `push`, `pop`, `peek`, `esta_vacia`, `limpiar`), complejidades O(1)/O(n) (§6.1), `TestPilaDinamica` (pila de 1000 nodos) y verificación de pila vacía antes de cada `pop` (`expresiones.py`, `_sacar_de_pila`). |
| Conversión de expresiones (15 %)             | **Superior**: precedencia, asociatividad (incluida la de la derecha en `^`) y validaciones completas.                                      | Shunting Yard (§6.3),`2^3^2` → `232^^`, `A%B%C` → `AB%C%`, `(A+B)*(C-D)` → `AB+CD-*` / `*+AB-CD`, clase `TestConversiones`.                                                                                                                       |
| Evaluación de expresiones (15 %)             | **Superior**: muestra de forma clara las operaciones realizadas y el resultado final, con traza de la pila paso a paso.                      | Lista`Evaluacion.operaciones` (`2 + 3 = 5`; `5 * 4 = 20`), `RESULTADO FINAL: 20`, `evidencias/trazas_paso_a_paso.txt`, capturas `05`–`07`.                                                                                                             |
| Estructura y organización del código (10 %) | **Superior**: código limpio, reutilizable y documentado, con POO y separación entre lógica e interfaz.                                    | Seis módulos con responsabilidad única, docstrings, type hints,`__all__`, `PilaVaciaError`, 59 pruebas automatizadas, §6 y §9.                                                                                                                                |
| Interfaz gráfica de usuario (10 %)           | **Superior**: intuitiva, amigable y organizada; muestra conversiones, evaluaciones y mensajes de error diferenciados (sintaxis vs cálculo). | `interfaz.py` (campo de entrada, los 4 botones exigidos + *Limpiar* + *Ayuda / Sintaxis*), panel *Detalle del proceso*, §5.3 y capturas `08`–`12`.                                                                                                      |
| Pruebas y validaciones (5 %)                  | **Superior**: pruebas exhaustivas y documentadas con expresiones complejas, manejo de errores y validaciones completas.                      | 59 pruebas en 8 clases (§7),`evidencias/informe_pruebas.txt`, contraste con `eval()` de Python y validación de `(A+B*`, `+A`, `2 3 + 4`, `*+23`, `5 0 /`.                                                                                             |

### 11.1 Entregables exigidos por el taller

| Entregable (PDF, p. 4)   | Dónde está                                                                                   |
| ------------------------ | ---------------------------------------------------------------------------------------------- |
| Código fuente completo  | `pila.py`, `expresiones.py`, `interfaz.py`, `pruebas.py`, `capturas.py`, `main.py` |
| Capturas de ejecución   | `evidencias/01..12` (12 archivos PNG)                                                        |
| Evidencia de pruebas     | `evidencias/informe_pruebas.txt` (+ 3 archivos TXT de apoyo)                                 |
| Análisis de complejidad | §6 de este README y los docstrings de`pila.py` y `expresiones.py`                         |

### 11.2 Casos de prueba exigidos por el taller

| Caso del PDF              | Dónde se demuestra                                                                          |
| ------------------------- | -------------------------------------------------------------------------------------------- |
| `(A+B)*C` (válida)     | `TestConversiones` y `TestInterfazGrafica`, captura `02_conversion_postfija.png`       |
| `(A+B)*(C-D)` (válida) | `TestConversiones`, captura `03_conversion_prefija.png`                                  |
| `(A+B*` (inválida)     | `TestValidacion` y `TestInterfazGrafica`, captura `08_error_parentesis.png`            |
| `+A` (inválida)        | `TestValidacion`, captura `09_error_operador.png`                                        |
| `23+4*` (evaluación)   | `TestEvaluacionPostfija` y `TestInterfazGrafica`, captura `05_evaluacion_postfija.png` |
| `*+234` (evaluación)   | `TestEvaluacionPrefija` y `TestInterfazGrafica`, captura `06_evaluacion_prefija.png`   |

Además de los casos del taller, el programa detecta operadores inválidos
(`A & B`), expresiones incompletas (`2 3 + 4`, `*+23`), paréntesis
desbalanceados (`(A+B*`) y la pila vacía antes de operar (probado en
`TestPilaDinamica` y verificado dentro de los algoritmos).
