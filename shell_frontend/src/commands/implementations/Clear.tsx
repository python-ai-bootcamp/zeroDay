import { useEffect } from 'react';

const Clear = ({ setHistory }: { setHistory: React.Dispatch<React.SetStateAction<string[]>> }) => {
  
useEffect(() => {
    setHistory([]); // Clear the history when this component is mounted
  }, [setHistory]);

  return null; // No need to render anything
};

export default Clear;
