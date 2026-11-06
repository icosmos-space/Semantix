import { GPTVis } from '@antv/gpt-vis'

const chartMap = new WeakMap<Element, GPTVis>()

export function mountGptVisIn(root: HTMLElement) {
  const hosts = root.querySelectorAll<HTMLElement>('[data-gpt-vis]')
  hosts.forEach((el) => {
    const encoded = el.dataset.gptVis
    if (!encoded) return
    const syntax = decodeURIComponent(encoded)
    let chart = chartMap.get(el)
    if (!chart) {
      chart = new GPTVis({ container: el, height: 320 })
      chartMap.set(el, chart)
    }
    try {
      chart.render(syntax)
    } catch (err) {
      el.textContent = `GPT-Vis render failed: ${String(err)}`
    }
  })
}

export function destroyGptVisIn(root: HTMLElement) {
  const hosts = root.querySelectorAll<HTMLElement>('[data-gpt-vis]')
  hosts.forEach((el) => {
    const chart = chartMap.get(el)
    chart?.destroy()
    chartMap.delete(el)
  })
}
