// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Javier Núñez
//
// Effects guard. A flow never charges, buys, signs, registers or writes to a third party for real.
// Each product declares in products/<product>/e2e/effects.json the operations that have such
// effects, and the guard cuts them before they reach the backend unless every condition in
// decide() holds. Without a policy the product runs strict: reads only.
//
// effects.json:
//   {
//     "strict": false,                       true: any write outside allowedWrites is cut
//     "effects": [{ "id": "payment", "category": "money",
//                   "graphql": ["createCharge"],                 root fields that have the effect
//                   "rest": [{ "method": "POST", "path": "^/api/payments" }],
//                   "requiresSimulated": ["payments"] }],        or ["never"]: never authorised
//     "allowedWrites": ["^/api/session"],     path patterns a strict product may still write
//     "reads": ["searchOrders"]               GraphQL root fields that only read; once listed, any
//                                            other root field counts as a write
//   }
import fs from 'node:fs'
import path from 'node:path'

import { PRODUCTS_DIR, list } from './environment.js'

const WRITE_METHODS = new Set(['POST', 'PUT', 'PATCH', 'DELETE'])

export const loadPolicy = (product, productsDir = PRODUCTS_DIR) => {
  const file = path.join(productsDir, product, 'e2e', 'effects.json')
  if (!fs.existsSync(file)) {
    return { strict: true, effects: [], allowedWrites: [], reads: [] }
  }
  const policy = JSON.parse(fs.readFileSync(file, 'utf8'))
  return {
    strict: Boolean(policy.strict),
    effects: policy.effects || [],
    allowedWrites: (policy.allowedWrites || []).map((r) => new RegExp(r)),
    reads: policy.reads || []
  }
}

// What the run asked for. Authorisations come from the person launching it, never from CI.
export const runSettings = (productEnv = {}, env = process.env) => {
  const unattended = Boolean(env.CI || env.E2E_UNATTENDED)
  return {
    unattended,
    simulated: list(productEnv.SIMULATED),
    authorized: unattended ? [] : list(env.E2E_EFFECTS),
    maxEffects: Number(env.E2E_MAX_EFFECTS || 20)
  }
}

export const effectsAuthorized = (env = process.env) => Boolean(env.E2E_EFFECTS) && !env.CI && !env.E2E_UNATTENDED

// The root fields of a GraphQL operation, past aliases, arguments and selections.
export const rootFields = (query) => {
  const start = query.indexOf('{')
  if (start < 0) return []
  const fields = []
  let depth = 0
  let parens = 0
  let token = ''
  let afterToken = false
  for (let i = start + 1; i < query.length; i++) {
    const ch = query[i]
    if (ch === '"') {
      i = query.indexOf('"', i + 1)
      if (i < 0) break
      continue
    }
    if (ch === '(') parens++
    else if (ch === ')') parens--
    if (parens > 0 || ch === ')') continue
    if (ch === '{') depth++
    else if (ch === '}') {
      if (depth === 0) break
      depth--
    }
    if (depth !== 0) continue
    if (/\w/.test(ch)) {
      if (afterToken && token) {
        fields.push(token)
        token = ''
      }
      afterToken = false
      token += ch
    } else if (ch === ':' && token) {
      token = '' // an alias: the field comes next
    } else if (token) {
      afterToken = true
    }
  }
  if (token) fields.push(token)
  return fields.filter((f) => f !== 'on' && !/^\d/.test(f))
}

export const describeCall = (method, url, postData) => {
  const { pathname } = new URL(url)
  let body = null
  try {
    body = postData ? JSON.parse(postData) : null
  } catch {
    body = null
  }
  const ops = body && (Array.isArray(body) ? body : [body]).filter((op) => op && typeof op.query === 'string')
  const graphql = ops && ops.length
    ? ops.map((op) => ({ name: op.operationName || null, fields: rootFields(op.query), mutation: /^\s*mutation\b/.test(op.query) }))
    : null
  return { method: method.toUpperCase(), path: pathname, graphql }
}

const label = (call) => call.graphql
  ? call.graphql.map((op) => op.fields.join('+') || op.name || '(no field)').join(',')
  : `${call.method} ${call.path}`

const matchEffect = (policy, call) => {
  for (const effect of policy.effects) {
    for (const op of call.graphql || []) {
      const field = op.fields.find((f) => (effect.graphql || []).includes(f))
      if (field) return effect
    }
    for (const rule of effect.rest || []) {
      if ((!rule.method || rule.method.toUpperCase() === call.method) && new RegExp(rule.path).test(call.path)) return effect
    }
  }
  return null
}

// A GraphQL read also travels as a POST: it writes when it is a mutation, or, once the policy
// lists its reads, when it asks for a root field that is not one of them.
const writes = (policy, call) => {
  if (!call.graphql) return WRITE_METHODS.has(call.method)
  return call.graphql.some((op) => op.mutation || (policy.reads.length > 0 && op.fields.some((f) => !policy.reads.includes(f))))
}

export const needsSimulated = (effect) => [].concat((effect && effect.requiresSimulated) || [])

// effectsUsed: how many effects this run already let out, across workers.
export const decide = ({ policy, settings, tags, call, effectsUsed = 0 }) => {
  const operation = label(call)
  const effect = matchEffect(policy, call)
  if (effect) {
    const reasons = []
    if (settings.unattended) reasons.push('the run is unattended')
    if (!tags.includes(`@effect-${effect.id}`)) reasons.push(`the case does not declare @effect-${effect.id}`)
    if (needsSimulated(effect).includes('never')) reasons.push(`"${effect.id}" is never authorised in a flow`)
    for (const integration of needsSimulated(effect).filter((i) => i !== 'never')) {
      if (!settings.simulated.includes(integration)) reasons.push(`"${integration}" is not declared simulated in SIMULATED`)
    }
    if (!settings.authorized.includes(effect.id)) reasons.push(`the run did not authorise "${effect.id}" in E2E_EFFECTS`)
    if (effectsUsed >= settings.maxEffects) reasons.push(`the cap of ${settings.maxEffects} effects was reached`)
    return { effect: effect.id, category: effect.category || null, operation, allowed: reasons.length === 0, reasons }
  }
  if (policy.strict && writes(policy, call) && !policy.allowedWrites.some((r) => r.test(call.path))) {
    return { effect: null, operation, allowed: false, reasons: ['the product has no complete effects policy and this call writes'] }
  }
  return { effect: null, operation, allowed: true, reasons: [] }
}

// Shared run state (several workers append to the same files in the run folder).
const runFile = (name) => path.join(process.env.E2E_RUN_DIR || '.', name)
export const readLines = (name) =>
  fs.existsSync(runFile(name)) ? fs.readFileSync(runFile(name), 'utf8').split('\n').filter(Boolean).map((l) => JSON.parse(l)) : []
export const effectsUsed = () => readLines('calls.jsonl').filter((e) => e.decision === 'allowed' && e.effect).length

export const recordDecision = (testInfo, call, decision, status) => {
  const entry = {
    at: new Date().toISOString(),
    case: testInfo.title,
    product: testInfo.project.name,
    method: call.method,
    path: call.path,
    operation: decision.operation,
    effect: decision.effect,
    decision: decision.allowed ? 'allowed' : 'cut',
    reasons: decision.reasons,
    status: status ?? null
  }
  fs.appendFileSync(runFile('calls.jsonl'), `${JSON.stringify(entry)}\n`)
  return entry
}
