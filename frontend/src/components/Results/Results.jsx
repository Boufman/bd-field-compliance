// Results.jsx — ColdProof v3.6 (Clinical Minimal Panel)
// Option A — Summary-only UI + GEYER + Fridge Signature + AM/PM Notice

import React, { useContext } from "react";
import { AppContext } from "../../context/AppContext.jsx";
import styles from "./Results.module.css";

export default function Results() {
  const { state } = useContext(AppContext);
  const analysis = state?.analysis;

  if (!analysis) {
    return (
      <section className={styles.resultsSection}>
        <h2 className={styles.sectionTitle}>Report Summary</h2>
        <p className={styles.sectionSubtitle}>
          Upload a file and run analysis to see results.
        </p>
      </section>
    );
  }

  // Destructure cleanly
  const summary = analysis.summary || {};
  const geyer = analysis.geyer || {};
  const fridge = analysis.fridge_signature || {};
  const ampm = analysis.am_pm_logging || {};

  const minT = analysis.min_temp ?? "—";
  const maxT = analysis.max_temp ?? "—";
  const excCount = analysis.total_excursions ?? "—";

  return (
    <section className={styles.resultsSection}>
      <h2 className={styles.sectionTitle}>Report Summary</h2>
      <p className={styles.sectionSubtitle}>
        ColdProof analysis completed at {analysis.generated || "—"}.
      </p>

      <div className={styles.resultsGrid}>

        {/* ------------------ LEFT BLOCK: SUMMARY ------------------ */}
        <div className={styles.resultBlock}>
          <h3>Summary</h3>

          <div className={styles.resultRow}>
            <span className={styles.resultLabel}>Classification:</span>
            <span className={styles.resultValue}>{summary.classification || "—"}</span>
          </div>

          <div className={styles.resultRow}>
            <span className={styles.resultLabel}>Excursions:</span>
            <span className={styles.resultValue}>{excCount}</span>
          </div>

          <div className={styles.resultRow}>
            <span className={styles.resultLabel}>Min / Max Temp:</span>
            <span className={styles.resultValue}>
              {minT}°C / {maxT}°C
            </span>
          </div>

          <div className={styles.resultRow}>
            <span className={styles.resultLabel}>Period:</span>
            <span className={styles.resultValue}>
              {summary.period_label || "—"}
            </span>
          </div>

          {/* GEYER */}
          <div className={styles.geyerBlock}>
            <div className={styles.geyerHeader}>
              GEYER Level:
              <span
                className={`${styles.geyerTag} ${
                  styles["level" + (geyer.level || "NEUTRAL").toUpperCase()]
                }`}
              >
                {geyer.level || "—"}
              </span>
            </div>

            {geyer.headline && (
              <div className={styles.headline}>{geyer.headline}</div>
            )}

            {geyer.recommendation && (
              <div className={styles.explanation}>{geyer.recommendation}</div>
            )}
          </div>
        </div>

        {/* ------------------ RIGHT BLOCK: FRIDGE SIGNATURE ------------------ */}
        <div className={styles.resultBlock}>
          <h3>Fridge Signature</h3>

          <div className={styles.resultRow}>
            <span className={styles.resultLabel}>Type:</span>
            <span className={styles.resultValue}>{fridge.fridge_type || "—"}</span>
          </div>

          <div className={styles.resultRow}>
            <span className={styles.resultLabel}>Temp Range:</span>
            <span className={styles.resultValue}>
              {typeof fridge.range === "number"
                ? `${fridge.range.toFixed(2)} °C`
                : "—"}
            </span>
          </div>

          <div className={styles.resultRow}>
            <span className={styles.resultLabel}>Stability (SD):</span>
            <span className={styles.resultValue}>
              {typeof fridge.std === "number" ? fridge.std.toFixed(2) : "—"}
            </span>
          </div>

          {fridge.notes?.length > 0 && (
            <div className={styles.fridgeSummary}>
              {fridge.notes.map((n, i) => (
                <div key={i}>• {n}</div>
              ))}
            </div>
          )}

          {ampm?.required && (
            <div className={styles.amPmNote}>{ampm.note || ""}</div>
          )}
        </div>
      </div>
    </section>
  );
}
