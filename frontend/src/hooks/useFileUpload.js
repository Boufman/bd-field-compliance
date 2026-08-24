import { useState } from "react";
import axios from "axios";

export default function useFileUpload() {
  const [file, setFile] = useState(null);
  const [filename, setFilename] = useState("");
  const [preview, setPreview] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [pdfEndpoint, setPdfEndpoint] = useState(null);
  const [archiveTimestamp, setArchiveTimestamp] = useState(null);

  const [status, setStatus] = useState({ level: "NEUTRAL", message: "" });
  const [error, setError] = useState(null);

  // ------------ File Handling ------------
  const handleFileChange = (e) => {
    const f = e.target.files[0];
    if (!f) return;

    setFile(f);
    setFilename(f.name);
    resetOutputs();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const f = e.dataTransfer.files[0];
    if (!f) return;

    setFile(f);
    setFilename(f.name);
    resetOutputs();
  };

  const handleDragOver = (e) => e.preventDefault();
  const handleDragLeave = () => {};

  const resetOutputs = () => {
    setPreview(null);
    setAnalysis(null);
    setPdfEndpoint(null);
    setArchiveTimestamp(null);
    setStatus({ level: "NEUTRAL", message: "" });
    setError(null);
  };

  // ------------ API Helpers ------------
  const uploadFormData = () => {
    const fd = new FormData();
    fd.append("file", file);
    return fd;
  };

  // ------------ Preview CSV ------------
  const previewCsv = async () => {
    try {
      setStatus({ level: "NEUTRAL", message: "Loading preview…" });

      const response = await axios.post(
        "/api/preview-logger",
        uploadFormData(),
        { headers: { "Content-Type": "multipart/form-data" } }
      );

      setPreview(response.data.preview);
      setAnalysis(response.data); // analysis + preview
      setStatus({ level: "YELLOW", message: "Preview loaded." });

    } catch (err) {
      setError(err.response?.data?.detail || "Preview failed.");
      setStatus({ level: "RED", message: "Preview error" });
    }
  };

  // ------------ Analyse Logger ------------
  const analyseCsv = async () => {
    try {
      setStatus({ level: "NEUTRAL", message: "Analysing…" });

      const response = await axios.post(
        "/api/analyse-logger",
        uploadFormData(),
        { headers: { "Content-Type": "multipart/form-data" } }
      );

      setAnalysis(response.data);

      setStatus({
        level: response.data.geyer?.level || "YELLOW",
        message: "Analysis complete.",
      });

    } catch (err) {
      setError(err.response?.data?.detail || "Analysis failed.");
      setStatus({ level: "RED", message: "Analysis error" });
    }
  };

  // ------------ Generate PDF ------------
  const generateReport = async () => {
    try {
      setStatus({ level: "NEUTRAL", message: "Generating PDF…" });

      const response = await axios.post(
        "/api/generate-report",
        uploadFormData(),
        { headers: { "Content-Type": "multipart/form-data" } }
      );

      setPdfEndpoint(response.data.pdf_endpoint);
      setArchiveTimestamp(response.data.archive_timestamp);
      setAnalysis(response.data.analysis);

      setStatus({ level: "GREEN", message: "PDF ready." });

    } catch (err) {
      setError(err.response?.data?.detail || "PDF generation failed.");
      setStatus({ level: "RED", message: "PDF error" });
    }
  };

  return {
    file,
    filename,
    preview,
    analysis,
    pdfEndpoint,
    archiveTimestamp,

    status,
    error,

    handleFileChange,
    handleDrop,
    handleDragOver,
    handleDragLeave,

    previewCsv,
    analyseCsv,
    generateReport,
  };
}

