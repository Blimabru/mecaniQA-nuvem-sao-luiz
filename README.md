# MecaniQA Infrastructure

Este repositório contém a infraestrutura necessária para a atividade OAT 1 da MecâniQA Tech, cobrindo empacotamento de serviços, orquestração local com Docker Compose, gestão declarativa com Kubernetes e provisionamento inicial em Terraform.

**Membros da Equipe:**
1. Bruno Moreira Lima
2. Claudio Pales Costa
3. Gabriel Honorato Santos Ferraz
4. Kéven Moraes Patrício
5. Tiago Ferraz de Novais

## Requisitos atendidos

- Dockerfile para a aplicação Java.
- Dockerfile isolado para MySQL.
- Dockerfile isolado para Redis.
- docker-compose.yml com rede interna, DNS por nome de serviço e persistência de dados.
- Manifestos declarativos em Kubernetes para API, MySQL e Redis.
- Configuração inicial em Terraform para provisionar a infraestrutura local via Docker.

## Estrutura do projeto

- Dockerfile: imagem da API Java.
- docker/mysql/Dockerfile: imagem customizada do MySQL.
- docker/redis/Dockerfile: imagem customizada do Redis.
- docker-compose.yml: orquestração local completa.
- k8s/: manifests do Kubernetes.
- terraform/: provisionamento inicial com Terraform.

## Pré-requisitos

- Docker e Docker Compose instalados.
- Terraform instalado, se for usar a infraestrutura em IaC.
- Arquivo app.jar na raiz do projeto, conforme exigido pela imagem da API Java.

## Execução com Docker Compose

Valide a configuração:

```bash
docker compose config
```

Suba todo o ecossistema:

```bash
docker compose up --build
```

A API ficará disponível em http://localhost:8080.

Para remover os containers e preservar os volumes:

```bash
docker compose down
```

Para remover também os dados persistidos:

```bash
docker compose down -v
```

## Execução com Kubernetes

Aplicar os manifestos:

```bash
kubectl apply -f k8s/
```

Verificar pods:

```bash
kubectl get pods
```

Verificar serviços:

```bash
kubectl get svc
```

Monitorar o cluster com K9s:

```bash
k9s
```

Remover os recursos:

```bash
kubectl delete -f k8s/
```

## Provisionamento com Terraform

A partir da pasta terraform:

```bash
terraform init
terraform plan
terraform apply
```

Para destruir os recursos provisionados:

```bash
terraform destroy
```

> O ambiente Terraform está configurado para provisionar os containers do Docker localmente, representando a base inicial de infraestrutura como código da solução.
