import React from 'react';
import commandRegistry from '../commands/commandRegistry'; // import command registry
import { useUser } from '../hooks/userContext'; 

export function useCommandExecutor(triggerScroll: () => void, setHistory: React.Dispatch<React.SetStateAction<(string | JSX.Element)[]>>, setHidePrompt: React.Dispatch<React.SetStateAction<boolean>>, hidePrompt: boolean, terminalCommandHistory: string[]) {
  const user = useUser();
  const executeCommand = (input: string) => {
    const [cmd, ...args] = input.trim().split(' '); // split command and args
    const commandExecutor = commandRegistry[cmd];
    if (commandExecutor) {
      const result = commandExecutor(args, triggerScroll, setHistory, setHidePrompt, hidePrompt, terminalCommandHistory)
      console.log('result', result)
      
      if (typeof result === 'string' || React.isValidElement(result)) {
        console.log('result in condition', result)
        setHistory(prev => [...prev, `${user?.name_nospace}@zeroDay$ ${input}`, result]); // show result
      }
    } else {
      setHistory(prev => [...prev, `${user?.name_nospace}@zeroDay$ ${input}`, `Command not found: ${cmd}`]); // show error
    }
  };

  return executeCommand;
}
