import 'dotenv/config'
import type { EventConfig, FlowContext } from 'motia'
import { z } from 'zod'

const input = z.object({ requestId: z.string(), url: z.string() })

// 2) Web scraping: Firecrawl turns the page into clean markdown
export const config: EventConfig = {
  type: 'event',
  name: 'ScrapeArticle',
  description: 'Scrapes the article with Firecrawl and converts it to markdown',
  subscribes: ['scrape-article'],
  emits: ['generate-content'],
  input,
  flows: ['content-generation'],
}

export const handler = async (data: z.infer<typeof input>, { emit, logger }: FlowContext<any>) => {
  logger.info('Scraping article', { url: data.url })
  const res = await fetch('https://api.firecrawl.dev/v1/scrape', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${process.env.FIRECRAWL_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ url: data.url, formats: ['markdown'], onlyMainContent: true }),
  })
  if (!res.ok) throw new Error(`Firecrawl failed: ${res.status} ${await res.text()}`)

  const json: any = await res.json()
  const markdown: string = json.data?.markdown ?? ''
  const title: string = json.data?.metadata?.title ?? data.url
  logger.info('Article scraped', { title, chars: markdown.length })

  await emit({
    topic: 'generate-content',
    data: { requestId: data.requestId, url: data.url, title, content: markdown.slice(0, 15000) },
  })
}
