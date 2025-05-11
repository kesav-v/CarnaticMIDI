import React, { useEffect, useState } from "react";
import MonacoEditor from "react-monaco-editor";

interface MonacoEditorProps {
  initialValue?: string;
  onSave?: (content: string) => void;
}

const MonacoTextEditor: React.FC<MonacoEditorProps> = ({
  initialValue,
  onSave,
}) => {
  const [editor, setEditor] = useState<any>(null);

  useEffect(() => {
    // Ensure the layout is correct on initial load or if window resizes
    const handleResize = () => {
      if (editor) {
        editor.layout(); // Refresh the layout when the window is resized
      }
    };

    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, [editor]);

  const handleEditorDidMount = (editorInstance: any, monaco: any) => {
    setEditor(editorInstance);
    editorInstance.layout(); // Initial layout adjustment
    editorInstance.updateOptions({
      keyBinding: "vim",
    });
  };
  const options = {
    selectOnLineNumbers: true,
  };
  return (
    <MonacoEditor
      language="text"
      editorDidMount={handleEditorDidMount}
      value={initialValue ?? "// Write your code here"}
      theme="vs-dark"
      options={options}
      height="500px"
    />
  );
};

export default MonacoTextEditor;
