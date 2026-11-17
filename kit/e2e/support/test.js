// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Javier Núñez
//
// The fixtures every flow imports instead of @playwright/test:
//   import { test, expect } from '../../../e2e/support/test.js'
// The page and the `api` helper send every call through the effects guard, and the page never
// reaches an origin the product did not declare.
import { test as base, expect } from '@playwright/test'

import { decide, describeCall, effectsUsed, loadPolicy, needsSimulated, recordDecision, runSettings } from './effects.js'
import { envFile, list } from './environment.js'

const tagsOf = (testInfo) => [...new Set(testInfo.titlePath.join(' ').match(/@[\w-]+/g) || [])]
const isApiCall = (call) => Boolean(call.graphql) || call.method !== 'GET' || /\/api\//.test(call.path)

export const test = base.extend({
  // The product's settings, handed over by playwright.config.js
  productEnv: [{}, { option: true }],

  // Without a declared environment, the product's flows are skipped and say why
  requireEnvironment: [
    async ({ baseURL }, use, testInfo) => {
      testInfo.skip(!baseURL, `No BASE_URL in ${envFile(testInfo.project.name)}`)
      await use()
    },
    { auto: true }
  ],

  effects: [
    async ({ productEnv }, use, testInfo) => {
      const policy = loadPolicy(testInfo.project.name)
      const settings = runSettings(productEnv)
      const tags = tagsOf(testInfo)
      // A case with an effect runs only when the run authorises it and the environment simulates it
      for (const id of tags.filter((t) => t.startsWith('@effect-')).map((t) => t.slice('@effect-'.length))) {
        const effect = policy.effects.find((e) => e.id === id)
        testInfo.skip(settings.unattended, `Case with effect "${id}": never runs unattended`)
        testInfo.skip(!effect, `Effect "${id}" is not in the product's policy`)
        const missing = needsSimulated(effect).filter((i) => !settings.simulated.includes(i))
        testInfo.skip(missing.length > 0, `Case with effect "${id}": the environment does not declare ${missing.join(', ')} in SIMULATED`)
        testInfo.skip(!settings.authorized.includes(id), `Case with effect "${id}": the run did not authorise it in E2E_EFFECTS`)
      }
      const log = []
      const guard = (call) => {
        const decision = decide({ policy, settings, tags, call, effectsUsed: effectsUsed() })
        return { decision, record: (status) => log.push(recordDecision(testInfo, call, decision, status)) }
      }
      await use({ policy, settings, tags, guard })

      await testInfo.attach('calls', { body: JSON.stringify(log, null, 2), contentType: 'application/json' })
      const cut = log.filter((e) => e.decision === 'cut')
      if (cut.length) {
        throw new Error('The effects guard cut calls of this case:\n' + cut.map((e) => `  · ${e.operation}: ${e.reasons.join('; ')}`).join('\n'))
      }
    },
    { auto: true }
  ],

  page: async ({ page, baseURL, productEnv, effects }, use) => {
    const origins = [...(baseURL ? [new URL(baseURL).origin] : []), ...list(productEnv.ALLOWED_ORIGINS)]
    await page.route('**/*', async (route) => {
      const request = route.request()
      if (!origins.includes(new URL(request.url()).origin)) return route.abort()
      const call = describeCall(request.method(), request.url(), request.postData())
      if (!isApiCall(call)) return route.continue()
      const { decision, record } = effects.guard(call)
      if (!decision.allowed) {
        record('cut')
        return route.abort('blockedbyclient')
      }
      let response
      try {
        response = await route.fetch()
      } catch (error) {
        // The case ended with the call in flight: not an error of the case
        if (page.isClosed() || /Test ended|Target page|closed/.test(String(error))) return
        throw error
      }
      record(response.status())
      return route.fulfill({ response }).catch(() => {})
    })
    await use(page)
    await page.unrouteAll({ behavior: 'ignoreErrors' })
  },

  // API flows go through the same guard: api.post(url, { data }) instead of request.post
  api: async ({ request, effects, baseURL }, use) => {
    const send = (method) => async (url, options = {}) => {
      const absolute = new URL(url, baseURL || 'http://localhost').toString()
      const call = describeCall(method, absolute, options.data === undefined ? null : JSON.stringify(options.data))
      const { decision, record } = effects.guard(call)
      if (!decision.allowed) {
        record('cut')
        throw new Error(`Call cut by the effects guard: ${decision.operation}: ${decision.reasons.join('; ')}`)
      }
      const response = await request.fetch(url, { ...options, method })
      record(response.status())
      return response
    }
    await use({ get: send('GET'), post: send('POST'), put: send('PUT'), patch: send('PATCH'), delete: send('DELETE') })
  }
})

export { expect }
