# MecaniQA

## Teste com Docker Compose

### Pré-requisitos

- Docker instalado e em execução.
- Arquivo `app.jar` na raiz do projeto, conforme definido no `Dockerfile`.

### Execução

Na raiz do projeto, valide a configuração:

```bash
docker compose config
```

Inicie a API, o MySQL e o Redis:

```bash
docker compose up --build
```

A API estará disponível em `http://localhost:8080`. Os serviços podem ser
encerrados com `Ctrl+C`.

### Limpeza

Para remover os contêineres e a rede:

```bash
docker compose down
```

Para remover também os dados persistidos do MySQL:

```bash
docker compose down -v
```

## Teste com Kubernetes (K8s)

### Execução

Na raiz do projeto, aplique todos os manifestos do Kubernetes de uma única vez. Isso instruirá o Cluster a criar os Deployments e Services da nossa arquitetura:

```bash
kubectl apply -f k8s/
```

### Validação e Monitoramento

Para verificar se todos os Pods (Java, MySQL e Redis) estão em execução:

```bash
kubectl get pods
```

Para verificar se o Service da API disponibilizou o IP/Porta de acesso externo:

```bash
kubectl get svc
```

Para inspecionar o cluster de forma visual, verificar uso de recursos e diagnosticar eventuais `CrashLoopBackOff`, utilize a interface do K9s:

```bash
k9s
```

### Limpeza (K8s)

Para apagar todos os recursos e limpar o cluster, execute:

```bash
kubectl delete -f k8s/
```
