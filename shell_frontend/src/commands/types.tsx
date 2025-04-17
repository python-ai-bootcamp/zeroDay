import type { JSX } from 'react';


export interface CommandExecutorParams {
  setHistory: React.Dispatch<React.SetStateAction<string[]>>;
  // Add any other properties that might be passed into the command executor
}

export type CommandExecutor = (
  args: string[],
  setHistory: React.Dispatch<React.SetStateAction<(string | JSX.Element)[]>>
) => string | JSX.Element | void;


