// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Javier Núñez
//
// The evidence of every run, outside the repository, in <E2E home>/evidence/<stamp>/ (0700): who
// ran it, from which commit of the system, against what, with which authorisations, the result of each
// case, every call that went out with an effect or was cut, and a manifest with the SHA-256 of
// each file, written last, to show later that nothing was altered.
import crypto from 'node:crypto'
import { execFileSync } from 'node:child_process'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'

import { readLines } from './effects.js'
import { SYSTEM } from './environment.js'

const git = (...args) => {
  try {
    return execFileSync('git', ['-C', SYSTEM, ...args], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim()
  } catch {
    return ''
  }
}
const sha256 = (file) => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex')
const walk = (dir) => fs.existsSync(dir)
  ? fs.readdirSync(dir, { withFileTypes: true }).flatMap((e) => (e.isDirectory() ? walk(path.join(dir, e.name)) : [path.join(dir, e.name)]))
  : []
const LISTING = process.argv.includes('--list')

export default class EvidenceReporter {
  onBegin(config, suite) {
    if (LISTING) return
    this.dir = process.env.E2E_RUN_DIR
    this.results = []
    this.meta = {
      run: path.basename(this.dir),
      started: new Date().toISOString(),
      who: git('config', 'user.email') || os.userInfo().username,
      machine: os.hostname(),
      system: { commit: git('rev-parse', 'HEAD'), branch: git('rev-parse', '--abbrev-ref', 'HEAD'), dirty: Boolean(git('status', '--porcelain', '--', 'e2e', 'products')) },
      playwright: config.version,
      unattended: Boolean(process.env.CI || process.env.E2E_UNATTENDED),
      authorisedEffects: process.env.E2E_EFFECTS || '',
      cap: Number(process.env.E2E_MAX_EFFECTS || 20),
      arguments: process.argv.slice(2).join(' '),
      products: config.projects.map((p) => ({
        product: p.name,
        host: p.use.baseURL ? new URL(p.use.baseURL).host : null,
        simulated: (p.use.productEnv && p.use.productEnv.SIMULATED) || ''
      })),
      planned: suite.allTests().length
    }
  }

  onTestEnd(test, result) {
    if (LISTING) return
    this.results.push({
      product: test.parent.project()?.name,
      case: test.titlePath().slice(3).join(' › '),
      status: result.status,
      skipped: result.annotations.filter((a) => a.type === 'skip').map((a) => a.description).join('; '),
      ms: result.duration,
      retry: result.retry,
      error: result.error ? String(result.error.message || '').split('\n')[0] : null
    })
  }

  onEnd(result) {
    if (LISTING) return
    const meta = { ...this.meta, ended: new Date().toISOString(), result: result.status }
    fs.writeFileSync(path.join(this.dir, 'run.json'), JSON.stringify({ ...meta, cases: this.results }, null, 2))
    const calls = readLines('calls.jsonl')
    const out = calls.filter((c) => c.decision === 'allowed' && c.effect)
    const cut = calls.filter((c) => c.decision === 'cut')
    const count = (s) => this.results.filter((r) => r.status === s).length
    const cell = (t) => String(t || '').replace(/\|/g, '\\|')
    const lines = [
      `# Evidence of run ${meta.run}`,
      '',
      `- Who: ${meta.who} on ${meta.machine}`,
      `- From ${meta.started} to ${meta.ended}, result ${meta.result}`,
      `- System: ${meta.system.branch} @ ${meta.system.commit.slice(0, 10)}${meta.system.dirty ? ' (uncommitted changes in e2e or products)' : ''}, Playwright ${meta.playwright}`,
      `- Unattended: ${meta.unattended ? 'yes, so no effect could go out' : 'no'}`,
      `- Authorised effects: ${meta.authorisedEffects || 'none'}, cap ${meta.cap}`,
      ...meta.products.map((p) => `- ${p.product}: ${p.host || 'no environment declared'}, simulated: ${p.simulated || 'none'}`),
      '',
      `Cases: ${this.results.length}. Passed ${count('passed')}, failed ${count('failed') + count('timedOut')}, skipped ${count('skipped')}.`,
      `Effects that went out: ${out.length}. Calls cut by the guard: ${cut.length}.`,
      '',
      '## Cases',
      '',
      '| Case | Result | Duration | Note |',
      '| --- | --- | --- | --- |',
      ...this.results.map((r) => `| ${cell(r.case)} | ${r.status} | ${(r.ms / 1000).toFixed(1)} s | ${cell(r.error || r.skipped)} |`),
      '',
      '## Effects that went out',
      '',
      ...(out.length ? out.map((c) => `- ${c.at} · ${c.case} · ${c.effect} · ${c.operation} · ${c.status}`) : ['None.']),
      '',
      '## Calls cut',
      '',
      ...(cut.length ? cut.map((c) => `- ${c.at} · ${c.case} · ${c.operation}: ${c.reasons.join('; ')}`) : ['None.']),
      ''
    ]
    fs.writeFileSync(path.join(this.dir, 'summary.md'), lines.join('\n'))
  }

  // Last, once the HTML report and the other reporters have finished writing.
  async onExit() {
    if (LISTING) {
      fs.rmSync(this.dir || process.env.E2E_RUN_DIR, { recursive: true, force: true })
      return
    }
    const files = walk(this.dir).filter((f) => path.basename(f) !== 'manifest.json')
    const manifest = files.map((f) => ({ file: path.relative(this.dir, f), bytes: fs.statSync(f).size, sha256: sha256(f) }))
    fs.writeFileSync(path.join(this.dir, 'manifest.json'), JSON.stringify({ run: path.basename(this.dir), files: manifest }, null, 2))
    console.log(`\nEvidence of the run: ${path.join(this.dir, 'summary.md')}`)
  }

  printsToStdio() {
    return false
  }
}
