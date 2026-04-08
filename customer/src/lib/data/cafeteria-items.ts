export interface FoodItem {
    id: string;
    name: string;
    description: string;
    price: number;
    image: string;
    category: "Breakfast" | "Lunch" | "Snacks" | "Drinks";
    isVeg: boolean;
    rating: number;
    votes: number;
}

export const cafeteriaItems: FoodItem[] = [
    {
        id: "1",
        name: "Masala Dosa",
        description: "Crispy rice crepe filled with spiced potato mix, served with chutney and sambar.",
        price: 45,
        image: "https://images.unsplash.com/photo-1589301760580-f8da953e3823?w=800&q=80",
        category: "Breakfast",
        isVeg: true,
        rating: 4.8,
        votes: 1240,
    },
    {
        id: "2",
        name: "Idli Sambar",
        description: "Steamed rice cakes served with lentil soup and coconut chutney.",
        price: 30,
        image: "https://images.unsplash.com/photo-1589301760580-f8da953e3823?w=800&q=80", // Reusing generic south indian placeholder or find better
        category: "Breakfast",
        isVeg: true,
        rating: 4.5,
        votes: 850,
    },
    {
        id: "3",
        name: "Veg Meals",
        description: "Complete wholesome meal with rice, sambar, rasam, kootu, and curd.",
        price: 80,
        image: "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=800&q=80",
        category: "Lunch",
        isVeg: true,
        rating: 4.2,
        votes: 2100,
    },
    {
        id: "4",
        name: "Chicken Biryani",
        description: "Aromatic basmati rice cooked with tender chicken and spices.",
        price: 120,
        image: "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=800&q=80",
        category: "Lunch",
        isVeg: false,
        rating: 4.9,
        votes: 3500,
    },
    {
        id: "5",
        name: "Samosa (2 pcs)",
        description: "Crispy pastry filled with spiced potatoes and peas.",
        price: 20,
        image: "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=800&q=80",
        category: "Snacks",
        isVeg: true,
        rating: 4.6,
        votes: 900,
    },
    {
        id: "6",
        name: "Egg Puff",
        description: "Flaky puff pastry filled with a boiled egg and masala.",
        price: 25,
        image: "https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?w=800&q=80",
        category: "Snacks",
        isVeg: false,
        rating: 4.3,
        votes: 560,
    },
    {
        id: "7",
        name: "Cold Coffee",
        description: "Creamy blended coffee topped with chocolate powder.",
        price: 40,
        image: "https://images.unsplash.com/photo-1572442388796-11668a67e53d?w=800&q=80",
        category: "Drinks",
        isVeg: true,
        rating: 4.7,
        votes: 1100,
    },
    {
        id: "8",
        name: "Fresh Lime Soda",
        description: "Refreshing lemon drink with a pinch of salt and sugar.",
        price: 25,
        image: "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=800&q=80",
        category: "Drinks",
        isVeg: true,
        rating: 4.4,
        votes: 450,
    },
];
