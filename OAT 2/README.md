# MecâniQA Tech — OAT 2: Monitoramento, Observabilidade e Continuidade de Negócios

Este repositório contém a entrega técnica completa da **OAT 2** da **MecâniQA Tech**, implementando uma arquitetura robusta de observabilidade, escalonamento dinâmico (HPA) e engenharia de continuidade operacional para suportar o tráfego massivo de sensores IoT automotivos gerado pelas oficinas mecânicas clientes.

---

## 1. Visão Geral da Arquitetura

O sistema elimina a "caixa preta" operacional por meio de instrumentação com métricas OpenMetrics/Prometheus, coleta automatizada via Kubernetes Service Discovery, painéis analíticos no Grafana estruturados sobre os **Golden Signals** e governança operacional baseada em **SRE/ITSM** (SLAs, SLOs, SLIs, RTO, RPO e Runbooks executáveis).

```
                      +---------------------------------------+
                      |         OFICINAS MECÂNICAS            |
                      |   Milhares de Sensores IoT Veiculares |
                      +---------------------------------------+
                                          |
                        Picos de Carga: 08:00 e 17:00
                                          v
                      +---------------------------------------+
                      |        Cluster Kubernetes (K8s)       |
                      |                                       |
                      |  +---------------------------------+  |
                      |  |     simulador-sensores (Pod)    |  |
                      |  |   - Python + prometheus_client  |  |
                      |  |   - /health (Probes)            |  |
                      |  |   - /metrics (Porta 8000)       |  |
                      |  +---------------------------------+  |
                      |             ^             |           |
                      |             |             | Scrape    |
           Escala HPA |             |             v (15s)     |
    (1 a 5 pods / v2) |  +-------------------+  +-----------+ |
                      |  |   Metrics Server  |  |Prometheus | |
                      |  |  (CPU 70%/Mem 80%)|  |TSDB (9090)| |
                      |  +-------------------+  +-----------+ |
                      |                               |       |
                      |                               v       |
                      |                         +-----------+ |
                      |                         |  Grafana  | |
                      |                         |Auto-prov. | |
                      |                         +-----------+ |
                      +---------------------------------------+
                                          |
                                          v
                      +---------------------------------------+
                      |   DASHBOARDS & ALERTAS OPERACIONAIS   |
                      | - 4 Golden Signals (CPU, Mem, Err, OK)|
                      | - 4 Alarmes com contenção de 5 min    |
                      | - Runbooks de Resolução de Incidentes |
                      +---------------------------------------+
```

---

## 2. Catálogo de Componentes do Repositório

| Componente | Caminho | Descrição Técnica |
| :--- | :--- | :--- |
| **Aplicação Base** | `app/sensor_simulator.py` | Microserviço em Python instrumentado com `prometheus_client`. Emite telemetria veicular (temperatura, vibração, pressão, saúde e contadores particionados) e expõe `/metrics` e `/health`. |
| **Empacotamento** | `app/Dockerfile` | Imagem enxuta baseada em `python:3.12-slim` configurada para execução sem privilégios desnecessários. |
| **Dependências** | `app/requirements.txt` | Especificação de bibliotecas (`prometheus-client==0.21.1`). |
| **Serviço & Deployment** | `k8s/simulador-sensores.yaml` | Deployment resiliente com probes HTTP de liveness e readiness, requests/limits computacionais rigorosos e anotações de auto-descoberta. |
| **Servidor Prometheus** | `k8s/prometheus.yaml` | Implantação do Prometheus v2.55.1 com RBAC (ServiceAccount, ClusterRole, Binding), Service Discovery de endpoints K8s e persistência TSDB. |
| **Regras de Alerta** | `k8s/prometheus-rules.yaml` | 4 regras de alerta (CPU > 80%, Memória > 80%, Taxa de Erro > 10% e Taxa de Sucesso < 90%) com janela de 5 minutos contra falsos positivos. |
| **Autoscaling (HPA)** | `k8s/hpa.yaml` | Manifesto `autoscaling/v2` com escala dinâmica de 1 a 5 réplicas baseada em 70% de CPU e 80% de memória, com janelas de estabilização (*stabilization windows*). |
| **Servidor Grafana** | `k8s/grafana.yaml` | Implantação do Grafana 11.2.0 com volumes projetados e auto-provisionamento declarativo. |
| **Dashboards Provisionados** | `k8s/grafana-dashboards.yaml` | ConfigMaps contendo o Data Source Prometheus e a definição JSON completa do Dashboard da MecâniQA com os **4 Golden Signals obrigatórios** e os gráficos de telemetria dos sensores. |
| **Governança & Runbooks** | `docs/RUNBOOKS_E_SLA.md` | Documento executável com o passo a passo técnico de troubleshooting para cada alarme, cálculo matemático de SLA (99,9%), SLO, SLI, RTO e RPO. |
| **Caderno de Guias** | `../docs/oat2/OAT 2 - CADERNO DE GUIAS - Monitorando a Continuidade.md` | Registro formal das decisões de arquitetura e respostas aos brainstorms investigativos e guiados de todos os 4 encontros da sprint. |

---

## 3. Os 4 Dashboards Obrigatórios (Golden Signals)

O Grafana vem pré-configurado declarativamente através do manifesto `k8s/grafana-dashboards.yaml`, apresentando na seção superior os **4 painéis obrigatórios de Golden Signals**:

1. **Consumo de CPU do Simulador (Infraestrutura):**  
   Mede a utilização percentual de CPU do processo em relação ao request alocado.  
   *PromQL:* `rate(process_cpu_seconds_total[1m]) * 100`  
   *Limiares Visuais:* Verde (< 70%), Amarelo (70% - Gatilho HPA), Vermelho (> 80% - Alerta).

2. **Consumo de Memória do Simulador (Infraestrutura):**  
   Mede a memória física residente (RSS) utilizada pelo processo em relação ao limite do contêiner (128Mi).  
   *PromQL:* `process_resident_memory_bytes`  
   *Limiares Visuais:* Normal até 102 MiB (80%); Alerta em 102.4 MiB.

3. **Taxa de Erro na Aplicação (Golden Signal — Erros):**  
   Proporção de leituras de telemetria com status de anomalia/falha sobre o total emitido.  
   *PromQL:* `(sum(rate(sensor_readings_total{status="error"}[1m])) / sum(rate(sensor_readings_total[1m]))) * 100`  
   *Limiares Visuais:* Verde (< 5%), Amarelo (5% a 10%), Vermelho (> 10% - Alerta Crítico).

4. **Taxa de Sucesso na Aplicação (SLI de Disponibilidade):**  
   Percentual de leituras válidas processadas com êxito. Mede o cumprimento do SLO contratual.  
   *PromQL:* `(sum(rate(sensor_readings_total{status="ok"}[1m])) / sum(rate(sensor_readings_total[1m]))) * 100`  
   *Limiares Visuais:* Vermelho (< 85%), Amarelo (85% a 90%), Verde (>= 90% - Meta Enterprise).

*Painéis Complementares:* O dashboard também renderiza os medidores de grandezas físicas dos veículos: **Temperatura do Motor (°C)**, **Vibração Mecânica (mm/s)**, **Pressão do Óleo (kPa)** e **Saúde Operacional do Sensor (Gauge binário)**.

---

## 4. Engenharia de Alertas e Escalonamento Dinâmico

### 4.1. Regras de Alarme (`k8s/prometheus-rules.yaml`)
Para evitar sobrecarga de alertas (*alert fatigue*) e garantir que apenas anomalias genuínas notifiquem o time de sobreaviso, todas as 4 regras contam com a diretiva de contenção `for: 5m`:

| Alarme | Categoria | Threshold (Gatilho) | Janela (`for`) | Severidade | Ação Esperada |
| :--- | :--- | :--- | :---: | :---: | :--- |
| `SensorSimulatorHighCPU` | Infraestrutura | Utilização CPU > 80% | 5 min | `Warning` | Verificar réplicas do HPA e logs de threads. |
| `SensorSimulatorHighMemory` | Infraestrutura | Memória RSS > 80% | 5 min | `Warning` | Avaliar vazamento de heap e ajustar limits. |
| `SensorSimulatorHighErrorRate`| Aplicação IoT | Taxa de falhas > 10% | 5 min | `Critical` | Isolar payload anômalo e inspecionar sensores. |
| `SensorSimulatorLowSuccessRate`| Aplicação IoT| Taxa de sucesso < 90% | 5 min | `Critical` | Avaliar violação de SLO e acionar contingência. |

### 4.2. Escalonamento Automático com HPA (`k8s/hpa.yaml`)
Configurado para reagir autonomamente aos picos de tráfego das oficinas (08:00 e 17:00):
* **Piso/Teto:** Mínimo de 1 pod (otimização de custos) e máximo de 5 pods (suporte a tempestades de tráfego).
* **Métricas Alvo:** CPU média em 70% ou Memória média em 80%.
* **Políticas de Estabilização:**
  * `scaleUp` com janela de 60s (+100% réplicas por minuto): reação ultrarrápida a picos;
  * `scaleDown` com janela de 300s (-25% réplicas por minuto): contenção contra oscilação cíclica (*pod flapping*).

---

## 5. Pré-requisitos e Instalação do Cluster

### Pré-requisitos
* **Docker Desktop** com Kubernetes ativo (ou cluster minikube/k3s/EKS/GKE funcional).
* **kubectl** instalado e autenticado.
* **Metrics Server** (obrigatório para fornecer métricas ao HPA).

### Instalação do Metrics Server no Docker Desktop
```powershell
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
$patch = '[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"},{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-preferred-address-types=InternalIP,Hostname,ExternalIP"}]'
kubectl patch deployment metrics-server -n kube-system --type=json -p $patch
kubectl rollout status deployment/metrics-server -n kube-system
```

Valide a disponibilidade da API de métricas:
```powershell
kubectl top nodes
kubectl top pods -n kube-system
```

---

## 6. Implantação e Execução

### Opção A: Execução no Kubernetes (Modo Produção)

1. **Construir a imagem local da aplicação:**
   ```powershell
   cd "OAT 2/app"
   docker build -t mecaniqa-simulador-sensores:local .
   cd ..
   ```

2. **Aplicar os manifestos na ordem recomendada:**
   ```powershell
   kubectl apply -f k8s/prometheus-rules.yaml
   kubectl apply -f k8s/prometheus.yaml
   kubectl apply -f k8s/simulador-sensores.yaml
   kubectl apply -f k8s/hpa.yaml
   kubectl apply -f k8s/grafana.yaml
   kubectl apply -f k8s/grafana-dashboards.yaml
   ```

3. **Verificar a integridade dos recursos implantados:**
   ```powershell
   kubectl get pods -o wide
   kubectl get svc
   kubectl get hpa simulador-sensores
   ```

4. **Acessar as interfaces gráficas:**
   Em terminais distintos, habilite o redirecionamento de portas:
   ```powershell
   # Acesso ao Prometheus Server (http://localhost:9090)
   kubectl port-forward svc/prometheus 9090:9090

   # Acesso ao Grafana (http://localhost:3000 - Usuário: admin | Senha: admin)
   kubectl port-forward svc/grafana 3000:3000
   ```

### Opção B: Execução com Docker (Modo Contêiner Isolado)

Caso deseje rodar e testar o microserviço simulador de sensores de forma isolada com Docker:

```powershell
# 1. Construir a imagem local
cd "OAT 2/app"
docker build -t mecaniqa-simulador-sensores:local .

# 2. Executar o contêiner mapeando a porta 8000
docker run -d --name mecaniqa-simulador -p 8000:8000 -e SENSOR_ERROR_RATE=0.05 -e SENSOR_INTERVAL_SECONDS=2 mecaniqa-simulador-sensores:local

# 3. Testar os endpoints de saúde e telemetria
curl http://localhost:8000/health
curl http://localhost:8000/metrics

# 4. Encerrar o contêiner após os testes
docker stop mecaniqa-simulador
docker rm mecaniqa-simulador
```

### Opção C: Execução Local em Python (Ambiente de Desenvolvimento)

Para executar o simulador diretamente no interpretador Python do host:

```powershell
cd "OAT 2/app"

# Criação e ativação do ambiente virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # No Linux/macOS: source .venv/bin/activate

# Instalação das dependências
pip install -r requirements.txt

# Execução do simulador com variáveis customizadas
$env:SENSOR_ERROR_RATE="0.05"
$env:SENSOR_INTERVAL_SECONDS="2"
python sensor_simulator.py

# Em outro terminal, teste os endpoints:
curl http://localhost:8000/health
curl http://localhost:8000/metrics
```

---

## 7. Roteiro de Validação e Teste de Estresse

Execute os testes abaixo para validar a resiliência e coletar evidências:

### Teste 1: Validação do Scrape do Prometheus
* Abra `http://localhost:9090/targets` e confirme que o target `kubernetes-services` referente ao `simulador-sensores:8000` está com status **UP**.
* Na aba `Graph`, consulte:
  ```promql
  sensor_readings_total
  sensor_temperature_celsius
  ```

### Teste 2: Validação do Escalonamento Automático do HPA
Em um terminal, monitore o comportamento do HPA e dos pods:
```powershell
kubectl get hpa simulador-sensores --watch
kubectl get pods -l app=simulador-sensores --watch
```

Em outro terminal, injete carga computacional contínua no pod do simulador:
```powershell
kubectl exec deployment/simulador-sensores -- python -c "while True: pass"
```

**Resultado Esperado:**  
O Metrics Server registrará a utilização de CPU acima de 70% e o HPA adicionará réplicas gradativamente até equilibrar o consumo (escalando para 2 ou 3 pods). Para encerrar o estresse, pressione `Ctrl + C`. Após a janela de estabilização de 5 minutos, o HPA reduzirá suavemente as réplicas de volta para 1.

### Teste 3: Validação dos Alarmes Customizados de Aplicação
Altere deliberadamente a taxa de anomalia sintética para 20% (acima do threshold de 10%):
```powershell
kubectl set env deployment/simulador-sensores SENSOR_ERROR_RATE=0.20
kubectl rollout status deployment/simulador-sensores
```

Acompanhe no Prometheus (`http://localhost:9090/alerts`) ou no Grafana:
* O alarme `SensorSimulatorHighErrorRate` entrará no estado `Pending`;
* Após 5 minutos ininterruptos, transitará para `Firing`;
* Restaure o ambiente nominal ao término do teste:
  ```powershell
  kubectl set env deployment/simulador-sensores SENSOR_ERROR_RATE=0.05
  kubectl rollout status deployment/simulador-sensores
  ```

---

## 8. Evidências Visuais Operacionais (Screenshots)

As evidências visuais de execução no navegador foram geradas e armazenadas em `docs/images/`:

| Evidência | Arquivo | Descrição |
| :--- | :--- | :--- |
| **Dashboard Grafana (Golden Signals)** | `docs/images/06_grafana_dashboard_golden_signals.png` | Painel completo com CPU, Memória, Taxa de Erro, Taxa de Sucesso e Telemetria IoT. |
| **Prometheus Targets** | `docs/images/03_prometheus_targets.png` | Status operacional `UP` do simulador e da instância Prometheus. |
| **Prometheus Alarmes** | `docs/images/04_prometheus_alerts.png` | As 4 regras de alarme ativas avaliando em tempo real. |
| **Prometheus Gráfico Temporal** | `docs/images/05_prometheus_graph.png` | Série temporal de temperatura e telemetria plotada em tempo real. |
| **Métricas OpenMetrics** | `docs/images/02_sensor_metrics_prometheus.png` | Endpoint `/metrics` expondo Gauges e Counters instrumentados. |
| **Health Check API** | `docs/images/01_sensor_health_api.png` | Endpoint `/health` respondendo payload JSON com status operacional. |

---

## 9. Governança de TI, SLA e Runbooks

Consulte o documento executivo formal em:
* [RUNBOOKS_E_SLA.md](file:///c:/Users/Bruno/Documents/Projetos/mecaniQA-nuvem-sao-luiz/OAT%202/docs/RUNBOOKS_E_SLA.md)

Este documento contém:
* **Matriz Contratual de SLA (99,9% de Uptime):** Cálculo do *Error Budget* (máximo de 8h 45m 36s de indisponibilidade anual);
* **SLOs e SLIs:** Expressões formais em PromQL para monitoramento contínuo de qualidade e latência;
* **Metas de Continuidade:** RTO de 45 minutos e RPO de 5 minutos;
* **Análise de Desastre:** Impacto do blackout de 45 minutos em região de nuvem;
* **4 Runbooks Operacionais:** Procedimento técnico detalhado de diagnóstico, comandos `kubectl` e mitigação para cada alerta.

---

**MecâniQA Tech — Engenharia de Confiabilidade de Sites (SRE)**  
Vitória da Conquista, 2026.
