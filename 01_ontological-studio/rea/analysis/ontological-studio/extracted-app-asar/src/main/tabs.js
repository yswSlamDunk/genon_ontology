'use strict'
// Tabbed windows. Each window's own page is the shell (tab strip in the title bar +
// the home launcher); every tab is a WebContentsView laid over it below the strip —
// a Studio instance (opened on a view, a conversation or a data source) or the
// Ontological portal. Studio and the portal can therefore be open side by side, and a
// tab can be moved to a window of its own without reloading.
const { BrowserWindow, WebContentsView, ipcMain, shell, Menu } = require('electron')
const path = require('path')

const BAR = 38 // the shell's strip; the traffic lights sit inside it (macOS)
const PRELOAD = path.join(__dirname, '..', 'preload', 'index.js')
const BOOT = path.join(__dirname, '..', 'renderer', 'boot.html')
const windows = new Set()
let ctx = null // { ports, graph, dirs, info: () => {...} } once the services are up
let seq = 0

const STUDIO_VIEWS = { build: '온톨로지 구축', act: '질의·액션', board: '대시보드', quality: '품질 검수', datasources: '데이터소스', systems: '시스템 등록', browser: 'Ontological Portal' }

function shellUrl() { return `http://127.0.0.1:${ctx.ports.web}/lite-shell/` }
function urlFor(t) {
  if (t.kind === 'portal') return `http://127.0.0.1:${ctx.ports.portal}/`
  if (t.kind === 'app') return `http://127.0.0.1:${ctx.ports.web}/apps/${encodeURIComponent(t.app)}/`
  const q = new URLSearchParams()
  for (const k of ['view', 'session', 'ds']) if (t[k]) q.set(k, String(t[k]))
  const qs = q.toString()
  return `http://127.0.0.1:${ctx.ports.web}/${qs ? `?${qs}` : ''}`
}
function titleFor(t) {
  if (t.kind === 'portal') return 'Ontological Portal'
  if (t.kind === 'app') return t.title || '앱'
  return t.title || STUDIO_VIEWS[t.view] || 'Ontological Studio'
}
const isStudio = (url) => !!ctx && url.startsWith(`http://127.0.0.1:${ctx.ports.web}/`) && !url.includes('/lite-shell/') && !isApp(url)
const isApp = (url) => !!ctx && url.startsWith(`http://127.0.0.1:${ctx.ports.web}/apps/`)
const isPortal = (url) => !!ctx && url.startsWith(`http://127.0.0.1:${ctx.ports.portal}/`)

class TabWindow {
  constructor({ bounds } = {}) {
    this.tabs = []
    this.active = 'home'
    this.win = new BrowserWindow({
      width: 1440, height: 900, minWidth: 1024, minHeight: 640, ...(bounds || {}),
      title: 'Ontological Studio', backgroundColor: '#14171c', show: true,
      ...(process.platform === 'darwin' ? { titleBarStyle: 'hidden', trafficLightPosition: { x: 14, y: 13 } } : {}),
      ...(process.platform === 'win32' ? { titleBarStyle: 'hidden', titleBarOverlay: { color: '#191d24', symbolColor: '#e6eaf0', height: 38 } } : {}),
      webPreferences: { contextIsolation: true, nodeIntegration: false, sandbox: true, preload: PRELOAD },
    })
    windows.add(this)
    this.win.on('resize', () => this.layout())
    for (const [ev, on] of [['enter-full-screen', true], ['leave-full-screen', false]]) {
      this.win.on(ev, () => this.win.webContents.send('lite:fullscreen', on))
    }
    this.win.on('closed', () => {
      for (const t of this.tabs) t.view.webContents.close()
      this.tabs = []
      windows.delete(this)
    })
    this.win.webContents.on('did-finish-load', () => this.sync())
    this.win.webContents.setWindowOpenHandler(({ url }) => this.routeOpen(url))
    if (ctx) this.win.loadURL(shellUrl())
    else this.win.loadFile(BOOT)
  }

  tab(id) { return this.tabs.find((t) => t.id === id) }

  /** A link that wants a new window: ours becomes a tab, anything else goes to the browser. */
  routeOpen(url) {
    if (isPortal(url)) this.open({ kind: 'portal' })
    else if (isApp(url)) this.open({ kind: 'app', app: url.split('/apps/')[1].split('/')[0] })
    else if (isStudio(url)) this.open({ kind: 'studio' })
    else shell.openExternal(url)
    return { action: 'deny' }
  }

  open(target, { activate = true } = {}) {
    const t = { kind: target.kind === 'portal' || target.kind === 'app' ? target.kind : 'studio' }
    if (t.kind === 'app') {
      // a code app (codeapps.js): its own tab, without the shell's preload — generated code gets no shell API
      t.app = String(target.app || '')
      if (!/^[a-z0-9-]{4,64}$/.test(t.app)) return null
      if (target.title) t.title = String(target.title)
    }
    if (t.kind === 'studio') {
      if (STUDIO_VIEWS[target.view]) t.view = target.view
      if (target.session) t.session = String(target.session)
      if (target.ds) t.ds = String(target.ds)
      if (target.title) t.title = String(target.title)
    }
    const view = new WebContentsView({ webPreferences: { contextIsolation: true, nodeIntegration: false, sandbox: true, ...(t.kind === 'app' ? {} : { preload: PRELOAD }) } })
    view.setBackgroundColor('#14171c')
    const tab = { id: `t${++seq}`, target: t, view, title: titleFor(t), loading: true }
    this.adopt(tab, activate)
    view.webContents.loadURL(urlFor(t))
    return tab.id
  }

  /** Put an existing tab (new, or moved from another window) into this window. */
  adopt(tab, activate = true) {
    const wc = tab.view.webContents
    wc.removeAllListeners('page-title-updated')
    wc.removeAllListeners('did-start-loading')
    wc.removeAllListeners('did-stop-loading')
    // Studio keeps document.title = its current view (overlay tab bridge); the portal's own
    // title says "Ontological Studio", which is not what the tab should read.
    wc.on('page-title-updated', (_e, title) => {
      if ((tab.target.kind === 'studio' || tab.target.kind === 'app') && title && !/^ONTOLOGIC Studio$/.test(title)) { tab.title = title; this.sync() }
    })
    wc.on('did-start-loading', () => { tab.loading = true; this.sync() })
    wc.on('did-stop-loading', () => { tab.loading = false; this.sync() })
    wc.setWindowOpenHandler(({ url }) => this.routeOpen(url))
    wc.on('will-navigate', (e, url) => { if (!isStudio(url) && !isPortal(url)) { e.preventDefault(); shell.openExternal(url) } })
    this.win.contentView.addChildView(tab.view)
    this.tabs.push(tab)
    if (activate) this.activate(tab.id)
    else { tab.view.setVisible(false); this.layout(); this.sync() }
  }

  activate(id) {
    if (id !== 'home' && !this.tab(id)) id = 'home'
    this.active = id
    for (const t of this.tabs) t.view.setVisible(t.id === id)
    this.layout()
    const t = this.tab(id)
    if (t) t.view.webContents.focus()
    else this.win.webContents.focus()
    this.sync()
  }

  /** Remove from this window without destroying it (close or move). */
  take(id) {
    const i = this.tabs.findIndex((t) => t.id === id)
    if (i < 0) return null
    const [t] = this.tabs.splice(i, 1)
    this.win.contentView.removeChildView(t.view)
    if (this.active === id) this.activate((this.tabs[i] || this.tabs[i - 1] || { id: 'home' }).id)
    else this.sync()
    return t
  }

  close(id) {
    const t = this.take(id)
    if (t) t.view.webContents.close()
  }

  detach(id) {
    const t = this.tab(id)
    if (!t) return
    const [x, y] = this.win.getPosition()
    const [width, height] = this.win.getSize()
    this.take(id)
    const w = new TabWindow({ bounds: { x: x + 40, y: y + 40, width, height } })
    w.win.webContents.once('did-finish-load', () => w.adopt(t, true))
  }

  cycle(step) {
    const ids = ['home', ...this.tabs.map((t) => t.id)]
    const i = ids.indexOf(this.active)
    this.activate(ids[(i + step + ids.length) % ids.length])
  }

  nth(n) { // ⌘1 = home, ⌘2.. = tabs, ⌘9 = last
    const ids = ['home', ...this.tabs.map((t) => t.id)]
    this.activate(n >= 9 ? ids[ids.length - 1] : ids[n - 1] || ids[ids.length - 1])
  }

  layout() {
    const [width, height] = this.win.getContentSize()
    for (const t of this.tabs) t.view.setBounds({ x: 0, y: BAR, width, height: Math.max(0, height - BAR) })
  }

  sync() {
    if (this.win.isDestroyed()) return
    this.win.webContents.send('lite:tabs', {
      active: this.active,
      tabs: this.tabs.map((t) => ({ id: t.id, title: t.title, kind: t.target.kind, view: t.target.view || '', loading: t.loading })),
    })
  }

  activeContents() {
    const t = this.tab(this.active)
    return t ? t.view.webContents : this.win.webContents
  }

  tabMenu(id) {
    const t = this.tab(id)
    if (!t) return
    Menu.buildFromTemplate([
      { label: '새로고침', click: () => t.view.webContents.reload() },
      { label: '새 창으로 분리', click: () => this.detach(id) },
      { type: 'separator' },
      { label: '탭 닫기', click: () => this.close(id) },
      { label: '다른 탭 닫기', enabled: this.tabs.length > 1, click: () => this.tabs.filter((x) => x.id !== id).forEach((x) => this.close(x.id)) },
    ]).popup({ window: this.win })
  }
}

function owner(sender) {
  for (const w of windows) {
    if (w.win.webContents === sender) return { w, from: 'shell' }
    if (w.tabs.some((t) => t.view.webContents === sender)) return { w, from: 'tab' }
  }
  return null
}
function focused() {
  const bw = BrowserWindow.getFocusedWindow()
  for (const w of windows) if (w.win === bw) return w
  return [...windows][0] || null
}

function wireIpc(actions) {
  const shellOnly = (fn) => (e, ...a) => { const o = owner(e.sender); if (o && o.from === 'shell') return fn(o.w, ...a) }
  const anyOfOurs = (fn) => (e, ...a) => { const o = owner(e.sender); if (o) return fn(o.w, ...a) }
  ipcMain.handle('lite:tabs:get', shellOnly((w) => ({ active: w.active, tabs: w.tabs.map((t) => ({ id: t.id, title: t.title, kind: t.target.kind, view: t.target.view || '', loading: t.loading })) })))
  ipcMain.handle('lite:tabs:open', anyOfOurs((w, target) => w.open(target || {})))
  ipcMain.handle('lite:tabs:activate', shellOnly((w, id) => w.activate(String(id))))
  ipcMain.handle('lite:tabs:close', shellOnly((w, id) => w.close(String(id))))
  ipcMain.handle('lite:tabs:menu', shellOnly((w, id) => w.tabMenu(String(id))))
  ipcMain.handle('lite:window:new', anyOfOurs(() => { new TabWindow() }))
  ipcMain.handle('lite:open', anyOfOurs((w, what) => actions.open(String(what))))
  ipcMain.handle('lite:info', anyOfOurs(() => actions.info()))
  ipcMain.handle('lite:is-fullscreen', anyOfOurs((w) => w.win.isFullScreen()))
}

/** Menu items that act on the focused window's tabs. */
function menuItems() {
  const on = (fn) => () => { const w = focused(); if (w) fn(w) }
  return [
    { label: '홈', accelerator: 'CmdOrCtrl+T', click: on((w) => w.activate('home')) },
    { label: '새 창', accelerator: 'CmdOrCtrl+N', click: () => { if (ctx) new TabWindow() } },
    { label: '탭 닫기', accelerator: 'CmdOrCtrl+W', click: on((w) => (w.active === 'home' ? w.win.close() : w.close(w.active))) },
    { label: '탭 새로고침', accelerator: 'CmdOrCtrl+R', click: on((w) => w.activeContents().reload()) },
    { type: 'separator' },
    { label: '다음 탭', accelerator: 'Ctrl+Tab', click: on((w) => w.cycle(1)) },
    { label: '이전 탭', accelerator: 'Ctrl+Shift+Tab', click: on((w) => w.cycle(-1)) },
    ...[1, 2, 3, 4, 5, 6, 7, 8, 9].map((n) => ({ label: `탭 ${n}`, accelerator: `CmdOrCtrl+${n}`, visible: false, click: on((w) => w.nth(n)) })),
    { type: 'separator' },
    { label: '개발자 도구 (현재 탭)', accelerator: 'Alt+CmdOrCtrl+I', click: on((w) => w.activeContents().toggleDevTools()) },
  ]
}

/** Services are up: every window swaps its boot page for the shell. */
function ready(c) {
  ctx = c
  for (const w of windows) w.win.loadURL(shellUrl())
}

module.exports = { TabWindow, ready, wireIpc, menuItems, focused, windows: () => [...windows], BAR }
