# Dockerfile específico para o serviço de cache Redis.
# Usa a imagem oficial leve do Redis e aplica uma configuração local customizada.
FROM redis:alpine

# Copia a configuração local do Redis para dentro do container
COPY redis.conf /usr/local/etc/redis/redis.conf

# Expõe a porta padrão do Redis
EXPOSE 6379

# Inicia o Redis com o arquivo de configuração personalizado
CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]
