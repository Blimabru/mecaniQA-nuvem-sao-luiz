"""
================================================================================
MecâniQA Tech - Simulador de Telemetria de Sensores IoT Automotivos
Módulo: OAT 2 - Monitoramento, Observabilidade e Continuidade de Negócios
================================================================================

Descrição:
    Este microserviço simula o envio contínuo de telemetria de sensores
    automotivos (temperatura do motor, vibração mecânica e pressão do óleo),
    expondo métricas no formato padrão OpenMetrics/Prometheus para coleta (scrape)
    e provendo um endpoint de integridade operacional (Health Check).

Arquitetura de Observabilidade:
    - Prometheus Scrape Endpoint: Porta TCP 8000, caminho /metrics
    - Health Check Endpoint: Porta TCP 8000, caminho /health
    - Mecanismo de Injeção de Falhas Sintéticas: Variável SENSOR_ERROR_RATE
================================================================================
"""

import json
import os
import random
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Tuple

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, generate_latest

# ==============================================================================
# CONFIGURAÇÕES OPERACIONAIS VIA VARIÁVEIS DE AMBIENTE
# ==============================================================================
# Nome identificador do microserviço no ecossistema
SERVICE_NAME: str = os.getenv("SERVICE_NAME", "sensor-simulator")

# Porta TCP em que o servidor HTTP atenderá as requisições
PORT: int = int(os.getenv("PORT", "8000"))

# Taxa percentual configurada para geração de leituras com anomalia/erro (ex: 0.05 = 5%)
ERROR_RATE: float = float(os.getenv("SENSOR_ERROR_RATE", "0.05"))

# Intervalo em segundos entre as emissões sintéticas de telemetria
INTERVAL_SECONDS: float = float(os.getenv("SENSOR_INTERVAL_SECONDS", "2"))

# ==============================================================================
# DEFINIÇÃO DE MÉTRICAS INSTRUMENTADAS (PROMETHEUS)
# ==============================================================================

# Métrica do tipo Gauge: Registra o valor instantâneo da temperatura do motor em Celsius.
# Faixa nominal: 72.0°C a 98.0°C | Faixa de anomalia: 105.0°C a 130.0°C
TEMPERATURE = Gauge(
    "sensor_temperature_celsius",
    "Leitura instantanea da temperatura do motor do veiculo em graus Celsius.",
    labelnames=("sensor",),
)

# Métrica do tipo Gauge: Registra a intensidade da vibração mecânica em mm/s.
# Faixa nominal: 0.5 a 1.8 mm/s | Faixa de anomalia: 2.2 a 4.0 mm/s
VIBRATION = Gauge(
    "sensor_vibration_mm_s",
    "Leitura instantanea da vibracao mecanica do motor em milimetros por segundo.",
    labelnames=("sensor",),
)

# Métrica do tipo Gauge: Registra a pressão do sistema de lubrificação em kPa.
# Faixa nominal: 30.0 a 35.0 kPa | Faixa de anomalia: 38.0 a 52.0 kPa
PRESSURE = Gauge(
    "sensor_pressure_kpa",
    "Leitura instantanea da pressao do sistema automotivo em kilopascal.",
    labelnames=("sensor",),
)

# Métrica do tipo Gauge: Estado binário de integridade do sensor (1 = Operacional / 0 = Falha).
HEALTH = Gauge(
    "sensor_health",
    "Estado de saude operacional do sensor (1 = Saudavel/Normal, 0 = Falha/Anomalia).",
    labelnames=("sensor",),
)

# Métrica do tipo Gauge: Exposição da taxa nominal configurada de erro sintético.
ERROR_RATE_GAUGE = Gauge(
    "sensor_error_rate",
    "Taxa nominal configurada de falhas sinteticas aplicadas ao simulador de sensores.",
    labelnames=("sensor",),
)

# Métrica do tipo Counter: Contador cumulativo e monotônico crescente de leituras.
# Particionado por rótulos (labels) 'sensor' e 'status' ('ok' ou 'error').
# Permite o cálculo em tempo real das taxas de sucesso e erro através de funções rate().
READINGS_TOTAL = Counter(
    "sensor_readings_total",
    "Numero cumulativo de leituras de telemetria processadas pelo simulador.",
    labelnames=("sensor", "status"),
)


# ==============================================================================
# LÓGICA DE SIMULAÇÃO DE TELEMETRIA E INJEÇÃO DE ANOMALIAS
# ==============================================================================
def emit_reading() -> None:
    """
    Gera uma amostra de telemetria sintética para o sensor especificado.
    
    A função calcula valores estocásticos dentro de faixas normais ou anômalas,
    baseando-se na probabilidade definida por ERROR_RATE. Em seguida, atualiza
    os Gauges instantâneos e incrementa o Counter de telemetria com o status correspondente.
    """
    sensor_name = "motor-01"
    
    # Avaliação probabilística para determinação de falha/anomalia
    should_error = random.random() < ERROR_RATE

    if should_error:
        # Padrões de telemetria em condição de anomalia mecânica/térmica
        temperature_value = random.uniform(105.0, 130.0)
        vibration_value = random.uniform(2.2, 4.0)
        pressure_value = random.uniform(38.0, 52.0)
        status = "error"
        HEALTH.labels(sensor_name).set(0)
    else:
        # Padrões de telemetria em regime normal de funcionamento
        temperature_value = random.uniform(72.0, 98.0)
        vibration_value = random.uniform(0.5, 1.8)
        pressure_value = random.uniform(30.0, 35.0)
        status = "ok"
        HEALTH.labels(sensor_name).set(1)

    # Atualização das séries temporais no registro Prometheus
    TEMPERATURE.labels(sensor_name).set(temperature_value)
    VIBRATION.labels(sensor_name).set(vibration_value)
    PRESSURE.labels(sensor_name).set(pressure_value)
    ERROR_RATE_GAUGE.labels(sensor_name).set(ERROR_RATE)
    
    # Incremento do contador com label de status (essencial para SLI de taxa de erro)
    READINGS_TOTAL.labels(sensor_name, status).inc()


# ==============================================================================
# MANIPULADOR DE REQUISIÇÕES HTTP (HTTP REQUEST HANDLER)
# ==============================================================================
class SensorHandler(BaseHTTPRequestHandler):
    """
    Manipulador HTTP responsável por rotear as chamadas aos endpoints
    de serviço, integridade (/health) e telemetria Prometheus (/metrics).
    """

    def do_GET(self) -> None:
        """
        Trata as requisições GET encaminhadas pelos clientes e agentes de coleta.
        """
        # Endpoint raiz (/): Retorna mensagem básica de identificação do serviço
        if self.path in ("/", ""):
            payload = {
                "status": "UP",
                "service": SERVICE_NAME,
                "message": "Simulador de sensores automotivos da MecâniQA Tech em execucao.",
            }
            self._send_json_response(200, payload)
            return

        # Endpoint de Liveness e Readiness Probe (/health):
        # Utilizado pelo Kubernetes para verificar se o contêiner está saudável e apto a receber tráfego
        if self.path == "/health":
            payload = {
                "status": "UP",
                "service": SERVICE_NAME,
                "error_rate": ERROR_RATE,
                "interval_seconds": INTERVAL_SECONDS,
                "port": PORT,
            }
            self._send_json_response(200, payload)
            return

        # Endpoint de Coleta de Métricas (/metrics):
        # Raspado periodicamente pelo coletor Prometheus (scrape_interval: 15s)
        if self.path == "/metrics":
            payload = generate_latest()
            self.send_response(200)
            self.send_header("Content-Type", CONTENT_TYPE_LATEST)
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        # Resposta padrão para rotas não mapeadas (404 Not Found)
        self.send_response(404)
        self.end_headers()

    def _send_json_response(self, status_code: int, data: dict) -> None:
        """
        Método auxiliar para envio de respostas HTTP com payload JSON formatado.
        """
        body = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        """
        Sobrescreve a saída padrão de log HTTP para evitar poluição desnecessária
        nos logs operacionais do contêiner durante os testes contínuos de estresse.
        """
        return


# ==============================================================================
# ROTINA DO TRABALHADOR EM SEGUNDO PLANO (BACKGROUND WORKER)
# ==============================================================================
def background_worker() -> None:
    """
    Executa um laço contínuo em thread secundária (daemon) para emissão
    periódica das leituras de telemetria automotiva.
    """
    while True:
        emit_reading()
        time.sleep(INTERVAL_SECONDS)


# ==============================================================================
# PONTO DE ENTRADA PRINCIPAL (MAIN ENTRYPOINT)
# ==============================================================================
def run_server() -> None:
    """
    Inicializa o servidor HTTP na interface 0.0.0.0 e porta parametrizada.
    """
    server_address = ("0.0.0.0", PORT)
    server = HTTPServer(server_address, SensorHandler)
    print(f"[INFO] Simulador MecâniQA ativo e escutando em http://0.0.0.0:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("[INFO] Sinal de interrupção recebido. Encerrando servidor HTTP...")
        server.server_close()


if __name__ == "__main__":
    # Inicialização das métricas base para evitar inconsistências no primeiro scrape
    HEALTH.labels("motor-01").set(1)
    ERROR_RATE_GAUGE.labels("motor-01").set(ERROR_RATE)

    # Inicialização da thread produtora de telemetria em segundo plano
    telemetry_thread = threading.Thread(target=background_worker, daemon=True)
    telemetry_thread.start()

    # Execução do servidor HTTP na thread principal
    run_server()
