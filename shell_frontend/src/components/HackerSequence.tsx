import { useState, useEffect } from 'react';

const HackerSequence = () => {
  const [hackTextVisible, setHackTextVisible] = useState<boolean>(true); // Control visibility of sequence
  const [dotsCount, setDotsCount] = useState<number>(0); // Control dots for loading effect
  const [sequenceEnded, setSequenceEnded] = useState<boolean>(false); // Track sequence completion
  const [history, setHistory] = useState<string[]>([]); // Store history of events
  const [previousMessages, setPreviousMessages] = useState<Set<string>>(new Set()); // Store previous messages to avoid repetition

  // Function to simulate loading dots
  const showLoadingDots = async (message: string) => {
    setHackTextVisible(true);

    // Only show the message if it hasn't been displayed before
    if (!previousMessages.has(message)) {
      setPreviousMessages(prev => new Set(prev.add(message)));
      setHistory(prev => [...prev, message]);
    }

    // Simulate dot loading effect
    for (let i = 0; i < 3; i++) {
      setDotsCount(i + 1);
      await new Promise(resolve => setTimeout(resolve, 500)); // Add a dot every 0.5 seconds
    }
    setDotsCount(0);
  };

  useEffect(() => {
    const runHackerySequence = async () => {
      // Simulate "Locating IP" with dots
      await showLoadingDots('Locating IP');
      
      // Simulate "Getting system info" with dots
      await showLoadingDots('Getting system info');
      
      // Simulate "Connecting to node" with dots
      await showLoadingDots('Connecting to node');
      setHistory(prev => [
        ...prev,
        `Connected to node: zeroDay-${Math.random().toString(16).slice(2, 8)}`,
        `Session token: 0x${crypto.randomUUID().slice(0, 8)}...`
      ]);

      // Simulate root access attempt
      await showLoadingDots('Attempting root access');
      setHistory(prev => [
        ...prev,
        `Root access: ${Math.random() > 0.2 ? 'GRANTED' : 'DENIED (override)'}`,
        `Port scan: 22 open • 80 open • 443 open`,
        `Cipher strength: AES-256`,
        `Entropy pool: Sufficient`
      ]);

      // Simulate final system info loading
      await showLoadingDots('Accessing system info');
      
      // Add system data to history
      setHistory(prev => [
        ...prev,
        `Platform: unknown`,
        `Cores: unknown`,
        `Memory: unknown GB`,
        `Touch: unknown`,
        `Cookies: unknown`,
        `Online: unknown`,
        `Screen: unknown`
      ]);

      // Mark the end of the sequence
      setSequenceEnded(true);

      // Set a timeout to hide the sequence after it ends
      setTimeout(() => {
        setHackTextVisible(false); // Hide the sequence after 3 seconds (adjust as needed)
      }, 3000); // 3 seconds after sequence completion
    };

    // Run the sequence after the component mounts
    runHackerySequence();

    return () => {
      // Cleanup if the component unmounts
      setHackTextVisible(false);
    };
  }, []);

  return (
    <div>
      {/* Display the hacker sequence */}
      {hackTextVisible && (
        <div
          style={{
            color: 'lime', // Green terminal text
            fontFamily: 'monospace', // Monospace font for terminal style
            fontSize: '12px', // Smaller font size for a more terminal feel
            whiteSpace: 'pre-wrap', // Preserve line breaks
          }}
        >
          {/* Show the history of hackery sequence */}
          {history.map((line, index) => (
            <p key={index}>
              {line} {dotsCount > 0 && <span>{'.'.repeat(dotsCount)}</span>}
            </p>
          ))}

          {/* When sequence ends, show the final message */}
          {sequenceEnded && <p>Attempting to bypass security... (Sequence Complete)</p>}
        </div>
      )}
    </div>
  );
};

export default HackerSequence;
