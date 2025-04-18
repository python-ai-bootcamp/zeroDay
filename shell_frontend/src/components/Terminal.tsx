import React, { useState, useEffect} from 'react';
import { useCommandExecutor } from '../hooks/useCommandExecutor'; // import command executor hook
import { UserData } from '../types/types'; // import UserData type


const Terminal = () => {
  const initial_message = '🖥️ Welcome to Zero Day Terminal OS, \nplease enter `help` for a list of commands';
  const [command, setCommand] = useState('');
  const [history, setHistory] = useState<string[]>([initial_message]);
  const [hidePrompt, setHidePrompt] = useState(false); // state to control prompt visibility
  const executeCommand = useCommandExecutor(setHistory, setHidePrompt, hidePrompt);

  
  const [userData, setUserData] = useState<UserData | null>(null);
  
  useEffect(() => {

      const fetchUserData = async () => {
        try {
          const response = await fetch('http://127.0.0.1:8000/v2/user?hacker_id=5r4xxv'); // replace with your actual endpoint
          if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
          }
          const data = await response.json();
          console.log(data); // Log the response data
          setUserData(data);
        } catch (error) {
          console.error('Error fetching user data:', error);
        }
      };

      fetchUserData();
    
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
  typeof entry === 'string' ? (
    entry.split('\n').map((line, i) => <div key={`${index}-${i}`}>{line}</div>)
  ) : (
    <div key={index}>{entry}</div>
  )
)}

      {/* Command prompt */}
      {!hidePrompt && ( 
        <div className="flex">
        {userData ? <span>{userData.name}@zeroDay$&nbsp;</span> : <span>root@zeroDay$&nbsp;</span>}
        <input
          type="text"
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          onKeyDown={handleCommand}
          className="bg-transparent border-none outline-none w-full text-green-500"
          autoFocus
        />
      </div>
      )}

    </div>
  );
};

export default Terminal;
