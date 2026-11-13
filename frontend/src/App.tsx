import { useEffect, useState } from "react";
import axios from "axios";
import "./styles.css";

// In Vite development the backend runs separately; in production both share one origin.
const API = window.location.port === "5173" ? `${window.location.protocol}//${window.location.hostname}:8000` : "";

type ProjectInfo = { title: string; algorithms: string[]; status: string; default_repeated_runs: number };
type DataStatus = { ready_for_baselines: boolean; train_present: boolean; test_present: boolean };
type MonitorStatus = {
  windows_socket_monitor: string;
  socket_ml_inference: boolean;
  compatible_flow_csv_inference: string;
  alerts_present: boolean;
  notice: string;
};
type Connection = {
  timestamp_utc: string;
  protocol: string;
  local_address: string;
  remote_address: string;
  status: string;
  pid: number | null;
  process_name: string | null;
};
type Alert = {
  source: string;
  prediction: number;
  attack_probability?: number | null;
  record?: Record<string, unknown>;
};
type Method = {
  method: string;
  macro_f1_mean: string;
  macro_f1_std: string;
  selected_features_mean: string;
  feature_reduction_pct_mean: string;
  false_positive_rate_mean: string;
};

function percent(value: string | number, decimals = 1) {
  return `${Number(value).toFixed(decimals)}%`;
}

export default function App() {
  const [project, setProject] = useState<ProjectInfo | null>(null);
  const [data, setData] = useState<DataStatus | null>(null);
  const [monitor, setMonitor] = useState<MonitorStatus | null>(null);
  const [connections, setConnections] = useState<Connection[]>([]);
  const [totalConnections, setTotalConnections] = useState(0);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [methods, setMethods] = useState<Method[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [updated, setUpdated] = useState<string>("—");
  const [autoRefresh, setAutoRefresh] = useState(true);

  async function load() {
    try {
      const [p, d, m, c, a, r] = await Promise.all([
        axios.get<ProjectInfo>(`${API}/api/project`),
        axios.get<DataStatus>(`${API}/api/data/status`),
        axios.get<MonitorStatus>(`${API}/api/ids/status`),
        axios.get<{ count: number; connections: Connection[] }>(`${API}/api/ids/connections`),
        axios.get<{ alerts: Alert[] }>(`${API}/api/ids/alerts`),
        axios.get<{ methods: Method[] }>(`${API}/api/research/comparison`),
      ]);
      setProject(p.data);
      setData(d.data);
      setMonitor(m.data);
      setConnections(c.data.connections);
      setTotalConnections(c.data.count);
      setAlerts(a.data.alerts);
      setMethods(r.data.methods);
      setUpdated(new Date().toLocaleTimeString());
      setError(null);
    } catch {
      setError("API unreachable. Run uvicorn backend.app.main:app --host 127.0.0.1 --port 8000");
    }
  }

  useEffect(() => {
    void load();
    if (!autoRefresh) return;
    const handle = setInterval(() => void load(), 5000);
    return () => clearInterval(handle);
  }, [autoRefresh]);

  const highAlerts = alerts.filter((a) => a.prediction === 1).length;
  const best = methods.find((m) => m.method === "GA + RF");
  return (
    <main className="shell">
      <header className="header">
        <div>
          <p className="eyebrow">COMP-1818 • EVONIDS • DEFENSIVE RESEARCH</p>
          <h1>Network Intrusion Detection</h1>
          <p className="subtitle">{project?.title ?? "Multi-objective evolutionary feature selection"}</p>
        </div>
        <div className="controls">
          <button onClick={() => void load()}>Refresh</button>
          <label className="refresh"><input type="checkbox" checked={autoRefresh} onChange={(e) => setAutoRefresh(e.target.checked)} /> 5s auto-refresh</label>
          <small>Updated {updated}</small>
        </div>
      </header>
      {error && <div className="error" role="alert">{error}</div>}
      <section className="metrics">
        <article className="metric"><span>Windows sockets</span><strong>{totalConnections}</strong><small>Passive observations</small></article>
        <article className="metric"><span>Compatible-flow predictions</span><strong>{alerts.length}</strong><small>Latest 100 logged decisions</small></article>
        <article className="metric"><span>Flagged flow records</span><strong>{highAlerts}</strong><small>From CSV model input only</small></article>
        <article className="metric"><span>GA + RF test Macro-F1</span><strong>{best ? Number(best.macro_f1_mean).toFixed(4) : "—"}</strong><small>Historical five-seed benchmark</small></article>
      </section>
      <div className="notice"><strong>Validity boundary:</strong> {monitor?.notice ?? "Windows socket metadata is not UNSW-NB15 flow data."} The socket table below is not classified by the ML model.</div>
      <section className="panel">
        <div className="section-title"><div><h2>Live connection snapshots</h2><p>Read-only TCP/UDP metadata; up to 250 rows displayed</p></div><span className="tag">PASSIVE</span></div>
        <div className="table-wrap"><table><thead><tr><th>Protocol</th><th>Local address</th><th>Remote address</th><th>State</th><th>PID</th><th>Process</th></tr></thead>
        <tbody>{connections.length ? connections.map((c,i) => <tr key={`${c.pid}-${c.local_address}-${i}`}><td>{c.protocol}</td><td>{c.local_address || "—"}</td><td>{c.remote_address || "—"}</td><td>{c.status || "—"}</td><td>{c.pid ?? "—"}</td><td>{c.process_name || "—"}</td></tr>) : <tr><td colSpan={6}>No connections available. Some process details require Windows privileges.</td></tr>}</tbody></table></div>
      </section>
      <div className="two-columns">
        <section className="panel"><div className="section-title"><div><h2>Flow-model decisions</h2><p>From results/alerts.jsonl, produced by the compatible CSV watcher</p></div><span className="tag">CSV INFERENCE</span></div>
          {alerts.length ? <div className="alert-list">{alerts.slice(0, 12).map((a,i) => <div className="alert-row" key={i}><span className={a.prediction ? "status attack" : "status normal"}>{a.prediction ? "ATTACK" : "NORMAL"}</span><span>{a.attack_probability == null ? "Probability unavailable" : `Attack probability: ${(100*a.attack_probability).toFixed(1)}%`}</span></div>)}</div> : <p className="muted">No flow decisions yet. Run the separate watch-flows CLI using an appropriately trained model.</p>}
        </section>
        <section className="panel"><h2>Environment readiness</h2><div className="statusline"><span>API</span><strong>{error ? "Disconnected" : "Connected"}</strong></div><div className="statusline"><span>UNSW-NB15 training CSV</span><strong>{data?.train_present ? "Found" : "Not present"}</strong></div><div className="statusline"><span>UNSW-NB15 testing CSV</span><strong>{data?.test_present ? "Found" : "Not present"}</strong></div><div className="statusline"><span>Socket classification</span><strong>Disabled by design</strong></div><p className="muted">No traffic is intercepted, blocked, or relabelled. The compatible flow watcher is a separate process.</p></section>
      </div>
      <section className="panel"><div className="section-title"><div><h2>Final research comparison</h2><p>Reported held-out test means, five seeds. Not current live detection results.</p></div><span className="tag">BENCHMARK</span></div>
        <div className="table-wrap"><table><thead><tr><th>Method</th><th>Macro-F1</th><th>SD</th><th>FPR</th><th>Mean features</th><th>Reduction</th></tr></thead><tbody>{methods.map((m) => <tr key={m.method} className={m.method === "GA + RF" ? "highlight" : ""}><th>{m.method}</th><td>{Number(m.macro_f1_mean).toFixed(4)}</td><td>{Number(m.macro_f1_std).toFixed(4)}</td><td>{Number(m.false_positive_rate_mean).toFixed(4)}</td><td>{Number(m.selected_features_mean).toFixed(1)}</td><td>{percent(m.feature_reduction_pct_mean)}</td></tr>)}</tbody></table></div>
        <p className="muted">Full-feature XGBoost has the strongest Macro-F1; GA + RF offers the best compact feature-selection trade-off.</p>
      </section>
      <footer>Research prototype • localhost-only API recommended • No automatic blocking</footer>
    </main>
  );
}
