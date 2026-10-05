import 'dotenv/config'
import { mkdir, writeFile } from 'node:fs/promises'
import path from 'node:path'
import type { EventConfig, FlowContext } from 'motia'
import { z } from 'zod'

const input = z.object({
  requestId: z.string(),
  platform: z.enum(['twitter', 'linkedin']),
  title: z.string(),
  post: z.string(),
})

// 4) Scheduling: draft the post in Typefully for review (and always keep a local copy)
export const config: EventConfig = {
  type: 'event',
  name: 'ScheduleTypefully',
  description: 'Creates a Typefully draft for each generated post',
  subscribes: ['schedule-content'],
  emits: [],
  input,
  flows: ['content-generation'],
}

export const handler = async (data: z.infer<typeof input>, { logger, state }: FlowContext<any>) => {
  const outDir = path.join(process.cwd(), 'output')
  await mkdir(outDir, { recursive: true })
  const file = path.join(outDir, `${data.requestId}-${data.platform}.md`)
  await writeFile(file, `# ${data.title} (${data.platform})\n\n${data.post}\n`, 'utf-8')
  await state.set(data.requestId, data.platform, data.post)
  logger.info('Saved post locally', { file })

  const apiKey = process.env.TYPEFULLY_API_KEY
  if (!apiKey) {
    logger.warn('TYPEFULLY_API_KEY not set — skipping Typefully draft')
    return
  }

  // Typefully splits threads on 4 consecutive newlines
  const content = data.platform === 'twitter' ? data.post.split(/\n\s*---\s*\n/).join('\n\n\n\n') : data.post
  const res = await fetch('https://api.typefully.com/v1/drafts/', {
    method: 'POST',
    headers: { 'X-API-KEY': `Bearer ${apiKey}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ content, threadify: false, share: true }),
  })
  if (!res.ok) {
    logger.error('Typefully draft failed', { status: res.status, body: await res.text() })
    return
  }
  const draft: any = await res.json()
  logger.info('Typefully draft created', { platform: data.platform, shareUrl: draft.share_url })
}
