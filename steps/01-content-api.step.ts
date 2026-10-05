import type { ApiRequest, ApiRouteConfig, FlowContext } from 'motia'
import { z } from 'zod'

const bodySchema = z.object({ url: z.string().url() })

// 1) Entry point: POST /generate-content { "url": "https://..." }
export const config: ApiRouteConfig = {
  type: 'api',
  name: 'ContentGenerationApi',
  description: 'Accepts a URL and starts the content generation workflow',
  path: '/generate-content',
  method: 'POST',
  bodySchema,
  emits: ['scrape-article'],
  flows: ['content-generation'],
}

export const handler = async (req: ApiRequest<z.infer<typeof bodySchema>>, { emit, logger, traceId }: FlowContext<any>) => {
  logger.info('Content generation requested', { url: req.body.url })
  await emit({ topic: 'scrape-article', data: { requestId: traceId, url: req.body.url } })
  return {
    status: 200,
    body: { message: 'Content generation started', requestId: traceId },
  }
}
