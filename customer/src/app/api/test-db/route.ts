import { NextResponse } from 'next/server';
import { db } from '@/lib/db';

export async function GET() {
    try {
        const userCount = await db.user.count();
        return NextResponse.json({ message: "Database connection successful", userCount });
    } catch (error) {
        console.error("Database connection error:", error);
        return NextResponse.json({ error: "Failed to connect to the database" }, { status: 500 });
    }
}
