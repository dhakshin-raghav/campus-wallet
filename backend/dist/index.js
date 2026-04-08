"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const cors_1 = __importDefault(require("cors"));
const app = (0, express_1.default)();
const PORT = 4000;
// ─── CORS ───────────────────────────────────────────────────────────────────
app.use((0, cors_1.default)({
    origin: ["http://localhost:3000", "http://localhost:3001"],
    methods: ["GET", "POST", "PATCH", "OPTIONS"],
    allowedHeaders: ["Content-Type"],
}));
app.use(express_1.default.json());
// ─── In-memory store ─────────────────────────────────────────────────────────
let orders = [];
let tokenCounter = 100;
function nextToken() {
    return String(tokenCounter++);
}
// ─── SSE Clients ─────────────────────────────────────────────────────────────
// Merchant: streams ALL order events
const merchantClients = new Set();
// User: streams events for a specific order
const userClients = new Map(); // orderId → set of responses
function broadcastToMerchant(event, data) {
    const payload = `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`;
    for (const res of merchantClients) {
        res.write(payload);
    }
}
function broadcastToUser(orderId, event, data) {
    const clients = userClients.get(orderId);
    if (!clients)
        return;
    const payload = `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`;
    for (const res of clients) {
        res.write(payload);
    }
}
// ─── Routes ──────────────────────────────────────────────────────────────────
// POST /api/orders — place a new order
app.post("/api/orders", (req, res) => {
    const { items, total, paymentMethod } = req.body;
    if (!items || !Array.isArray(items) || items.length === 0) {
        res.status(400).json({ error: "items is required" });
        return;
    }
    if (typeof total !== "number" || total <= 0) {
        res.status(400).json({ error: "total must be a positive number" });
        return;
    }
    if (paymentMethod !== "online" && paymentMethod !== "book") {
        res.status(400).json({ error: "paymentMethod must be 'online' or 'book'" });
        return;
    }
    const order = {
        id: `order-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
        token: nextToken(),
        items,
        total,
        paymentMethod,
        status: "pending",
        placedAt: new Date().toISOString(),
    };
    orders.push(order);
    // Notify merchant clients
    broadcastToMerchant("new_order", order);
    res.status(201).json(order);
});
// GET /api/orders — list all orders (merchant)
app.get("/api/orders", (_req, res) => {
    res.json(orders);
});
// ── SSE ROUTES MUST COME BEFORE /:id WILDCARD ROUTES ─────────────────────────
// GET /api/orders/stream — SSE for merchant dashboard (all events)
app.get("/api/orders/stream", (req, res) => {
    res.setHeader("Content-Type", "text/event-stream");
    res.setHeader("Cache-Control", "no-cache");
    res.setHeader("Connection", "keep-alive");
    res.flushHeaders();
    // Send current orders as initial snapshot
    res.write(`event: snapshot\ndata: ${JSON.stringify(orders)}\n\n`);
    merchantClients.add(res);
    // Keep-alive ping every 25 seconds
    const ping = setInterval(() => {
        res.write(": ping\n\n");
    }, 25000);
    req.on("close", () => {
        merchantClients.delete(res);
        clearInterval(ping);
    });
});
// GET /api/orders/:id/stream — SSE for user tracking one order
app.get("/api/orders/:id/stream", (req, res) => {
    const { id } = req.params;
    const order = orders.find((o) => o.id === id);
    res.setHeader("Content-Type", "text/event-stream");
    res.setHeader("Cache-Control", "no-cache");
    res.setHeader("Connection", "keep-alive");
    res.flushHeaders();
    if (order) {
        // Send current status immediately
        res.write(`event: status_changed\ndata: ${JSON.stringify({ status: order.status })}\n\n`);
    }
    if (!userClients.has(id)) {
        userClients.set(id, new Set());
    }
    userClients.get(id).add(res);
    const ping = setInterval(() => {
        res.write(": ping\n\n");
    }, 25000);
    req.on("close", () => {
        userClients.get(id)?.delete(res);
        clearInterval(ping);
    });
});
// GET /api/orders/:id — get a single order (AFTER stream routes)
app.get("/api/orders/:id", (req, res) => {
    const order = orders.find((o) => o.id === req.params.id);
    if (!order) {
        res.status(404).json({ error: "order not found" });
        return;
    }
    res.json(order);
});
// PATCH /api/orders/:id/status — merchant advances status
app.patch("/api/orders/:id/status", (req, res) => {
    const order = orders.find((o) => o.id === req.params.id);
    if (!order) {
        res.status(404).json({ error: "order not found" });
        return;
    }
    const statusFlow = {
        pending: "preparing",
        preparing: "ready",
        ready: null,
    };
    const nextStatus = statusFlow[order.status];
    if (!nextStatus) {
        res.status(400).json({ error: "order is already in terminal state" });
        return;
    }
    order.status = nextStatus;
    // Notify merchant and the specific user
    broadcastToMerchant("order_updated", order);
    broadcastToUser(order.id, "status_changed", { status: order.status });
    res.json(order);
});
// ─── Health check ─────────────────────────────────────────────────────────────
app.get("/health", (_req, res) => {
    res.json({ ok: true, orders: orders.length });
});
// ─── Start ───────────────────────────────────────────────────────────────────
app.listen(PORT, () => {
    console.log(`\n✅ cafeteria-api running at http://localhost:${PORT}\n`);
});
