# Usa uma imagem base otimizada e leve do JDK 17
FROM eclipse-temurin:17-jdk-alpine

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o pacote JAR da aplicação para dentro do container
# (Assumimos que o JAR chama-se app.jar. Adapte o caminho caso necessário)
COPY app.jar app.jar

# Expõe a porta que a aplicação Java vai escutar
EXPOSE 8080

# Comando para manter o container rodando no primeiro plano e iniciar a aplicação
CMD ["java", "-jar", "app.jar"]
