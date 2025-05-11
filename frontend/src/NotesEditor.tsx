import React, { useEffect, useState } from "react";
import "./App.css";
import Editor from "react-simple-code-editor";
import DropdownSelect from "./DropdownSelect";
import { useParams, useSearchParams } from "react-router-dom";
import MonacoTextEditor from "./MonacoTextEditor";
import "./notes-editor.scss";

interface TalamDescription {
  avarthi: number[];
  line: number;
  splits: number[];
}

const noteMap: Record<string, JSX.Element> = {
  "1": <span>S </span>,
  "2": <span>R </span>,
  "3": <span>G </span>,
  "4": <span>M </span>,
  "5": <span>P </span>,
  "6": <span>D </span>,
  "7": <span>N </span>,
  "1q": <span>S&#775; </span>,
  "2q": <span>R&#775; </span>,
  "3q": <span>G&#775; </span>,
  "4q": <span>M&#775; </span>,
  "5q": <span>P&#775; </span>,
  "6q": <span>D&#775; </span>,
  "7q": <span>N&#775; </span>,
  "1u": <span>S&#803; </span>,
  "2u": <span>R&#803; </span>,
  "3u": <span>G&#803; </span>,
  "4u": <span>M&#803; </span>,
  "5u": <span>P&#803; </span>,
  "6u": <span>D&#803; </span>,
  "7u": <span>N&#803; </span>,
  "|": <span>&nbsp;&nbsp;</span>,
  "||": <span>&nbsp;&nbsp;|&nbsp;&nbsp;</span>,
  "|||": (
    <span>
      <span>&nbsp;&nbsp;||</span>
    </span>
  ),
  ",": <span>, </span>,
  "-": <span>- </span>,
};

const TALAM_OPTIONS = [
  "Adi",
  "khanDa cApu",
  "miSra cApu",
  "rUpaka",
  "khanDa aTa",
];

const breakMap: Record<string, TalamDescription> = {
  "khanDa cApu": {
    avarthi: [10, 10, 10, 10],
    line: 40,
    splits: [4, 6, 10],
  },
  Adi: {
    avarthi: [16, 16],
    line: 32,
    splits: [4, 8, 12, 16],
  },
  "miSra cApu": {
    avarthi: [14, 14],
    line: 28,
    splits: [2, 6, 10, 14],
  },
  rUpaka: {
    avarthi: [12, 12, 12, 12],
    line: 48,
    splits: [4, 8, 12],
  },
  "khanDa aTa": {
    avarthi: [20, 20, 16],
    line: 56,
    splits: [4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56],
  },
};

const NotesEditor: React.FC<{}> = () => {
  const [talam, setTalam] = useState<string>("Adi");
  const [code, setCode] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [searchParams, _setSearchParams] = useSearchParams();
  const path = searchParams.get("path") ?? "";

  useEffect(() => {
    if (path) {
      setLoading(false);
      fetch(`http://localhost:5000/file?path=${path}`)
        .then((response) => response.text())
        .then((data: string) => {
          console.log({ data });
          setCode(JSON.parse(data).content);
          setLoading(false);
        })
        .catch((error) => console.error("Error fetching data:", error));
    }
  }, [path]);

  const dashLetterMap = (s: string): JSX.Element => {
    if (noteMap.hasOwnProperty(s)) return noteMap[s];
    return <span>{s}</span>;
  };

  const breakParts = (avarthi: JSX.Element[]) => {
    const { splits } = breakMap[talam];
    let splitIndex = 0;
    let splitAvarthis = [];
    for (let j = 0; j < avarthi.length; j++) {
      if (j === splits[splitIndex]) {
        splitIndex++;
        splitAvarthis.push(noteMap["|"]);
      }
      splitAvarthis.push(avarthi[j]);
    }
    return splitAvarthis;
  };

  const breakAvarthis = (line: JSX.Element[]) => {
    const step = breakMap[talam].avarthi;
    let withAvarthis = [];
    let index = 0;
    let aIndex = 0;
    while (index < line.length) {
      const av = line.slice(index, index + step[aIndex]);
      withAvarthis.push(breakParts(av));
      if (av.length === step[aIndex] && index + step[aIndex] !== line.length)
        withAvarthis.push(noteMap["||"]);
      index += step[aIndex];
      aIndex = (aIndex + 1) % step.length;
    }
    return withAvarthis;
  };

  const processMatches = (m: string[]) => {
    const spans = m.map((match) => noteMap[match]);
    // console.log(m);
    const step = breakMap[talam].line;
    let withLines = [];
    for (let i = 0; i < spans.length; i += step) {
      const line = spans.slice(i, i + step);
      withLines.push(breakAvarthis(line));
      if (line.length === step) withLines.push(noteMap["|||"]);
    }
    withLines.push(
      <span>
        <br />
        <br />
      </span>
    );
    return withLines;
  };

  const processDashes = (
    dashes: string[],
    lengths: number[],
    syllables: string[],
    numbers: number[]
  ) => {
    let i = 0;
    let sylIndex = 0;
    while (i < dashes.length) {
      const syl = syllables[sylIndex];
      const sylLen = lengths[sylIndex];
      const n = numbers[sylIndex];
      for (let j = i; j < i + sylLen; j++) {
        dashes[j] = syl.slice((j - i) * 2, (j - i + 1) * 2);
        if (dashes[j].length === 1) {
          dashes[j] += " ";
        }
      }
      i += n;
      sylIndex++;
    }
    const spans = dashes.map(dashLetterMap);
    const step = breakMap[talam].line;
    let withLines = [];
    for (let i = 0; i < spans.length; i += step) {
      const line = spans.slice(i, i + step);
      withLines.push(breakAvarthis(line));
      if (line.length === step) withLines.push(noteMap["|||"]);
    }
    withLines.push(
      <span>
        <br />
        <br />
      </span>
    );
    return withLines;
  };

  const processLyrics = (line: string) => {
    const num = /[0-9]+/g;
    const noNum = /[^0-9]+/g;
    const numbers = (line.match(num) || []).map((n) => parseInt(n));
    const sum = numbers.reduce((total, num) => total + num, 0);
    const syllables = line.match(noNum) || [];
    const lengths = syllables.map((s) => Math.ceil(s.length / 2));
    const a = Array(sum).fill("-");
    const dashes = processDashes(a, lengths, syllables, numbers).flat(5);
    console.log({ a });
    console.log({ dashes, lengths, syllables, numbers });
    let count = 0;
    for (let i = 0; i < numbers.length; i++) {
      const sylLen = lengths[i];
      const syl = syllables[i];
      const dur = numbers[i];
      if (syl !== "-") {
        for (let j = 0; j < sylLen; j++) {
          console.log({ a: typeof dashes[count + j] });
          // dashes[count + j].text = syl.slice(2*j, 2*(j+1));
        }
      }
      count += dur;
    }
    // console.log({ numbers, syllables, lengths });
    return dashes;
  };

  const updateFormat = (code: string): string[] => {
    const matches = code.match(/(([1234567][qu]?)|(,))/g);
    let returnedMatches: string[] = [];
    if (matches !== null) {
      returnedMatches = matches as string[];
    }
    return returnedMatches;
  };

  return (
    <div className="notes-editor-container">
      <div className="monaco-container">
        <span style={{ marginRight: "4px" }}>
          (
          <a href="/" className="product-link">
            Home
          </a>
          )
        </span>
        <span>{path}</span>
        <DropdownSelect
          options={Object.keys(breakMap)}
          value={talam}
          onChange={setTalam}
          caption="Choose talam"
        />
        <MonacoTextEditor initialValue={code} />
      </div>
      <div className="prettified-notes-container">
        {code.split("\n").map((line) => {
          let notation = line.match(/{.*}/g);
          if (notation !== null)
            return processLyrics(line.substring(1, line.length - 1));
          let comment = line.substring(0, 2) === "//";
          if (comment)
            return (
              <span>
                {line.substring(2).trim()}
                <br />
              </span>
            );
          return processMatches(updateFormat(line));
        })}
      </div>
    </div>
  );
};

export default NotesEditor;
