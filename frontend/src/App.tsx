import { useEffect, useState } from "react";
import axios from "axios";

type ProjectInfo = {
  title: string;
  algorithms: string[];
  classifiers: string[];
  default_repeated_runs: number;
  status: string;
};

type DataStatus = {
  train_expected: string;
  test_expected: string;
  train_present: boolean;
  test_present: boolean;
  ready_for_baselines: boolean;
};

export default function App() {
  const [project, setProject] = useState<ProjectInfo | null>(null);
  const [dataStatus, setDataStatus] = useState<DataStatus | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([
      axios.get<ProjectInfo>("http://127.0.0.1:8000/api/project"),
      axios.get<DataStatus>("http://127.0.0.1:8000/api/data/status"),
    ])
      .then(([projectResponse, dataResponse]) => {
        setProject(projectResponse.data);
        setDataStatus(dataResponse.data);
      })
      .catch(() =>
        setError("API not connected. Start FastAPI on port 8000.")
      );
  }, []);

  return (
    <main className="shell">
      <header>
        <p className="eyebrow">COMP-1818 • EvoNIDS</p>
        <h1>Evolutionary Network Intrusion Detection</h1>
        <p className="subtitle">
          Multi-objective feature selection with GA, BPSO, PSO and NSGA-II.
        </p>
      </header>

      <section className="grid">
        <article className="card">
          <h2>Project phase</h2>
          <strong>{project?.status ?? "Connecting..."}</strong>
          {error && <p>{error}</p>}
        </article>

        <article className="card">
          <h2>Dataset</h2>
          <strong>
            {dataStatus?.ready_for_baselines ? "READY" : "NOT LOADED"}
          </strong>
          <p>UNSW-NB15 official train/test partitions</p>
        </article>

        <article className="card">
          <h2>Repeated runs</h2>
          <strong>{project?.default_repeated_runs ?? 5}</strong>
          <p>seeds per stochastic configuration</p>
        </article>

        <article className="card">
          <h2>Primary metric</h2>
          <strong>Macro-F1</strong>
          <p>plus recall, FPR and computational cost</p>
        </article>
      </section>

      <section className="card">
        <h2>UNSW-NB15 readiness</h2>
        <p>
          Training CSV: {dataStatus?.train_present ? "found" : "missing"}
        </p>
        <p>
          Testing CSV: {dataStatus?.test_present ? "found" : "missing"}
        </p>
        <p className="pipeline">
          data/raw/UNSW_NB15_training-set.csv
          <br />
          data/raw/UNSW_NB15_testing-set.csv
        </p>
      </section>

      <section className="card">
        <h2>Experimental protocol</h2>
        <div className="pipeline">
          Official training partition → training + validation
          <br />
          Official testing partition → untouched final test
          <br />
          Baselines → GA → BPSO → PSO → NSGA-II
        </div>
      </section>
    </main>
  );
}
