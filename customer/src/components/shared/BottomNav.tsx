"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, UtensilsCrossed, Ticket } from "lucide-react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { useOrderStore } from "@/lib/order-store";

const items = [
    { href: "/", icon: Home, label: "Home" },
    { href: "/services/cafeteria", icon: UtensilsCrossed, label: "Menu" },
    { href: "/orders", icon: Ticket, label: "My Orders" },
];

export function BottomNav() {
    const pathname = usePathname();
    const { orders } = useOrderStore();
    const activeOrders = orders.filter(o => o.status !== "ready").length;

    return (
        <div className="fixed bottom-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-xl border-t border-border pt-2 px-6 pb-4">
            <div className="flex justify-around items-center max-w-md mx-auto">
                {items.map((item) => {
                    const isActive = pathname === item.href;
                    const badge = item.href === "/orders" && activeOrders > 0;
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={cn(
                                "flex flex-col items-center justify-center space-y-1 relative px-4 py-1 transition-colors",
                                isActive ? "text-primary" : "text-neutral-500 hover:text-neutral-300"
                            )}
                        >
                            {isActive && (
                                <motion.div
                                    layoutId="nav-pill"
                                    className="absolute -top-3 w-8 h-1 bg-primary rounded-full shadow-[0_0_10px_var(--primary)]"
                                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                                />
                            )}
                            <div className="relative">
                                <item.icon className={cn("w-6 h-6", isActive && "drop-shadow-[0_0_5px_rgba(255,255,255,0.5)]")} />
                                {badge && (
                                    <span className="absolute -top-1.5 -right-1.5 w-4 h-4 bg-amber-500 text-white text-[9px] font-bold flex items-center justify-center rounded-full border border-background">
                                        {activeOrders}
                                    </span>
                                )}
                            </div>
                            <span className="text-[10px] font-medium">{item.label}</span>
                        </Link>
                    );
                })}
            </div>
        </div>
    );
}
