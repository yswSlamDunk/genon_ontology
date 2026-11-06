'use strict'
// Menu bar (tray) icon: the brand mark, as a template image on macOS so it follows the
// menu bar's light/dark tint. Its menu shows where start-up is and opens the common places.
// Icons come from `npm run icon` (resources/tray/).
const { Tray, Menu, nativeImage } = require('electron')
const path = require('path')

const PHASES = { starting: '시작하는 중', postgres: 'PostgreSQL 시작 중', bootstrap: '첫 실행 준비 중', ontological: 'Ontological 시작 중', studio: 'Studio 시작 중', ready: '실행 중', error: '시작하지 못함' }

let tray = null
let ctx = null // { resources, phase(), agent(), open(target), home(), newWindow(), shellOpen(what), quit() }

function create(c) {
  ctx = c
  const mac = process.platform === 'darwin'
  const img = nativeImage.createFromPath(path.join(ctx.resources, 'tray', mac ? 'trayTemplate.png' : 'tray.png'))
  if (mac) img.setTemplateImage(true)
  tray = new Tray(img)
  tray.setToolTip('Ontological Studio')
  update()
  return tray
}

function update() {
  if (!tray || tray.isDestroyed()) return
  const phase = ctx.phase()
  const ready = phase === 'ready'
  const agent = ctx.agent()
  tray.setContextMenu(Menu.buildFromTemplate([
    { label: `Ontological Studio — ${PHASES[phase] || phase}`, enabled: false },
    ...(agent ? [{ label: `에이전트: ${agent.label}`, enabled: false }] : []),
    { type: 'separator' },
    { label: '홈 열기', enabled: ready, click: () => ctx.home() },
    { label: 'Ontological Portal 탭', enabled: ready, click: () => ctx.open({ kind: 'portal' }) },
    { label: '데이터소스 탭', enabled: ready, click: () => ctx.open({ kind: 'studio', view: 'datasources' }) },
    { label: '새 창', enabled: ready, click: () => ctx.newWindow() },
    { type: 'separator' },
    { label: '설정 파일 열기 (studio.env)', click: () => ctx.shellOpen('settings') },
    { label: '로그 폴더 열기', click: () => ctx.shellOpen('logs') },
    { type: 'separator' },
    { label: '종료', click: () => ctx.quit() },
  ]))
}

function destroy() {
  if (tray && !tray.isDestroyed()) tray.destroy()
  tray = null
}

module.exports = { create, update, destroy, current: () => tray }
