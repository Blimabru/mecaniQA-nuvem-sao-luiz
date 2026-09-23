# Dockerfile específico para o serviço de cache Redis da MecaniQA.
#
# Esta imagem utiliza a distribuição oficial leve do Redis para reduzir o peso do
# contêiner e manter o ambiente mínimo necessário para execução do cache em
# memória. A customização da configuração permite adaptar o comportamento do
# serviço ao ambiente de infraestrutura local do laboratório.
FROM redis:alpine

# Cópia do arquivo de configuração personalizada para o contêiner.
# O arquivo redis.conf define parâmetros essenciais de rede e segurança,
# incluindo a interface de bind, a porta de escuta e a política do modo seguro.
COPY redis.conf /usr/local/etc/redis/redis.conf

# Exportação da porta padrão do Redis.
# A porta 6379 é a interface de comunicação do cache e deve estar disponível para
# a aplicação Java e para eventuais verificações locais.
EXPOSE 6379

# Inicialização do serviço Redis com a configuração personalizada.
# O processo redis-server deve continuar em execução em primeiro plano para manter
# o contêiner em estado funcional e acessível ao sistema.
CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]
