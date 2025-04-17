import React from 'react';
import commandRegistry from '../commands/commandRegistry'; // import command registry

export function useCommandExecutor(setHistory: React.Dispatch<React.SetStateAction<(string | JSX.Element)[]>>) {
  const executeCommand = (input: string) => {
    const [cmd, ...args] = input.trim().split(' '); // split command and args
    const commandExecutor = commandRegistry[cmd];

    if (commandExecutor) {
      console.log('commandExecutor', commandExecutor)
      const result = commandExecutor(args, setHistory)
      console.log('result', result)
      
      if (typeof result === 'string' || React.isValidElement(result)) {
        console.log('result in condition', result)
        setHistory(prev => [...prev, `root@zeroDay$ ${input}`, result]); // show result
      }
    } else {
      setHistory(prev => [...prev, `root@zeroDay$ ${input}`, `Command not found: ${cmd}`]); // show error
    }
  };

  return executeCommand;
}
