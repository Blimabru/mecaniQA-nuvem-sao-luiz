# OAT 2 - Monitoramento com Prometheus e Grafana

Este módulo simula um sensor de veículos e expõe métricas Prometheus em `/metrics`, além de um endpoint de saúde em `/health`.

## Componentes

- `app/sensor_simulator.py`: gerador de métricas do tipo temperatura, vibração e pressão.
- `app/Dockerfile`: imagem da aplicação.
- `app/requirements.txt`: dependências Python.
- `k8s/prometheus.yaml`: instalação do Prometheus com descoberta dinâmica de serviços.
- `k8s/prometheus-rules.yaml`: quatro regras de alerta de infraestrutura e aplicação.
- `k8s/simulador-sensores.yaml`: deployment e service do simulador.
- `k8s/hpa.yaml`: escalonamento entre 1 e 5 pods por CPU e memória.
- `k8s/grafana.yaml` e `k8s/grafana-dashboards.yaml`: provisionamento do Grafana e do dashboard inicial.

## Pré-requisitos do Kubernetes

Instale e deixe disponíveis:

- Docker Desktop com Kubernetes habilitado, ou outro cluster Kubernetes funcional.
- `kubectl` configurado para apontar para o cluster correto.
- Metrics Server, obrigatório para o HPA obter CPU e memória.

Confirme o acesso ao cluster:

```powershell
kubectl cluster-info
kubectl get nodes
```

No Docker Desktop, instale o Metrics Server com:

```powershell
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
$patch = '[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"},{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-preferred-address-types=InternalIP,Hostname,ExternalIP"}]'
kubectl patch deployment metrics-server -n kube-system --type=json -p $patch
kubectl rollout status deployment/metrics-server -n kube-system
```

Se o patch informar que esses argumentos já existem, não o execute novamente.
Verifique o Deployment e siga diretamente para a validação:

```powershell
kubectl get deployment metrics-server -n kube-system -o jsonpath='{.spec.template.spec.containers[0].args}'
kubectl rollout status deployment/metrics-server -n kube-system
kubectl top pods
```

Valide a API antes de aplicar o HPA:

```powershell
kubectl get pods -n kube-system -l k8s-app=metrics-server
kubectl top nodes
kubectl top pods
```

Se `kubectl top` retornar `Metrics API not available`, consulte o diagnóstico:

```powershell
kubectl logs -n kube-system deployment/metrics-server
kubectl describe apiservice v1beta1.metrics.k8s.io
```

## Executar localmente

```bash
cd "OAT 2/app"
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
SENSOR_ERROR_RATE=0.05 SENSOR_INTERVAL_SECONDS=2 python sensor_simulator.py
```

Depois do boot, teste:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/metrics
```

## Executar com Docker

```bash
cd "OAT 2/app"
docker build -t mecaniqa-simulador-sensores:local .
docker run --rm -p 8000:8000 -e SENSOR_ERROR_RATE=0.05 -e SENSOR_INTERVAL_SECONDS=2 mecaniqa-simulador-sensores:local
```

No Docker Desktop, a imagem local fica disponível para o cluster Kubernetes integrado.
Em clusters que não compartilham o daemon Docker local, publique a imagem em um
registry e altere `spec.template.spec.containers[].image` em `k8s/simulador-sensores.yaml`.

## Executar no Kubernetes

```bash
kubectl apply -f k8s/prometheus-rules.yaml
kubectl apply -f k8s/prometheus.yaml
kubectl apply -f k8s/simulador-sensores.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/grafana.yaml
kubectl apply -f k8s/grafana-dashboards.yaml
```

O HPA requer o Metrics Server no cluster. Para acompanhar o teste de estresse:

```powershell
kubectl get hpa simulador-sensores --watch
kubectl get pods -l app=simulador-sensores --watch
kubectl top pods -l app=simulador-sensores
```

O manifesto usa `autoscaling/v2`, mantém de 1 a 5 réplicas e escala quando a média
atinge 70% do request de CPU ou 80% do request de memória. O scale down aguarda
5 minutos para evitar oscilações.

Para gerar carga sem depender de uma ferramenta adicional, execute requisições ao
endpoint de métricas a partir do cluster e guarde a saída dos comandos como evidência:

```powershell
kubectl run stress-sensors --rm -i --restart=Never --image=curlimages/curl -- sh -c 'for i in $(seq 1 600); do curl -fsS http://simulador-sensores:8000/metrics >/dev/null; done'
kubectl describe hpa simulador-sensores
kubectl get events --sort-by=.lastTimestamp
```

### Roteiro completo de validação

Execute os testes abaixo nesta ordem e salve as saídas como evidência.

1. **Saúde dos componentes:**

```powershell
kubectl get pods -o wide
kubectl get svc
kubectl get hpa simulador-sensores
kubectl top pods
```

O HPA deve mostrar valores numéricos em `TARGETS`; `<unknown>` significa que o
Metrics Server ainda não está funcionando.

2. **Scrape do Prometheus:**

```powershell
kubectl port-forward svc/prometheus 9090:9090
```

Em outro terminal, abra `http://localhost:9090/targets` e confirme que o target
`simulador-sensores` está `UP`. Em `http://localhost:9090/graph`, consulte:

```text
sensor_readings_total
sensor_health
sensor_temperature_celsius
```

3. **Teste do HPA:** em um segundo terminal, acompanhe o escalonamento:

```powershell
kubectl get hpa simulador-sensores --watch
kubectl get pods -l app=simulador-sensores --watch
```

Em um terceiro terminal, gere CPU diretamente no pod do simulador. O comando fica
em primeiro plano; interrompa-o com `Ctrl+C` depois que o HPA criar uma réplica extra:

```powershell
kubectl exec deployment/simulador-sensores -- python -c "while True: pass"
```

Registre a evidência e finalize o processo. Depois aguarde a janela de 5 minutos
do scale down:

```powershell
kubectl describe hpa simulador-sensores
kubectl get events --sort-by=.lastTimestamp
```

4. **Teste dos alertas customizados:** altere temporariamente a taxa de erro para
20%, acima do limite de 10%, e reaplique o Deployment:

```powershell
kubectl set env deployment/simulador-sensores SENSOR_ERROR_RATE=0.20
kubectl rollout status deployment/simulador-sensores
```

Após pelo menos 5 minutos, confirme `SensorSimulatorHighErrorRate` e
`SensorSimulatorLowSuccessRate` no Prometheus ou no Grafana. Ao finalizar, restaure
o cenário normal:

```powershell
kubectl set env deployment/simulador-sensores SENSOR_ERROR_RATE=0.05
kubectl rollout status deployment/simulador-sensores
```

5. **Teste dos alertas de infraestrutura:** acompanhe CPU e memória no Grafana e
confirme as regras `SensorSimulatorHighCPU` e `SensorSimulatorHighMemory`. Os alertas
devem permanecer em `Pending` ou `Alerting` por 5 minutos antes de serem considerados
disparados, evitando falsos positivos.

O teste será aprovado quando o HPA deixar de exibir `<unknown>`, aumentar as réplicas
durante a carga e os pods permanecerem `Running` e `Ready`. Após o fim da carga, as
réplicas devem retornar gradualmente ao mínimo. Salve a saída dos comandos e as telas
do Grafana como evidências.

Acesso sugerido:

- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000` (usuário `admin`, senha `admin`)
