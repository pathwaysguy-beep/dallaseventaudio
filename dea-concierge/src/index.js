var __defProp = Object.defineProperty;
var __name = (target, value) => __defProp(target, "name", { value, configurable: true });

import { DEA_SYSTEM_PROMPT } from "./prompt.js";

// src/index.js
var ANTHROPIC_URL = "https://api.anthropic.com/v1/messages";
var ANTHROPIC_VERSION = "2023-06-01";
var MAX_TOKENS = 1024;
var MAX_TURNS = 40;
var MAX_CHARS = 24e3;
var MAX_BODY_BYTES = 64 * 1024;
var JSON_HEADERS = { "content-type": "application/json; charset=utf-8" };
var FRIENDLY_ERROR = "Sorry, something went wrong on our end. Please call or text 817-210-7957.";
var FRIENDLY_BUSY = "I'm getting a lot of questions right now. Give it a moment and try again, or call or text 817-210-7957.";
function allowedOrigins(env) {
  return String(env.ALLOWED_ORIGINS || "").split(",").map((s) => s.trim()).filter(Boolean);
}
__name(allowedOrigins, "allowedOrigins");
function corsHeaders(env, request) {
  const origin = request.headers.get("Origin") || "";
  const list = allowedOrigins(env);
  const ok = list.includes(origin);
  return {
    "access-control-allow-origin": ok ? origin : list[0] || "",
    "access-control-allow-methods": "POST, OPTIONS",
    "access-control-allow-headers": "content-type",
    "access-control-max-age": "86400",
    vary: "Origin"
  };
}
__name(corsHeaders, "corsHeaders");
function json(body, status, extra) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...JSON_HEADERS, ...extra || {} }
  });
}
__name(json, "json");
function todayInDallas() {
  return new Intl.DateTimeFormat("en-US", {
    timeZone: "America/Chicago",
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric"
  }).format(/* @__PURE__ */ new Date());
}
__name(todayInDallas, "todayInDallas");
function validateHistory(raw) {
  if (!Array.isArray(raw)) return { error: "history must be an array" };
  if (raw.length === 0) return { error: "history is empty" };
  if (raw.length > MAX_TURNS) return { error: "conversation too long" };
  let total = 0;
  const history = [];
  for (const m of raw) {
    if (!m || typeof m !== "object") return { error: "bad message" };
    if (m.role !== "user" && m.role !== "assistant") {
      return { error: "bad role" };
    }
    if (typeof m.content !== "string") return { error: "bad content" };
    const content = m.content.trim();
    if (!content) return { error: "empty message" };
    total += content.length;
    if (total > MAX_CHARS) return { error: "conversation too long" };
    history.push({ role: m.role, content });
  }
  if (history[history.length - 1].role !== "user") {
    return { error: "last message must be from the visitor" };
  }
  return { history };
}
__name(validateHistory, "validateHistory");
function hasUsableContact(lead) {
  const name = String(lead.name || "").trim();
  const contact = String(lead.contact || "").trim();
  if (!name || !contact) return false;
  const looksEmail = extractEmail(contact) !== null;
  const digits = (contact.match(/\d/g) || []).length;
  return looksEmail || digits >= 7;
}
__name(hasUsableContact, "hasUsableContact");
function extractEmail(text) {
  const m = String(text || "").match(
    /[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}/
  );
  if (!m) return null;
  const addr = m[0];
  if (addr.length > 254 || addr.includes("..")) return null;
  return addr;
}
__name(extractEmail, "extractEmail");
function escapeHtml(s) {
  return String(s == null ? "" : s).replace(
    /[&<>"']/g,
    (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]
  );
}
__name(escapeHtml, "escapeHtml");
var LEAD_FIELDS = [
  ["name", "Name"],
  ["contact", "Contact"],
  ["persona", "Who they are"],
  ["event_type", "Event type"],
  ["event_date", "Event date"],
  ["venue", "Venue"],
  ["city", "City"],
  ["guest_count", "Guests"],
  ["services", "Services"],
  ["recurring", "Recurring"],
  ["company", "Company"],
  ["notes", "Notes"]
];
async function emailLead(env, lead) {
  if (!env.RESEND_API_KEY || !env.LEAD_TO || !env.LEAD_FROM) return false;
  const rows = LEAD_FIELDS.filter(([k]) => String(lead[k] || "").trim()).map(
    ([k, label]) => `<tr><td style="padding:4px 14px 4px 0;color:#666;white-space:nowrap">${label}</td><td style="padding:4px 0"><strong>${escapeHtml(lead[k])}</strong></td></tr>`
  ).join("");
  const subject = `Chat lead: ${lead.name || "no name"}${lead.event_type ? " - " + lead.event_type : ""}${lead.event_date ? " - " + lead.event_date : ""}`;
  let res;
  try {
    res = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        authorization: `Bearer ${env.RESEND_API_KEY}`,
        "content-type": "application/json"
      },
      body: JSON.stringify({
        from: env.LEAD_FROM,
        to: String(env.LEAD_TO).split(",").map((s) => s.trim()),
        reply_to: extractEmail(lead.contact) || void 0,
        subject,
        html: `<p style="font:14px system-ui">From the AV Concierge on dallaseventaudio.com.</p><table style="font:14px system-ui;border-collapse:collapse">${rows}</table>`
      })
    });
  } catch (e) {
    console.error("LEAD EMAIL: request failed", String(e));
    return false;
  }
  let detail = "";
  try {
    detail = JSON.stringify(await res.json()).slice(0, 400);
  } catch {
    detail = "(no json body)";
  }
  if (!res.ok) {
    console.error(
      "LEAD EMAIL FAILED",
      res.status,
      detail,
      "| from:",
      env.LEAD_FROM,
      "| to:",
      env.LEAD_TO
    );
    return false;
  }
  console.log("LEAD EMAIL SENT", detail);
  return true;
}
__name(emailLead, "emailLead");
async function storeLead(env, lead, meta) {
  if (!env.DB) return false;
  await env.DB.prepare(
    `INSERT INTO leads
      (created_at, name, contact, persona, event_type, event_date, venue, city,
       guest_count, services, recurring, company, notes, source, status, raw)
     VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`
  ).bind(
    (/* @__PURE__ */ new Date()).toISOString(),
    lead.name || "",
    lead.contact || "",
    lead.persona || "",
    lead.event_type || "",
    lead.event_date || "",
    lead.venue || "",
    lead.city || "",
    lead.guest_count || "",
    lead.services || "",
    lead.recurring || "",
    lead.company || "",
    lead.notes || "",
    "chat",
    meta.status || "new",
    JSON.stringify(lead)
  ).run();
  return true;
}
__name(storeLead, "storeLead");
function parseSignals(raw) {
  let reply = String(raw || "").trim();
  let ended = false;
  let abusive = false;
  const endMatch = reply.match(/<<<END\s+(\w+)\s*>>>/);
  if (endMatch) {
    ended = true;
    abusive = endMatch[1] === "abusive";
    reply = reply.replace(endMatch[0], "").trim();
  }
  let lead = null;
  let leadMalformed = false;
  const leadMatch = reply.match(/<<<LEAD\s+([\s\S]*?)\s*>>>/);
  if (leadMatch) {
    reply = reply.replace(leadMatch[0], "").trim();
    try {
      lead = JSON.parse(leadMatch[1]);
      if (!lead || typeof lead !== "object" || Array.isArray(lead)) {
        lead = null;
        leadMalformed = true;
      }
    } catch {
      leadMalformed = true;
    }
  }
  return { reply, ended, abusive, lead, leadMalformed };
}
__name(parseSignals, "parseSignals");
async function underDailyCap(env) {
  const cap = Number(env.DAILY_CAP || 0);
  if (!cap || !env.RATE) return { ok: true, used: null, cap };
  const day = new Intl.DateTimeFormat("en-CA", {
    timeZone: "America/Chicago",
    year: "numeric",
    month: "2-digit",
    day: "2-digit"
  }).format(/* @__PURE__ */ new Date());
  const key = "chat-count:" + day;
  const used = Number(await env.RATE.get(key) || 0);
  if (used >= cap) return { ok: false, used, cap };
  await env.RATE.put(key, String(used + 1), { expirationTtl: 60 * 60 * 48 });
  return { ok: true, used: used + 1, cap };
}
__name(underDailyCap, "underDailyCap");
var index_default = {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const cors = corsHeaders(env, request);
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors });
    }
    if (url.pathname === "/api/health") {
      return json({ ok: true, model: env.MODEL || null }, 200, cors);
    }
    if (url.pathname !== "/api/chat") {
      return json({ error: "not found" }, 404, cors);
    }
    if (request.method !== "POST") {
      return json({ error: "method not allowed" }, 405, cors);
    }
    const origin = request.headers.get("Origin") || "";
    const list = allowedOrigins(env);
    if (list.length && !list.includes(origin)) {
      return json({ error: "forbidden" }, 403, cors);
    }
    const declared = Number(request.headers.get("content-length") || 0);
    if (declared > MAX_BODY_BYTES) {
      return json({ error: "body too large" }, 413, cors);
    }
    if (env.CHAT_LIMIT) {
      const ip = request.headers.get("CF-Connecting-IP") || "unknown";
      const { success } = await env.CHAT_LIMIT.limit({ key: ip });
      if (!success) return json({ reply: FRIENDLY_BUSY }, 429, cors);
    }
    const daily = await underDailyCap(env);
    if (!daily.ok) {
      console.error("daily chat cap reached", daily.used, "of", daily.cap);
      return json({ reply: FRIENDLY_BUSY }, 429, cors);
    }
    let body;
    try {
      body = await request.json();
    } catch {
      return json({ error: "invalid json" }, 400, cors);
    }
    const checked = validateHistory(body && body.history);
    if (checked.error) return json({ error: checked.error }, 400, cors);
    if (!env.ANTHROPIC_API_KEY) {
      console.error("ANTHROPIC_API_KEY is not set");
      return json({ reply: FRIENDLY_ERROR }, 500, cors);
    }
    // The static prompt goes first and is cached across requests; the date
    // rides in a second block so it never breaks the cache.
    const system = [
      { type: "text", text: DEA_SYSTEM_PROMPT, cache_control: { type: "ephemeral" } },
      { type: "text", text: `Today's date is ${todayInDallas()}.` }
    ];
    let data;
    try {
      const res = await fetch(ANTHROPIC_URL, {
        method: "POST",
        headers: {
          "content-type": "application/json",
          "x-api-key": env.ANTHROPIC_API_KEY,
          "anthropic-version": ANTHROPIC_VERSION
        },
        body: JSON.stringify({
          model: env.MODEL || "claude-sonnet-4-5",
          max_tokens: MAX_TOKENS,
          system,
          messages: checked.history
        })
      });
      data = await res.json();
      if (!res.ok) {
        console.error("anthropic error", res.status, data && data.error && data.error.type);
        return json({ reply: FRIENDLY_ERROR }, 502, cors);
      }
    } catch (e) {
      console.error("anthropic fetch failed", String(e));
      return json({ reply: FRIENDLY_ERROR }, 502, cors);
    }
    if (!data || !Array.isArray(data.content)) {
      return json({ reply: FRIENDLY_ERROR }, 502, cors);
    }
    const raw = data.content.map((b) => b.text || "").join("").trim();
    const { reply: cleaned, ended, abusive, lead, leadMalformed } = parseSignals(raw);
    let reply = cleaned;
    if (leadMalformed) console.error("lead json did not parse");
    let leadSaved = false;
    {
      if (lead && hasUsableContact(lead)) {
        leadSaved = true;
        ctx.waitUntil(
          Promise.allSettled([
            emailLead(env, lead),
            storeLead(env, lead, { status: "new" })
          ]).then(([mail, db]) => {
            console.log(
              "LEAD OUTCOME email:",
              mail.status === "fulfilled" ? mail.value : "threw " + mail.reason,
              "db:",
              db.status === "fulfilled" ? db.value : "threw " + db.reason
            );
          })
        );
      } else if (lead) {
        console.warn("lead dropped: no usable name and contact");
      }
    }
    if (abusive) {
      ctx.waitUntil(
        storeLead(
          env,
          { notes: "Session ended for abusive conduct." },
          { status: "abusive" }
        ).catch(() => {
        })
      );
    }
    return json({ reply, leadSaved, ended }, 200, cors);
  }
};
export {
  index_default as default,
  extractEmail,
  hasUsableContact,
  parseSignals,
  todayInDallas,
  validateHistory
};
