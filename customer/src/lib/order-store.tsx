"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { ApiOrder, OrderStatus, fetchOrderById } from "@/lib/api";

export type { OrderStatus };

export interface TrackedOrderItem {
    name: string;
    qty: number;
    price: number;
}

export interface TrackedOrder {
    id: string;
    token: string;
    items: TrackedOrderItem[];
    total: number;
    paymentMethod: "online" | "book";
    status: OrderStatus;
    placedAt: string; // ISO string
}

interface OrderStoreContextType {
    orders: TrackedOrder[];
    addOrder: (order: ApiOrder) => void;
    updateOrderStatus: (id: string, status: OrderStatus) => void;
    refreshOrder: (id: string) => Promise<void>;
}

const OrderStoreContext = createContext<OrderStoreContextType | null>(null);

// We only persist the order IDs to localStorage; the live state comes from the API.
const ORDER_IDS_KEY = "cafeteria_order_ids";

function apiOrderToTracked(o: ApiOrder): TrackedOrder {
    return {
        id: o.id,
        token: o.token,
        items: o.items.map((i) => ({ name: i.name, qty: i.qty, price: i.price })),
        total: o.total,
        paymentMethod: o.paymentMethod,
        status: o.status,
        placedAt: o.placedAt,
    };
}

export function OrderStoreProvider({ children }: { children: React.ReactNode }) {
    const [orders, setOrders] = useState<TrackedOrder[]>([]);

    // On mount: reload orders from the API using stored IDs
    useEffect(() => {
        async function loadOrders() {
            try {
                const raw = localStorage.getItem(ORDER_IDS_KEY);
                if (!raw) return;
                const ids: string[] = JSON.parse(raw);
                const results = await Promise.all(ids.map((id) => fetchOrderById(id)));
                const valid = results.filter(Boolean) as ApiOrder[];
                setOrders(valid.map(apiOrderToTracked));
            } catch {
                // ignore errors on load
            }
        }
        loadOrders();
    }, []);

    const addOrder = useCallback((apiOrder: ApiOrder) => {
        const tracked = apiOrderToTracked(apiOrder);
        setOrders((prev) => {
            const next = [tracked, ...prev];
            // Persist IDs
            localStorage.setItem(ORDER_IDS_KEY, JSON.stringify(next.map((o) => o.id)));
            return next;
        });
    }, []);

    const updateOrderStatus = useCallback((id: string, status: OrderStatus) => {
        setOrders((prev) => prev.map((o) => (o.id === id ? { ...o, status } : o)));
    }, []);

    const refreshOrder = useCallback(async (id: string) => {
        const apiOrder = await fetchOrderById(id);
        if (!apiOrder) return;
        setOrders((prev) =>
            prev.map((o) => (o.id === id ? apiOrderToTracked(apiOrder) : o))
        );
    }, []);

    return (
        <OrderStoreContext.Provider value={{ orders, addOrder, updateOrderStatus, refreshOrder }}>
            {children}
        </OrderStoreContext.Provider>
    );
}

export function useOrderStore() {
    const ctx = useContext(OrderStoreContext);
    if (!ctx) throw new Error("useOrderStore must be within OrderStoreProvider");
    return ctx;
}
