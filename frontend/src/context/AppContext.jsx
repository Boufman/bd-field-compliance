
import React, { createContext, useReducer } from "react";

export const AppContext = createContext(null);

// -------------------------
// Initial State
// -------------------------
const initialState = {
  file: null,
  filename: "",
  preview: null,
  analysis: null,

  pdfUrl: null,
  pdfTimestamp: null,

  loading: false,

  status: {
    level: "NEUTRAL",
    message: "Waiting for upload…",
  },

  error: null,
};

// -------------------------
// Reducer
// -------------------------
function appReducer(state, action) {
  console.log("REDUCER ACTION:", action.type, action);

  switch (action.type) {
    case "SET_FILE":
      return {
        ...state,
        file: action.file,
        filename: action.filename,
        preview: null,
        analysis: null,
        pdfUrl: null,
        pdfTimestamp: null,
        status: { level: "NEUTRAL", message: "File loaded. Ready to preview." },
        error: null,
      };

    case "SET_LOADING":
      return { ...state, loading: action.loading };

    case "SET_PREVIEW":
      return {
        ...state,
        preview: action.preview,
        status: { level: "YELLOW", message: "Preview loaded." },
      };

    case "SET_ANALYSIS":
      return {
        ...state,
        analysis: action.analysis,
        status: {
          level:
            action.analysis?.summary?.geyer?.level ||
            action.analysis?.geyer?.level ||
            "NEUTRAL",
          message: "Analysis complete.",
        },
      };

    case "SET_PDF":
      return {
        ...state,
        pdfUrl: action.pdfEndpoint,
        pdfTimestamp: action.timestamp,
        status: { level: "GREEN", message: "PDF ready." },
      };

    case "SET_ERROR":
      return {
        ...state,
        error: action.error,
        status: { level: "RED", message: "An error occurred." },
        loading: false,
      };

    case "RESET_ALL":
      return { ...initialState };

    default:
      return state;
  }
}

// -------------------------
// Provider
// -------------------------
export const AppProvider = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState);

  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  );
};