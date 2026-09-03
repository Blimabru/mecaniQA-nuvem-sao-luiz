# MecaniQA — Infraestrutura de Contêineres

## Objetivo

Estabilizar o sistema legado por meio do isolamento da API Java, do MySQL e do
Redis na camada de virtualização de contêineres.

## Arquitetura da Solução

A solução é composta pelos seguintes serviços:

- **API:** aplicação Java empacotada localmente.
- **Banco de dados:** MySQL 8.0, obtido do Registry oficial.
- **Cache:** Redis Alpine, obtido do Registry oficial.

O `Dockerfile` utiliza `eclipse-temurin:17-jdk-alpine`, uma imagem otimizada por
compartilhar o kernel do sistema hospedeiro. A aplicação é copiada para
`/app`, utiliza a porta `8080` e é executada em primeiro plano.

## Orquestração e Fluxo de Execução

O `docker-compose.yml` coordena a inicialização simultânea da API, do banco e
do cache. Ao identificar a instrução `build`, o Docker Compose constrói
localmente a imagem da API por meio do `Dockerfile`. As imagens oficiais do
MySQL 8.0 e do Redis Alpine são consumidas diretamente do Registry.

## Descoberta de Serviço

Todos os serviços são conectados à rede virtual exclusiva
`mecaniqa-network`. A comunicação interna utiliza resolução DNS por nome de
serviço, permitindo que a API acesse `db` e `redis` sem depender de IPs fixos.

## Persistência e Alta Disponibilidade

Os dados do MySQL são preservados no volume `mysql_data`, montado em
`/var/lib/mysql`. A política `restart: unless-stopped` reinicia
automaticamente os contêineres após quedas, mantendo a disponibilidade dos
serviços.

## Instruções de Uso

Pré-requisitos:

- Docker instalado e em execução.
- Arquivo `app.jar` na raiz do projeto.

Na raiz do repositório, execute:

```bash
docker-compose up -d --build
```

A API ficará disponível em `http://localhost:8080`.

Para interromper os serviços:

```bash
docker-compose down
```
