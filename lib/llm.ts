import 'dotenv/config'

// Any OpenAI-compatible chat completions endpoint. Defaults to a local model served by Ollama.
const BASE_URL = process.env.LLM_BASE_URL ?? 'http://localhost:11434/v1'
const API_KEY = process.env.LLM_API_KEY ?? 'ollama'
const MODEL = process.env.LLM_MODEL ?? 'deepseek-r1:7b'

export async function generate(system: string, user: string): Promise<string> {
  const res = await fetch(`${BASE_URL.replace(/\/$/, '')}/chat/completions`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${API_KEY}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: MODEL,
      temperature: 0.7,
      messages: [
        { role: 'system', content: system },
        { role: 'user', content: user },
      ],
    }),
  })
  if (!res.ok) throw new Error(`LLM request failed: ${res.status} ${await res.text()}`)

  const json: any = await res.json()
  const text: string = json.choices?.[0]?.message?.content ?? ''
  // reasoning models (DeepSeek-R1, Qwen3) wrap their chain of thought in <think> tags
  return text.replace(/<think>[\s\S]*?<\/think>/g, '').trim()
}
