"use client";

import { motion } from "framer-motion";
import { UtensilsCrossed, Clock, Star, ChevronRight } from "lucide-react";
import { ThemeToggle } from "@/components/shared/ThemeToggle";
import { BottomNav } from "@/components/shared/BottomNav";
import Link from "next/link";

const highlights = [
  { icon: Clock, label: "Ready in 15 min", color: "text-amber-400", bg: "bg-amber-400/10" },
  { icon: Star, label: "4.8 Rating", color: "text-yellow-400", bg: "bg-yellow-400/10" },
  { icon: UtensilsCrossed, label: "30+ Items", color: "text-emerald-400", bg: "bg-emerald-400/10" },
];

const featuredCategories = [
  { label: "Breakfast", emoji: "🍳", desc: "Start your day right", href: "/services/cafeteria" },
  { label: "Lunch", emoji: "🍱", desc: "Hearty midday meals", href: "/services/cafeteria" },
  { label: "Snacks", emoji: "🥪", desc: "Quick bites", href: "/services/cafeteria" },
  { label: "Drinks", emoji: "☕", desc: "Hot & cold beverages", href: "/services/cafeteria" },
];

export default function Home() {
  return (
    <div className="min-h-screen bg-background text-foreground pb-24 font-sans selection:bg-primary/20">
      {/* Header */}
      <header className="flex justify-between items-center p-6 pt-8">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary/80 to-primary flex items-center justify-center shadow-lg shadow-primary/20">
            <UtensilsCrossed className="w-5 h-5 text-primary-foreground" />
          </div>
          <div>
            <h1 className="text-sm font-medium text-neutral-400">Campus</h1>
            <p className="text-lg font-bold text-foreground">Cafeteria</p>
          </div>
        </div>
        <ThemeToggle />
      </header>

      <main className="px-6 space-y-8">
        {/* Hero */}
        <motion.section
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-primary/20 via-primary/10 to-transparent border border-primary/20 p-6"
        >
          <div className="absolute top-0 right-0 w-32 h-32 bg-primary/10 rounded-full -translate-y-1/2 translate-x-1/2 blur-2xl" />
          <p className="text-xs font-semibold text-primary uppercase tracking-widest mb-2">Good morning 🌤</p>
          <h2 className="text-2xl font-extrabold text-foreground mb-1">What would you<br />like to eat today?</h2>
          <p className="text-sm text-muted-foreground mb-5">Pre-order your meal and skip the queue.</p>
          <Link
            href="/services/cafeteria"
            className="inline-flex items-center gap-2 bg-primary text-primary-foreground font-semibold px-5 py-2.5 rounded-xl text-sm shadow-lg shadow-primary/30 hover:bg-primary/90 active:scale-95 transition-all"
          >
            Browse Menu <ChevronRight className="w-4 h-4" />
          </Link>
        </motion.section>

        {/* Highlights */}
        <section className="grid grid-cols-3 gap-3">
          {highlights.map((h, i) => (
            <motion.div
              key={h.label}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className={`flex flex-col items-center gap-2 p-3 rounded-2xl ${h.bg} border border-white/5`}
            >
              <h.icon className={`w-5 h-5 ${h.color}`} />
              <span className="text-[10px] font-semibold text-center text-muted-foreground leading-tight">{h.label}</span>
            </motion.div>
          ))}
        </section>

        {/* Categories */}
        <section>
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-bold text-foreground">Browse by Category</h3>
            <Link href="/services/cafeteria" className="text-xs text-primary font-medium hover:underline">
              View All
            </Link>
          </div>
          <div className="grid grid-cols-2 gap-3">
            {featuredCategories.map((cat, i) => (
              <motion.div
                key={cat.label}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.2 + i * 0.08 }}
              >
                <Link
                  href={cat.href}
                  className="flex items-center gap-3 p-4 rounded-2xl bg-neutral-900/50 border border-white/5 hover:bg-neutral-800/60 hover:border-border active:scale-95 transition-all group"
                >
                  <span className="text-2xl">{cat.emoji}</span>
                  <div>
                    <p className="font-semibold text-foreground text-sm">{cat.label}</p>
                    <p className="text-[10px] text-muted-foreground">{cat.desc}</p>
                  </div>
                  <ChevronRight className="w-4 h-4 text-muted-foreground ml-auto group-hover:text-primary transition-colors" />
                </Link>
              </motion.div>
            ))}
          </div>
        </section>

        {/* CTA Banner */}
        <motion.section
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="rounded-2xl bg-neutral-900/50 border border-white/5 p-5 flex items-center justify-between"
        >
          <div>
            <p className="font-bold text-foreground">Ready to order?</p>
            <p className="text-xs text-muted-foreground mt-0.5">Get your token instantly</p>
          </div>
          <Link
            href="/services/cafeteria"
            className="shrink-0 bg-primary/10 text-primary font-semibold text-sm px-4 py-2 rounded-xl border border-primary/20 hover:bg-primary/20 active:scale-95 transition-all"
          >
            Order Now
          </Link>
        </motion.section>
      </main>
      <BottomNav />
    </div>
  );
}
