import React, { useContext } from "react";
import { AppContext } from "../../context/AppContext.jsx";
import styles from "./DownloadPDF.module.css";

export default function DownloadPDF() {
  const { state } = useContext(AppContext);
  const { pdfUrl, loading } = state;

  if (!pdfUrl) return null;

  const handleDownload = () => {
    // Trigger browser download using a direct link
    const link = document.createElement("a");
    link.href = pdfUrl;
    link.download = "ColdProof_Report.pdf";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <button
      className={styles.button}
      onClick={handleDownload}
      disabled={loading}
    >
      ⬇ Download PDF
    </button>
  );
}