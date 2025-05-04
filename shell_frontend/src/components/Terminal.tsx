import React, { useRef, useState, useEffect, useLayoutEffect } from 'react';
import { useCommandExecutor } from '../hooks/useCommandExecutor'; // import command executor hook
import { useUser } from '../hooks/userContext'; 
import commandRegistry from '../commands/commandRegistry'; // import command registry


let tempHistoryIndex: number | null = null;
const Terminal = () => {
  const initial_message = '🖥️ Welcome to Zero Day Terminal OS, \nplease enter `help` for a list of commands';
  const [command, setCommand] = useState('');
  const [terminalCommandHistory, setTerminalCommandHistory]  = useState<string[]>([initial_message]);
  const commands=Object.keys(commandRegistry);
  const [unsavedCommand, setUnsavedCommand] = useState<string | null>(null);

  const [history, setHistory] = useState<string[]>([initial_message]);
  const [hidePrompt, setHidePrompt] = useState(false); // state to control prompt visibility
  const user = useUser();
  const scrollRef = useRef<HTMLDivElement>(null);
  const triggerScroll = () => { // need to figure out how to send it to each command so it will execute it in appropriate times to give a smotther feeling to console commands
    setTimeout(() => {
      scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
      inputRef.current?.focus();
    }, 100);  // Delay scroll by 0.1s to ensure content is rendered
  };
  const possibleCommands:Record<string, string[]> = {"current":[]}
  const executeCommand = useCommandExecutor(triggerScroll, setHistory, setHidePrompt, hidePrompt, terminalCommandHistory, possibleCommands);
  const inputRef = useRef<HTMLInputElement>(null);
  const tabTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);
  const tabCount = useRef(0);
  useEffect(() => {
    const handleDocumentClick = (e: Event) => {
      console.log("handleDocumentClick was called")
      if (inputRef.current && document.activeElement !== inputRef.current) {
        inputRef.current.focus();
      }
    };

    document.addEventListener('click', handleDocumentClick);
    document.addEventListener('contextmenu', handleDocumentClick);
    document.addEventListener('touchend', handleDocumentClick); // support mobile
    return () => {
      document.removeEventListener('click', handleDocumentClick);
      document.removeEventListener('contextmenu', handleDocumentClick);
      document.removeEventListener('touchend', handleDocumentClick);
    };
  }, []);

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, [command]);

  const handleKeyboardInterrupt = () =>{
    setCommand(`${command}^C`);
    setHistory((prev) => [...prev, `${user?.name_nospace ?? 'root'}@zeroDay$ ${command}^C`]);
    setCommand('');
  }

  const handleCommand = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Tab') {
      e.preventDefault();
    
      tabCount.current += 1;
    
      if (tabCount.current === 1) {
        tabTimeout.current = setTimeout(() => {
          console.log('Single Tab detected (no double Tab)');
          tabCount.current = 0;
          tabTimeout.current = null;
        }, 350);
      } else if (tabCount.current === 2) {
        console.log('🔥 Double Tab detected!');
        if (tabTimeout.current) clearTimeout(tabTimeout.current);
        tabCount.current = 0;
        tabTimeout.current = null;
    
        console.log(`detected double tab with command='${command}'`)
        possibleCommands.current=commands.filter(x=>x.startsWith(command));
        console.log(`detected possibleCommands='${possibleCommands.current}'`)
        if(possibleCommands.current.length==1){
          setCommand(possibleCommands.current[0])
        }else if(possibleCommands.current.length>=2){
          console.log("need to implement possible commands presentation")
          executeCommand(command)
        }

      }
    
      return;
    }
    
    if (e.ctrlKey && (e.key === 'c' || e.key === 'C')) {
      e.preventDefault();
      handleKeyboardInterrupt();
      return;
    }

    if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (terminalCommandHistory.length === 0) return;
      if (tempHistoryIndex === null) {
        setUnsavedCommand(command);
        tempHistoryIndex = terminalCommandHistory.length - 1;        
      } else {
        tempHistoryIndex = Math.max(tempHistoryIndex - 1, 1);
      }
      setCommand(terminalCommandHistory[tempHistoryIndex]);
      return;
    }
    
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (tempHistoryIndex === null) return;
  
      tempHistoryIndex += 1;
  
      if (tempHistoryIndex >= terminalCommandHistory.length) {
        setCommand(unsavedCommand || '');
        setUnsavedCommand(null);
        tempHistoryIndex = null;
      } else {
        setCommand(terminalCommandHistory[tempHistoryIndex]);
      }
      return;
    }

    if (e.key === 'Enter') {
      console.log("command::",command)
      triggerScroll()
      if (command.trim()) { //if the command is not empty, need to execute it
        if (command.trim()!==""){
          setTerminalCommandHistory(prev => [...prev, command]);
        }
        executeCommand(command);
      }else{ //if command is empty, don't execute it, but add extra empyy prompt to history 
        setHistory((prev) => [...prev, `${user?.name_nospace ?? 'root'}@zeroDay$ ${command}`,]);
      }
      setCommand('');//on either case need clear the prompt after and then reset the terminalcommandHistory temp index to null
      tempHistoryIndex = null;
      setUnsavedCommand(null);
    }
  };

  console.log("hidePromet=",hidePrompt)
  
  return (
    <div className="w-full h-screen p-4 bg-black text-green-500 font-mono overflow-y-auto">
      {/* Command history */}
      {history.map((entry, index) =>
          typeof entry === 'string' ? (entry
                                        .split('\n')
                                        .map((line, i) => <div key={`${index}-${i}`}>{line}</div>)) 
                                    : ( <div key={index}>{entry}</div>)
      )}

      {/* Command prompt */}
      {!hidePrompt && ( 
        <div className="flex">
        {user ? <span>{user.name_nospace}@zeroDay$&nbsp;</span> : <span>root@zeroDay$&nbsp;</span>}
        <input
          ref={inputRef}
          type="text"
          value={command}
          onInput={(e) => setCommand((e.target as HTMLInputElement).value)}
          onKeyDown={handleCommand}
          className="bg-transparent border-none outline-none w-full text-green-500"
        />
      </div>
      )}
      <div ref={scrollRef} />
    </div>
  );
};

export default Terminal;
