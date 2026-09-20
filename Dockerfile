# Dockerfile da aplicação Java da MecaniQA.
# Essa imagem empacota o backend e o executa em um container isolado.
FROM eclipse-temurin:17-jdk-alpine

# Diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo JAR gerado pela aplicação para dentro da imagem.
# O arquivo app.jar deve existir na raiz do projeto antes do build.
COPY app.jar /app/app.jar

# Expõe a porta da aplicação para comunicação externa
EXPOSE 8080

# Comando de inicialização da API Java
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
