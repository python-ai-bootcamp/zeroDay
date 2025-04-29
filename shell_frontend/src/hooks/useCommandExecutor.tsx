import React, { useRef }from 'react';
import commandRegistry from '../commands/commandRegistry'; // import command registry
import { useUser } from '../hooks/userContext'; 

export function useCommandExecutor(setHistory: React.Dispatch<React.SetStateAction<(string | JSX.Element)[]>>, setHidePrompt: React.Dispatch<React.SetStateAction<boolean>>, hidePrompt: boolean) {
  const user = useUser();
  const executedCommandsHistoryRef = useRef<string[]>([]);
  const executeCommand = (input: string) => {
    executedCommandsHistoryRef.current.push(input);
    console.log("useCommandExecutor command received following history array::\n",executedCommandsHistoryRef.current)
    const [cmd, ...args] = input.trim().split(' '); // split command and args
    const commandExecutor = commandRegistry[cmd];
    if (commandExecutor) {
      console.log('commandExecutor', commandExecutor)
      const result = commandExecutor(args, setHistory, setHidePrompt, hidePrompt, executedCommandsHistoryRef.current)
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
