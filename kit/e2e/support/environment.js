// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Javier Núñez
//
// Where each person's configuration lives and which hosts a run may reach. Nothing here touches
// the network.
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

export const SYSTEM = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..')
// The older name of the same folder, kept for the organisation's own tests that import it.
export const SDLC = SYSTEM
export const PRODUCTS_DIR = process.env.E2E_PRODUCTS_DIR || path.join(SYSTEM, 'products')

// organisation.short_name from system.yml (sdlc.yml before tools/migrate.sh), so two
// organisations' runs never share a folder.
export const orgName = (system = SYSTEM) => {
  const config = ['system.yml', 'sdlc.yml'].map((f) => path.join(system, f)).find((f) => fs.existsSync(f))
  try {
    const text = fs.readFileSync(config, 'utf8')
    const m = text.match(/^organisation:\n(?:[ \t]+.*\n|\s*\n)*?[ \t]+short_name:[ \t]*["']?([A-Za-z0-9_-]+)/m)
    return m ? m[1] : 'system'
  } catch {
    return 'system'
  }
}

// Outside the repository, only readable by the person: ~/.<org>-e2e, or E2E_HOME.
export const e2eHome = () => process.env.E2E_HOME || path.join(os.homedir(), `.${orgName()}-e2e`)
export const envFile = (product) => path.join(e2eHome(), `${product}.env`)

// KEY=value lines; blank lines and # comments ignored; surrounding quotes removed.
export const parseEnv = (text) => {
  const env = {}
  for (const raw of text.split(/\r?\n/)) {
    const line = raw.trim()
    if (!line || line.startsWith('#')) continue
    const m = line.match(/^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$/)
    if (!m) continue
    env[m[1]] = m[2].replace(/^(['"])(.*)\1$/, '$2')
  }
  return env
}

// The product's settings. A file other people can read holds test users and keys in the open, so
// the run refuses it until its mode is 0600. Windows has no such mode to check.
export const readProductEnv = (product) => {
  const file = envFile(product)
  if (!fs.existsSync(file)) return {}
  if (process.platform !== 'win32' && (fs.statSync(file).mode & 0o077) !== 0) {
    throw new Error(`${file} can be read by other people. Run: chmod 600 "${file}"`)
  }
  return parseEnv(fs.readFileSync(file, 'utf8'))
}

export const list = (value) => (value || '').split(',').map((item) => item.trim()).filter(Boolean)

// Only hosts declared as test environments. Production is never declared, and neither is
// localhost unless the person says so.
export const assertTestEnvironment = (product, env) => {
  if (!env.BASE_URL) return
  const { hostname } = new URL(env.BASE_URL)
  if (!list(env.ALLOWED_HOSTS).includes(hostname)) {
    throw new Error(
      `The flows of ${product} do not run against ${hostname}: it is not in ALLOWED_HOSTS of ${envFile(product)}. ` +
        'Declare test environments only, never production.'
    )
  }
}
