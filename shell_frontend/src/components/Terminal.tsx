import React, { useState, useEffect} from 'react';
import { useCommandExecutor } from '../hooks/useCommandExecutor'; // import command executor hook
import HackerSequence from './HackerSequence'; // import the hacker sequence component





const Terminal = () => {
  const initial_message = '🖥️ Welcome to Zero Day Terminal OS, \nplease enter `help` for a list of commands';
  const [command, setCommand] = useState('');
  const [history, setHistory] = useState<string[]>([initial_message]);
  const executeCommand = useCommandExecutor(setHistory);




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
  typeof entry === 'string' ? (
    entry.split('\n').map((line, i) => <div key={`${index}-${i}`}>{line}</div>)
  ) : (
    <div key={index}>{entry}</div>
  )
)}

      {/* Command prompt */}
      <div className="flex">
        <span>root@zeroDay$&nbsp;</span>
        <input
          type="text"
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          onKeyDown={handleCommand}
          className="bg-transparent border-none outline-none w-full text-green-500"
          autoFocus
        />
      </div>
    </div>
  );
};

export default Terminal;
