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
