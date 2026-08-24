// OPTION X — CLINICAL + PREMIUM GRAPH ENGINE
// Apple × Tencent × McKinsey Hybrid (FINAL & CORRECTED)

import React, { useContext, useMemo } from "react";
import { AppContext } from "../../context/AppContext.jsx";
import styles from "./GraphPreview.module.css";

// Colours
const GOLD = "#D4AF37";
const RED = "#FF3B30";
const LIGHT_GRID = "rgba(255,255,255,0.22)";
const RED_ZONE = "rgba(255,59,48,0.12)";
const BLUE_ZONE = "rgba(52,120,246,0.14)";

const COLOR_LINE_2C = "#4db6e3"; // cold threshold
const COLOR_LINE_8C = "#FF6b6b"; // hot threshold

// AU clinical 24-hr format
function formatClinTime(d) {
  if (!(d instanceof Date)) return "";
  const dd = String(d.getDate()).padStart(2, "0");
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const yyyy = d.getFullYear();
  const HH = String(d.getHours()).padStart(2, "0");
  const MM = String(d.getMinutes()).padStart(2, "0");
  return `${dd}-${mm}-${yyyy} ${HH}:${MM}`;
}

function parseTime(str) {
  if (!str) return null;

  // Expect "DD-MM-YYYY HH:MM"
  const [datePart, timePart] = str.split(" ");
  if (!datePart) return null;

  const [dd, mm, yyyy] = datePart.split("-").map(Number);

  let hh = 0;
  let min = 0;
  if (timePart) {
    [hh, min] = timePart.split(":").map(Number);
  }

  // (Month is zero-indexed in JS)
  return new Date(yyyy, mm - 1, dd, hh, min, 0);
}

export default function GraphPreview() {
  const { state } = useContext(AppContext);
  const preview = state.preview;

  // ------------------ Early Guard -----------------------------------------
  if (!preview || !preview.rows || preview.rows.length < 2) {
    return (
      <div className={styles.placeholder}>
        <p className={styles.placeholderText}>Preview will appear here.</p>
      </div>
    );
  }

  // ------------------ Build points -----------------------------------------
  const points = preview.rows
    .map((r) => ({ t: parseTime(r.time), temp: Number(r.temp) }))
    .filter((p) => p.t && !isNaN(p.temp));

  if (points.length < 2) {
    return (
      <div className={styles.placeholder}>
        <p className={styles.placeholderText}>Invalid data.</p>
      </div>
    );
  }

  // Raw min/max for use in overlays
  const temps = points.map((p) => p.temp);
  const rawMin = Math.min(...temps);
  const rawMax = Math.max(...temps);

  // --------------------------------------------------------------------------------
  // GEOMETRY (premium clinical scaling)
  // --------------------------------------------------------------------------------
  const { w, h, pad, xScale, yScale, path, excursions } = useMemo(() => {
    const w = 900;
    const h = 360;
    const pad = 60;

    // Excel-style dynamic Y axis
    const ymin = Math.floor(Math.min(0, rawMin) - 1);
    const ymax = Math.ceil(Math.max(12, rawMax) + 2);

    const xScale = (i) =>
      pad + (i / (points.length - 1)) * (w - pad * 2);

    const yScale = (v) =>
      h - pad - ((v - ymin) / (ymax - ymin)) * (h - pad * 2);

    // ---- Polyline (no smoothing, strong peaks) ----
    let d = "";
    points.forEach((p, i) => {
      const x = xScale(i);
      const y = yScale(p.temp);
      if (i === 0) d += `M ${x},${y}`;
      else d += ` L ${x},${y}`;
    });

    // ---- Excursions detected on-graph (> 8°C) ----
    const excursions = points
      .map((p, i) => (p.temp > 8 ? { x: xScale(i), temp: p.temp } : null))
      .filter(Boolean);

    return { w, h, pad, xScale, yScale, path: d, excursions };
  }, [points, rawMin, rawMax]);

  // --------------------------------------------------------------------------------
  // RENDER
  // --------------------------------------------------------------------------------

  return (
    <div className={styles.card}>
      <h3 className={styles.title}>Temperature Preview</h3>

      <svg className={styles.svg} width="100%z" height={h} viewBox={`0 0 ${w} ${h}`} preserveAspectRatio={"xMidYMid meet"}>

        {/* --- CLINICAL SHADING ZONES --- */}

        {/* Danger zone > 8°C */}
        <rect
          x={pad}
          y={yScale(8)}
          width={w - pad * 2}
          height={yScale(0) - yScale(8)}
          fill={RED_ZONE}
        />

        {/* Freezing zone < 2°C */}
        <rect
          x={pad}
          y={yScale(2)}
          width={w - pad * 2}
          height={yScale(2) - yScale(-10)}
          fill={BLUE_ZONE}
        />

        {/* 2°C reference line */}
        <line
          x1={pad}
          x2={w - pad}
          y1={yScale(2)}
          y2={yScale(2)}
          stroke={COLOR_LINE_2C}
          strokeWidth="1.8"
          strokeDasharray="4 3"
        />

        <text
          x={pad - 8}
          y={yScale(2) + 4}
          fill={COLOR_LINE_2C}
          fontSize="13"
          textAnchor="end"
        >
          2°C
        </text>

        {/* 8°C reference line */}
        <line
          x1={pad}
          x2={w - pad}
          y1={yScale(8)}
          y2={yScale(8)}
          stroke={COLOR_LINE_8C}
          strokeWidth="2.2"
          strokeDasharray="4 3"
        />

        <text
          x={pad - 8}
          y={yScale(8) + 4}
          fill={COLOR_LINE_8C}
          fontSize="13"
          textAnchor="end"
        >
          8°C
        </text>

        {/* ----------- EXCURSION MARKERS (gold + red) ---------------- */}
        {excursions.map((e, i) => (
          <g key={i}>
            <rect
              x={e.x - 2}
              y={pad}
              width={4}
              height={h - pad * 2}
              fill={GOLD}
              opacity="0.9"
            />
            <rect
              x={e.x - 0.9}
              y={pad}
              width={1.8}
              height={h - pad * 2}
              fill={RED}
              opacity="0.85"
            />
          </g>
        ))}

        {/* TEMPERATURE LINE */}
        <path
          d={path}
          fill="none"
          stroke={GOLD}
          strokeWidth="3.1"
          strokeLinecap="round"
        />

        {/* SPIKE DOTS (hot peaks) */}
        {points.map((p, i) =>
          p.temp > 8 ? (
            <circle
              key={i}
              cx={xScale(i)}
              cy={yScale(p.temp)}
              r={4.5}
              fill={RED}
              stroke={GOLD}
              strokeWidth="1.2"
            />
          ) : null
        )}

        {/* ---------------- AXES LABELS ---------------- */}

        {/* Y-axis */}
        <text
          x={pad - 45}
          y={h / 2}
          fill="white"
          opacity="0.75"
          fontSize="14"
          textAnchor="middle"
          transform={`rotate(-90 ${pad - 45},${h / 2})`}
        >
          Temperature (°C)
        </text>

        {/* X-axis */}
        <text
          x={w / 2}
          y={h - 10}
          fill="white"
          opacity="0.75"
          fontSize="14"
          textAnchor="middle"
        >
          Time / Date (DD-MM-YYYY 24hr)
        </text>

        {/* First timestamp */}
        <text
          x={pad}
          y={h - pad + 25}
          fill="white"
          opacity="0.75"
          fontSize="12"
          textAnchor="start"
        >
          {formatClinTime(points[0].t)}
        </text>

        {/* Last timestamp */}
        <text
          x={w - pad}
          y={h - pad + 25}
          fill="white"
          opacity="0.75"
          fontSize="12"
          textAnchor="end"
        >
          {formatClinTime(points[points.length - 1].t)}
        </text>
      </svg>

      {/* --------------------- McKinsey Insight Overlays ---------------------- */}

      {excursions.length > 0 && (
        <div className={styles.insight} style={{ top: 80, right: 30 }}>
          <strong>Excursion Detected</strong><br />
          Peaks above 8°C indicate potential breach events.<br />
          Review duration vs GEYER thresholds.
        </div>
      )}

      {rawMax > 10 && (
        <div className={styles.insight} style={{ top: 150, right: 30 }}>
          <strong>High Temperature Behaviour</strong><br />
          Temperature reached {rawMax.toFixed(1)}°C.<br />
          Cooling-return slope should be assessed.
        </div>
      )}

      {rawMin < 1 && (
        <div className={styles.insight} style={{ top: 220, right: 30 }}>
          <strong>Low Temperature Risk</strong><br />
          Freezing-risk behaviour (below 2°C)<br />
          may compromise vaccine integrity.
        </div>
      )}

      {/* LEGEND */}
      <div className={styles.legendBox}>
        <div className={styles.legendRow}>
          <span className={styles.goldSwatch}></span> Temperature Trace
        </div>
        <div className={styles.legendRow}>
          <span className={styles.excursionSwatch}></span> Excursion Marker
        </div>
        <div className={styles.legendRow}>
          <span className={styles.redDot}></span> Above 8°C Spike
        </div>
      </div>
    </div>
  );
}