// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Javier Núñez
//
// One project per product with flows in products/<product>/e2e/, found on its own. Each product
// reads its settings from outside the repository and only reaches the hosts declared there.
import fs from 'node:fs'
import path from 'node:path'

import { defineConfig, devices } from '@playwright/test'

import { effectsAuthorized } from './support/effects.js'
import { PRODUCTS_DIR, assertTestEnvironment, e2eHome, readProductEnv } from './support/environment.js'

// Every worker inherits the variable, so all of them write to the same evidence folder.
if (!process.env.E2E_RUN_DIR) {
  const stamp = new Date().toISOString().replace(/[:T]/g, '-').slice(0, 19)
  process.env.E2E_RUN_DIR = path.join(e2eHome(), 'evidence', stamp)
}
const RUN_DIR = process.env.E2E_RUN_DIR
fs.mkdirSync(RUN_DIR, { recursive: true, mode: 0o700 })
fs.chmodSync(RUN_DIR, 0o700)

// With effects authorised, one case at a time and no retries: a retry could repeat a charge.
const serial = effectsAuthorized()

const products = fs.existsSync(PRODUCTS_DIR)
  ? fs.readdirSync(PRODUCTS_DIR).filter((name) => !name.startsWith('_') && fs.existsSync(path.join(PRODUCTS_DIR, name, 'e2e')))
  : []

const projects = products.map((product) => {
  const env = readProductEnv(product)
  assertTestEnvironment(product, env)
  return {
    name: product,
    testDir: path.join(PRODUCTS_DIR, product, 'e2e'),
    use: { ...devices['Desktop Chrome'], baseURL: env.BASE_URL, productEnv: env }
  }
})

export default defineConfig({
  testMatch: '**/*.e2e.js',
  fullyParallel: !serial,
  workers: serial ? 1 : undefined,
  retries: serial ? 0 : 1,
  forbidOnly: Boolean(process.env.CI),
  reporter: [
    ['list'],
    ['html', { open: 'never', outputFolder: path.join(RUN_DIR, 'report') }],
    ['./support/evidence-reporter.js']
  ],
  outputDir: path.join(RUN_DIR, 'results'),
  // Evidence of every case, pass or fail
  use: { trace: 'on', screenshot: 'on', video: 'on' },
  projects
})
