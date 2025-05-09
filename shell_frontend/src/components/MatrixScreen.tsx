import { useEffect, useRef, useState } from 'react';

const MatrixScreen = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [visible, setVisible] = useState(true);
  const [fadeOut, setFadeOut] = useState(false);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const fontSize = 16;
    const columns = Math.floor(canvas.width / fontSize);
    const drops = Array(columns).fill(1);

    const characters = 'アァカサタナハマヤャラワンABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#$%&*+-/<>';
    
    const draw = () => {
      ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.fillStyle = '#0F0';
      ctx.font = `${fontSize}px monospace`;

      for (let i = 0; i < drops.length; i++) {
        const char = characters[Math.floor(Math.random() * characters.length)];
        ctx.fillText(char, i * fontSize, drops[i] * fontSize);

        if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
          drops[i] = 0;
        }

        drops[i]++;
      }
    };

    const interval = setInterval(draw, 37);

    const fadeTimer = setTimeout(() => {
      setFadeOut(true);  // start fade out
    }, 5000); // wait 6.5 sec

    const removeTimer = setTimeout(() => {
      setVisible(false);  // actually remove
      clearInterval(interval);
    }, 11000); // 6.5 + 1.5 sec for fade

    return () => {
      clearInterval(interval);
      clearTimeout(fadeTimer);
      clearTimeout(removeTimer);
    };
  }, []);

  if (!visible) return null;

  return (
    <canvas
      ref={canvasRef}
      style={{
        display: 'block',
        position: 'fixed',  // ensure it covers everything
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        transition: 'opacity 6s ease',  // smooth fade over 1.5 sec
        opacity: fadeOut ? 0 : 1,  // fade out when fadeOut is true
        pointerEvents: 'none', // make sure it doesn't block clicks during fade
        zIndex: 9999, // keep it on top
      }}
    />
  );
};

export default MatrixScreen;
