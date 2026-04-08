import type { Metadata } from "next";
import "./globals.css";
import { ThemeProvider } from "@/components/shared/ThemeProvider";
import { OrderStoreProvider } from "@/lib/order-store";

export const metadata: Metadata = {
  title: "Campus Cafeteria",
  description: "Order food from the campus cafeteria",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased font-sans">
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem
          disableTransitionOnChange
        >
          <OrderStoreProvider>
            {children}
          </OrderStoreProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}

