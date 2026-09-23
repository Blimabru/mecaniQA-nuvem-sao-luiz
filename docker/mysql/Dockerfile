# Dockerfile específico para o banco de dados MySQL da aplicação MecaniQA.
#
# Esta imagem é baseada na distribuição oficial do MySQL 8.0 e foi estruturada
# para atender ao requisito de isolamento do serviço de persistência de dados.
# O objetivo é manter o banco em um contêiner dedicado, com configuração mínima
# e ambiente operacional previsível para uso em desenvolvimento, testes e
# orquestração local.
FROM mysql:8.0

# Definição das variáveis de ambiente do banco de dados.
# MYSQL_DATABASE define o nome da base de dados inicial criada no processo de
# inicialização do contêiner; MYSQL_ROOT_PASSWORD define a credencial do usuário
# administrativo do sistema.
ENV MYSQL_DATABASE=mecaniqa
ENV MYSQL_ROOT_PASSWORD=root

# Exportação da porta padrão do serviço de banco de dados.
# A porta 3306 é a interface de comunicação padrão do MySQL e deve permanecer
# acessível para a aplicação Java e para operações de administração local.
EXPOSE 3306

# Inicialização do processo do banco dentro do contêiner.
# O comando mysqld é o processo principal do MySQL e deve permanecer em primeiro
# plano para manter o container em execução.
CMD ["mysqld"]
