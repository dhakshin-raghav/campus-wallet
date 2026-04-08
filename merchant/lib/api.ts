/**
 * API client for cafeteria-api (http://localhost:4000)
 * Used by the cafeteria-merchant dashboard.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://44.213.82.44:8000";

export type OrderStatus = "pending" | "preparing" | "ready";
export type PaymentMethod = "online" | "book";

export interface OrderItem {
    name: string;
    qty: number;
    price: number;
}

export interface ApiOrder {
    id: string;
    token: string;
    items: OrderItem[];
    total: number;
    paymentMethod: PaymentMethod;
    status: OrderStatus;
    placedAt: string;
}

// ── Fetch all orders ─────────────────────────────────────────────────────────
export async function fetchAllOrders(): Promise<ApiOrder[]> {
    const res = await fetch(`${API_BASE}/api/orders`);
    if (!res.ok) throw new Error("Failed to fetch orders");
    return res.json() as Promise<ApiOrder[]>;
}

// ── Advance an order's status ────────────────────────────────────────────────
export async function advanceOrderStatus(id: string): Promise<ApiOrder> {
    const res = await fetch(`${API_BASE}/api/orders/${id}/status`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error((err as { error?: string }).error ?? "Failed to update status");
    }
    return res.json() as Promise<ApiOrder>;
}

// ── Subscribe to all order events (SSE) ─────────────────────────────────────
export function streamAllOrders(callbacks: {
    onSnapshot: (orders: ApiOrder[]) => void;
    onNewOrder: (order: ApiOrder) => void;
    onOrderUpdated: (order: ApiOrder) => void;
    onConnectionChange?: (connected: boolean) => void;
}): () => void {
    let es: EventSource | null = null;
    let retryTimeout: ReturnType<typeof setTimeout> | null = null;

    function connect() {
        es = new EventSource(`${API_BASE}/api/orders/stream`);

        es.addEventListener("snapshot", (e: MessageEvent) => {
            callbacks.onConnectionChange?.(true);
            try {
                callbacks.onSnapshot(JSON.parse(e.data) as ApiOrder[]);
            } catch { /* ignore */ }
        });

        es.addEventListener("new_order", (e: MessageEvent) => {
            try {
                callbacks.onNewOrder(JSON.parse(e.data) as ApiOrder);
            } catch { /* ignore */ }
        });

        es.addEventListener("order_updated", (e: MessageEvent) => {
            try {
                callbacks.onOrderUpdated(JSON.parse(e.data) as ApiOrder);
            } catch { /* ignore */ }
        });

        es.onerror = () => {
            callbacks.onConnectionChange?.(false);
            es?.close();
            // Reconnect after 3 seconds
            retryTimeout = setTimeout(connect, 3000);
        };
    }

    connect();

    return () => {
        if (retryTimeout) clearTimeout(retryTimeout);
        es?.close();
    };
}
