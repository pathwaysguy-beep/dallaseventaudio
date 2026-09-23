// Runs with plain node: node --test test/
// Stubs D1, KV and fetch so the chat path, the conversation store and the
// digest can be exercised without a network or a wrangler session.
import test from "node:test";
import assert from "node:assert/strict";
import worker, { cleanPage, cleanSid, dayInDallas, digestPack } from "../src/index.js";

function fakeDb() {
  const rows = new Map();
  const digests = new Map();
  const log = [];
  return {
    rows, digests, log,
    prepare(sql) {
      const stmt = { sql, args: [] };
      stmt.bind = (...a) => { stmt.args = a; return stmt; };
      stmt.run = async () => {
        log.push(sql.trim().split(/\s+/).slice(0, 3).join(" "));
        if (sql.includes("INSERT INTO conversations")) {
          const [id, day, ts, page, turns, ended, lead, errored, transcript] = stmt.args;
          const prev = rows.get(id);
          rows.set(id, {
            id, day, started_at: prev ? prev.started_at : ts, updated_at: ts,
            page: prev ? prev.page : page, last_page: page, turns,
            ended: Math.max(prev ? prev.ended : 0, ended),
            lead: Math.max(prev ? prev.lead : 0, lead),
            errored: Math.max(prev ? prev.errored : 0, errored),
            transcript
          });
        } else if (sql.includes("INTO digests")) {
          digests.set(stmt.args[0], stmt.args);
        }
        return { success: true };
      };
      stmt.first = async () => {
        if (sql.includes("FROM digests")) return digests.has(stmt.args[0]) ? { day: stmt.args[0] } : null;
        return null;
      };
      stmt.all = async () => {
        if (sql.includes("FROM conversations")) {
          return { results: [...rows.values()].filter((r) => r.day === stmt.args[0]) };
        }
        return { results: [] };
      };
      return stmt;
    }
  };
}

function env(extra) {
  return {
    ALLOWED_ORIGINS: "https://www.dallaseventaudio.com",
    ANTHROPIC_API_KEY: "test",
    RESEND_API_KEY: "test",
    LEAD_FROM: "a@b.c",
    LEAD_TO: "steve@example.com",
    DB: fakeDb(),
    ...extra
  };
}

function ctx() {
  const waits = [];
  return { waits, waitUntil: (p) => waits.push(p), settle: () => Promise.allSettled(waits) };
}

function chat(body) {
  return new Request("https://w.example/api/chat", {
    method: "POST",
    headers: { "content-type": "application/json", origin: "https://www.dallaseventaudio.com" },
    body: JSON.stringify(body)
  });
}

const calls = [];
function stubFetch(reply) {
  calls.length = 0;
  globalThis.fetch = async (url, init) => {
    calls.push({ url: String(url), body: JSON.parse(init.body) });
    if (String(url).includes("anthropic")) {
      return new Response(JSON.stringify({ content: [{ type: "text", text: reply }] }), { status: 200 });
    }
    return new Response(JSON.stringify({ id: "email_1" }), { status: 200 });
  };
}

test("validators", () => {
  assert.equal(cleanSid("AB12cd34ef56ab12cd34"), "ab12cd34ef56ab12cd34");
  assert.equal(cleanSid("short"), null);
  assert.equal(cleanSid("zz12cd34ef56ab12cd34"), null);
  assert.equal(cleanPage("/rent-uplighting?gclid=abc#x"), "/rent-uplighting");
  assert.equal(cleanPage("//evil"), null);
  assert.equal(cleanPage("rent"), null);
  assert.equal(cleanPage("/post/what-is-de-feedback-for-live-events"), "/post/what-is-de-feedback-for-live-events");
  assert.match(dayInDallas(new Date("2026-09-23T04:30:00Z")), /^2026-09-22$/);
});

test("a turn with a sid is stored and updated in place", async () => {
  const e = env();
  const c = ctx();
  stubFetch("Sure, what date is the event?");
  const sid = "0123456789abcdef0123";
  let res = await worker.fetch(chat({
    sid, page: "/rent-uplighting?gclid=1",
    history: [{ role: "assistant", content: "Welcome" }, { role: "user", content: "do you do uplighting in Frisco" }]
  }), e, c);
  assert.equal(res.status, 200);
  await c.settle();
  assert.equal(e.DB.rows.size, 1);
  let row = e.DB.rows.get(sid);
  assert.equal(row.page, "/rent-uplighting");
  assert.equal(row.turns, 1);
  assert.equal(JSON.parse(row.transcript).length, 3);

  const c2 = ctx();
  stubFetch("Great. <<<LEAD {\"name\":\"Ann\",\"contact\":\"817-555-0100\"} >>> I have passed that along.");
  res = await worker.fetch(chat({
    sid, page: "/contact",
    history: [
      { role: "assistant", content: "Welcome" }, { role: "user", content: "do you do uplighting in Frisco" },
      { role: "assistant", content: "Sure, what date is the event?" }, { role: "user", content: "Oct 3, Ann 817-555-0100" }
    ]
  }), e, c2);
  const out = await res.json();
  assert.equal(out.leadSaved, true);
  await c2.settle();
  row = e.DB.rows.get(sid);
  assert.equal(e.DB.rows.size, 1);
  assert.equal(row.turns, 2);
  assert.equal(row.lead, 1);
  assert.equal(row.page, "/rent-uplighting");
  assert.equal(row.last_page, "/contact");
  const mail = calls.find((k) => k.url.includes("resend"));
  assert.ok(mail, "lead email still sent");
  assert.match(mail.body.subject, /Chat lead: Ann/);
});

test("no sid means nothing is stored and the chat still answers", async () => {
  const e = env();
  const c = ctx();
  stubFetch("Hello");
  const res = await worker.fetch(chat({ history: [{ role: "user", content: "hi" }] }), e, c);
  assert.equal(res.status, 200);
  await c.settle();
  assert.equal(e.DB.rows.size, 0);
});

test("an upstream failure is stored as an errored turn", async () => {
  const e = env();
  const c = ctx();
  globalThis.fetch = async () => new Response(JSON.stringify({ error: { type: "overloaded" } }), { status: 529 });
  const res = await worker.fetch(chat({
    sid: "abcdefabcdefabcdef01", page: "/",
    history: [{ role: "user", content: "hello?" }]
  }), e, c);
  assert.equal(res.status, 502);
  await c.settle();
  const row = e.DB.rows.get("abcdefabcdefabcdef01");
  assert.equal(row.errored, 1);
  assert.match(JSON.parse(row.transcript)[1].content, /something went wrong/);
});

test("digest summarizes the day, emails once, skips empty days", async () => {
  const e = env({ DIGEST_KEY: "k" });
  const c = ctx();
  stubFetch("Thanks, what city?");
  const day = dayInDallas();
  await worker.fetch(chat({ sid: "1111111111111111", page: "/weddings", history: [{ role: "user", content: "wedding sound for 150 people" }] }), e, c);
  await worker.fetch(chat({ sid: "2222222222222222", page: "/", history: [{ role: "user", content: "how much is a projector" }] }), e, c);
  await c.settle();
  assert.equal(e.DB.rows.size, 2);

  stubFetch("2 conversations, 0 leads, 1 one and gone.\n\n/weddings: a couple asked...\n\nPatterns: pricing came up.");
  const req = (body, key) => new Request("https://w.example/api/digest", {
    method: "POST", headers: { "content-type": "application/json", "x-digest-key": key || "k", origin: "https://www.dallaseventaudio.com" },
    body: JSON.stringify(body)
  });
  let res = await worker.fetch(req({ day }, "wrong"), e, ctx());
  assert.equal(res.status, 404);

  res = await worker.fetch(req({ day }), e, ctx());
  let out = await res.json();
  assert.equal(res.status, 200, JSON.stringify(out));
  assert.equal(out.sent, 2);
  const summarize = calls.find((k) => k.url.includes("anthropic"));
  assert.match(summarize.body.messages[0].content, /wedding sound for 150 people/);
  assert.match(summarize.body.messages[0].content, /started on \/weddings/);
  const mail = calls.find((k) => k.url.includes("resend"));
  assert.match(mail.body.subject, /Concierge digest .* 2 chats, 0 leads/);
  assert.match(mail.body.html, /Patterns: pricing came up/);

  res = await worker.fetch(req({ day }), e, ctx());
  out = await res.json();
  assert.equal(out.skipped, "already sent");

  res = await worker.fetch(req({ day: "2020-01-01" }), e, ctx());
  out = await res.json();
  assert.equal(out.skipped, "no conversations");

  const pack = digestPack([...e.DB.rows.values()]);
  assert.match(pack, /Conversation 2/);
});

test("scheduled handler targets yesterday and runs the digest", async () => {
  const e = env();
  const c = ctx();
  const yesterday = dayInDallas(new Date(Date.now() - 864e5));
  // seed one row for yesterday straight into the fake table
  await e.DB.prepare("INSERT INTO conversations x").bind("3333333333333333", yesterday, "t", "/", 1, 0, 0, 0, JSON.stringify([{ role: "user", content: "hi" }])).run();
  stubFetch("1 conversation.");
  await worker.scheduled({ cron: "0 12 * * *" }, e, c);
  await c.settle();
  assert.ok(e.DB.digests.has(yesterday), "digest recorded for " + yesterday);
});
