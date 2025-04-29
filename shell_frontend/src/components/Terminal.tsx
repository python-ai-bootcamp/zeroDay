import React, { useRef, useState, useEffect} from 'react';
import { useCommandExecutor } from '../hooks/useCommandExecutor'; // import command executor hook
import { useUser } from '../hooks/userContext'; 


const Terminal = () => {
  const initial_message = '🖥️ Welcome to Zero Day Terminal OS, \nplease enter `help` for a list of commands';
  const [command, setCommand] = useState('');
  const [terminalCommandHistory, setTerminalCommandHistory]  = useState<string[]>([initial_message]);
  const [historyIndex, setHistoryIndex] = useState<number | null>(null);
  const [unsavedCommand, setUnsavedCommand] = useState<string | null>(null);

  const [history, setHistory] = useState<string[]>([initial_message]);
  const [hidePrompt, setHidePrompt] = useState(false); // state to control prompt visibility
  const user = useUser();
  const executeCommand = useCommandExecutor(setHistory, setHidePrompt, hidePrompt, terminalCommandHistory);
  const inputRef = useRef<HTMLInputElement>(null);
  
  useEffect(() => {
    const handleDocumentClick = (e: Event) => {
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

  const handleKeyboardInterrupt = () =>{
    setCommand(`${command}^C`);
    setHistory((prev) => [...prev, `${user?.name_nospace ?? 'root'}@zeroDay$ ${command}^C`]);
    setCommand('');
  }

  const handleCommand = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.ctrlKey && (e.key === 'c' || e.key === 'C')) {
      e.preventDefault();
      handleKeyboardInterrupt();
      return;
    }
    if (e.key === 'ArrowUp') {
      e.preventDefault();
      setHistoryIndex((prev) => {
        if (terminalCommandHistory.length === 0) return null;
        
        if (prev === null) {
          // Starting to navigate history – save current input
          setUnsavedCommand(command);
          const lastIndex = terminalCommandHistory.length - 1;
          setCommand(terminalCommandHistory[lastIndex]);
          return lastIndex;
        }
    
        const nextIndex = Math.max(prev - 1, 1);
        setCommand(terminalCommandHistory[nextIndex]);
        return nextIndex;
      });
      return;
    }
    
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setHistoryIndex((prev) => {
        if (prev === null) return null; // not in history mode
    
        const nextIndex = prev + 1;
        if (nextIndex >= terminalCommandHistory.length) {
          // End of history, restore unsaved command
          setCommand(unsavedCommand || '');
          setUnsavedCommand(null);
          return null;
        }
    
        setCommand(terminalCommandHistory[nextIndex]);
        return nextIndex;
      });
      return;
    }
    if (e.key === 'Enter') {
      if (command.trim()) { //if the command is not empty, need to execute it
        if (command.trim()!==""){
          setTerminalCommandHistory(prev => [...prev, command]);
        }
        executeCommand(command);
      }else{ //if command is empty, don't execute it, but add extra empyy prompt to history 
        setHistory((prev) => [
          ...prev,
          `${user?.name_nospace ?? 'root'}@zeroDay$ ${command}`,
        ]);
      }
      setCommand('');//on either case need clear the prompt after
      setHistoryIndex(null);
      setUnsavedCommand(null);
    }
  };


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
          onChange={(e) => setCommand(e.target.value)}
          onKeyDown={handleCommand}
          className="bg-transparent border-none outline-none w-full text-green-500"
        />
      </div>
      )}

    </div>
  );
};

export default Terminal;
