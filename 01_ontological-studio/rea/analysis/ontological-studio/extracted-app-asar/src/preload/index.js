'use strict'
// The only bridge the pages get. Main frame only (the portal iframe inside Studio gets
// nothing). Main checks who is asking: tab-strip calls are honoured only from a window's
// own shell page; a tab may only open another tab or the fixed shell actions.
const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('liteShell', {
  platform: process.platform,
  /** 'settings' (studio.env) | 'logs' | 'data' | 'portal' (in the browser) */
  open: (what) => ipcRenderer.invoke('lite:open', String(what)),
  info: () => ipcRenderer.invoke('lite:info'),
  isFullScreen: () => ipcRenderer.invoke('lite:is-fullscreen'),
  onFullScreen: (cb) => { ipcRenderer.on('lite:fullscreen', (_e, on) => cb(!!on)) },
  newWindow: () => ipcRenderer.invoke('lite:window:new'),
  /** { kind: 'studio', view?, session?, ds? } | { kind: 'portal' } */
  openTab: (target) => ipcRenderer.invoke('lite:tabs:open', target),
  /** Ontological portal: a question in words → { cypher, note, agent, ms, checked, write, error? } (cliagents) */
  nl2cypher: (question, graph) => ipcRenderer.invoke('lite:nl2cypher', { question: String(question), graph: String(graph) }),
  tabs: {
    get: () => ipcRenderer.invoke('lite:tabs:get'),
    activate: (id) => ipcRenderer.invoke('lite:tabs:activate', String(id)),
    close: (id) => ipcRenderer.invoke('lite:tabs:close', String(id)),
    menu: (id) => ipcRenderer.invoke('lite:tabs:menu', String(id)),
    onChange: (cb) => { ipcRenderer.on('lite:tabs', (_e, state) => cb(state)) },
  },
})
