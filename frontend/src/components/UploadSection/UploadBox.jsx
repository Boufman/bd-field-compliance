import React, { useContext, useRef, useState } from "react";
import { AppContext } from "../../context/AppContext.jsx";
import styles from "./UploadBox.module.css";
import { Upload, Check, X } from "lucide-react";

const BACKEND = "http://127.0.0.1:8000";
const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

export default function UploadBox() {
  const { state, dispatch } = useContext(AppContext);
  const fileInputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);

  // -------------------------------
  // File Handling
  // -------------------------------
  const handleFile = (file) => {
    if (!file) return;

    const valid =
      file.name.endsWith(".csv") ||
      file.name.endsWith(".xlsx") ||
      file.type.includes("csv") ||
      file.type.includes("spreadsheet");

    if (!valid) {
      dispatch({ type: "SET_ERROR", error: "Only CSV or XLSX files allowed." });
      return;
    }

    dispatch({ type: "SET_FILE", file, filename: file.name });
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) handleFile(file);
  };

  const triggerFileSelect = () => fileInputRef.current?.click();

  // -------------------------------
  // Drag-and-Drop
  // -------------------------------
  const handleDrag = (e) => {
    e.preventDefault();
    if (e.type === "dragenter" || e.type === "dragover") setIsDragging(true);
    if (e.type === "dragleave") setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleFile(file);
  };

  // -------------------------------
  // Helper: Build FormData (IMPORTANT)
  // -------------------------------
  const makeFormData = () => {
    const fd = new FormData();
    fd.append("file", state.file);
    fd.append("timezone", userTimezone);   // ← CRITICAL LINE
    return fd;
  };

  // -------------------------------
  // Preview CSV
  // -------------------------------
  const previewCsv = async () => {
    if (!state.file) return;

    dispatch({ type: "SET_LOADING", loading: true });
    dispatch({ type: "SET_ERROR", error: null });

    try {
      const res = await fetch(`${BACKEND}/api/preview-logger`, {
        method: "POST",
        body: makeFormData(),        // sends timezone
      });

      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();

      dispatch({ type: "SET_PREVIEW", preview: data.preview });
    } catch (err) {
      dispatch({ type: "SET_ERROR", error: err.message });
    } finally {
      dispatch({ type: "SET_LOADING", loading: false });
    }
  };

  // -------------------------------
  // Analyse CSV
  // -------------------------------
  const analyseCsv = async () => {
    if (!state.file) return;

    dispatch({ type: "SET_LOADING", loading: true });
    dispatch({ type: "SET_ERROR", error: null });

    try {
      const res = await fetch(`${BACKEND}/api/analyse-logger`, {
        method: "POST",
        body: makeFormData(),        // sends timezone
      });

      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();

      dispatch({ type: "SET_ANALYSIS", analysis: data });
    } catch (err) {
      dispatch({ type: "SET_ERROR", error: err.message });
    } finally {
      dispatch({ type: "SET_LOADING", loading: false });
    }
  };

  // -------------------------------
  // Generate Report
  // -------------------------------
  const generateReport = async () => {
    if (!state.file) return;

    dispatch({ type: "SET_LOADING", loading: true });
    dispatch({ type: "SET_ERROR", error: null });

    try {
      const res = await fetch(`${BACKEND}/api/generate-report`, {
        method: "POST",
        body: makeFormData(),        // sends timezone → fixes PDF + CPVault
      });

      if (!res.ok) throw new Error(await res.text());

      const data = await res.json();

      dispatch({
        type: "SET_PDF",
        pdfEndpoint: `${BACKEND}${data.pdf_endpoint}`,
        timestamp: data.archive_timestamp,
      });
    } catch (err) {
      dispatch({ type: "SET_ERROR", error: err.message });
    } finally {
      dispatch({ type: "SET_LOADING", loading: false });
    }
  };

  const refreshReport = () => generateReport();

  const clearForm = () => dispatch({ type: "RESET_ALL" });

  // -------------------------------
  // Render
  // -------------------------------
  return (
    <div className={styles.container}>
      <input
        ref={fileInputRef}
        type="file"
        accept=".csv,.xlsx"
        onChange={handleFileSelect}
        className={styles.hiddenInput}
      />

      {/* DROP ZONE */}
      <div
        className={`${styles.dropZone} 
          ${isDragging ? styles.dragging : ""} 
          ${state.filename ? styles.hasFile : ""}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={triggerFileSelect}
      >
        {state.filename ? (
          <div className={styles.fileInfo}>
            <Check className={styles.checkIcon} size={32} />
            <div>
              <p className={styles.filename}>{state.filename}</p>
              <p className={styles.subtext}>Ready to process</p>
            </div>
            <button
              className={styles.removeBtn}
              onClick={(e) => {
                e.stopPropagation();
                clearForm();
              }}
            >
              <X size={16} />
            </button>
          </div>
        ) : (
          <>
            <Upload size={48} className={styles.uploadIcon} />
            <p className={styles.title}>Drop your logger file here</p>
            <p className={styles.subtitle}>
              or click to browse • CSV or XLSX only
            </p>
          </>
        )}
      </div>

      {/* BUTTON GRID */}
      <div className={styles.buttonRow}>
        <button className={styles.btn} disabled={!state.file} onClick={previewCsv}>
          Preview CSV
        </button>

        <button className={styles.btnPrimary} disabled={!state.file} onClick={analyseCsv}>
          Analyse Logger
        </button>

        <button className={styles.btnAccent} disabled={!state.file} onClick={generateReport}>
          Generate Report
        </button>

        <button className={styles.btnSecondary} disabled={!state.file} onClick={refreshReport}>
          Refresh Report
        </button>

        <button className={styles.clearBtn} onClick={clearForm}>
          Clear Form
        </button>
      </div>
    </div>
  );
}