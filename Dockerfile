# Usa uma imagem leve com JDK 17 para executar a aplicação.
FROM eclipse-temurin:17-jdk-alpine

# Define o diretório de trabalho do contêiner.
WORKDIR /app

# Copia o pacote JAR para o contêiner.
COPY app.jar app.jar

# Documenta a porta utilizada pela API.
EXPOSE 8080

# Inicia a aplicação Java em primeiro plano.
CMD ["java", "-jar", "app.jar"]
