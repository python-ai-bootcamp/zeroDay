import React, { useRef, useState, useEffect} from 'react';
import { useCommandExecutor } from '../hooks/useCommandExecutor'; // import command executor hook
import { useUser } from '../hooks/userContext'; 

const Terminal = () => {
  const initial_message = '🖥️ Welcome to Zero Day Terminal OS, \nplease enter `help` for a list of commands';
  const [command, setCommand] = useState('');
  const [history, setHistory] = useState<string[]>([initial_message]);
  const [hidePrompt, setHidePrompt] = useState(false); // state to control prompt visibility
  const user = useUser();
  const executeCommand = useCommandExecutor(setHistory, setHidePrompt, hidePrompt);
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


  const handleCommand = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && command.trim()) {
      executeCommand(command);
      //setHistory((prev) => [...prev, `root@zeroDay$ ${command}`]);
      setCommand('');
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
