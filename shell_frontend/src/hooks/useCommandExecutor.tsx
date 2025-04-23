import React from 'react';
import commandRegistry from '../commands/commandRegistry'; // import command registry
import {UserData} from "../types/types.tsx"

export function useCommandExecutor(setHistory: React.Dispatch<React.SetStateAction<(string | JSX.Element)[]>>, setHidePrompt: React.Dispatch<React.SetStateAction<boolean>>, hidePrompt: boolean, user:UserData|null) {
  const executeCommand = (input: string) => {
    const [cmd, ...args] = input.trim().split(' '); // split command and args
    const commandExecutor = commandRegistry[cmd];
    const userName=user?.name_nospace ?? false
    if (commandExecutor) {
      console.log('commandExecutor', commandExecutor)
      const result = commandExecutor(args, setHistory, setHidePrompt, hidePrompt)
      console.log('result', result)
      
      if (typeof result === 'string' || React.isValidElement(result)) {
        console.log('result in condition', result)
        setHistory(prev => [...prev, `${userName}@zeroDay$ ${input}`, result]); // show result
      }
    } else {
      setHistory(prev => [...prev, `${userName}@zeroDay$ ${input}`, `Command not found: ${cmd}`]); // show error
    }
  };

  return executeCommand;
}
