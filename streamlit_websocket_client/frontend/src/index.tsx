import React from "react"
import ReactDOM from "react-dom/client"
import StreamlitWebSocket from "./StreamlitWebSocket"

// Get the root element
const rootElement = document.getElementById("root")
if (!rootElement) {
  throw new Error("Failed to find the root element")
}

// Create root and render
const root = ReactDOM.createRoot(rootElement)
root.render(
  <React.StrictMode>
    <StreamlitWebSocket />
  </React.StrictMode>
)