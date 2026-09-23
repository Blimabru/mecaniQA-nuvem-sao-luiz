package com.mecaniqa;

/**
 * Aplicação Java genérica para validação da infraestrutura da MecaniQA Tech.
 *
 * Esta classe foi concebida como um artefato de teste para demonstrar a execução
 * mínima de uma API em um ambiente containerizado. O objetivo principal é validar
 * a disponibilidade do processo Java, a exposição de portas e a resposta HTTP em
 * ambiente de desenvolvimento e integração contínua.
 *
 * A implementação foi deliberadamente mantida simples para reduzir dependências e
 * permitir a execução com o Java Runtime Environment padrão, sem a necessidade de
 * frameworks adicionais. Isso facilita a verificação de comportamento em Docker,
 * Docker Compose e Kubernetes.
 */

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;

import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.concurrent.Executors;

/**
 * Classe principal da aplicação.
 *
 * O método principal é o ponto de entrada exigido pela máquina virtual Java.
 * A execução do processo em primeiro plano é essencial para manter o container
 * ativo e permitir que o orquestrador e os clientes realizem requisições HTTP.
 */
public class App {

    /**
     * Nome funcional do serviço representado por este artefato de teste.
     *
     * A nomenclatura acompanha o contexto da MecaniQA: uma plataforma de gestão
     * e diagnóstico automotivo destinada a oficinas mecânicas.
     */
    private static final String SERVICE_NAME = "MecaniQA - API de Gestão e Diagnóstico Automotivo";

    /**
     * Porta padrão da API.
     *
     * O valor pode ser sobrescrito por meio da variável de ambiente SERVER_PORT,
     * preservando a portabilidade do artefato em diferentes contextos de execução.
     */
    private static final int PORT = Integer.parseInt(
            System.getenv().getOrDefault("SERVER_PORT", "8080")
    );

    /**
     * Método principal da JVM.
     *
     * Este método é obrigatório em qualquer aplicação executável. Quando a mesma
     * é iniciada por meio de "java -jar", a JVM procura explicitamente por esse
     * ponto de entrada e mantém o processo ativo enquanto o servidor HTTP estiver
     * em execução.
     */
    public static void main(String[] args) throws IOException {
        // O HttpServer é uma classe nativa do JDK que permite criar um servidor HTTP
        // leve, sem depender de bibliotecas externas. Esse modelo é suficiente para
        // validar a infraestrutura de rede, exposição de portas e resposta de serviço.
        HttpServer server = HttpServer.create(new InetSocketAddress(PORT), 0);

        // As rotas comumente utilizadas em testes de infraestrutura são registradas
        // neste ponto. A raiz fornece uma resposta simples e a rota /health permite
        // verificação por orquestradores e sistemas de monitoramento.
        server.createContext("/", App::handleRootRequest);
        server.createContext("/health", App::handleHealthRequest);

        // O executor determina quantas threads atenderão requisições concorrentes.
        // Esse componente é necessário para evitar bloqueios em cenários com múltiplos
        // acessos simultâneos ao container.
        server.setExecutor(Executors.newFixedThreadPool(4));

        // O processo é iniciado para permanecer em execução durante toda a vida útil do
        // contêiner. Em ambientes Docker e Kubernetes, esse comportamento é necessário
        // para que o contêiner permaneça saudável e acessível.
        server.start();

        System.out.println("=============================================================");
        System.out.println("API de Gestão e Diagnóstico Automotivo da MecaniQA está em execução.");
        System.out.println("Escutando na porta: " + PORT);
        System.out.println("Endpoints:");
        System.out.println("  - http://localhost:" + PORT + "/");
        System.out.println("  - http://localhost:" + PORT + "/health");
        System.out.println("=============================================================");
    }

    /**
     * Manipula a rota raiz da API.
     *
     * Esta rota retorna uma mensagem de boas-vindas e valida a disponibilidade do
     * serviço em um nível mínimo de infraestrutura. Em um ambiente real, a raiz pode
     * ser utilizada para documentação pública ou indicadores gerais de sistema.
     */
    private static void handleRootRequest(HttpExchange exchange) throws IOException {
        String responseBody = buildResponse(SERVICE_NAME, "OK", "Endpoint principal disponível.");
        sendJsonResponse(exchange, 200, responseBody);
    }

    /**
     * Manipula a rota de saúde do serviço.
     *
     * A rota /health é amplamente utilizada por orquestradores, balanceadores e
     * ferramentas de monitoramento para verificar disponibilidade. O retorno deve
     * ser rápido, estável e independente de contextos externos para reduzir falsos
     * negativos.
     */
    private static void handleHealthRequest(HttpExchange exchange) throws IOException {
        String responseBody = buildResponse(SERVICE_NAME, "UP", "Serviço disponível e saudável.");
        sendJsonResponse(exchange, 200, responseBody);
    }

    /**
     * Produz um payload JSON de resposta.
     *
     * O uso de variáveis de ambiente permite que a aplicação adapte seu estado de
     * execução ao contexto do contêiner sem exigir alterações no código-fonte. Este
     * mecanismo é relevante para comunicação com banco de dados e cache.
     */
    private static String buildResponse(String service, String status, String detail) {
        Map<String, String> environment = System.getenv();

        String datasourceUrl = environment.getOrDefault("SPRING_DATASOURCE_URL", "jdbc:mysql://db:3306/mecaniqa");
        String redisHost = environment.getOrDefault("SPRING_REDIS_HOST", "redis");
        String redisPort = environment.getOrDefault("SPRING_REDIS_PORT", "6379");

        return String.format(
                "{\n" +
                        "  \"service\": \"%s\",\n" +
                        "  \"status\": \"%s\",\n" +
                        "  \"detail\": \"%s\",\n" +
                        "  \"port\": %d,\n" +
                        "  \"database\": \"%s\",\n" +
                        "  \"redis\": \"%s:%s\"\n" +
                        "}\n",
                service,
                status,
                detail,
                PORT,
                datasourceUrl,
                redisHost,
                redisPort
        );
    }

    /**
     * Envia uma resposta HTTP em formato JSON.
     *
     * A definição explícita do tipo de conteúdo e do código de status é essencial
     * para interoperabilidade com clientes HTTP e ferramentas de observabilidade.
     * A conversão para bytes em UTF-8 preserva compatibilidade com caracteres
     * especiais e conteúdo textual internacionalizado.
     */
    private static void sendJsonResponse(HttpExchange exchange, int statusCode, String body) throws IOException {
        byte[] responseBytes = body.getBytes(StandardCharsets.UTF_8);

        exchange.getResponseHeaders().set("Content-Type", "application/json; charset=UTF-8");
        exchange.sendResponseHeaders(statusCode, responseBytes.length);

        try (OutputStream outputStream = exchange.getResponseBody()) {
            outputStream.write(responseBytes);
        }
    }
}
