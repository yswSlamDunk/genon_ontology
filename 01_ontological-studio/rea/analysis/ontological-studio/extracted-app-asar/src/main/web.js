'use strict'
// One local origin for the UI: the Studio SPA, /api and /mcp reverse-proxied to
// the Python processes (SSE streams pass through untouched), /app/* for shell
// info, /fabric-bridge/* for the data-fabric compatible catalog, /codeapps/api/* and
// /apps/* for code apps.
const http = require('http')
const fs = require('fs')
const path = require('path')

const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.ico': 'image/x-icon', '.woff2': 'font/woff2', '.woff': 'font/woff', '.ttf': 'font/ttf', '.wasm': 'application/wasm', '.mp4': 'video/mp4', '.webm': 'video/webm', '.map': 'application/json' }

function proxy(req, res, port, rewrite = (u) => u) {
  const up = http.request({ host: '127.0.0.1', port, method: req.method, path: rewrite(req.url), headers: { ...req.headers, host: `127.0.0.1:${port}` } }, (r) => {
    res.writeHead(r.statusCode, r.headers)
    r.pipe(res)
  })
  up.on('error', (e) => { if (!res.headersSent) res.writeHead(502, { 'content-type': 'application/json' }); res.end(JSON.stringify({ error: `upstream :${port} ${e.code || e.message}` })) })
  req.on('aborted', () => up.destroy())
  req.pipe(up)
}

// Only Vite's /assets/* carry content hashes and can be cached for good. Everything else
// (index.html, the shell, brand-mark.svg, favicon) is revalidated, so an app update never
// leaves a stale copy behind.
function serveStatic(root, req, res, { revalidate = false } = {}) {
  let p = decodeURIComponent(new URL(req.url, 'http://x').pathname)
  if (p === '/') p = '/index.html'
  let file = path.join(root, path.normalize(p).replace(/^(\.\.[/\\])+/, ''))
  if (!file.startsWith(root) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) file = path.join(root, 'index.html')
  const ext = path.extname(file)
  res.writeHead(200, { 'content-type': MIME[ext] || 'application/octet-stream', 'cache-control': !revalidate && p.startsWith('/assets/') ? 'max-age=31536000, immutable' : 'no-cache' })
  fs.createReadStream(file).pipe(res)
}

const NOT_IN_LITE = `<!doctype html><meta charset="utf-8"><body style="margin:0;font:14px/1.6 -apple-system,'Apple SD Gothic Neo',sans-serif;background:#14171c;color:#93a1b3;padding:48px">
<h2 style="color:#e6eaf0;font-size:17px;font-weight:650">Ontological Studio 에 포함되지 않은 화면입니다</h2>
<p>이 화면(robo-data-frontend: 코드 분석·데이터소스 상세)은 robo-analyzer · robo-catalog · MindsDB 를 필요로 합니다.</p>
<p>Ontological Studio 에서 데이터소스는 Ontological 데이터 패브릭에 있습니다 — Studio 의 <b style="color:#e6eaf0">데이터소스</b> 탭에서 연결·가상 노드·관계를 다루거나,
<b style="color:#e6eaf0">Ontological Portal</b> 에서 <code style="color:#18b6a0">SHOW DATASOURCES</code>, <code style="color:#18b6a0">MATCH (s:Supplier) RETURN s</code> 로 조회하세요.</p></body>`

// kinetic-action (the executor behind 「시스템 등록」 and actions) runs inside the package
// (kinetic.js). Until it is up — or if it could not start — say so in the panel's own terms
// instead of letting the backend report a connection error to a placeholder address.
const KINETIC_ABSENT = {
  url: '시작하지 않음', identity: null, reachable: false,
  error: '키네틱 액션 실행기(kinetic-action)가 아직 시작되지 않았거나 시작하지 못했습니다. 로그 폴더의 kinetic.log 를 확인하세요.',
}

// The window's own page: tab strip + home launcher (src/renderer/shell). Same origin as
// Studio, so it reads the same theme setting and the same /api.
const SHELL_DIR = path.join(__dirname, '..', 'renderer', 'shell')

function start({ port, frontend, ports, graph, bridge, status, kineticOn, jwks, codeapps }) {
  const server = http.createServer((req, res) => {
    const u = req.url
    if (u === '/lite-shell' || u.startsWith('/lite-shell/')) {
      req.url = u.slice('/lite-shell'.length) || '/'
      return serveStatic(SHELL_DIR, req, res, { revalidate: true })
    }
    // (The registry panel shows a failed list's `detail` as its banner.)
    // kinetic-action verifies the tokens the app minted against this key set (kinetic.js)
    if (u === '/kinetic-idp/jwks.json') { res.writeHead(200, { 'content-type': 'application/json' }); return res.end(JSON.stringify(jwks())) }
    if (!kineticOn() && req.method === 'GET' && (u === '/api/act/health' || u === '/api/act/systems')) {
      res.writeHead(u === '/api/act/health' ? 200 : 503, { 'content-type': 'application/json; charset=utf-8' })
      return res.end(JSON.stringify(u === '/api/act/health' ? KINETIC_ABSENT : { detail: KINETIC_ABSENT.error }))
    }
    if (u === '/app/portal-info') { res.writeHead(200, { 'content-type': 'application/json' }); return res.end(JSON.stringify({ url: `http://127.0.0.1:${ports.portal}`, graph })) }
    if (u === '/app/status') { res.writeHead(200, { 'content-type': 'application/json' }); return res.end(JSON.stringify(status())) }
    if (u.startsWith('/fabric-bridge/')) return bridge(req, res, u.slice('/fabric-bridge'.length))
    // code apps (codeapps.js): their API and the apps themselves
    if (codeapps && u.startsWith('/codeapps/api/')) return codeapps.handle(req, res, u.slice('/codeapps/api'.length))
    if (codeapps && (u === '/apps' || u.startsWith('/apps/'))) return codeapps.serve(req, res, u.slice('/apps'.length))
    // Paths the SPA's datasource panel uses (the full desktop's gateway shim).
    if (u.startsWith('/api/gateway/data-fabric/')) return bridge(req, res, u.slice('/api/gateway/data-fabric'.length))
    if (u.startsWith('/api/gateway/text2sql/')) return bridge(req, res, u.slice('/api/gateway'.length))
    if (u === '/api' || u.startsWith('/api/')) return proxy(req, res, ports.backend)
    if (u.startsWith('/mcp')) return proxy(req, res, ports.mcp)
    // robo-data-frontend (code-analysis / datasource detail screens) needs robo-analyzer,
    // robo-catalog and MindsDB, which this package does not ship. Say so instead of
    // letting the SPA fallback render Studio inside its own iframe.
    if (u === '/analyzer' || u.startsWith('/analyzer/')) {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' })
      return res.end(NOT_IN_LITE)
    }
    serveStatic(frontend, req, res)
  })
  server.keepAliveTimeout = 5000
  return new Promise((resolve, reject) => { server.once('error', reject); server.listen(port, '127.0.0.1', () => resolve(server)) })
}

module.exports = { start }
