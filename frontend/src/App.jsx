import { useEffect, useMemo, useState } from "react";
import { api } from "./services/api.js";

const SAFE = "Increase the payment API timeout from 2 seconds to 5 seconds.";
const DANGEROUS = "Increase the payment API timeout from 2 seconds to 60 seconds.";
const liveSteps = [
  "Creating Daytona sandbox",
  "Uploading repository",
  "Installing dependencies",
  "Running baseline tests",
  "Applying AI-generated change",
  "Running regression tests",
  "Calculating deterministic risk",
  "Generating validation report",
];

function Badge({ children, tone = "neutral" }) {
  return <span className={`badge ${tone}`}>{children}</span>;
}

function Icon({ children }) {
  return <span className="nav-icon" aria-hidden="true">{children}</span>;
}

function Sidebar({ screen, navigate, dark, setDark }) {
  return (
    <aside className="sidebar">
      <button className="brand" onClick={() => navigate("dashboard")}>
        <span className="brand-mark">C</span>
        <span>ChangeGuard <b>AI</b></span>
      </button>
      <div className="workspace-label">WORKSPACE</div>
      <nav aria-label="Primary navigation">
        <button className={screen === "dashboard" ? "active" : ""} onClick={() => navigate("dashboard")}><Icon>⌂</Icon>Overview</button>
        <button className={screen !== "dashboard" ? "active" : ""} onClick={() => navigate("new")}><Icon>＋</Icon>New validation</button>
        <button disabled><Icon>◎</Icon>Validation runs</button>
        <button disabled><Icon>✓</Icon>Approvals</button>
      </nav>
      <div className="sidebar-spacer" />
      <div className="security-card">
        <span className="pulse" />
        <div><strong>Daytona connected</strong><small>Isolated execution ready</small></div>
      </div>
      <button className="theme-button" onClick={() => setDark(!dark)} aria-label="Toggle color theme">
        {dark ? "☀ Light mode" : "☾ Dark mode"}
      </button>
      <div className="reviewer"><span>HR</span><div><strong>Human Reviewer</strong><small>Change approver</small></div></div>
    </aside>
  );
}

function Header({ title, eyebrow, onNew }) {
  return (
    <header className="page-header">
      <div><span className="eyebrow">{eyebrow}</span><h1>{title}</h1></div>
      {onNew && <button className="button primary" onClick={onNew}>＋ New change</button>}
    </header>
  );
}

function Dashboard({ changes, onNew, onOpen }) {
  const approved = changes.filter((item) => item.status === "approved").length;
  const blocked = changes.filter((item) => ["blocked", "rejected"].includes(item.status)).length;
  return <>
    <Header eyebrow="Command center" title="Software changes, safely governed" onNew={onNew} />
    <section className="hero-panel">
      <div><Badge tone="blue">DAYTONA-NATIVE VALIDATION</Badge><h2>Trust the evidence.<br />Not the generated code.</h2><p>Plan with AI, execute in an isolated sandbox, and keep the final decision human.</p></div>
      <div className="hero-orbit"><span>AI</span><i>→</i><span className="shield">◆</span><i>→</i><span>✓</span></div>
    </section>
    <section className="stats-grid">
      <article><small>TOTAL CHANGES</small><strong>{changes.length}</strong><span>Controlled validation requests</span></article>
      <article><small>APPROVED</small><strong>{approved}</strong><span className="positive">Human-reviewed evidence</span></article>
      <article><small>BLOCKED</small><strong>{blocked}</strong><span className="negative">Unsafe changes contained</span></article>
      <article><small>SANDBOX POSTURE</small><strong className="ready">Ready</strong><span>Daytona isolation active</span></article>
    </section>
    <section className="panel recent-panel">
      <div className="section-title"><div><span className="eyebrow">ACTIVITY</span><h2>Recent changes</h2></div><button className="button ghost" onClick={onNew}>Create first change →</button></div>
      {changes.length ? <div className="change-list">{changes.map((item) => <button key={item.id} onClick={() => onOpen(item)}><code>{item.id}</code><div><strong>{item.title}</strong><small>{item.request}</small></div><Badge tone={item.status === "approved" ? "green" : item.status === "blocked" || item.status === "rejected" ? "red" : "amber"}>{item.status}</Badge><span>→</span></button>)}</div> : <div className="empty"><span>◇</span><h3>No validation history yet</h3><p>Start with one of the controlled payment timeout examples.</p></div>}
    </section>
  </>;
}

function NewChange({ value, setValue, onSubmit, busy }) {
  return <>
    <Header eyebrow="Step 1 of 4" title="Describe the software change" />
    <div className="two-column">
      <section className="panel form-panel">
        <div className="section-title"><div><h2>New change request</h2><p>AI will plan the modification. Nothing executes until you explicitly start Daytona.</p></div></div>
        <div className="form-row"><label>Repository<input value="payment-service" disabled /></label><label>Environment<select defaultValue="Staging"><option>Staging</option></select></label></div>
        <label>Describe the change<textarea value={value} onChange={(event) => setValue(event.target.value)} rows="7" placeholder="Increase the payment API timeout..." /></label>
        <div className="examples"><span>TRY AN EXAMPLE</span><button onClick={() => setValue(SAFE)}><b>Safe change</b><small>2 seconds → 5 seconds</small></button><button onClick={() => setValue(DANGEROUS)}><b>Dangerous change</b><small>2 seconds → 60 seconds</small></button></div>
        <button className="button primary full" disabled={busy || value.trim().length < 5} onClick={onSubmit}>{busy ? "Generating bounded plan…" : "Generate change plan →"}</button>
      </section>
      <aside className="panel guardrails"><span className="shield-large">◆</span><h3>ChangeGuard boundaries</h3><ul><li><i>✓</i> AI proposes; it never approves</li><li><i>✓</i> Generated code never runs on this host</li><li><i>✓</i> Only the Daytona copy is modified</li><li><i>✓</i> Test evidence drives deterministic risk</li></ul></aside>
    </div>
  </>;
}

function ChangePlan({ change, onValidate, busy }) {
  const plan = change.plan;
  return <>
    <Header eyebrow={`${change.id} · Step 2 of 4`} title="Review the AI change plan" />
    <div className="plan-layout">
      <section>
        <article className="panel request-card"><span className="eyebrow">REQUEST</span><h2>{plan.summary}</h2><p>{change.request}</p></article>
        <article className="panel diff-card"><div className="section-title"><div><span className="eyebrow">PROPOSED CHANGE</span><h2>{plan.affected_files[0]}</h2></div><Badge tone="blue">1 FILE</Badge></div><div className="diff"><div className="removed"><span>−</span><code>{plan.changes[0].old_code}</code></div><div className="added"><span>＋</span><code>{plan.changes[0].new_code}</code></div></div><p className="reason"><b>AI reasoning</b>{plan.changes[0].reason}</p></article>
      </section>
      <aside className="panel risk-preview"><span className="eyebrow">INITIAL RISK</span><div className={`risk-gauge ${plan.risk_level}`}><strong>{plan.risk_level.toUpperCase()}</strong></div><p>{plan.risk_level === "high" ? "The requested value exceeds the approved timeout threshold and is expected to fail policy tests." : "A runtime configuration changes, but the requested value remains within the approved threshold."}</p><hr /><h3>Execution boundary</h3><p>ChangeGuard will create an ephemeral Daytona sandbox, upload the original project, verify the baseline, then apply this exact diff.</p><button className="button primary full" disabled={busy} onClick={onValidate}>{busy ? "Starting Daytona…" : "Run safely in Daytona →"}</button><small className="human-note">No approval happens automatically.</small></aside>
    </div>
  </>;
}

function Validation({ progress }) {
  return <>
    <Header eyebrow="Step 3 of 4" title="Secure validation in progress" />
    <div className="validation-layout">
      <section className="panel steps-panel"><div className="live-header"><span className="spinner" /><div><h2>Daytona sandbox is working</h2><p>Generated code is isolated from the ChangeGuard host.</p></div><Badge tone="blue">LIVE</Badge></div><div className="steps">{liveSteps.map((step, index) => <div key={step} className={index < progress ? "done" : index === progress ? "current" : "pending"}><span>{index < progress ? "✓" : index === progress ? "●" : "○"}</span><p>{step}</p>{index < progress && <small>Complete</small>}</div>)}</div></section>
      <aside className="terminal"><div className="terminal-top"><span /><span /><span /><b>DAYTONA SANDBOX</b></div><pre><span>$</span> preparing isolated workspace{"\n"}<em>policy: ephemeral / no production secrets</em>{"\n\n"}<span>$</span> python -m pytest -v{"\n"}<em>collecting controlled payment tests...</em>{"\n\n"}<i>Validation evidence will appear here.</i></pre></aside>
    </div>
  </>;
}

function Report({ change, onDecision, busy }) {
  const validation = change.validation;
  const safe = validation.overall_status === "safe_to_approve";
  const risk = validation.risk;
  return <>
    <Header eyebrow={`${change.id} · Step 4 of 4`} title="Change validation report" />
    <section className={`verdict ${safe ? "safe" : "blocked"}`}><div className="verdict-icon">{safe ? "✓" : "!"}</div><div><span>OVERALL STATUS</span><h2>{safe ? "SAFE TO APPROVE" : "CHANGE BLOCKED"}</h2><p>{safe ? "All automated controls passed. A human decision is still required." : "Regression evidence violates the enterprise timeout policy."}</p></div><div className="risk-score"><small>RISK SCORE</small><strong>{risk.score}<i>/100</i></strong><Badge tone={safe ? "green" : "red"}>{risk.level.toUpperCase()}</Badge></div></section>
    <div className="report-grid">
      <section className="panel evidence"><div className="section-title"><div><span className="eyebrow">VALIDATION EVIDENCE</span><h2>Daytona execution</h2></div><code>{validation.sandbox_id?.slice(0, 13)}…</code></div><div className="evidence-grid"><div><small>BASELINE</small><strong className="positive">✓ Passed</strong></div><div><small>AFTER CHANGE</small><strong className={safe ? "positive" : "negative"}>{safe ? "✓ Passed" : "✕ Failed"}</strong></div><div><small>REGRESSION</small><strong className={safe ? "positive" : "negative"}>{safe ? "None detected" : `${validation.after_change.tests_failed || 1} failed`}</strong></div><div><small>EXECUTION TIME</small><strong>{validation.execution_time_seconds}s</strong></div></div><div className="terminal compact"><div className="terminal-top"><span /><span /><span /><b>TEST OUTPUT</b></div><pre>{validation.after_change.output || validation.error}</pre></div></section>
      <aside className="panel decision"><span className="eyebrow">HUMAN DECISION</span><h2>{change.status === "approved" ? "Change approved" : change.status === "rejected" ? "Change rejected" : "Review the evidence"}</h2><div className="risk-reasons">{risk.reasons.map((reason) => <p key={reason}><span>{reason.includes("failed") || reason.includes("exceeds") ? "!" : "✓"}</span>{reason}</p>)}</div>{["approved", "rejected"].includes(change.status) ? <div className={`decision-done ${change.status}`}><b>{change.status === "approved" ? "✓ Approved by a human" : "✕ Rejected by a human"}</b><small>Validated safely in Daytona before the decision.</small></div> : <><button className="button reject full" disabled={busy} onClick={() => onDecision("reject")}>Reject change</button><button className="button approve full" disabled={busy || !safe} onClick={() => onDecision("approve")}>Approve change</button>{!safe && <small className="blocked-note">Approval is disabled because validation failed.</small>}</>}</aside>
    </div>
  </>;
}

export default function App() {
  const [screen, setScreen] = useState("dashboard");
  const [request, setRequest] = useState(SAFE);
  const [changes, setChanges] = useState([]);
  const [change, setChange] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [progress, setProgress] = useState(0);
  const [dark, setDark] = useState(false);

  useEffect(() => { api.listChanges().then(setChanges).catch(() => {}); }, []);
  useEffect(() => { document.documentElement.dataset.theme = dark ? "dark" : "light"; }, [dark]);
  useEffect(() => {
    if (screen !== "validation") return undefined;
    const timer = window.setInterval(() => setProgress((value) => Math.min(value + 1, liveSteps.length - 1)), 1500);
    return () => window.clearInterval(timer);
  }, [screen]);

  const content = useMemo(() => {
    const create = async () => { setBusy(true); setError(""); try { const result = await api.createChange(request); setChange(result); setChanges((items) => [result, ...items]); setScreen("plan"); } catch (err) { setError(err.message); } finally { setBusy(false); } };
    const validate = async () => { setBusy(true); setProgress(0); setError(""); setScreen("validation"); try { const result = await api.validateChange(change.id); setChange(result); setChanges((items) => items.map((item) => item.id === result.id ? result : item)); setScreen("report"); } catch (err) { setError(err.message); setScreen("plan"); } finally { setBusy(false); } };
    const decide = async (decision) => { setBusy(true); setError(""); try { const result = await api.decide(change.id, decision); setChange(result); setChanges((items) => items.map((item) => item.id === result.id ? result : item)); } catch (err) { setError(err.message); } finally { setBusy(false); } };
    if (screen === "new") return <NewChange value={request} setValue={setRequest} onSubmit={create} busy={busy} />;
    if (screen === "plan" && change) return <ChangePlan change={change} onValidate={validate} busy={busy} />;
    if (screen === "validation") return <Validation progress={progress} />;
    if (screen === "report" && change?.validation) return <Report change={change} onDecision={decide} busy={busy} />;
    return <Dashboard changes={changes} onNew={() => setScreen("new")} onOpen={(item) => { setChange(item); setScreen(item.validation ? "report" : "plan"); }} />;
  }, [screen, request, change, changes, busy, progress]);

  const navigate = (destination) => { setError(""); setScreen(destination); };
  return <div className="app-shell"><Sidebar screen={screen} navigate={navigate} dark={dark} setDark={setDark} /><main>{error && <div className="error-banner"><b>ChangeGuard stopped safely.</b> {error}</div>}{content}<footer><span>ChangeGuard AI · Hackathon MVP</span><span>AI plans · Daytona validates · Humans decide</span></footer></main></div>;
}

