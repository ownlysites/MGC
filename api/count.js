// Plans-built counter.
//
// The whole contract: GET returns the number, POST adds one and returns it.
// There is no request body in either direction and nothing is read from the
// caller — no report, no answers, no identifier. The only thing this endpoint
// knows how to say is a single integer, which is why it can exist without
// weakening the promise that nothing about a person's file leaves their
// browser.
//
// Storage is one Redis key on the project's own KV store (Vercel KV and
// Upstash expose the same REST shape). Until a store is attached the route
// answers with the seed and reports configured:false, so the page still
// renders a number instead of a dash.

const SEED = 5025;
const KEY = 'mgc:plans';

const REST_URL = process.env.KV_REST_API_URL || process.env.UPSTASH_REDIS_REST_URL || '';
const REST_TOKEN = process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN || '';

async function redis(parts) {
  const url = REST_URL.replace(/\/+$/, '') + '/' + parts.map(encodeURIComponent).join('/');
  const r = await fetch(url, { headers: { Authorization: 'Bearer ' + REST_TOKEN } });
  if (!r.ok) throw new Error('kv ' + r.status);
  const j = await r.json();
  return j.result;
}

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store, max-age=0');
  res.setHeader('Content-Type', 'application/json; charset=utf-8');

  if (req.method !== 'GET' && req.method !== 'POST' && req.method !== 'HEAD') {
    res.statusCode = 405;
    return res.end(JSON.stringify({ error: 'method not allowed' }));
  }

  if (!REST_URL || !REST_TOKEN) {
    res.statusCode = 200;
    return res.end(JSON.stringify({ count: SEED, configured: false }));
  }

  try {
    // SETNX only writes when the key does not exist, so the seed is applied
    // exactly once in the life of the store and never resets the running total.
    await redis(['setnx', KEY, String(SEED)]);
    const v = req.method === 'POST' ? await redis(['incr', KEY]) : await redis(['get', KEY]);
    const n = parseInt(v, 10);
    res.statusCode = 200;
    return res.end(JSON.stringify({
      count: isFinite(n) && n > 0 ? n : SEED,
      configured: true
    }));
  } catch (e) {
    // A store that is down must not break the page. Report the seed and say so.
    res.statusCode = 200;
    return res.end(JSON.stringify({ count: SEED, configured: false, degraded: true }));
  }
};
