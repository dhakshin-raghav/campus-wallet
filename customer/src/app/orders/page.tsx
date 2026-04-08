"use client";

import { useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Clock, Flame, CheckCircle2, ShoppingBag, Circle, Ticket } from "lucide-react";
import { useOrderStore, TrackedOrder, OrderStatus } from "@/lib/order-store";
import { streamOrderStatus } from "@/lib/api";
import { BottomNav } from "@/components/shared/BottomNav";
import { ThemeToggle } from "@/components/shared/ThemeToggle";
import { cn } from "@/lib/utils";

const statusSteps: { id: OrderStatus; label: string; icon: React.ElementType }[] = [
    { id: "pending", label: "Order Placed", icon: Clock },
    { id: "preparing", label: "Preparing", icon: Flame },
    { id: "ready", label: "Ready!", icon: CheckCircle2 },
];

const statusOrder: OrderStatus[] = ["pending", "preparing", "ready"];

function OrderStatusStepper({ status }: { status: OrderStatus }) {
    const currentIdx = statusOrder.indexOf(status);
    return (
        <div className="flex items-center gap-0 mt-3">
            {statusSteps.map((step, i) => {
                const done = i <= currentIdx;
                const active = i === currentIdx;
                const Icon = step.icon;
                return (
                    <div key={step.id} className="flex items-center flex-1 last:flex-none">
                        <div className="flex flex-col items-center gap-1">
                            <div className={cn(
                                "w-8 h-8 rounded-full flex items-center justify-center border-2 transition-all duration-500",
                                done
                                    ? active
                                        ? "bg-primary border-primary text-primary-foreground shadow-[0_0_12px_var(--primary)]"
                                        : "bg-primary/20 border-primary text-primary"
                                    : "bg-muted border-border text-muted-foreground"
                            )}>
                                {active ? (
                                    <motion.div
                                        animate={{ scale: [1, 1.2, 1] }}
                                        transition={{ duration: 1.5, repeat: Infinity }}
                                    >
                                        <Icon className="w-4 h-4" />
                                    </motion.div>
                                ) : (
                                    <Icon className="w-4 h-4" />
                                )}
                            </div>
                            <span className={cn(
                                "text-[9px] font-semibold whitespace-nowrap",
                                done ? "text-primary" : "text-muted-foreground"
                            )}>
                                {step.label}
                            </span>
                        </div>
                        {i < statusSteps.length - 1 && (
                            <div className={cn(
                                "flex-1 h-0.5 mb-4 mx-1 rounded-full transition-all duration-700",
                                i < currentIdx ? "bg-primary" : "bg-border"
                            )} />
                        )}
                    </div>
                );
            })}
        </div>
    );
}

function OrderCard({ order }: { order: TrackedOrder }) {
    const { updateOrderStatus } = useOrderStore();
    const isReady = order.status === "ready";
    const borderColor = isReady ? "border-emerald-400/30" : order.status === "preparing" ? "border-blue-400/20" : "border-amber-400/20";
    const bgColor = isReady ? "bg-emerald-400/5" : order.status === "preparing" ? "bg-blue-400/5" : "bg-amber-400/5";

    // Subscribe to real-time status updates for this order via SSE
    useEffect(() => {
        if (order.status === "ready") return; // Already terminal — no need to stream
        const unsubscribe = streamOrderStatus(order.id, (status) => {
            updateOrderStatus(order.id, status);
        });
        return unsubscribe;
    }, [order.id, order.status, updateOrderStatus]);

    return (
        <motion.div
            layout
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            className={cn("p-4 rounded-2xl border", bgColor, borderColor)}
        >
            <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                    {/* Token badge */}
                    <div className="w-12 h-12 rounded-xl bg-background/70 border border-border flex flex-col items-center justify-center shrink-0">
                        <span className="text-[8px] text-muted-foreground leading-none font-medium">TOKEN</span>
                        <span className="text-lg font-black text-foreground leading-tight">#{order.token}</span>
                    </div>
                    <div>
                        <p className="text-sm font-semibold text-foreground">
                            {order.items.map(i => `${i.qty}× ${i.name}`).join(", ")}
                        </p>
                        <p className="text-[11px] text-muted-foreground mt-0.5">
                            {new Date(order.placedAt).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })}
                            {" · "}
                            <span className={order.paymentMethod === "online" ? "text-emerald-400" : "text-orange-400"}>
                                {order.paymentMethod === "online" ? "Paid online" : "Pay at counter"}
                            </span>
                        </p>
                    </div>
                </div>
                <p className="font-bold text-foreground shrink-0">₹{order.total}</p>
            </div>

            {/* Stepper */}
            <OrderStatusStepper status={order.status} />

            {isReady && (
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="mt-3 py-2.5 rounded-xl bg-emerald-500/10 border border-emerald-400/20 text-emerald-400 text-sm font-bold flex items-center justify-center gap-2"
                >
                    <CheckCircle2 className="w-4 h-4" />
                    Your order is ready! Show token #{order.token} at the counter.
                </motion.div>
            )}
        </motion.div>
    );
}

export default function MyOrdersPage() {
    const { orders } = useOrderStore();
    const active = orders.filter(o => o.status !== "ready");
    const past = orders.filter(o => o.status === "ready");

    return (
        <div className="min-h-screen bg-background text-foreground pb-28 font-sans">
            <header className="sticky top-0 z-40 bg-background/80 backdrop-blur-md border-b border-border p-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary/60 to-primary flex items-center justify-center">
                        <Ticket className="w-5 h-5 text-primary-foreground" />
                    </div>
                    <div>
                        <h1 className="text-lg font-bold leading-none">My Orders</h1>
                        <p className="text-[11px] text-muted-foreground">Track your food status</p>
                    </div>
                </div>
                <ThemeToggle />
            </header>

            <main className="p-4 space-y-6">
                {orders.length === 0 ? (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="flex flex-col items-center justify-center py-24 gap-4 text-center"
                    >
                        <div className="w-20 h-20 rounded-full bg-muted flex items-center justify-center">
                            <ShoppingBag className="w-10 h-10 text-muted-foreground opacity-40" />
                        </div>
                        <div>
                            <p className="font-bold text-foreground text-lg">No orders yet</p>
                            <p className="text-sm text-muted-foreground mt-1">Your placed orders will appear here</p>
                        </div>
                    </motion.div>
                ) : (
                    <>
                        {active.length > 0 && (
                            <section className="space-y-3">
                                <div className="flex items-center gap-2">
                                    <Circle className="w-2 h-2 fill-amber-400 text-amber-400 animate-pulse" />
                                    <h2 className="text-sm font-bold text-foreground uppercase tracking-wider">Active Orders</h2>
                                </div>
                                <AnimatePresence>
                                    {active.map(o => <OrderCard key={o.id} order={o} />)}
                                </AnimatePresence>
                            </section>
                        )}

                        {past.length > 0 && (
                            <section className="space-y-3">
                                <h2 className="text-sm font-bold text-muted-foreground uppercase tracking-wider">Completed</h2>
                                {past.map(o => <OrderCard key={o.id} order={o} />)}
                            </section>
                        )}
                    </>
                )}
            </main>

            <BottomNav />
        </div>
    );
}
