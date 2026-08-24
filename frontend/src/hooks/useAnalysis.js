import { useState } from "react";

const API_BASE = "http://127.0.0.1:8000";

const useAnalysis = () => {
  const [results, setResults] = useState(null);
  const [status, setStatus] = useState({
    level: "",
    message: "No analysis run yet.",
  });
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const clearError = () => setError("");

  const analyseFile = async (file, timezone) => {
    if (!file) {
      setError("Please select a CSV file first.");
      return;
    }

    setIsLoading(true);
    clearError();
    setStatus({ level: "", message: "Analysing logger data…" });

    try {
      const fd = new FormData();
      fd.append("file", file);
      if (timezone) {
        fd.append("timezone", timezone);
      }

      // ✅ CORRECT v3.6 ENDPOINT
      const resp = await fetch(`${API_BASE}/api/analyse-logger`, {
        method: "POST",
        body: fd,
      });

      if (!resp.ok) {
        let detail = "";
        try {
          const errBody = await resp.json();
          detail = errBody.detail || "";
        } catch {
          // ignore
        }
        throw new Error(detail || `HTTP ${resp.status}`);
      }

      const data = await resp.json();

      // ✅ v3.6 response shape
      setResults(data);

      const level =
        data?.geyer?.level ||
        data?.summary?.classification ||
        "INFO";

      setStatus({
        level,
        message: "Analysis complete.",
      });

    } catch (err) {
      setError(err.message || "Analysis failed.");
      setStatus({ level: "ERROR", message: "Analysis failed." });
    } finally {
      setIsLoading(false);
    }
  };

  return {
    results,
    status,
    error,
    isLoading,
    analyseFile,
    clearError,
  };
};

export default useAnalysis;