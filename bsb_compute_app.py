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

def processo_servidor(id_servidor, capacidade, fila_tarefas, fila_resultados):
    """
    Loop principal do processo Worker.
    Simula o processamento e reporta ao pai via IPC.
    """
    tempo_ocupado = 0
    inicio_log = time.time()

    while True:
        try:
            # Tenta pegar tarefa com timeout curto para não travar desligamento
            tarefa = fila_tarefas.get(timeout=0.05)

            if tarefa == "PARAR":
                break

            # Simula tempo de execução: Tempo Base / Capacidade do Servidor
            tempo_execucao_real = tarefa.tempo_exec / capacidade

            # Sleep para simular o trabalho
            time.sleep(tempo_execucao_real * ESCALA_TEMPO)

            tempo_ocupado += tempo_execucao_real

            # IPC: Envia resultado para o processo pai
            fila_resultados.put({
                "id_servidor": id_servidor,
                "id_tarefa": tarefa.id,
                "tempo_exec": tempo_execucao_real,
                "prioridade": tarefa.prioridade,
                "chegada_original": tarefa.chegada,
                "status": "concluido"
            })

        except queue.Empty:
            continue

    # Ao encerrar, reporta uso de CPU
    tempo_total = (time.time() - inicio_log) / ESCALA_TEMPO
    pct_uso = (tempo_ocupado / tempo_total) * 100 if tempo_total > 0 else 0
    fila_resultados.put({"id_servidor": id_servidor, "status": "desligado", "uso": pct_uso})