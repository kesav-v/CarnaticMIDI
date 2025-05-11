import React from "react";
import { MenuItem, FormControl, Select, InputLabel } from "@mui/material";
import "./dropdown-select.scss";

interface DropdownSelectProps {
  options: string[];
  value: string;
  onChange: (value: string) => void;
  caption?: string;
  width?: string;
}

const DropdownSelect: React.FC<DropdownSelectProps> = ({
  options,
  value,
  onChange,
  caption,
}) => {
  return (
    <div className="dropdown-container">
      <FormControl fullWidth>
        <InputLabel>{caption ?? "Choose an option"}</InputLabel>
        <Select<string>
          value={value}
          onChange={(e) => onChange(e.target.value)}
          label={caption ?? "Choose an option"}
        >
          {options.map((option) => {
            return <MenuItem value={option}>{option}</MenuItem>;
          })}
        </Select>
      </FormControl>
    </div>
  );
};

export default DropdownSelect;
