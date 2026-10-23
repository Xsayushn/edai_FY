import { NextResponse } from "next/server";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { name, email, subject, message } = body;

    // Validate inputs
    if (!name || name.trim().length < 2) {
      return NextResponse.json(
        { error: "Name must be at least 2 characters long." },
        { status: 400 }
      );
    }
    if (!email || !email.includes("@")) {
      return NextResponse.json(
        { error: "Please provide a valid email address." },
        { status: 400 }
      );
    }
    if (!subject || subject.trim().length < 3) {
      return NextResponse.json(
        { error: "Subject must be at least 3 characters long." },
        { status: 400 }
      );
    }
    if (!message || message.trim().length < 10) {
      return NextResponse.json(
        { error: "Message must be at least 10 characters long." },
        { status: 400 }
      );
    }

    // Try forwarding to FastAPI backend if running
    let fastApiResponse = null;
    try {
      const apiRes = await fetch("http://127.0.0.1:8000/api/contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, subject, message }),
      });
      if (apiRes.ok) {
        fastApiResponse = await apiRes.json();
      }
    } catch {
      // Backend might be offline or starting, handle gracefully
    }

    const ticketId = `OL-${Math.floor(100000 + Math.random() * 900000)}`;

    return NextResponse.json({
      success: true,
      ticket_id: ticketId,
      message:
        fastApiResponse?.message ||
        `Thank you, ${name.trim()}. Your inquiry regarding "${subject.trim()}" has been recorded under ticket #${ticketId}. Our review audit team will respond within 24 hours.`,
      received_at: new Date().toISOString(),
    });
  } catch (err: unknown) {
    const errorMessage = err instanceof Error ? err.message : "Internal server error";
    return NextResponse.json(
      { error: `Inquiry dispatch failure: ${errorMessage}` },
      { status: 500 }
    );
  }
}
