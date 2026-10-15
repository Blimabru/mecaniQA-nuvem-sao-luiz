# Dockerfile da aplicação Java da MecaniQA.
#
# Este arquivo é responsável por empacotar a aplicação em um container isolado,
# preservando o comportamento esperado em cenários de desenvolvimento, teste e
# orquestração com Kubernetes. A imagem base escolhida é leve e compatível com
# a execução de aplicações Java em ambientes de produção e laboratório.
FROM eclipse-temurin:17-jdk-alpine

# Diretório de trabalho do contêiner.
# Todos os arquivos referenciados pela aplicação são organizados dentro deste
# caminho para manter o ambiente de execução previsível e isolado.
WORKDIR /app

# Copia o artefato compilado para o interior do contêiner.
# O arquivo app.jar é o resultado da compilação da aplicação Java e representa o
# binário executável utilizado pela JVM para iniciar a API em primeiro plano.
COPY build/app.jar /app/app.jar

# Expõe a porta da aplicação para permitir comunicação com o host e com outros
# serviços da rede interna definida pelo Docker Compose ou pelo Kubernetes.
EXPOSE 8080

# Comando de inicialização da aplicação Java.
# A JVM executa o arquivo JAR e mantém o processo ativo, o que é essencial para
# que o contêiner permaneça em execução e acessível.
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
