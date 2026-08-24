import React, { useContext, useMemo } from "react";
import { AppContext } from "../../context/AppContext.jsx";
import styles from "./PDFViewer.module.css";

const PDFViewer = () => {
  const { state } = useContext(AppContext);
  const { pdfUrl } = state || {};   // ✅ use pdfUrl, not pdfEndpoint

  // Build full URL safely
  const finalUrl = useMemo(() => {
    if (!pdfUrl) return null;
    return pdfUrl;
  }, [pdfUrl]);

  if (!finalUrl) return null;

  return (
    <div className={styles.viewerContainer}>
      <iframe
        className={styles.frame}
        src={finalUrl}
        title="ColdProof PDF"
        style={{ border: "none" }}
      />
    </div>
  );
};

export default PDFViewer;