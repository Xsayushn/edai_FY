const FASTAPI_URL = process.env.FASTAPI_INTERNAL_URL || "http://127.0.0.1:8000";

export async function GET(request: Request) {
  const incomingUrl = new URL(request.url);
  const brand = incomingUrl.searchParams.get("brand")?.trim();
  if (!brand) {
    return Response.json({ detail: "Choose a product category." }, { status: 400 });
  }

  try {
    const upstreamUrl = new URL("/api/products", FASTAPI_URL);
    upstreamUrl.searchParams.set("brand", brand);
    const response = await fetch(upstreamUrl, { cache: "no-store" });
    const body = await response.json();
    return Response.json(body, { status: response.status });
  } catch {
    return Response.json(
      { detail: "The product catalog is unavailable. Try again in a moment." },
      { status: 503 },
    );
  }
}
