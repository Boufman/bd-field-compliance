import React from "react";
import styles from "./Header.module.css";

const Header = () => {
  return (
    <header className={styles.appHeader}>
      <div className={styles.brandBlock}>
        <div className={styles.brandText}>
          <h1>FIELD COMPLIANCE</h1>
          <h3>BD · WA HEALTH FORTNIGHTLY REPORT</h3>
        </div>
      </div>
      <div className={styles.taglineChip}>
        Service Call & Work Order Compliance – Automation Equipment
      </div>
    </header>
  );
};

export default Header;