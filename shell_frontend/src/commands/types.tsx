import type { JSX } from 'react';


export interface CommandExecutorParams {
  setHistory: React.Dispatch<React.SetStateAction<string[]>>;
  // Add any other properties that might be passed into the command executor
}

export type CommandExecutor = (
  args: string[],
  triggerScroll: () => void,
  setHistory: React.Dispatch<React.SetStateAction<(string | JSX.Element)[]>>,
  setHidePrompt: React.Dispatch<React.SetStateAction<boolean>>,
  hidePrompt: boolean,
  terminalCommandHistory: string[]
) => string | JSX.Element | void;

export type AssignmentStatus = {
  assignment_id: number;
  submission_id: number;
  max_submission_id: number;
};


