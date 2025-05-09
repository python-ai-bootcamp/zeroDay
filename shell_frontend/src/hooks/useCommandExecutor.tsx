import React, { JSX } from 'react';
import commandRegistry from '../commands/commandRegistry'; // import command registry
import { useUser } from '../hooks/userContext'; 

function findLongestCommonPrefix(arr: string[], str: string): string {
  if (!arr.length) return str;
  let prefix = arr[0];
  for (let i = 1; i < arr.length; i++) {
    const current = arr[i];
    let j = 0;
    while (j < prefix.length && j < current.length && prefix[j] === current[j]) {
      j++;
    }
    prefix = prefix.slice(0, j);
    if (prefix === "") break;
  }
  if (prefix.length > str.length && prefix.startsWith(str)) {
    return prefix;
  }
  return str;
}

export function useCommandExecutor(triggerScroll: () => void, setHistory: React.Dispatch<React.SetStateAction<(string | JSX.Element)[]>>, setHidePrompt: React.Dispatch<React.SetStateAction<boolean>>, terminalCommandHistory: string[], possibleCommands:Record<string, string[]>, setCommand:React.Dispatch<React.SetStateAction<string>>,isTriggeredByEnterKey:Record<string, boolean>) {
  const user = useUser();
  const executeCommand = (input: string) => {
    const [cmd, ...args] = input.trim().split(' '); // split command and args
    const commandExecutor = commandRegistry[cmd];
    if (commandExecutor && isTriggeredByEnterKey.current) {
      const result = commandExecutor(args, triggerScroll, setHistory, setHidePrompt, terminalCommandHistory)
      console.log('result', result)
      
      if (typeof result === 'string' || React.isValidElement(result)) {
        console.log('result in condition', result)
        setHistory(prev => [...prev, `${user?.name_nospace}@zeroDay$ ${input}`, result]); // show result
      }
    } else {
      if (possibleCommands.current.length>0){
        const longestCommonPrefix=findLongestCommonPrefix(possibleCommands.current, cmd)
        console.log("useCommandExecutor:: longestCommonPrefix=",longestCommonPrefix)
        setHistory(prev => [...prev, `${user?.name_nospace}@zeroDay$ ${input}`, `Possible Commands: ${"\n"+possibleCommands.current.map(x=>`- ${x}`).join("\n")}`]); // show possible commands by partial command prefix
        setCommand(longestCommonPrefix)
        triggerScroll()
        return;
      }else{
        setHistory(prev => [...prev, `${user?.name_nospace}@zeroDay$ ${input}`, `Command not found: ${cmd}`]); // show error
      }
    }
  };
  return executeCommand;
}
