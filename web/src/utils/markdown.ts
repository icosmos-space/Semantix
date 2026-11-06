import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'

const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true,
})

const defaultFence =
  md.renderer.rules.fence ||
  ((tokens, idx, options, _env, self) => self.renderToken(tokens, idx, options))

md.renderer.rules.fence = (tokens, idx, options, env, self) => {
  const token = tokens[idx]
  const info = (token.info || '').trim()
  const lang = info.split(/\s+/g)[0]
  if (lang === 'GPT-Vis' || lang === 'gpt-vis') {
    const body = token.content.trim()
    const encoded = encodeURIComponent(body)
    return `<div class="gpt-vis-host" data-gpt-vis="${encoded}" style="min-height:320px;width:100%;margin:12px 0;"></div>`
  }
  return defaultFence(tokens, idx, options, env, self)
}

export function renderChatMarkdown(src: string): string {
  const dirty = md.render(src || '')
  return DOMPurify.sanitize(dirty, {
    ADD_ATTR: ['data-gpt-vis', 'style', 'class'],
  })
}
