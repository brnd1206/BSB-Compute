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

class Orquestrador:
    def __init__(self, dados_servidores, dados_tarefas, politica, modo_silencioso=False):
        self.politica = politica
        self.modo_silencioso = modo_silencioso
        self.fila_resultados = multiprocessing.Queue()
        self.servidores = []
        self.tarefas_pendentes = []

        # Prepara tarefas com tempos de chegada aleatórios
        tempo_atual = time.time()
        for t in dados_tarefas:
            atraso_chegada = random.uniform(0, 3) # Simula chegada dinâmica
            self.tarefas_pendentes.append(Tarefa(
                id=t['id'],
                tipo=t['tipo'],
                prioridade=t['prioridade'],
                tempo_exec=t['tempo_exec'],
                chegada=tempo_atual + atraso_chegada
            ))

        # Ordena inicial por chegada
        self.tarefas_pendentes.sort(key=lambda x: x.chegada)

        # Inicializa Processos (Workers)
        self.processos = []
        for s in dados_servidores:
            q = multiprocessing.Queue()
            p = multiprocessing.Process(
                target=processo_servidor,
                args=(s['id'], s['capacidade'], q, self.fila_resultados)
            )
            self.servidores.append(InfoServidor(s['id'], s['capacidade'], q))
            self.processos.append(p)
            p.start()

        if not self.modo_silencioso:
            print(f"--- BSB Compute: Iniciando Simulação Real ({self.politica.name}) ---")

    def _log(self, mensagem):
        if not self.modo_silencioso:
            print(mensagem)

    def _obter_tempo(self, inicio):
        decorrido = (time.time() - inicio) / ESCALA_TEMPO
        return f"{decorrido:05.2f}s"
    
    def executar(self):
        inicio_simulacao = time.time()
        tarefas_concluidas = 0
        total_tarefas = len(self.tarefas_pendentes)
        indice_rr = 0 # Para Round Robin

        fila_espera = []
        stats_servidor = {s.id: {"tarefas": 0, "uso": 0} for s in self.servidores}
        tempos_resposta = []

        # Loop Principal da Simulação
        while tarefas_concluidas < total_tarefas or len(fila_espera) > 0:
            tempo_real_atual = time.time()

            # 1. Verifica novas chegadas
            while self.tarefas_pendentes and self.tarefas_pendentes[0].chegada <= tempo_real_atual:
                tarefa = self.tarefas_pendentes.pop(0)
                fila_espera.append(tarefa)
                prio_txt = "Alta" if tarefa.prioridade == 1 else "Média" if tarefa.prioridade == 2 else "Baixa"
                self._log(f"[{self._obter_tempo(inicio_simulacao)}] Nova Requisição {tarefa.id} ({prio_txt}) chegou na fila.")

            # 2. Escalonamento (Scheduler)
            if fila_espera:
                # Aplica política de ordenação na fila de prontos
                if self.politica == Politica.SJF:
                    fila_espera.sort(key=lambda x: x.tempo_exec)
                elif self.politica == Politica.PRIORIDADE:
                    fila_espera.sort(key=lambda x: x.prioridade)
                # Round Robin não ordena, apenas pega o próximo (FIFO)

                # Distribui para o próximo servidor (Balanceamento Cíclico)
                servidor_alvo = self.servidores[indice_rr]
                indice_rr = (indice_rr + 1) % len(self.servidores)

                tarefa_para_executar = fila_espera.pop(0)
                servidor_alvo.fila.put(tarefa_para_executar) # Envia via IPC

                prio_txt = "Alta" if tarefa_para_executar.prioridade == 1 else "Baixa" if tarefa_para_executar.prioridade == 3 else "Média"
                self._log(f"[{self._obter_tempo(inicio_simulacao)}] Requisição {tarefa_para_executar.id} ({prio_txt}) atribuída ao Servidor {servidor_alvo.id}")

            # 3. Verifica conclusões (Non-blocking)
            try:
                while True:
                    resultado = self.fila_resultados.get_nowait()

                    if resultado['status'] == 'concluido':
                        tarefas_concluidas += 1
                        stats_servidor[resultado['id_servidor']]['tarefas'] += 1
                        
                        momento_conclusao = time.time()
                        tempo_sistema = (momento_conclusao - resultado['chegada_original']) / ESCALA_TEMPO
                        tempos_resposta.append(tempo_sistema)

                        self._log(f"[{self._obter_tempo(inicio_simulacao)}] Servidor {resultado['id_servidor']} concluiu Requisição {resultado['id_tarefa']}")

                    elif resultado['status'] == 'desligado':
                        stats_servidor[resultado['id_servidor']]['uso'] = resultado['uso']
            except queue.Empty:
                pass

            time.sleep(0.05) # Evita busy waiting excessivo

        # Fim do loop: Encerramento
        duracao = (time.time() - inicio_simulacao) / ESCALA_TEMPO
        
        # Poison Pill para desligar servidores
        for s in self.servidores:
            s.fila.put("PARAR")
            
        # Coleta estatísticas finais dos workers
        workers_ativos = len(self.processos)
        while workers_ativos > 0:
            res = self.fila_resultados.get()
            if res['status'] == 'desligado':
                stats_servidor[res['id_servidor']]['uso'] = res['uso']
                workers_ativos -= 1

        for p in self.processos:
            p.join()

        if not self.modo_silencioso:
            self._imprimir_relatorio_final(duracao, tempos_resposta, stats_servidor, total_tarefas)

        tempo_medio = sum(tempos_resposta) / len(tempos_resposta) if tempos_resposta else 0
        throughput = total_tarefas / duracao if duracao > 0 else 0
        return {"tempo_medio": tempo_medio, "throughput": throughput}

    def _imprimir_relatorio_final(self, duracao, tempos_resposta, stats_servidor, total_tarefas):
        tempo_medio = sum(tempos_resposta) / len(tempos_resposta) if tempos_resposta else 0
        media_cpu = sum(s['uso'] for s in stats_servidor.values()) / len(stats_servidor)
        espera_max = max(tempos_resposta) if tempos_resposta else 0

        print("\n" + "=" * 40)
        print("RESUMO FINAL (Relatório Técnico)")
        print("=" * 40)
        print(f"Tempo médio de resposta: {tempo_medio:.2f}s")
        print(f"Utilização média da CPU: {media_cpu:.1f}%")
        print(f"Taxa de espera máxima: {espera_max:.2f}s")
        print(f"Throughput: {total_tarefas / duracao:.2f} tarefas/segundo")
        print("-" * 40)
        print("Detalhamento por Nó:")
        for sid, stats in stats_servidor.items():
            print(f"Servidor {sid}: {stats['tarefas']} tarefas proc. | Carga CPU: {stats['uso']:.1f}%")
        print("=" * 40)