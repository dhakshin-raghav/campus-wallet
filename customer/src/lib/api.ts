/**
 * API client for cafeteria-api (http://localhost:4000)
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

// ── Place a new order ────────────────────────────────────────────────────────
export async function placeOrder(
    items: OrderItem[],
    total: number,
    paymentMethod: PaymentMethod
): Promise<ApiOrder> {
    const res = await fetch(`${API_BASE}/api/orders`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ items, total, paymentMethod }),
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error((err as { error?: string }).error ?? "Failed to place order");
    }
    return res.json() as Promise<ApiOrder>;
}

// ── Fetch all orders the user placed (by IDs saved locally) ─────────────────
export async function fetchOrderById(id: string): Promise<ApiOrder | null> {
    const res = await fetch(`${API_BASE}/api/orders/${id}`);
    if (res.status === 404) return null;
    if (!res.ok) throw new Error("Failed to fetch order");
    return res.json() as Promise<ApiOrder>;
}

// ── Subscribe to status changes for one order (SSE) ─────────────────────────
export function streamOrderStatus(
    orderId: string,
    onStatus: (status: OrderStatus) => void,
    onError?: () => void
): () => void {
    const es = new EventSource(`${API_BASE}/api/orders/${orderId}/stream`);
    es.addEventListener("status_changed", (e: MessageEvent) => {
        try {
            const data = JSON.parse(e.data) as { status: OrderStatus };
            onStatus(data.status);
        } catch {
            // ignore parse errors
        }
    });
    es.onerror = () => {
        onError?.();
    };
    return () => es.close();
}
