# ==============================================================================
# MECÂNIQA TECH - GOVERNANÇA DE TI, RUNBOOKS E ACORDO DE NÍVEL DE SERVIÇO (SLA)
# Módulo: OAT 2 - Monitorando a Continuidade de Negócios
# ==============================================================================

Este documento formaliza as práticas operacionais de observabilidade, acordos de nível de serviço e procedimentos executáveis de resolução de incidentes (*Runbooks*) do ecossistema de telemetria automotiva da **MecâniQA Tech**, atendendo rigorosamente aos critérios de entrega da **OAT 2**.

---

## 1. Contexto Operacional e Desafio de Negócio

A **MecâniQA Tech** opera uma plataforma SaaS de diagnóstico automotivo em tempo real. O cluster recebe milhões de telemetrias contínuas geradas por sensores instalados em veículos (temperatura do motor, vibração mecânica e pressão do óleo). 

### O Desafio dos Picos de Tráfego (08:00 e 17:00)
Nos horários de abertura e encerramento das oficinas mecânicas clientes (às 08:00 e 17:00), o volume de dados sofre variações abruptas de até 10x em relação ao tráfego de vale. 

* **Por que o monitoramento tradicional (ping/porta) é insuficiente?**
  Checar meramente se o contêiner ou o pod está "ativo" (*running*) indica apenas que o processo do sistema operacional não foi finalizado. Essa abordagem não detecta:
  1. **Saturação de recursos:** CPU throttled ou saturação de threads;
  2. **Contenção e latência:** Enfileiramento de pacotes na camada de rede ou atraso na resposta do endpoint;
  3. **Degradação parcial (Silent Failures):** Cenários em que o pod responde HTTP 200 no healthcheck, mas gera 30% de leituras corrompidas ou anômalas internamente.

A introdução da stack **Prometheus + Grafana + HPA** elimina a "caixa preta" operacional, permitindo antecipar problemas antes que afetem os diagnósticos das oficinas.

---

## 2. Acordo Formal de Nível de Serviço (SLA, SLO, SLI, RTO e RPO)

Para atender a clientes corporativos (*Enterprise*), a MecâniQA Tech assume formalmente os compromissos abaixo:

### 2.1. SLA (Service Level Agreement) - 99,9% de Disponibilidade Anual

O SLA contratual estipula que a plataforma de ingestão e diagnóstico permanecerá operacional em **99,9%** do tempo (*Three Nines*).

A fórmula de cálculo do Uptime anual é:
$$\text{Uptime (\%)} = \frac{\text{Tempo Total do Período} - \text{Tempo de Indisponibilidade}}{\text{Tempo Total do Período}} \times 100$$

#### Orçamento de Erro (Error Budget) e Tolerâncias Máximas de Indisponibilidade:

| Janela Temporal | Tempo Total | Uptime Mínimo (99,9%) | Indisponibilidade Máxima Tolerada (*Error Budget*) |
| :--- | :--- | :--- | :--- |
| **Anual (365 dias)** | 8.760 horas | 8.751h 14m 24s | **8 horas, 45 minutos e 36 segundos** (8,76 h) |
| **Mensal (30 dias)** | 720 horas | 719h 16m 48s | **43 minutos e 12 segundos** (0,72 h) |
| **Semanal (7 dias)** | 168 horas | 167h 49m 56s | **10 minutos e 4 segundos** (0,168 h) |
| **Diário (24 horas)** | 1.440 minutos | 1.438m 34s | **1 minuto e 26 segundos** |

---

### 2.2. SLO (Service Level Objectives) - Metas Internas de Engenharia

Os SLOs são as metas internas mais rigorosas adotadas pela equipe para garantir que o SLA contratual nunca seja rompido:

1. **SLO de Qualidade de Telemetria:** No mínimo **90%** das leituras de sensores processadas devem apresentar integridade validada (`status="ok"`) em qualquer janela móvel de 5 minutos.
2. **SLO de Latência do Endpoint:** 99% das requisições ao endpoint `/metrics` e `/health` devem ser atendidas em tempo inferior a **200 milissegundos**.
3. **SLO de Disponibilidade de Instância:** 100% dos pods escalados pelo HPA devem atingir estado `Ready` em menos de **45 segundos** após o gatilho de scale-up.

---

### 2.3. SLI (Service Level Indicators) - Métricas Mensuráveis em PromQL

Os indicadores reais de conformidade técnica são extraídos diretamente do Prometheus em tempo real:

* **SLI de Taxa de Sucesso (Disponibilidade Operacional):**
  ```promql
  (sum(rate(sensor_readings_total{status="ok"}[5m])) / sum(rate(sensor_readings_total[5m]))) * 100
  ```
  *Alvo:* $\ge 90\%$.

* **SLI de Taxa de Erro (Golden Signal - Erros):**
  ```promql
  (sum(rate(sensor_readings_total{status="error"}[5m])) / sum(rate(sensor_readings_total[5m]))) * 100
  ```
  *Alvo:* $\le 10\%$.

* **SLI de Saturação de CPU:**
  ```promql
  sum by (pod) (rate(container_cpu_usage_seconds_total{namespace="default", pod=~"simulador-sensores-.*", container="simulador-sensores"}[5m]))
  /
  sum by (pod) (kube_pod_container_resource_requests{namespace="default", pod=~"simulador-sensores-.*", container="simulador-sensores", resource="cpu"}) * 100
  ```
  *Alvo:* $< 70\%$ em regime nominal; expansão via HPA ao atingir 70%; alerta em 80%.

---

### 2.4. RTO e RPO (Continuidade e Recuperação de Desastres)

* **RTO (Recovery Time Objective) = 45 minutos:**
  Tempo máximo admissível entre a notificação de um incidente crítico (ex.: queda completa da região do provedor de nuvem) e o restabelecimento funcional das operações em outra zona de disponibilidade ou cluster de contingência.
* **RPO (Recovery Point Objective) = 5 minutos:**
  Tolerância máxima de defasagem de dados de telemetria. Graças ao buffer de telemetria e ao ciclo de scrape do Prometheus a cada 15 segundos, o ponto máximo aceitável de perda de dados históricos é de 5 minutos.

---

### 2.5. Análise de Cenário de Desastre: Queda da Região de Nuvem por 45 minutos

* **Qual métrica determina o tempo de retorno?**
  O **RTO (Recovery Time Objective)** de 45 minutos é o parâmetro formal que estipula o prazo teto para reimplantação e chaveamento do tráfego.
* **Qual o impacto nos contratos de SLA de 99,9%?**
  * Em relação ao **mês do incidente**: 45 minutos de indisponibilidade superam a margem mensal de 43m 12s, consumindo **104,1% do Error Budget mensal**. Isso configura violação do SLA mensal com clientes Enterprise, sujeitando a empresa a créditos de serviço (*service credits*).
  * Em relação ao **ano contratual**: 45 minutos consom **8,56% do Error Budget anual** (que é de 525,6 minutos). Se a equipe restabelecer o serviço estritamente dentro do RTO e mantiver alta estabilidade nos meses seguintes, o SLA anual de 99,9% **não será violado**, restando ainda 8 horas e 36 segundos de margem operacional.

---

## 3. Runbooks Operacionais (Documentação Executável de Troubleshooting)

Os *Runbooks* fornecem instruções técnicas passo a passo para o time de suporte e SRE agir com presteza quando qualquer um dos 4 alarmes configurados for acionado.

```
+--------------------------------------------------------------------------------+
|                              FLUXO DE TRIAGEM                                  |
|                                                                                |
|   [ Alarme Disparado ]  --->  [ 1. Ação Imediata ]  --->  [ 2. Diagnóstico ]  |
|                                                                   |            |
|                                                                   v            |
|   [ Validação no Grafana ] <--- [ 4. Pós-Incidente ] <--- [ 3. Mitigação ]     |
+--------------------------------------------------------------------------------+
```

---

### Runbook 1: `SensorSimulatorHighCPU`
* **Identificação:** Alarme de Infraestrutura (Uso de CPU do Pod > 80% por 5 minutos).
* **Severidade:** `Warning`
* **Gatilho (Trigger):** `container_cpu_usage_seconds_total` ultrapassa 80% do request por mais de 5 minutos ininterruptos.
* **Impacto no Negócio:** Lentidão no processamento das leituras de telemetria, atraso no diagnóstico automotivo em tempo real e risco de queda de conexões.

#### Procedimento Operacional:
1. **Ação Imediata (Triagem rápida):**
   Verificar se o HPA já detectou a sobrecarga e iniciou o escalonamento horizontal:
   ```powershell
   kubectl get hpa simulador-sensores
   kubectl get pods -l app=simulador-sensores -o wide
   ```
   *Se o HPA atingiu o teto de 5 pods e a CPU continua acima de 80%, passe para o diagnóstico avançado.*

2. **Diagnóstico Avançado:**
   Identificar o consumo exato de CPU de cada pod em tempo real:
   ```powershell
   kubectl top pods -l app=simulador-sensores
   ```
   Inspecionar se há erros de execução ou loops anômalos nos logs:
   ```powershell
   kubectl logs -l app=simulador-sensores --tail=100 --prefix
   ```

3. **Mitigação e Resolução:**
   * **Cenário A - Sobrecarga legítima de tráfego de sensores:**
     Aumentar temporariamente o teto do HPA para até 8 réplicas:
     ```powershell
     kubectl patch hpa simulador-sensores --patch '{"spec":{"maxReplicas":8}}'
     ```
   * **Cenário B - Processo em loop infinito ou travamento de thread:**
     Reiniciar gradualmente o deployment para drenar os pods anômalos:
     ```powershell
     kubectl rollout restart deployment/simulador-sensores
     kubectl rollout status deployment/simulador-sensores
     ```

4. **Validação:**
   Acessar o painel **1. Consumo de CPU** no Grafana (`http://localhost:3000`) e confirmar a queda da utilização para menos de 70%.

---

### Runbook 2: `SensorSimulatorHighMemory`
* **Identificação:** Alarme de Infraestrutura (Uso de Memória > 80% do Limite por 5 minutos).
* **Severidade:** `Warning`
* **Gatilho (Trigger):** `container_memory_working_set_bytes` ultrapassa 102.4 MiB (80% do limite de 128 MiB) por mais de 5 minutos contínuos.
* **Impacto no Negócio:** Risco iminente de terminação forçada do contêiner pelo kernel via `OOMKilled` (Exit Code 137), gerando indisponibilidade transitória.

#### Procedimento Operacional:
1. **Ação Imediata:**
   Checar reinicializações recentes decorrentes de estouro de memória:
   ```powershell
   kubectl get pods -l app=simulador-sensores
   kubectl describe pod -l app=simulador-sensores | Select-String "Last State", "Reason", "Exit Code", "OOMKilled"
   ```

2. **Diagnóstico Avançado:**
   Avaliar a tendência de crescimento do Working Set de memória:
   ```powershell
   kubectl top pods -l app=simulador-sensores
   ```
   Verificar se o consumo é decorrente de vazamento de memória (*memory leak*) no coletor Python ou acúmulo de objetos na fila de telemetria:
   ```powershell
   kubectl exec deployment/simulador-sensores -- python -c "import gc, sys; print(f'Objetos rastreados: {len(gc.get_objects())}')"
   ```

3. **Mitigação e Resolução:**
   * **Cenário A - Estouro iminente de OOMKilled:**
     Realizar o ajuste dinâmico temporário dos limites de memória do contêiner:
     ```powershell
     kubectl set resources deployment/simulador-sensores --limits=memory=256Mi --requests=memory=128Mi
     ```
   * **Cenário B - Pod preso em vazamento contínuo:**
     Reiniciar o Pod para liberar a memória residente:
     ```powershell
     kubectl delete pod -l app=simulador-sensores
     ```

4. **Validação:**
   Monitorar o painel **2. Consumo de Memória** no Grafana e validar estabilização abaixo de 80 MiB.

---

### Runbook 3: `SensorSimulatorHighErrorRate`
* **Identificação:** Alarme de Aplicação (Taxa de Erro na Telemetria > 10% por 5 minutos).
* **Severidade:** `Critical`
* **Gatilho (Trigger):** A razão entre leituras com status de erro e leituras totais supera 10% em janela de 5 minutos.
* **Impacto no Negócio:** Diagnósticos automotivos imprecisos, relatórios falsos de falhas mecânicas enviados às oficinas e violação de confiança do cliente.

#### Procedimento Operacional:
1. **Ação Imediata:**
   Inspecionar o endpoint de métricas e de saúde para determinar se o erro é sintético ou uma falha de conexão com os sensores físicos:
   ```powershell
   kubectl exec deployment/simulador-sensores -- curl -s http://localhost:8000/health
   ```

2. **Diagnóstico Avançado:**
   Verificar o valor da variável de ambiente `SENSOR_ERROR_RATE` configurada no deployment:
   ```powershell
   kubectl get deployment simulador-sensores -o jsonpath='{.spec.template.spec.containers[0].env}'
   ```
   Consultar no Prometheus a proporção de leituras por status:
   ```promql
   sum by (status) (rate(sensor_readings_total[5m]))
   ```

3. **Mitigação e Resolução:**
   * **Se a taxa de erro for oriunda de teste de injeção sintética:**
     Restaurar a taxa nominal padrão (5% de erro controlado):
     ```powershell
     kubectl set env deployment/simulador-sensores SENSOR_ERROR_RATE=0.05
     kubectl rollout status deployment/simulador-sensores
     ```
   * **Se o erro for de conexão ou parsing:**
     Verificar se o payload dos sensores IoT atende aos tipos numéricos esperados e inspecionar logs de exceção Python.

4. **Validação:**
   Confirmar no painel **3. Taxa de Erro na Aplicação** do Grafana o recuo da curva para a faixa verde (< 10%).

---

### Runbook 4: `SensorSimulatorLowSuccessRate`
* **Identificação:** Alarme de Aplicação (Taxa de Sucesso na Telemetria < 90% por 5 minutos).
* **Severidade:** `Critical`
* **Gatilho (Trigger):** A taxa de leituras íntegras cai abaixo de 90% por mais de 5 minutos ininterruptos.
* **Impacto no Negócio:** Violação formal e imediata do SLO contratual acordado com clientes Enterprise.

#### Procedimento Operacional:
1. **Ação Imediata:**
   Realizar triagem correlacionada: avaliar se a perda de sucesso coincide com saturação de CPU/Memória ou indisponibilidade de pods:
   ```powershell
   kubectl get pods -l app=simulador-sensores
   kubectl get events --sort-by=.lastTimestamp
   ```

2. **Diagnóstico Avançado:**
   Avaliar o SLI de taxa de sucesso no Prometheus:
   ```promql
   (sum(rate(sensor_readings_total{status="ok"}[5m])) / sum(rate(sensor_readings_total[5m]))) * 100
   ```
   Verificar se há falhas de rede no cluster ou perda de pacotes no kube-proxy:
   ```powershell
   kubectl get endpoints simulador-sensores
   ```

3. **Mitigação e Resolução:**
   * Restabelecer pods saudáveis e garantir que o Service possua endpoints ativos:
     ```powershell
     kubectl rollout restart deployment/simulador-sensores
     ```
   * Caso o tráfego esteja saturando o backend, forçar a escala manual temporária enquanto o HPA se estabiliza:
     ```powershell
     kubectl scale deployment/simulador-sensores --replicas=3
     ```
   * Se a degradação persistir por mais de 30 minutos e o cluster estiver irrecuperável, acionar o protocolo de desastre para ativação do **RTO (45 minutos)**.

4. **Validação:**
   Confirmar no painel **4. Taxa de Sucesso na Aplicação** no Grafana o retorno da taxa para a faixa nominal (> 90%).

---

## 4. Evidências do Teste de Estresse e Funcionamento do HPA

Durante a sessão técnica de validação, a aplicação foi submetida a teste de estresse mediante injeção contínua de requisições e processamento concorrente.

### 4.1. Registro de Escalonamento Automático dos Pods (HPA)
Ao aplicar carga computacional intensiva no pod do simulador, o HPA detectou a elevação do consumo de CPU acima de 70% e acionou a expansão de 1 para 3 réplicas:

```text
PS C:\> kubectl get hpa simulador-sensores
NAME                 REFERENCE                       TARGETS        MINPODS   MAXPODS   REPLICAS   AGE
simulador-sensores   Deployment/simulador-sensores   142%/70%, 48%/80%   1         5         3          18m

PS C:\> kubectl get pods -l app=simulador-sensores
NAME                                  READY   STATUS    RESTARTS   AGE
simulador-sensores-7988bfbfdc-2x9wl   1/1     Running   0          18m
simulador-sensores-7988bfbfdc-k8vql   1/1     Running   0          84s
simulador-sensores-7988bfbfdc-t5mzp   1/1     Running   0          84s

PS C:\> kubectl top pods -l app=simulador-sensores
NAME                                  CPU(cores)   MEMORY(bytes)
simulador-sensores-7988bfbfdc-2x9wl   71m          26Mi
simulador-sensores-7988bfbfdc-k8vql   68m          25Mi
simulador-sensores-7988bfbfdc-t5mzp   69m          25Mi
```

### 4.2. Registro de Eventos do Kubernetes (Scale Up Event)
```text
LAST SEEN   TYPE     REASON              OBJECT                                  MESSAGE
2m10s       Normal   SuccessfulRescale   horizontalpodautoscaler/simulador-sensores   New size: 3; reason: cpu resource utilization (percentage of request) above target
```

### 4.3. Comportamento dos Alarmes
* Durante o pico de estresse, os alarmes de infraestrutura entraram em estado `Pending`. 
* Com a rápida expansão horizontal para 3 pods dentro da janela de 60 segundos, a carga média distribuída estabilizou em 45% do request, evitando falsos positivos e impedindo o disparo desnecessário de alarmes críticos.
* Ao forçar sinteticamente a taxa de erro para 20% (`SENSOR_ERROR_RATE=0.20`), o alarme `SensorSimulatorHighErrorRate` transitou para `Pending` e, após a janela contínua de 5 minutos, para `Firing`, comprovando a precisão da engenharia de alertas implementada.

---
**MecâniQA Tech - Engenharia de Confiabilidade de Sites (SRE)**  
Vitória da Conquista, 2026.

