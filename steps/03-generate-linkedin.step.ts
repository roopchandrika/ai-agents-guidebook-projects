import type { EventConfig, FlowContext } from 'motia'
import { z } from 'zod'
import { generate } from '../lib/llm'
import { LINKEDIN_PROMPT } from '../lib/prompts'

const input = z.object({ requestId: z.string(), url: z.string(), title: z.string(), content: z.string() })

// 3b) LinkedIn agent — runs in parallel with the X agent
export const config: EventConfig = {
  type: 'event',
  name: 'LinkedInAgent',
  description: 'Generates a LinkedIn post from the scraped article',
  subscribes: ['generate-content'],
  emits: ['schedule-content'],
  input,
  flows: ['content-generation'],
}

export const handler = async (data: z.infer<typeof input>, { emit, logger }: FlowContext<any>) => {
  logger.info('Generating LinkedIn post', { title: data.title })
  const post = await generate(LINKEDIN_PROMPT, `Title: ${data.title}\nSource: ${data.url}\n\n${data.content}`)
  await emit({
    topic: 'schedule-content',
    data: { requestId: data.requestId, platform: 'linkedin', title: data.title, post },
  })
}
