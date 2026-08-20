import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;

public class StoreService {
    public static void main(String[] args) throws Exception {
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 8080), 0);
        server.createContext("/api/java/health", StoreService::health);
        server.createContext("/api/java/order", StoreService::order);
        server.setExecutor(null);
        System.out.println("Java service running at http://127.0.0.1:8080");
        server.start();
    }

    private static void health(HttpExchange ex) throws IOException {
        addCors(ex);
        if (!"GET".equalsIgnoreCase(ex.getRequestMethod())) {
            sendJson(ex, 405, "{\"error\":\"GET required\"}");
            return;
        }
        sendJson(ex, 200, "{\"ok\":true,\"service\":\"java-store-service\"}");
    }

    private static void order(HttpExchange ex) throws IOException {
        addCors(ex);
        if ("OPTIONS".equalsIgnoreCase(ex.getRequestMethod())) {
            ex.sendResponseHeaders(204, -1);
            return;
        }
        if (!"POST".equalsIgnoreCase(ex.getRequestMethod())) {
            sendJson(ex, 405, "{\"error\":\"POST required\"}");
            return;
        }

        byte[] body = ex.getRequestBody().readAllBytes();
        String requestBody = new String(body, StandardCharsets.UTF_8);
        System.out.println("New order notification: " + requestBody);

        sendJson(ex, 200,
            "{\"ok\":true,\"message\":\"Order received by Java service\",\"payloadLength\":"
                + requestBody.length() + "}");
    }

    private static void addCors(HttpExchange ex) {
        ex.getResponseHeaders().set("Access-Control-Allow-Origin", "*");
        ex.getResponseHeaders().set("Access-Control-Allow-Methods", "GET,POST,OPTIONS");
        ex.getResponseHeaders().set("Access-Control-Allow-Headers", "Content-Type");
    }

    private static void sendJson(HttpExchange ex, int status, String body) throws IOException {
        byte[] out = body.getBytes(StandardCharsets.UTF_8);
        ex.getResponseHeaders().set("Content-Type", "application/json; charset=utf-8");
        ex.sendResponseHeaders(status, out.length);
        try (OutputStream os = ex.getResponseBody()) {
            os.write(out);
        }
    }
}
