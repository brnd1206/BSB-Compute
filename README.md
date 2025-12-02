# 💻 BSB Compute - Orquestrador de Tarefas Distribuídas

![Python](https://img.shields.io/badge/PYTHON-3.8%2B-blue?style=for-the-badge)

---

## 📄 Sobre o Projeto

O **BSB Compute** é um software de simulação que atua como um orquestrador de tarefas para um cluster de inferência de Inteligência Artificial.

O foco principal deste projeto está na **aplicação prática de conceitos de SO**, como multiprocessamento, comunicação entre processos (IPC) e algoritmos de escalonamento de CPU, simulando um ambiente de alta demanda computacional.

### Objetivos Principais

* Simulação de uma arquitetura **Master-Slave** utilizando processos reais e independentes.
* Implementação de comunicação via filas (Queues) para troca de mensagens sem bloqueios (IPC).
* Comparação automática de desempenho entre diferentes políticas de escalonamento.
* Geração de relatórios técnicos de *throughput* e latência.

---

## 🛠️ Tecnologias Utilizadas

Este projeto foi construído utilizando as seguintes tecnologias:

* **Linguagem:** Python 3.8+
* **Bibliotecas:** Multiprocessing, Queue, Time, Random, Json
* **Arquitetura:** Produtor-Consumidor (Master/Workers)
* **Versionamento:** Git & GitHub

---

## ✨ Funcionalidades

O sistema BSB Compute oferece as seguintes funcionalidades principais:

1.  **Escalonamento Inteligente:** Suporte nativo aos algoritmos Round Robin (RR), Shortest Job First (SJF) e Prioridade.
2.  **Auto-Otimização:** O sistema executa uma pré-análise silenciosa dos algoritmos e seleciona automaticamente o mais eficiente para a carga de trabalho atual.
3.  **Simulação Visual em Tempo Real:** Exibe logs detalhados no terminal indicando chegada, atribuição e conclusão de tarefas (ex: `[00:05s] Tarefa 101 atribuída ao Servidor 1`).
4.  **Relatórios de Métricas:** Ao final da execução, gera estatísticas precisas sobre uso de CPU, tempo médio de resposta e vazão do sistema (throughput) .

---

## 📚 Manual de Instruções

### 1. Instalação e Pré-requisitos

Não é necessário instalar bibliotecas externas via `pip`, pois o projeto utiliza apenas bibliotecas padrão do Python.

1.  **Verifique o Python:**
    Abra seu terminal e digite:
    ```bash
    python --version
    ```
    *Deve ser exibida a versão 3.8 ou superior.*

2.  **Clone o Repositório:**
    ```bash
    git clone https://github.com/brnd1206/BSB-Compute.git
    cd BSB-Compute-main
    ```

### 2. Executando o Simulador

Para iniciar a orquestração, execute o comando:

```bash
python bsb_compute_app.py
```

---

## 📖 Fluxo de Execução (Casos de Uso)

Abaixo descrevemos o comportamento do sistema durante uma execução padrão.

| ID | Etapa | Ação do Sistema | Resultado Visual |
|----|-------------|----------------|----------|
| **E01** | **Análise Comparativa** | O sistema testa virtualmente os 3 algoritmos (RR, SJF, Prio) em background. | O usuário aguarda o cálculo das métricas. |
| **E02** | **Tomada de Decisão** | O sistema compara os tempos médios e escolhe o melhor algoritmo. | Uma tabela é exibida no terminal anunciando o vencedor. |
| **E03** | **Simulação Real** | O orquestrador inicia os processos *Workers* e distribui as tarefas. | Logs aparecem em tempo real mostrando a distribuição de carga. |
| **E04** | **Relatório Técnico** | O sistema consolida os dados da execução. | Exibição final das métricas de desempenho e encerramento. |

---

## 🤝 Contribuição

Sinta-se à vontade para contribuir! Se tiver sugestões ou quiser reportar bugs, abra uma *Issue* ou envie um *Pull Request*.

---

## 👨‍💻 Autores

| **Bernardo de Carvalho Leite** |
| https://github.com/brnd1206 |

| **Bernardo dos Santos Gomes** |
| https://github.com/bernardosgomes |
