// src/utils/temperatureParser.js
export function parseTemperatureData(csvText) {
  if (!csvText) return [];

  const lines = csvText.split(/\r?\n/).filter((l) => l.trim().length > 0);
  if (lines.length < 2) return [];

  const header = lines[0].split(/[,;\t]/).map((h) => h.toLowerCase().trim());
  const rows = lines.slice(1);

  let tempIdx = header.findIndex((h) => h.includes("temp"));
  let timeIdx = header.findIndex(
    (h) => h.includes("time") || h.includes("date")
  );

  if (tempIdx === -1) tempIdx = 1;
  if (timeIdx === -1) timeIdx = 0;

  const data = [];

  for (const line of rows) {
    const parts = line.split(/[,;\t]/);
    if (parts.length <= tempIdx || parts.length <= timeIdx) continue;

    const rawTime = parts[timeIdx].trim();
    const tempVal = parseFloat(parts[tempIdx].replace(",", "."));

    if (Number.isNaN(tempVal) || !rawTime) continue;

    const isExcursion = tempVal < 2 || tempVal > 8;

    data.push({
      time: rawTime,
      temperature: tempVal,
      excursionPoint: isExcursion ? tempVal : undefined,
      excursion: isExcursion,
    });
  }

  return data;
}
