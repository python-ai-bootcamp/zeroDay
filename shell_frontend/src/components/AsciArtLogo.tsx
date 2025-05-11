import { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';


//https://budavariam.github.io/asciiart-text/ ansi shado larry 3d lean Slant Relief Sub-Zero
// used Zub-Zero then replaced all \ with \\
const asciiArt = `
             ______     ______     ______     ______        _____     ______     __  __    
            /\\___  \\   /\\  ___\\   /\\  == \\   /\\  __ \\      /\\  __ \\  /\\  __ \\   /\\ \\_\\ \\   
            \\/_/  /__  \\ \\  __\\   \\ \\  __<   \\ \\ \\/\\ \\     \\ \\ \\/\\ \\ \\ \\  __ \\  \\ \\____ \\  
              /\\_____\\  \\ \\_____\\  \\ \\_\\ \\_\\  \\ \\_____\\     \\ \\____/  \\ \\_\\ \\_\\  \\/\\_____\\ 
              \\/_____/   \\/_____/   \\/_/ /_/   \\/_____/      \\/____/   \\/_/\\/_/   \\/_____/ 
                                                                                                               
`;


export default function ZeroDayAscii() {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const totalDuration = 7000;
    const timer = setTimeout(() => setVisible(false), totalDuration);
    return () => clearTimeout(timer);
  }, []);

  if (!visible) return null;

  const overlay = (
    <>
      <style>{`
        @keyframes fadeInOut {
          0% { opacity: 0; }
          28.5% { opacity: 1; }
          71.5% { opacity: 1; }
          100% { opacity: 0; }
        }
      `}</style>
      <div
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100vw',
          height: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          pointerEvents: 'none',
          zIndex: 9999,
        }}
      >
        <pre
          style={{
            color: '#00ff99',
            fontFamily: 'monospace',
            fontSize: '0.75rem',
            whiteSpace: 'pre-wrap',
            animation: 'fadeInOut 7s forwards',
            textShadow: `
              0 0 5px #00ff99,
              0 0 10px #00ff99,
              0 0 20px #00ff99,
              0 0 40px #00ff99
            `,
          }}
        >
          {asciiArt}
        </pre>
      </div>
    </>
  );

  return createPortal(overlay, document.body);
}
