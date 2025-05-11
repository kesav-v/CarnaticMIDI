import React, { useEffect, useState } from "react";
import { useLocation, useParams } from "react-router-dom";

interface FileInfo {
  type: string;
  path: string;
}

const FileViewer: React.FC<{}> = (): JSX.Element => {
  const [allFiles, setAllFiles] = useState<FileInfo[]>([]);
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const path = params.get("path") ?? "";
  useEffect(() => {
    let url = "http://localhost:5000/files";
    if (path.length > 0) {
      url += `?path=${path}`;
    }
    fetch(url)
      .then((response) => response.text())
      .then((data: string) => {
        setAllFiles(JSON.parse(data));
      })
      .catch((error) => console.error("Error fetching data:", error));
  }, [path]);
  const basePath = path ? `${path}/` : "";
  return (
    <div>
      {allFiles.map((file) => {
        return (
          <div>
            <a
              className="product-link"
              href={
                file.type === "dir"
                  ? `?path=${basePath}${file.path}`
                  : `/editor?path=${basePath}${file.path}`
              }
            >
              {file.path}
            </a>
          </div>
        );
      })}
    </div>
  );
};

export default FileViewer;
