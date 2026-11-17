// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Javier Núñez
//
// Tests of the effects guard and the environment checks. No browser, no network:
//   node --test support/*.test.js
import assert from 'node:assert/strict'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { beforeEach, test } from 'node:test'

import { decide, describeCall, effectsAuthorized, loadPolicy, rootFields, runSettings } from './effects.js'
import { assertTestEnvironment, orgName, parseEnv, readProductEnv } from './environment.js'

const API = 'https://api.test.example.com'
const gql = (query, operationName = null) => describeCall('POST', `${API}/graphql`, JSON.stringify({ operationName, query, variables: {} }))
const rest = (method, p, data = {}) => describeCall(method, `${API}${p}`, JSON.stringify(data))

let products
beforeEach(() => {
  products = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-guard-'))
  fs.mkdirSync(path.join(products, 'shop', 'e2e'), { recursive: true })
  fs.writeFileSync(path.join(products, 'shop', 'e2e', 'effects.json'), JSON.stringify({
    strict: true,
    effects: [
      { id: 'payment', category: 'money', graphql: ['createCharge'], rest: [{ method: 'POST', path: '^/api/payments' }], requiresSimulated: ['payments'] },
      { id: 'signature', graphql: ['signContract'], requiresSimulated: ['never'] }
    ],
    allowedWrites: ['^/api/session'],
    reads: ['searchOrders', 'order']
  }))
})

const shop = () => loadPolicy('shop', products)
const env = { SIMULATED: 'payments' }
const run = (vars = {}) => runSettings(env, vars)

test('an effect without the tag on the case is cut', () => {
  const d = decide({ policy: shop(), settings: run({ E2E_EFFECTS: 'payment' }), tags: [], call: rest('POST', '/api/payments') })
  assert.equal(d.allowed, false)
  assert.equal(d.effect, 'payment')
  assert.match(d.reasons.join(), /@effect-payment/)
})

test('tagged but not authorised by the run, it is cut', () => {
  const d = decide({ policy: shop(), settings: run(), tags: ['@effect-payment'], call: rest('POST', '/api/payments') })
  assert.equal(d.allowed, false)
  assert.match(d.reasons.join(), /E2E_EFFECTS/)
})

test('an integration not simulated is cut even when authorised', () => {
  const d = decide({ policy: shop(), settings: runSettings({}, { E2E_EFFECTS: 'payment' }), tags: ['@effect-payment'], call: gql('mutation { createCharge(amount: 1) { id } }') })
  assert.equal(d.allowed, false)
  assert.match(d.reasons.join(), /"payments" is not declared simulated/)
})

test('tagged, simulated and authorised, it goes out', () => {
  const d = decide({ policy: shop(), settings: run({ E2E_EFFECTS: 'payment' }), tags: ['@effect-payment'], call: gql('mutation Pay { charge: createCharge(amount: 1) { id } }') })
  assert.equal(d.allowed, true, d.reasons.join())
})

test('an unattended run lets no effect out, and authorises nothing', () => {
  for (const vars of [{ CI: '1', E2E_EFFECTS: 'payment' }, { E2E_UNATTENDED: '1', E2E_EFFECTS: 'payment' }]) {
    const settings = run(vars)
    assert.deepEqual(settings.authorized, [])
    const d = decide({ policy: shop(), settings, tags: ['@effect-payment'], call: rest('POST', '/api/payments') })
    assert.equal(d.allowed, false)
    assert.match(d.reasons.join(), /unattended/)
    assert.equal(effectsAuthorized(vars), false)
  }
  assert.equal(effectsAuthorized({ E2E_EFFECTS: 'payment' }), true)
})

test('the cap stops effects once reached', () => {
  const settings = run({ E2E_EFFECTS: 'payment', E2E_MAX_EFFECTS: '2' })
  const call = rest('POST', '/api/payments')
  assert.equal(decide({ policy: shop(), settings, tags: ['@effect-payment'], call, effectsUsed: 1 }).allowed, true)
  const d = decide({ policy: shop(), settings, tags: ['@effect-payment'], call, effectsUsed: 2 })
  assert.equal(d.allowed, false)
  assert.match(d.reasons.join(), /cap of 2/)
})

test('an effect marked never is never authorised', () => {
  const d = decide({ policy: shop(), settings: runSettings({ SIMULATED: 'never' }, { E2E_EFFECTS: 'signature' }), tags: ['@effect-signature'], call: gql('query { signContract(id: "1") }') })
  assert.equal(d.allowed, false)
  assert.match(d.reasons.join(), /never authorised/)
})

test('a strict product lets reads and its allowed writes through, and cuts other writes', () => {
  const policy = shop()
  const settings = run()
  assert.equal(decide({ policy, settings, tags: [], call: describeCall('GET', `${API}/api/orders`) }).allowed, true)
  assert.equal(decide({ policy, settings, tags: [], call: rest('POST', '/api/session') }).allowed, true)
  assert.equal(decide({ policy, settings, tags: [], call: gql('query { searchOrders { id } order(id: 1) { id } }') }).allowed, true)
  assert.equal(decide({ policy, settings, tags: [], call: rest('DELETE', '/api/orders/1') }).allowed, false)
  // a root field that is not a declared read writes, even in a query
  assert.equal(decide({ policy, settings, tags: [], call: gql('query { cancelOrder(id: 1) }') }).allowed, false)
})

test('without a policy the product runs strict: reads only', () => {
  const policy = loadPolicy('missing', products)
  assert.equal(policy.strict, true)
  const settings = run()
  assert.equal(decide({ policy, settings, tags: [], call: describeCall('GET', `${API}/api/orders`) }).allowed, true)
  assert.equal(decide({ policy, settings, tags: [], call: gql('query { anything { id } }') }).allowed, true)
  for (const call of [rest('POST', '/api/orders'), rest('PUT', '/x'), rest('PATCH', '/x'), describeCall('DELETE', `${API}/x`), gql('mutation { anything }')]) {
    assert.equal(decide({ policy, settings, tags: [], call }).allowed, false, call.method + call.path)
  }
})

test('root fields skip aliases, arguments and selections', () => {
  assert.deepEqual(rootFields('query Q($a: ID) { x: one(a: $a) { b { c } } two }'), ['one', 'two'])
})

test('the environment file must be private, and only declared hosts are reached', () => {
  const home = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-home-'))
  process.env.E2E_HOME = home
  try {
    const file = path.join(home, 'shop.env')
    fs.writeFileSync(file, '# test only\nBASE_URL="https://shop.test.example.com"\nALLOWED_HOSTS=shop.test.example.com\n')
    if (process.platform !== 'win32') {
      fs.chmodSync(file, 0o644)
      assert.throws(() => readProductEnv('shop'), /chmod 600/)
    }
    fs.chmodSync(file, 0o600)
    const env = readProductEnv('shop')
    assert.equal(env.BASE_URL, 'https://shop.test.example.com')
    assert.doesNotThrow(() => assertTestEnvironment('shop', env))
    assert.throws(() => assertTestEnvironment('shop', { ...env, BASE_URL: 'https://shop.example.com' }), /not in ALLOWED_HOSTS/)
    assert.doesNotThrow(() => assertTestEnvironment('shop', {}))
    assert.deepEqual(readProductEnv('other'), {})
  } finally {
    delete process.env.E2E_HOME
  }
})

test('env lines and the organisation name', () => {
  assert.deepEqual(parseEnv("export A=1\n\n# c\nB='two words'\nnot a line\n"), { A: '1', B: 'two words' })
  const system = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-system-'))
  assert.equal(orgName(system), 'system')
  fs.writeFileSync(path.join(system, 'sdlc.yml'), 'organisation:\n  name: "Acme"\n  short_name: "older"\n')
  assert.equal(orgName(system), 'older')
  fs.writeFileSync(path.join(system, 'system.yml'), 'organisation:\n  name: "Acme"\n  short_name: "acme"   # x\n')
  assert.equal(orgName(system), 'acme')
})
