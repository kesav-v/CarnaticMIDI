import React from "react";
import logo from "./logo.svg";
import "./App.css";
import NotesEditor from "./NotesEditor";
import { ThemeProvider, createTheme, CssBaseline } from "@mui/material";
import { BrowserRouter as Router, Route, Link, Routes } from "react-router-dom";
import FileViewer from "./FileViewer";

function App() {
  const darkTheme = createTheme({
    palette: {
      mode: "dark",
    },
  });
  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/" element={<FileViewer />} />
          <Route path="/" element={<FileViewer />} />
          <Route path="/editor" element={<NotesEditor />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
