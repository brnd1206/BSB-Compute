import multiprocessing
import time
import queue
import random
import copy
import json
import os
from dataclasses import dataclass
from enum import Enum

ESCALA_TEMPO = 0.2  # Acelerador de tempo para simulação

class Politica(Enum):
    ROUND_ROBIN = 1
    SJF = 2
    PRIORIDADE = 3

@dataclass
class Tarefa:
    """Representa uma unidade de trabalho (inferência)"""
    id: int
    tipo: str
    prioridade: int
    tempo_exec: int
    chegada: float

@dataclass
class InfoServidor:
    """Metadados do servidor para o Orquestrador"""
    id: int
    capacidade: int
    fila: multiprocessing.Queue