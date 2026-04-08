"use client";

import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  ChefHat,
  CheckCircle2,
  Clock,
  Flame,
  IndianRupee,
  Package,
  Bell,
  RefreshCw,
  Circle,
  TrendingUp,
  LayoutGrid,
  List,
  Wifi,
  WifiOff,
} from "lucide-react";
import { ThemeToggle } from "@/components/ThemeToggle";
import { cn } from "@/lib/utils";
import {
  ApiOrder,
  OrderStatus,
  fetchAllOrders,
  advanceOrderStatus,
  streamAllOrders,
} from "@/lib/api";

const statusCfg: Record<
  OrderStatus,
  {
    label: string;
    color: string;
    bg: string;
    border: string;
    icon: React.ElementType;
    next: OrderStatus | null;
    nextLabel: string | null;
    actionColor: string;
  }
> = {
  pending: {
    label: "Pending",
    color: "text-amber-400",
    bg: "bg-amber-400/10",
    border: "border-amber-400/20",
    icon: Clock,
    next: "preparing",
    nextLabel: "Start Preparing",
    actionColor: "bg-blue-500 hover:bg-blue-600 text-white",
  },
  preparing: {
    label: "Preparing",
    color: "text-blue-400",
    bg: "bg-blue-400/10",
    border: "border-blue-400/20",
    icon: Flame,
    next: "ready",
    nextLabel: "Mark Ready",
    actionColor: "bg-emerald-500 hover:bg-emerald-600 text-white",
  },
  ready: {
    label: "Ready for Pickup",
    color: "text-emerald-400",
    bg: "bg-emerald-400/10",
    border: "border-emerald-400/20",
    icon: CheckCircle2,
    next: null,
    nextLabel: null,
    actionColor: "",
  },
};

const filterTabs: { id: OrderStatus | "all"; label: string }[] = [
  { id: "all", label: "All" },
  { id: "pending", label: "Pending" },
  { id: "preparing", label: "Preparing" },
  { id: "ready", label: "Ready" },
];

export default function MerchantDashboard() {
  const [orders, setOrders] = useState<ApiOrder[]>([]);
  const [activeTab, setActiveTab] = useState<OrderStatus | "all">("all");
  const [justUpdated, setJustUpdated] = useState<string | null>(null);
  const [newOrderAlert, setNewOrderAlert] = useState(false);
  const [viewMode, setViewMode] = useState<"list" | "grid">("list");
  const [connected, setConnected] = useState(false);
  const [advancing, setAdvancing] = useState<string | null>(null);

  // ── Initial fetch + SSE subscription ────────────────────────────────────────
  useEffect(() => {
    // Fetch existing orders on mount
    fetchAllOrders()
      .then((data) => setOrders(data))
      .catch(() => {/* server might not be up yet; SSE snapshot will cover it */ });

    // Subscribe to real-time events
    const unsubscribe = streamAllOrders({
      onSnapshot: (snapshotOrders) => {
        setOrders(snapshotOrders);
        setConnected(true);
      },
      onNewOrder: (order) => {
        setOrders((prev) => {
          if (prev.some((o) => o.id === order.id)) return prev;
          return [order, ...prev];
        });
        setNewOrderAlert(true);
        setTimeout(() => setNewOrderAlert(false), 3000);
      },
      onOrderUpdated: (updated) => {
        setOrders((prev) =>
          prev.map((o) => (o.id === updated.id ? updated : o))
        );
        setJustUpdated(updated.id);
        setTimeout(() => setJustUpdated(null), 1000);
      },
      onConnectionChange: setConnected,
    });

    return unsubscribe;
  }, []);

  // ── Advance status via API ────────────────────────────────────────────────────
  const handleAdvance = useCallback(async (id: string) => {
    setAdvancing(id);
    try {
      const updated = await advanceOrderStatus(id);
      // The SSE event will update state, but also update optimistically
      setOrders((prev) => prev.map((o) => (o.id === updated.id ? updated : o)));
      setJustUpdated(id);
      setTimeout(() => setJustUpdated(null), 1000);
    } catch {
      // Ignore — SSE will keep state consistent
    } finally {
      setAdvancing(null);
    }
  }, []);

  const filtered =
    activeTab === "all" ? orders : orders.filter((o) => o.status === activeTab);

  const stats = {
    total: orders.length,
    pending: orders.filter((o) => o.status === "pending").length,
    preparing: orders.filter((o) => o.status === "preparing").length,
    ready: orders.filter((o) => o.status === "ready").length,
    revenue: orders
      .filter((o) => o.paymentMethod === "online")
      .reduce((s, o) => s + o.total, 0),
    pendingRevenue: orders
      .filter((o) => o.paymentMethod === "book")
      .reduce((s, o) => s + o.total, 0),
  };

  return (
    <div className="min-h-screen bg-background text-foreground font-sans">
      {/* Sticky Header */}
      <header className="sticky top-0 z-40 bg-background/90 backdrop-blur-xl border-b border-border px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-orange-500/80 to-orange-600 flex items-center justify-center shadow-lg shadow-orange-500/20">
            <ChefHat className="w-5 h-5 text-white" />
          </div>
          <div>
            <p className="text-[11px] text-muted-foreground leading-none">Campus Cafeteria</p>
            <h1 className="text-base font-bold leading-tight">Merchant Dashboard</h1>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {/* Connection indicator */}
          <div
            className={cn(
              "flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-semibold border transition-colors",
              connected
                ? "bg-emerald-400/10 border-emerald-400/20 text-emerald-400"
                : "bg-red-400/10 border-red-400/20 text-red-400"
            )}
          >
            {connected ? (
              <Wifi className="w-3 h-3" />
            ) : (
              <WifiOff className="w-3 h-3" />
            )}
            {connected ? "Live" : "Offline"}
          </div>

          {/* New order alert bell */}
          <motion.div
            animate={newOrderAlert ? { rotate: [0, -15, 15, -10, 10, 0] } : {}}
            transition={{ duration: 0.5 }}
            className={cn(
              "relative w-9 h-9 rounded-full border flex items-center justify-center transition-colors",
              newOrderAlert
                ? "bg-amber-400/20 border-amber-400/40 text-amber-400"
                : "bg-neutral-900/50 border-border text-muted-foreground"
            )}
          >
            <Bell className="w-4 h-4" />
            {stats.pending > 0 && (
              <span className="absolute -top-1 -right-1 min-w-[16px] h-4 px-1 bg-red-500 text-white text-[9px] font-bold flex items-center justify-center rounded-full border border-background">
                {stats.pending}
              </span>
            )}
          </motion.div>
          <ThemeToggle />
        </div>
      </header>

      {/* New order toast */}
      <AnimatePresence>
        {newOrderAlert && (
          <motion.div
            initial={{ y: -60, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: -60, opacity: 0 }}
            className="fixed top-16 left-1/2 -translate-x-1/2 z-50 bg-amber-500 text-black font-bold text-sm px-5 py-2.5 rounded-full shadow-xl flex items-center gap-2"
          >
            <Bell className="w-4 h-4" /> New order arrived!
          </motion.div>
        )}
      </AnimatePresence>

      <main className="p-4 space-y-5 max-w-2xl mx-auto pb-10">
        {/* Revenue + Stats Grid */}
        <div className="grid grid-cols-2 gap-3">
          {/* Revenue card */}
          <div className="col-span-2 p-5 rounded-2xl bg-gradient-to-br from-orange-500/15 via-orange-500/8 to-transparent border border-orange-500/20 flex items-center justify-between">
            <div>
              <p className="text-xs text-muted-foreground font-semibold uppercase tracking-widest mb-1">
                Today&apos;s Revenue
              </p>
              <p className="text-4xl font-black text-foreground">₹{stats.revenue}</p>
              <p className="text-[11px] text-muted-foreground mt-1.5 flex items-center gap-1.5">
                <span className="text-orange-400 font-semibold">
                  ₹{stats.pendingRevenue} pending
                </span>
                · {orders.filter((o) => o.paymentMethod === "online").length} paid orders
              </p>
            </div>
            <div className="w-14 h-14 rounded-2xl bg-orange-500/15 flex items-center justify-center border border-orange-500/20">
              <IndianRupee className="w-7 h-7 text-orange-400" />
            </div>
          </div>

          {/* Stat cards */}
          {[
            { label: "Total Orders", value: stats.total, icon: Package, color: "text-purple-400", bg: "bg-purple-400/10", border: "border-purple-400/10" },
            { label: "Pending", value: stats.pending, icon: Clock, color: "text-amber-400", bg: "bg-amber-400/10", border: "border-amber-400/10" },
            { label: "Preparing", value: stats.preparing, icon: Flame, color: "text-blue-400", bg: "bg-blue-400/10", border: "border-blue-400/10" },
            { label: "Ready", value: stats.ready, icon: CheckCircle2, color: "text-emerald-400", bg: "bg-emerald-400/10", border: "border-emerald-400/10" },
          ].map((s) => (
            <div key={s.label} className={`p-4 rounded-2xl border ${s.bg} ${s.border} flex items-center gap-3`}>
              <div className={`w-10 h-10 rounded-xl ${s.bg} flex items-center justify-center border ${s.border}`}>
                <s.icon className={`w-5 h-5 ${s.color}`} />
              </div>
              <div>
                <p className="text-2xl font-black">{s.value}</p>
                <p className="text-[11px] text-muted-foreground">{s.label}</p>
              </div>
            </div>
          ))}

          {/* Avg order trend indicator */}
          <div className="col-span-2 p-3 rounded-xl bg-neutral-900/40 border border-white/5 flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <TrendingUp className="w-4 h-4 text-emerald-400" />
              <span>Avg. order value</span>
            </div>
            <span className="font-bold text-foreground">
              ₹{orders.length ? Math.round(orders.reduce((s, o) => s + o.total, 0) / orders.length) : 0}
            </span>
          </div>
        </div>

        {/* Filter tabs + view toggle */}
        <div className="flex items-center justify-between gap-3">
          <div className="flex gap-2 overflow-x-auto pb-1 no-scrollbar flex-1">
            {filterTabs.map((tab) => {
              const count =
                tab.id === "all"
                  ? orders.length
                  : orders.filter((o) => o.status === tab.id).length;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={cn(
                    "flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-sm font-semibold whitespace-nowrap transition-all shrink-0",
                    activeTab === tab.id
                      ? "bg-orange-500 text-white shadow-lg shadow-orange-500/20"
                      : "bg-muted text-muted-foreground hover:bg-muted/80"
                  )}
                >
                  {tab.label}
                  <span
                    className={cn(
                      "text-[10px] font-bold w-4 h-4 rounded-full flex items-center justify-center",
                      activeTab === tab.id ? "bg-white/25" : "bg-neutral-700"
                    )}
                  >
                    {count}
                  </span>
                </button>
              );
            })}
          </div>

          {/* View mode toggle */}
          <div className="flex shrink-0 bg-muted rounded-lg p-0.5 border border-border">
            <button
              onClick={() => setViewMode("list")}
              className={cn("p-1.5 rounded-md transition-colors", viewMode === "list" ? "bg-background shadow text-foreground" : "text-muted-foreground")}
            >
              <List className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode("grid")}
              className={cn("p-1.5 rounded-md transition-colors", viewMode === "grid" ? "bg-background shadow text-foreground" : "text-muted-foreground")}
            >
              <LayoutGrid className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Orders */}
        <div className={cn("gap-3", viewMode === "grid" ? "grid grid-cols-2" : "flex flex-col")}>
          <AnimatePresence>
            {filtered.length === 0 ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="col-span-2 text-center py-16 text-muted-foreground"
              >
                <RefreshCw className="w-8 h-8 mx-auto mb-3 opacity-25" />
                <p>{connected ? "No orders in this category" : "Connecting to server…"}</p>
              </motion.div>
            ) : (
              filtered.map((order) => {
                const cfg = statusCfg[order.status];
                const StatusIcon = cfg.icon;
                const isAdvancing = advancing === order.id;
                return (
                  <motion.div
                    key={order.id}
                    layout
                    initial={{ opacity: 0, y: -8 }}
                    animate={{
                      opacity: 1,
                      y: 0,
                      scale: justUpdated === order.id ? [1, 1.02, 1] : 1,
                    }}
                    exit={{ opacity: 0, x: 30 }}
                    transition={{ duration: 0.2 }}
                    className={cn("p-4 rounded-2xl border transition-colors", cfg.bg, cfg.border)}
                  >
                    {/* Order header */}
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-2.5">
                        <div className="w-11 h-11 rounded-xl bg-background/60 border border-border flex flex-col items-center justify-center">
                          <span className="text-[9px] text-muted-foreground leading-none">TOKEN</span>
                          <span className="text-base font-black text-foreground leading-tight">#{order.token}</span>
                        </div>
                        <div>
                          <p className="text-[11px] text-muted-foreground">
                            {new Date(order.placedAt).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })}
                          </p>
                          <span className={cn("inline-flex items-center gap-1 text-[11px] font-semibold", cfg.color)}>
                            <Circle className="w-1.5 h-1.5 fill-current" />
                            {cfg.label}
                          </span>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-foreground text-base">₹{order.total}</p>
                        <span
                          className={cn(
                            "text-[10px] font-semibold px-2 py-0.5 rounded-full",
                            order.paymentMethod === "online"
                              ? "bg-emerald-400/15 text-emerald-400"
                              : "bg-orange-400/15 text-orange-400"
                          )}
                        >
                          {order.paymentMethod === "online" ? "✓ Paid" : "Pay Later"}
                        </span>
                      </div>
                    </div>

                    {/* Items */}
                    <div className={cn("space-y-0.5 mb-3", viewMode === "grid" && "hidden sm:block")}>
                      {order.items.map((item, i) => (
                        <div key={i} className="flex justify-between text-xs text-muted-foreground">
                          <span>{item.qty}× {item.name}</span>
                          <span className="font-medium">₹{item.qty * item.price}</span>
                        </div>
                      ))}
                    </div>
                    {viewMode === "grid" && (
                      <p className="text-xs text-muted-foreground mb-3 sm:hidden">
                        {order.items.reduce((s, i) => s + i.qty, 0)} item(s)
                      </p>
                    )}

                    {/* Action */}
                    {cfg.next ? (
                      <button
                        onClick={() => handleAdvance(order.id)}
                        disabled={isAdvancing}
                        className={cn(
                          "w-full py-2.5 rounded-xl text-sm font-bold flex items-center justify-center gap-2 transition-all active:scale-95 disabled:opacity-60 disabled:cursor-not-allowed",
                          cfg.actionColor
                        )}
                      >
                        <StatusIcon className={cn("w-4 h-4", isAdvancing && "animate-spin")} />
                        {isAdvancing ? "Updating…" : cfg.nextLabel}
                      </button>
                    ) : (
                      <div className="py-2.5 rounded-xl text-sm font-bold flex items-center justify-center gap-2 bg-emerald-400/10 text-emerald-400 border border-emerald-400/20">
                        <CheckCircle2 className="w-4 h-4" />
                        Ready for Pickup
                      </div>
                    )}
                  </motion.div>
                );
              })
            )}
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
}
