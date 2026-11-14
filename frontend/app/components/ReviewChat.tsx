"use client";

import { useState, type FormEvent } from "react";
import styles from "./ReviewChat.module.css";

interface ReviewSource {
  review_id: number | string;
  rating: number;
  quote: string;
}

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sources?: ReviewSource[];
}

const SUGGESTED_QUESTIONS = [
  "What do reviewers like most?",
  "What are the common complaints?",
  "How is the battery life?",
];

export default function ReviewChat({ productId }: { productId: string }) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [question, setQuestion] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState("");

  async function sendQuestion(value: string) {
    const cleanQuestion = value.trim();
    if (!cleanQuestion || isSending) return;

    const priorMessages = messages;
    setMessages([...priorMessages, { role: "user", content: cleanQuestion }]);
    setQuestion("");
    setError("");
    setIsSending(true);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          product_id: productId,
          question: cleanQuestion,
          history: priorMessages.slice(-8).map(({ role, content }) => ({ role, content })),
        }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || "Could not search the reviews.");
      setMessages([
        ...priorMessages,
        { role: "user", content: cleanQuestion },
        { role: "assistant", content: payload.answer, sources: payload.sources || [] },
      ]);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not search the reviews.");
    } finally {
      setIsSending(false);
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void sendQuestion(question);
  }

  return (
    <section className={styles.chat} aria-labelledby="review-chat-title">
      <div className={styles.heading}>
        <div>
          <h2 id="review-chat-title">Ask about these reviews</h2>
          <p>Answers use comments for this product and include links to the source reviews.</p>
        </div>
      </div>

      {messages.length === 0 ? (
        <div className={styles.suggestions}>
          <span>Try asking</span>
          {SUGGESTED_QUESTIONS.map((suggestion) => (
            <button key={suggestion} type="button" onClick={() => void sendQuestion(suggestion)}>
              {suggestion}
            </button>
          ))}
        </div>
      ) : (
        <div className={styles.messages} aria-live="polite">
          {messages.map((message, index) => (
            <article className={message.role === "user" ? styles.userMessage : styles.assistantMessage} key={`${message.role}-${index}`}>
              <span className={styles.speaker}>{message.role === "user" ? "You" : "OpinionLens"}</span>
              <p>{message.content}</p>
              {message.sources && message.sources.length > 0 && (
                <div className={styles.sources}>
                  {message.sources.map((source) => (
                    <details className={styles.source} key={source.review_id}>
                      <summary>Review #{source.review_id} · {source.rating}/5</summary>
                      <p>{source.quote}</p>
                      <a href={`#review-${source.review_id}`}>View in review list</a>
                    </details>
                  ))}
                </div>
              )}
            </article>
          ))}
          {isSending && <p className={styles.loading} role="status">Searching the reviews…</p>}
        </div>
      )}

      {error && <p className={styles.error} role="alert">{error}</p>}

      <form className={styles.form} onSubmit={handleSubmit}>
        <label className="sr-only" htmlFor="review-chat-question">Ask a question about this product</label>
        <input
          id="review-chat-question"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          maxLength={1200}
          placeholder="Ask about comfort, reliability, battery life…"
          disabled={isSending}
        />
        <button type="submit" disabled={isSending || question.trim().length < 2}>
          {isSending ? "Searching…" : "Ask"}
        </button>
      </form>
      <p className={styles.note}>Answers reflect the reviews in this catalog and may not cover every experience.</p>
    </section>
  );
}
