const FASTAPI_URL = process.env.FASTAPI_INTERNAL_URL || "http://127.0.0.1:8000";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const response = await fetch(`${FASTAPI_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      cache: "no-store",
    });
    const payload = await response.json();
    return Response.json(payload, { status: response.status });
  } catch {
    return Response.json(
      { detail: "The review assistant is unavailable. Please try again." },
      { status: 503 },
    );
  }
}
