// src/components/Footer/Footer.jsx
import React from "react";
import styles from "./Footer.module.css";
import ComplicoFooter from "../../assets/logos/COMPLICO.PNG";

const Footer = () => {
  return (
    <footer className={styles.appFooter}>
      <span>Powered by</span>
      <span className={styles.complicoMark}>
        <img src={ComplicoFooter} alt="COMPLICO" />
      </span>
      <span>COMPLICO – Complete compliance, without question.</span>
    </footer>
  );
};

export default Footer;
