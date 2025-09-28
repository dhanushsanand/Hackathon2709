// Frontend AI helper using fetch. It first attempts a local proxy at /api/ai.
// If not available, it can call Google's Generative Language API (Gemini) directly
// if an API key is provided via Vite env var VITE_GEMINI_API_KEY (not recommended in client).

type GeminiResponse = any;

export async function askAI(prompt: string, timeoutMs = 60000): Promise<string> {
	// helper to add timeout to promises
	const withTimeout = <T,>(p: Promise<T>, ms: number) =>
		new Promise<T>((resolve, reject) => {
			const id = setTimeout(() => reject(new Error("AI request timed out")), ms);
			p.then((res) => {
				clearTimeout(id);
				resolve(res);
			}, (err) => {
				clearTimeout(id);
				reject(err);
			});
		});

	// 1) Try local proxy at /api/ai
	try {
		const res = await withTimeout(
			fetch("/api/ai", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ prompt }),
			}),
			timeoutMs
		);

		if ((res as Response).ok) {
			const data = await (res as Response).json();
			if (data?.answer) return String(data.answer);
			if (typeof data === "string") return data;
		}
	} catch (err) {
		// ignore and continue to fallback
	}

	// 2) Fallback: call Gemini directly if VITE_GEMINI_API_KEY is present
	const key = (import.meta as any).env?.VITE_GEMINI_API_KEY as string | undefined;
	if (!key) throw new Error("No AI backend available and no GEMINI API key configured");

	// Build the request body similar to the curl the user provided
	const body = {
		contents: [
			{
				parts: [
					{
						text: prompt,
					},
				],
			},
		],
	};

	try {
		const res = await withTimeout(
			fetch(
				"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
				{
					method: "POST",
					headers: {
						"Content-Type": "application/json",
						"x-goog-api-key": key,
					},
					body: JSON.stringify(body),
				}
			),
			timeoutMs
		);

		if (!(res as Response).ok) {
			const txt = await (res as Response).text();
			throw new Error(`Gemini error: ${txt}`);
		}

		const data: GeminiResponse = await (res as Response).json();

		// Google's response contains candidates with output text — try to extract a string
		// Example path (may vary): data.candidates[0].content[0].text
			const candidate = data?.candidates?.[0] ?? data;
			if (candidate) {
				// Safely extract text from several possible Gemini response shapes
				const tryExtract = (cand: any): string | null => {
					try {
						// 1) candidate.output is sometimes a string
						if (typeof cand.output === "string" && cand.output.trim()) return cand.output.trim();

						// 2) candidate.text
						if (typeof cand.text === "string" && cand.text.trim()) return cand.text.trim();

						// 3) candidate.content can be an array or an object
						const content = cand.content;
						if (Array.isArray(content)) {
							const parts: string[] = [];
							for (const c of content) {
								if (!c) continue;
								if (typeof c.text === "string") parts.push(c.text);
								else if (Array.isArray(c.parts)) {
									for (const p of c.parts) {
										if (typeof p.text === "string") parts.push(p.text);
									}
								} else if (typeof c === "string") parts.push(c);
							}
							if (parts.length) return parts.join(" ").trim();
						} else if (content && typeof content === "object") {
							// content is an object with parts
							if (Array.isArray(content.parts)) {
								const parts = content.parts.map((p: any) => (p?.text ? String(p.text) : "")).filter(Boolean);
								if (parts.length) return parts.join(" ").trim();
							}
							if (typeof content.text === "string") return content.text.trim();
						}

						// 4) candidates[].message or candidates[].message.content
						if (cand.message) {
							const m = cand.message;
							if (typeof m.content === "string") return m.content.trim();
							if (Array.isArray(m.content)) {
								return m.content.map((x: any) => x?.text ?? String(x)).join(" ").trim();
							}
						}
					} catch (e) {
						// fallthrough
					}
					return null;
				};

				const text = tryExtract(candidate);
				if (text) return String(text).trim();
			}

		// fallback: stringify full response
		return JSON.stringify(data);
	} catch (err: any) {
		throw new Error(err?.message ?? "Gemini call failed");
	}
}

export default askAI;
