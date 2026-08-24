// src/components/StatusStrip/StatusStrip.jsx
import React, { useContext } from "react";
import { AppContext } from "../../context/AppContext.jsx";
import styles from "./StatusStrip.module.css";

const StatusStrip = () => {
  const context = useContext(AppContext);

  if (!context || !context.state) {
    return (
      <div className={styles.statusStrip}>
        <div className={`${styles.levelPill} ${styles.levelNeutral}`}>
          LEVEL —
        </div>
        <span className={styles.statusText}>Loading…</span>
      </div>
    );
  }

  const { state } = context;
  const { status = {}, error = "" } = state;

  const level = (status.level || "").toUpperCase();

  const levelClass =
    level === "GREEN"
      ? styles.levelGreen
      : level === "YELLOW"
      ? styles.levelYellow
      : level === "RED"
      ? styles.levelRed
      : styles.levelNeutral;

  return (
    <>
      <div className={styles.statusStrip}>
        <div className={`${styles.levelPill} ${levelClass}`}>
          LEVEL {status.level || "—"}
        </div>
        <span className={styles.statusText}>
          {status.message || "No analysis run yet."}
        </span>
      </div>

      {error && (
        <div className={styles.errorStrip}>
          <span className={styles.errorText}>{error}</span>
        </div>
      )}
    </>
  );
};

export default StatusStrip;