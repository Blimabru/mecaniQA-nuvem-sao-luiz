# OAT 2 - Monitoramento com Prometheus e Grafana

Este módulo simula um sensor de veículos e expõe métricas Prometheus em `/metrics`, além de um endpoint de saúde em `/health`.

## Componentes

- `app/sensor_simulator.py`: gerador de métricas do tipo temperatura, vibração e pressão.
- `app/Dockerfile`: imagem da aplicação.
- `app/requirements.txt`: dependências Python.
- `k8s/prometheus.yaml`: instalação do Prometheus com descoberta dinâmica de serviços.
- `k8s/simulador-sensores.yaml`: deployment e service do simulador.
- `k8s/grafana.yaml` e `k8s/grafana-dashboards.yaml`: provisionamento do Grafana e do dashboard inicial.

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
docker build -t mecaniqa-simulador-sensores:local .
docker run --rm -p 8000:8000 -e SENSOR_ERROR_RATE=0.05 -e SENSOR_INTERVAL_SECONDS=2 mecaniqa-simulador-sensores:local
```

## Executar no Kubernetes

```bash
kubectl apply -f k8s/prometheus.yaml
kubectl apply -f k8s/simulador-sensores.yaml
kubectl apply -f k8s/grafana.yaml
kubectl apply -f k8s/grafana-dashboards.yaml
```

Acesso sugerido:

- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000` (usuário `admin`, senha `admin`)
