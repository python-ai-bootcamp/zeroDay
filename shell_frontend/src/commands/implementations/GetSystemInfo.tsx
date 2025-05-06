import { useEffect, useState } from 'react';

function generateRandomPercentage() {
  const randomPercentage = Math.floor(Math.random() * 101);
  return `${randomPercentage}%`;
}

function generateRandomNumber() {
  return Math.floor(Math.random() * 10) + 5;
}

const data = [
  { key: 'Analyzing CPU Utilization:', numberOfDots: generateRandomNumber(), status: '[TEST COMPLETED]' },
  { key: 'CPU Utilization Result:', numberOfDots: 0, status: generateRandomPercentage() },
  { key: 'Check Memory For Corruption:', numberOfDots: generateRandomNumber(), status: '[TEST COMPLETED]' },
  { key: 'Memory Status Result:', numberOfDots: 0, status: 'OK' },
  { key: 'Check Network Speed:', numberOfDots: generateRandomNumber(), status: '[TEST COMPLETED]' },
  { key: 'Network Speed Result:', numberOfDots: 0, status: 'Nominal' },
  { key: 'Check HardDrive IO:', numberOfDots: generateRandomNumber(), status: '[TEST COMPLETED]' },
  { key: 'HardDrive IO Result:', numberOfDots: 0, status: 'Within Acceptable Range' },
  { key: 'Evaluate Random Generator Enthropy Levels:', numberOfDots: generateRandomNumber(), status: '[TEST COMPLETED]' },
  { key: 'Entrophy Peak:', numberOfDots: 0, status: generateRandomPercentage() },
];

const DotStatusList = ({
  setHidePrompt,
  triggerScroll,
}: {
  setHidePrompt: React.Dispatch<React.SetStateAction<boolean>>;
  triggerScroll: () => void;
}) => {
  const [lines, setLines] = useState(
    data.map(() => ({ dots: 0, showStatus: false }))
  );

  useEffect(() => {
    setHidePrompt(true);
    let lineIndex = 0;

    const animateLine = () => {
      if (lineIndex >= data.length) return;

      const { numberOfDots } = data[lineIndex];
      let dotCount = 0;

      if (numberOfDots === 0) {
        // immediately show status for 0 dots
        setLines((prev) => {
          const updated = [...prev];
          updated[lineIndex] = { ...updated[lineIndex], showStatus: true };
          return updated;
        });

        if (lineIndex === data.length - 1) {
          setHidePrompt(false);
          triggerScroll();
        }

        setTimeout(() => {
          lineIndex++;
          animateLine();
        }, 500);

        return;
      }

      const dotInterval = setInterval(() => {
        dotCount++;

        setLines((prev) => {
          const updated = [...prev];
          updated[lineIndex] = { ...updated[lineIndex], dots: dotCount };
          return updated;
        });

        if (dotCount === numberOfDots) {
          clearInterval(dotInterval);

          setTimeout(() => {
            setLines((prev) => {
              const updated = [...prev];
              updated[lineIndex] = { ...updated[lineIndex], showStatus: true };
              return updated;
            });

            if (lineIndex === data.length - 1) {
              setHidePrompt(false);
              triggerScroll();
            }

            setTimeout(() => {
              lineIndex++;
              animateLine();
            }, 500);
          }, 500);
        }
      }, 50);
    };

    animateLine();
  }, []);

  return (
    <div style={{ fontFamily: 'monospace', whiteSpace: 'pre' }}>
      {data.map((item, i) => {
        const dots = '.'.repeat(lines[i]?.dots || 0);
        const spaceBetween = ' '.repeat(item.numberOfDots - dots.length);
        const statusText = lines[i]?.showStatus ? item.status : '';
        return (
          <div key={i}>
            {lines[i].dots > 0 || lines[i].showStatus
              ? `${item.key.padEnd(25, ' ')} ${dots}${spaceBetween} ${statusText}`
              : ''}
          </div>
        );
      })}
    </div>
  );
};

export default DotStatusList;
