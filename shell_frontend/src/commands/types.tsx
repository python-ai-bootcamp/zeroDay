import type { JSX } from 'react';


export interface CommandExecutorParams {
  setHistory: React.Dispatch<React.SetStateAction<string[]>>;
  // Add any other properties that might be passed into the command executor
}

export type CommandExecutor = (
  args: string[],
  setHistory: React.Dispatch<React.SetStateAction<(string | JSX.Element)[]>>,
  setHidePrompt: React.Dispatch<React.SetStateAction<boolean>>,
  hidePrompt: boolean,
) => string | JSX.Element | void;


