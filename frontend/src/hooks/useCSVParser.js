// src/hooks/useCSVParser.js
import { useState } from "react";
import { parseTemperatureData } from "../utils/temperatureParser";

const useCSVParser = () => {
  const [csvPreview, setCsvPreview] = useState("");
  const [temperatureData, setTemperatureData] = useState([]);

  const previewCSV = async (file) => {
    if (!file) return;

    const text = await file.text();
    const lines = text.split(/\r?\n/).slice(0, 40);
    setCsvPreview(lines.join("\n") || "File appears to be empty.");

    const parsed = parseTemperatureData(text);
    setTemperatureData(parsed);
  };

  return {
    csvPreview,
    temperatureData,
    previewCSV,
  };
};

export default useCSVParser;
