'use strict'
// Preferred ports are tried first; a busy one falls back to an ephemeral port,
// so the app never collides with services already on the machine.
const net = require('net')

function tryListen(port) {
  return new Promise((resolve) => {
    const s = net.createServer()
    s.once('error', () => resolve(null))
    s.listen({ port, host: '127.0.0.1', exclusive: true }, () => {
      const p = s.address().port
      s.close(() => resolve(p))
    })
  })
}

const PREFERRED = { pg: 27432, bolt: 27687, portal: 27474, backend: 27800, mcp: 27810, web: 27900, kinetic: 27830, erp: 27841, wms: 27842, crm: 27843 }

/** `saved` = ports used last time (sticky), so data sources and MCP clients keep their address. */
async function allocate(saved = {}) {
  const out = {}
  const taken = new Set()
  for (const [k, pref] of Object.entries(PREFERRED)) {
    const envPref = Number(process.env[`ONTOLOGY_LITE_${k.toUpperCase()}_PORT`] || 0)
    let p = await tryListen(envPref || saved[k] || pref)
    while (!p || taken.has(p)) p = await tryListen(0)
    taken.add(p)
    out[k] = p
  }
  return out
}

module.exports = { allocate, PREFERRED }
