# -*- coding: utf-8 -*-
"""
pila.py
=======
Estructura de datos dinámica del Taller 1: **Pila (LIFO) implementada con
listas enlazadas simples** a partir de la clase `Nodo` estudiada en clase.

El taller exige que la conversión y evaluación de expresiones use pilas
dinámicas (no listas de Python) y que se implementen obligatoriamente las
operaciones fundamentales `push()`, `pop()` y la verificación de pila vacía.

Complejidad de las operaciones
------------------------------
+--------------+----------+-------------------+
| Operación    | Tiempo   | Memoria adicional |
+==============+==========+===================+
| push()       | O(1)     | O(1)              |
| pop()        | O(1)     | O(1)              |
| peek()       | O(1)     | O(1)              |
| esta_vacia() | O(1)     | O(1)              |
| limpiar()    | O(n)     | O(1)              |
| __iter__()   | O(n)     | O(1)              |
+--------------+----------+-------------------+
"""

from __future__ import annotations

from typing import Any, Iterator, List, Optional

__all__ = ["Nodo", "Pila", "PilaVaciaError"]


class PilaVaciaError(Exception):
    """Error lanzado al intentar `pop()` o `peek()` sobre una pila vacía."""


class Nodo:
    """
    Nodo de la lista enlazada simple que soporta la pila.

    Atributos:
        dato: valor almacenado (número, operador, letra, etc.).
        siguiente: referencia al nodo que quedó debajo en la pila (o None).
    """

    __slots__ = ("dato", "siguiente")

    def __init__(self, dato: Any = None, siguiente: Optional["Nodo"] = None) -> None:
        self.dato = dato
        self.siguiente = siguiente

    def __str__(self) -> str:
        return str(self.dato)

    def __repr__(self) -> str:
        return f"Nodo({self.dato!r})"


class Pila:
    """
    Pila dinámica LIFO construida con una lista enlazada simple.

    La cima de la pila es siempre `self.cima` (el primer nodo); cada nodo
    apunta al nodo que está debajo y el último nodo apunta a `None`.
    La pila crece y decrece según la demanda, por eso es *dinámica*.

    En las representaciones de texto (`__str__`, `a_lista()`) la cima se
    muestra a la **izquierda**: `[cima, ..., base]`.
    """

    def __init__(self) -> None:
        self.cima: Optional[Nodo] = None
        self.tamanio: int = 0

    # ------------------------------------------------------------------
    # Operaciones fundamentales
    # ------------------------------------------------------------------
    def esta_vacia(self) -> bool:
        """Devuelve True si la pila no tiene elementos. Complejidad O(1)."""
        return self.cima is None

    def push(self, dato: Any) -> None:
        """
        Inserta `dato` en la cima de la pila (agrega un nodo al inicio de la
        lista enlazada). Complejidad O(1).
        """
        nuevo = Nodo(dato, self.cima)
        self.cima = nuevo
        self.tamanio += 1

    def pop(self) -> Any:
        """
        Elimina y devuelve el dato que está en la cima. Complejidad O(1).

        Lanza `PilaVaciaError` si la pila está vacía, por lo que siempre se
        debe verificar previamente con `esta_vacia()`.
        """
        if self.cima is None:
            raise PilaVaciaError("pop(): no se puede desapilar de una pila vacía.")
        nodo = self.cima
        self.cima = nodo.siguiente
        nodo.siguiente = None  # ayuda al recolector de basura
        self.tamanio -= 1
        return nodo.dato

    def peek(self) -> Any:
        """
        Devuelve el dato de la cima sin eliminarlo. Complejidad O(1).

        Lanza `PilaVaciaError` si la pila está vacía.
        """
        if self.cima is None:
            raise PilaVaciaError("peek(): no hay elementos en la pila.")
        return self.cima.dato

    # Nombre alterno usado en algunos apuntes de clase.
    def cima_dato(self) -> Any:
        """Sinónimo de `peek()`."""
        return self.peek()

    def limpiar(self) -> None:
        """Vacía la pila liberando los nodos uno por uno. Complejidad O(n)."""
        while self.cima is not None:
            nodo = self.cima
            self.cima = nodo.siguiente
            nodo.siguiente = None
        self.tamanio = 0

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------
    def a_lista(self) -> List[Any]:
        """Devuelve los datos en una lista Python, de la cima a la base."""
        return list(self)          # el iterador ya recorre de la cima a la base

    def tamano(self) -> int:
        """Cantidad de elementos almacenados. Complejidad O(1)."""
        return self.tamanio

    def __iter__(self) -> Iterator[Any]:
        """Recorre la pila de la cima hacia la base (no la modifica)."""
        actual = self.cima
        while actual is not None:
            yield actual.dato
            actual = actual.siguiente

    def __len__(self) -> int:
        return self.tamanio

    def __bool__(self) -> bool:
        # Ojo: una pila con elementos es True; vacía es False.
        return self.cima is not None

    def __contains__(self, dato: Any) -> bool:
        return any(elemento == dato for elemento in self)

    def __str__(self) -> str:
        """Representación con la cima a la izquierda: [cima, ..., base]."""
        return "[" + ", ".join(str(elemento) for elemento in self) + "]"

    def __repr__(self) -> str:
        return f"Pila({self.a_lista()})"
