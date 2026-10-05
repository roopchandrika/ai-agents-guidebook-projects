import type { EventConfig, FlowContext } from 'motia'
import { z } from 'zod'
import { generate } from '../lib/llm'
import { TWITTER_PROMPT } from '../lib/prompts'

const input = z.object({ requestId: z.string(), url: z.string(), title: z.string(), content: z.string() })

// 3a) X (Twitter) agent — runs in parallel with the LinkedIn agent (both subscribe to the same topic)
export const config: EventConfig = {
  type: 'event',
  name: 'TwitterAgent',
  description: 'Generates an X thread from the scraped article',
  subscribes: ['generate-content'],
  emits: ['schedule-content'],
  input,
  flows: ['content-generation'],
}

export const handler = async (data: z.infer<typeof input>, { emit, logger }: FlowContext<any>) => {
  logger.info('Generating X thread', { title: data.title })
  const post = await generate(TWITTER_PROMPT, `Title: ${data.title}\nSource: ${data.url}\n\n${data.content}`)
  await emit({
    topic: 'schedule-content',
    data: { requestId: data.requestId, platform: 'twitter', title: data.title, post },
  })
}
