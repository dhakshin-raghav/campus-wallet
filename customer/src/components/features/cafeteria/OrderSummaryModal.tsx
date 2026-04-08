"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, CheckCircle, Loader2, CreditCard, Ticket, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { FoodItem } from "@/lib/data/cafeteria-items";
import { useOrderStore } from "@/lib/order-store";
import { placeOrder, PaymentMethod } from "@/lib/api";
import Link from "next/link";

interface OrderSummaryModalProps {
    isOpen: boolean;
    onClose: () => void;
    cart: { item: FoodItem; quantity: number }[];
    total: number;
    onOrderPlaced: () => void;
}

export function OrderSummaryModal({ isOpen, onClose, cart, total, onOrderPlaced }: OrderSummaryModalProps) {
    const [step, setStep] = useState<"summary" | "processing" | "success" | "error">("summary");
    const [paymentMethod, setPaymentMethod] = useState<PaymentMethod>("online");
    const [token, setToken] = useState<string>("");
    const [errorMsg, setErrorMsg] = useState<string>("");
    const { addOrder } = useOrderStore();

    useEffect(() => {
        if (isOpen) {
            setStep("summary");
            setErrorMsg("");
        }
    }, [isOpen]);

    const handlePlaceOrder = async (method: PaymentMethod) => {
        setPaymentMethod(method);
        setStep("processing");
        try {
            const apiOrder = await placeOrder(
                cart.map(({ item, quantity }) => ({
                    name: item.name,
                    qty: quantity,
                    price: item.price,
                })),
                total,
                method
            );
            addOrder(apiOrder);
            setToken(apiOrder.token);
            setStep("success");
            onOrderPlaced();
        } catch (err) {
            setErrorMsg(err instanceof Error ? err.message : "Something went wrong");
            setStep("error");
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/80 backdrop-blur-sm p-4">
            <motion.div
                initial={{ opacity: 0, scale: 0.95, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95, y: 20 }}
                className="w-full max-w-md bg-card border border-border rounded-2xl shadow-2xl overflow-hidden"
            >
                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b border-border bg-muted/20">
                    <h2 className="font-bold text-lg">
                        {step === "summary" && "Order Summary"}
                        {step === "processing" && (paymentMethod === "online" ? "Processing Payment…" : "Booking Order…")}
                        {step === "success" && "Order Confirmed! 🎉"}
                        {step === "error" && "Order Failed"}
                    </h2>
                    {step !== "processing" && (
                        <button onClick={onClose} className="p-1.5 hover:bg-muted rounded-full transition-colors">
                            <X className="w-5 h-5" />
                        </button>
                    )}
                </div>

                <div className="p-5">
                    <AnimatePresence mode="wait">
                        {step === "summary" && (
                            <motion.div key="summary" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-4">
                                <div className="space-y-2.5 max-h-56 overflow-y-auto pr-1">
                                    {cart.map(({ item, quantity }) => (
                                        <div key={item.id} className="flex justify-between items-center text-sm">
                                            <div className="flex items-center gap-2">
                                                <div className="w-6 h-6 flex items-center justify-center bg-primary/10 rounded-md text-xs font-bold text-primary">
                                                    {quantity}×
                                                </div>
                                                <span className="text-foreground font-medium">{item.name}</span>
                                            </div>
                                            <span className="font-semibold">₹{item.price * quantity}</span>
                                        </div>
                                    ))}
                                </div>

                                <div className="pt-3 border-t border-border flex justify-between items-center font-bold text-xl">
                                    <span>Total</span>
                                    <span>₹{total}</span>
                                </div>

                                <div className="grid gap-2.5 pt-1">
                                    <Button onClick={() => handlePlaceOrder("online")} className="w-full py-6 text-base font-bold rounded-xl" size="lg">
                                        <CreditCard className="w-5 h-5 mr-2" />
                                        Pay Online · ₹{total}
                                    </Button>
                                    <Button onClick={() => handlePlaceOrder("book")} variant="outline" className="w-full py-6 text-base font-bold rounded-xl" size="lg">
                                        <Ticket className="w-5 h-5 mr-2" />
                                        Book &amp; Pay at Counter
                                    </Button>
                                </div>
                            </motion.div>
                        )}

                        {step === "processing" && (
                            <motion.div key="processing" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                                className="flex flex-col items-center justify-center py-10 space-y-4">
                                <Loader2 className="w-12 h-12 animate-spin text-primary" />
                                <p className="text-muted-foreground text-center text-sm">
                                    {paymentMethod === "online" ? "Contacting payment gateway…" : "Generating your token…"}
                                </p>
                            </motion.div>
                        )}

                        {step === "success" && (
                            <motion.div key="success" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                                className="flex flex-col items-center py-4 space-y-5 text-center">
                                <motion.div
                                    initial={{ scale: 0 }}
                                    animate={{ scale: 1 }}
                                    transition={{ type: "spring", stiffness: 300, damping: 20 }}
                                    className="w-16 h-16 bg-green-500/10 rounded-full flex items-center justify-center border-2 border-green-500/30"
                                >
                                    <CheckCircle className="w-8 h-8 text-green-500" />
                                </motion.div>

                                <div>
                                    <h3 className="text-xl font-bold">
                                        {paymentMethod === "online" ? "Payment Successful!" : "Booking Confirmed!"}
                                    </h3>
                                    <p className="text-muted-foreground text-sm mt-1">
                                        {paymentMethod === "online"
                                            ? "Your order has been sent to the kitchen."
                                            : "Please pay at the counter to collect your order."}
                                    </p>
                                </div>

                                {/* Token display */}
                                <div className="w-full bg-muted rounded-2xl border border-border p-5">
                                    <p className="text-xs uppercase text-muted-foreground font-bold tracking-widest mb-1">Your Token</p>
                                    <p className="text-5xl font-black tracking-widest text-primary">{token}</p>
                                    <p className="text-xs text-muted-foreground mt-2">Show this at the counter when your order is ready</p>
                                </div>

                                <div className="w-full grid gap-2.5">
                                    <Link href="/orders" onClick={onClose} className="w-full">
                                        <Button className="w-full rounded-xl font-bold" size="lg">
                                            Track Order <ArrowRight className="w-4 h-4 ml-1" />
                                        </Button>
                                    </Link>
                                    <Button variant="outline" onClick={onClose} className="w-full rounded-xl">
                                        Back to Menu
                                    </Button>
                                </div>
                            </motion.div>
                        )}

                        {step === "error" && (
                            <motion.div key="error" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                                className="flex flex-col items-center py-8 space-y-4 text-center">
                                <div className="w-14 h-14 bg-red-500/10 rounded-full flex items-center justify-center border-2 border-red-500/20">
                                    <X className="w-7 h-7 text-red-400" />
                                </div>
                                <p className="text-sm text-muted-foreground">{errorMsg || "Could not connect to the server. Please try again."}</p>
                                <Button onClick={() => setStep("summary")} variant="outline" className="w-full rounded-xl">
                                    Try Again
                                </Button>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </motion.div>
        </div>
    );
}
