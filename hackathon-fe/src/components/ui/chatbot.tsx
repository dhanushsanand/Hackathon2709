import { useEffect, useRef, useState } from "react";
import { askAI } from "../../lib/ai";
import { marked } from "marked";
import DOMPurify from "dompurify";

type Message = {
  id: string;
  from: "user" | "bot";
  text: string;
};

type ChatbotProps = {
  initialOpen?: boolean;
  initialMessages?: Message[];
  title?: string;
};

export default function Chatbot({ initialOpen = false, initialMessages, title = "ASU Safety Assistant" }: ChatbotProps) {
  const [open, setOpen] = useState<boolean>(initialOpen);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>(
    initialMessages ?? [
      { id: "m1", from: "bot", text: "Hi — I'm the ASU Safety Assistant. Ask me about emergency contacts, escorts, or safety resources." },
    ]
  );
  const scrollRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, open]);

  function addMessage(from: Message["from"], text: string) {
    const id = String(Math.random());
    setMessages((m) => [...m, { id, from, text }]);
    return id;
  }

  async function handleSend() {
    const trimmed = input.trim();
    if (!trimmed) return;

    // add user message
    addMessage("user", trimmed);
    setInput("");

    // placeholder bot message
    const placeholderId = addMessage("bot", "Thinking...");

    // Basic local moderation: if the user asks vulgar or clearly off-topic content,
    // return a canned response saying it's not related to ASU safety topics.
    // This prevents sending inappropriate queries to the AI and keeps the assistant on-topic.
    const blacklist = ["penis", "fuck", "shit", "bitch", "cock", "dick"];
    const pattern = new RegExp("\\b(" + blacklist.map(w => w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|") + ")\\b", "i");
    if (pattern.test(trimmed)) {
      const canned = "That is not related to ASU safety topics.";
      setMessages((ms) => ms.map((m) => (m.id === placeholderId ? { ...m, text: canned } : m)));
      return;
    }

    try {
      const answer = await askAI(trimmed);
      setMessages((ms) => ms.map((m) => (m.id === placeholderId ? { ...m, text: answer } : m)));
    } catch (err: any) {
      const msg = err?.message ?? "I couldn't reach the AI agent. Try again later.";
      setMessages((ms) => ms.map((m) => (m.id === placeholderId ? { ...m, text: msg } : m)));
    }
  }

  function quick(question: string) {
    setInput(question);
    setTimeout(() => {
      // send after a little delay so users see the text
      handleSend();
    }, 150);
  }

  // Render user text and convert URLs to clickable links (keep plain text)
  function renderUserText(text: string) {
    const urlRegex = /(https?:\/\/[\w\-_.~:\/?#\[\]@!$&'()*+,;=%]+)/g;
    const parts = text.split(urlRegex);
    return parts.map((part, i) => {
      if (urlRegex.test(part)) {
        return (
          <a key={i} href={part} target="_blank" rel="noopener noreferrer" className="underline text-blue-600">
            {part}
          </a>
        );
      }
      return <span key={i}>{part}</span>;
    });
  }

  // Render bot text as sanitized Markdown -> HTML
  function renderBotMarkdown(text: string) {
    // Convert markdown to HTML
    const rawHtml = marked.parse(text || "");
    // Sanitize the HTML to prevent XSS
    const clean = DOMPurify.sanitize(rawHtml, { ALLOWED_ATTR: ["href", "target", "rel", "class"] });
    return <div dangerouslySetInnerHTML={{ __html: clean }} />;
  }

  return (
    <div className="fixed right-6 bottom-6 z-50">
      <div className="flex flex-col items-end">
        {open && (
          <div className="w-80 md:w-96 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg mb-3 overflow-hidden">
            <div className="px-4 py-3 bg-blue-600 dark:bg-blue-700 text-white flex items-center justify-between">
              <div className="font-semibold">{title}</div>
              <button aria-label="Close chat" onClick={() => setOpen(false)} className="opacity-90 hover:opacity-100">✕</button>
            </div>

            <div ref={scrollRef} className="p-3 h-64 overflow-y-auto space-y-3" aria-live="polite">
              {messages.map((m) => (
                <div key={m.id} className={m.from === "bot" ? "text-left" : "text-right"}>
                  <div className={(m.from === "bot" ? "inline-block bg-gray-100 dark:bg-gray-700 text-gray-900" : "inline-block bg-blue-500 text-white") + " px-3 py-2 rounded-lg max-w-full break-words"}>
                    {m.from === "bot" ? renderBotMarkdown(m.text) : renderUserText(m.text)}
                  </div>
                </div>
              ))}
            </div>

            <div className="p-3 border-t border-gray-100 dark:border-gray-700">
              <div className="flex gap-2">
                <input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSend()}
                  placeholder="Ask about safety, e.g. 'How do I report an emergency?'"
                  className="flex-1 rounded-md border border-gray-200 dark:border-gray-700 px-3 py-2 bg-white dark:bg-gray-800 text-sm focus:outline-none"
                />
                <button onClick={handleSend} className="px-3 py-2 rounded-md bg-blue-600 text-white text-sm">Send</button>
              </div>

              <div className="mt-2 text-xs text-gray-500 dark:text-gray-400 flex gap-2">
                <button onClick={() => quick("How do I report an emergency?")} className="underline">Report emergency</button>
                <button onClick={() => quick("Are there safety escorts available?")} className="underline">Safety escorts</button>
                <button onClick={() => quick("ASU counseling services")} className="underline">Counseling</button>
              </div>
            </div>
          </div>
        )}

        <button
          onClick={() => setOpen((v) => !v)}
          className="w-14 h-14 rounded-full bg-blue-600 hover:bg-blue-700 text-white flex items-center justify-center shadow-xl"
          aria-label="Toggle ASU Safety Chat"
        >
          💬
        </button>
      </div>
    </div>
  );
}
