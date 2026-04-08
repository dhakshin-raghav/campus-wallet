"use client";

import { motion } from "framer-motion";
import { Plus, Minus, Star } from "lucide-react";
import { FoodItem } from "@/lib/data/cafeteria-items";

interface FoodItemCardProps {
    item: FoodItem;
    quantity: number;
    onAdd: () => void;
    onRemove: () => void;
}

export function FoodItemCard({ item, quantity, onAdd, onRemove }: FoodItemCardProps) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex gap-3 p-3 rounded-2xl bg-card border border-border/50 hover:border-border/80 transition-all group overflow-hidden"
        >
            {/* Image */}
            <div className="relative w-28 h-28 rounded-xl overflow-hidden shrink-0 shadow-md">
                <img
                    src={item.image}
                    alt={item.name}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                />
                {/* Veg/Non-veg indicator */}
                <div className={`absolute top-2 left-2 w-4 h-4 rounded-sm border-2 flex items-center justify-center bg-background/80 backdrop-blur-sm ${item.isVeg ? "border-green-500" : "border-red-500"}`}>
                    <div className={`w-2 h-2 rounded-full ${item.isVeg ? "bg-green-500" : "bg-red-500"}`} />
                </div>
                {/* Rating badge */}
                <div className="absolute bottom-2 left-2 flex items-center gap-0.5 px-1.5 py-0.5 rounded-md bg-black/60 backdrop-blur-sm">
                    <Star className="w-2.5 h-2.5 text-yellow-400 fill-yellow-400" />
                    <span className="text-[10px] font-bold text-white">{item.rating}</span>
                </div>
            </div>

            {/* Content */}
            <div className="flex-1 flex flex-col justify-between min-w-0 py-0.5">
                <div>
                    <h3 className="font-bold text-base text-foreground leading-tight truncate">{item.name}</h3>
                    <p className="text-xs text-muted-foreground mt-1 line-clamp-2 leading-relaxed">{item.description}</p>
                    <p className="text-[10px] text-muted-foreground/60 mt-1">{item.votes.toLocaleString()} ratings</p>
                </div>

                <div className="flex items-center justify-between mt-2">
                    <span className="font-black text-lg text-foreground">₹{item.price}</span>

                    {quantity === 0 ? (
                        <motion.button
                            whileTap={{ scale: 0.93 }}
                            onClick={onAdd}
                            className="flex items-center gap-1.5 px-4 py-1.5 rounded-xl bg-primary/10 text-primary border border-primary/20 hover:bg-primary/20 transition-colors text-xs font-bold uppercase tracking-wide"
                        >
                            <Plus className="w-3.5 h-3.5" /> Add
                        </motion.button>
                    ) : (
                        <motion.div
                            initial={{ scale: 0.8, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            className="flex items-center bg-primary/10 rounded-xl border border-primary/20 h-8 overflow-hidden"
                        >
                            <button
                                onClick={onRemove}
                                className="w-8 h-full flex items-center justify-center text-primary hover:bg-primary/10 transition-colors"
                            >
                                <Minus className="w-3.5 h-3.5" />
                            </button>
                            <span className="w-7 text-center text-sm font-black text-primary">{quantity}</span>
                            <button
                                onClick={onAdd}
                                className="w-8 h-full flex items-center justify-center text-primary hover:bg-primary/10 transition-colors"
                            >
                                <Plus className="w-3.5 h-3.5" />
                            </button>
                        </motion.div>
                    )}
                </div>
            </div>
        </motion.div>
    );
}
