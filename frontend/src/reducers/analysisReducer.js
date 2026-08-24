// src/reducers/analysisReducer.js

export const initialState = {
  file: null,
  filename: "",
  preview: null,          // backend preview payload
  results: null,          // full analysis payload
  temperatureData: [],    // for GraphPreview
  status: {
    level: "",
    message: "",
  },
  error: "",
  loading: {
    preview: false,
    analyse: false,
    report: false,
  },
  pdfEndpoint: "",
  archiveTimestamp: "",
};

export function analysisReducer(state, action) {
  switch (action.type) {
    case "SET_FILE":
      return {
        ...state,
        file: action.payload.file,
        filename: action.payload.filename,
        error: "",
        status: { level: "", message: "File selected" },
      };

    case "SET_PREVIEW_START":
      return {
        ...state,
        loading: { ...state.loading, preview: true },
        error: "",
        status: { level: "", message: "Parsing CSV preview…" },
      };

    case "SET_PREVIEW_SUCCESS":
      return {
        ...state,
        preview: action.payload.preview,
        temperatureData: action.payload.temperatureData,
        loading: { ...state.loading, preview: false },
        status: { level: "", message: "CSV preview ready" },
      };

    case "SET_ANALYSE_START":
      return {
        ...state,
        loading: { ...state.loading, analyse: true },
        error: "",
        status: { level: "", message: "Analysing logger…" },
      };

    case "SET_ANALYSE_SUCCESS":
      return {
        ...state,
        results: action.payload.results,
        temperatureData: action.payload.temperatureData,
        loading: { ...state.loading, analyse: false },
        status: {
          level: action.payload.results?.geyer?.level || "",
          message: "Analysis complete",
        },
      };

    case "SET_REPORT_START":
      return {
        ...state,
        loading: { ...state.loading, report: true },
        error: "",
        status: {
          level: state.results?.geyer?.level || "",
          message: "Generating ColdProof report…",
        },
      };

    case "SET_REPORT_SUCCESS":
      return {
        ...state,
        loading: { ...state.loading, report: false },
        pdfEndpoint: action.payload.pdfEndpoint,
        archiveTimestamp: action.payload.archiveTimestamp,
        status: {
          level: state.results?.geyer?.level || "",
          message: "Report generated and archived.",
        },
      };

    case "SET_ERROR":
      return {
        ...state,
        loading: { preview: false, analyse: false, report: false },
        error: action.payload,
        status: {
          level: "",
          message: "An error occurred – please try again.",
        },
      };

    case "CLEAR_ERROR":
      return {
        ...state,
        error: "",
      };

    default:
      return state;
  }
}
