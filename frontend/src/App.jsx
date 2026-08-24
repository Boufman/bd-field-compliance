// src/App.jsx
import React from "react";
import Header from "./components/Header/Header";
import UploadSection from "./components/UploadSection/UploadSection";
import StatusStrip from "./components/StatusStrip/StatusStrip";
import GraphPreview from "./components/GraphPreview/GraphPreview";
import Results from "./components/Results/Results";
import PDFViewer from "./components/PDFViewer/PDFViewer";
import Footer from "./components/Footer/Footer";
import styles from "./App.module.css";

export default function App() {
  return (
    <div className={styles.app}>
      {/* Fixed Header */}
      <Header />

      {/* FIXED HEIGHT MAIN CONTENT AREA */}
      <div className={styles.mainLayout}>

        {/* LEFT PANEL – scrolls independently */}
        <aside className={styles.leftPanel}>
          <div className={styles.section}>
            <UploadSection />
          </div>

          <div className={styles.section}>
            <StatusStrip />
          </div>
        </aside>

        {/* RIGHT PANEL – scrolls independently */}
        <main className={styles.rightPanel}>

          <section className={styles.card}>
            <h2 className={styles.sectionTitle}>Graph Preview</h2>
            <GraphPreview />
          </section>

          <section className={styles.card}>
            <h2 className={styles.sectionTitle}>Analysis Results</h2>
            <Results />
          </section>

          <section className={styles.card}>
            <h2 className={styles.sectionTitle}>Generated Report</h2>
            <PDFViewer />
          </section>

        </main>
      </div>

      {/* Fixed footer */}
      <Footer />
    </div>
  );
}