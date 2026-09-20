# Dockerfile específico para o banco MySQL da aplicação.
# Baseia-se na imagem oficial do MySQL 8.0 e configura o banco da MecaniQA.
FROM mysql:8.0

# Variáveis de ambiente do banco
ENV MYSQL_DATABASE=mecaniqa
ENV MYSQL_ROOT_PASSWORD=root

# Expõe a porta padrão do MySQL
EXPOSE 3306

# Inicializa o banco em modo padrão do container
CMD ["mysqld"]
