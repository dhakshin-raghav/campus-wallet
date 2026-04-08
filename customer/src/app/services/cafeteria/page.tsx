"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowLeft, ShoppingBag, Search } from "lucide-react";
import Link from "next/link";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { cafeteriaItems, FoodItem } from "@/lib/data/cafeteria-items";
import { FoodItemCard } from "@/components/features/cafeteria/FoodItemCard";
import { OrderSummaryModal } from "@/components/features/cafeteria/OrderSummaryModal";
import { BottomNav } from "@/components/shared/BottomNav";

const categories = ["All", "Breakfast", "Lunch", "Snacks", "Drinks"];

export default function CafeteriaPage() {
    const [selectedCategory, setSelectedCategory] = useState("All");
    const [searchQuery, setSearchQuery] = useState("");
    const [cart, setCart] = useState<{ item: FoodItem; quantity: number }[]>([]);
    const [isOrderModalOpen, setIsOrderModalOpen] = useState(false);

    const filteredItems = cafeteriaItems.filter((item) => {
        const matchesCategory = selectedCategory === "All" || item.category === selectedCategory;
        const matchesSearch = item.name.toLowerCase().includes(searchQuery.toLowerCase());
        return matchesCategory && matchesSearch;
    });

    const getItemQuantity = (id: string) => {
        return cart.find((i) => i.item.id === id)?.quantity || 0;
    };

    const handleAdd = (item: FoodItem) => {
        setCart((prev) => {
            const existing = prev.find((i) => i.item.id === item.id);
            if (existing) {
                return prev.map((i) =>
                    i.item.id === item.id ? { ...i, quantity: i.quantity + 1 } : i
                );
            }
            return [...prev, { item, quantity: 1 }];
        });
    };

    const handleRemove = (id: string) => {
        setCart((prev) => {
            const existing = prev.find((i) => i.item.id === id);
            if (existing && existing.quantity > 1) {
                return prev.map((i) =>
                    i.item.id === id ? { ...i, quantity: i.quantity - 1 } : i
                );
            }
            return prev.filter((i) => i.item.id !== id);
        });
    };

    const totalAmount = cart.reduce((acc, curr) => acc + curr.item.price * curr.quantity, 0);
    const totalItems = cart.reduce((acc, curr) => acc + curr.quantity, 0);

    const handleOrderPlaced = () => {
        // Clear cart after successful order (logic happens in modal usually, but we can do it here too to be safe)
        setCart([]);
    }

    return (
        <div className="min-h-screen bg-background text-foreground pb-28 font-sans">
            {/* Header */}
            <header className="sticky top-0 z-40 bg-background/80 backdrop-blur-md border-b border-border p-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <Link href="/" className="p-2 -ml-2 rounded-full hover:bg-muted transition-colors">
                        <ArrowLeft className="w-5 h-5" />
                    </Link>
                    <div>
                        <h1 className="text-xl font-bold">Cafeteria</h1>
                        <p className="text-xs text-muted-foreground">Order food & drinks</p>
                    </div>
                </div>

                {/* Cart Icon / Amount */}
                {totalItems > 0 && (
                    <motion.button
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        onClick={() => setIsOrderModalOpen(true)}
                        className="relative p-2 bg-primary text-primary-foreground rounded-full shadow-lg"
                    >
                        <ShoppingBag className="w-5 h-5" />
                        <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-[10px] font-bold flex items-center justify-center rounded-full border-2 border-background">
                            {totalItems}
                        </span>
                    </motion.button>
                )}
            </header>

            <main className="p-4 space-y-6">
                {/* Search Bar */}
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <Input
                        placeholder="Search for dishes..."
                        className="pl-9 bg-muted/50 border-transparent focus:bg-background focus:border-primary/20 transition-all font-medium"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                    />
                </div>

                {/* Categories */}
                <div className="flex gap-2 overflow-x-auto pb-2 no-scrollbar">
                    {categories.map((cat) => (
                        <button
                            key={cat}
                            onClick={() => setSelectedCategory(cat)}
                            className={`px-4 py-1.5 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${selectedCategory === cat
                                ? "bg-primary text-primary-foreground"
                                : "bg-muted text-muted-foreground hover:bg-muted/80"
                                }`}
                        >
                            {cat}
                        </button>
                    ))}
                </div>

                {/* Food List */}
                <div className="space-y-4">
                    {filteredItems.length > 0 ? (
                        filteredItems.map((item) => (
                            <FoodItemCard
                                key={item.id}
                                item={item}
                                quantity={getItemQuantity(item.id)}
                                onAdd={() => handleAdd(item)}
                                onRemove={() => handleRemove(item.id)}
                            />
                        ))
                    ) : (
                        <div className="text-center py-10 text-muted-foreground">
                            <p>No items found.</p>
                        </div>
                    )}
                </div>
            </main>

            {/* Floating Cart Button (visible if items in cart) */}
            <AnimatePresence>
                {totalItems > 0 && (
                    <motion.div
                        initial={{ y: 100, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                        exit={{ y: 100, opacity: 0 }}
                        className="fixed bottom-6 left-4 right-4 z-40"
                    >
                        <Button
                            onClick={() => setIsOrderModalOpen(true)}
                            className="w-full h-14 rounded-xl shadow-2xl flex items-center justify-between px-6 text-lg font-bold bg-primary text-primary-foreground hover:bg-primary/90"
                        >
                            <span>{totalItems} items</span>
                            <span>View Cart • ₹{totalAmount}</span>
                        </Button>
                    </motion.div>
                )}
            </AnimatePresence>

            <OrderSummaryModal
                isOpen={isOrderModalOpen}
                onClose={() => setIsOrderModalOpen(false)}
                cart={cart}
                total={totalAmount}
                onOrderPlaced={handleOrderPlaced}
            />
            <BottomNav />
        </div>
    );
}
