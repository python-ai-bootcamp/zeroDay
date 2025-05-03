import { useEffect, useState } from 'react';

const History = ({ args, triggerScroll }: { args: string[]; triggerScroll: () => void }) => {
  const [html, setHtml] = useState<string>('');
  console.log("History:: args=",args)
  useEffect(() => {
    const displayHistory = async () => {
      //const historyHtml=args
      //  .map((command, index)=>`<div><pre>${String(index).padStart(4, ' ')}  ${command?.replace(/^ */,"")}</pre></div>`)
      //  .slice(0, -1)
      //  .join("")       
      const historyHtml=args
          .map((command, index)=>`<div><pre>${String(index).padStart(4, ' ')}  ${command?.replace(/^ */,"")}</pre></div>`)
          .slice(1)
          .join("")       
      console.log("Help:: historyHtml=",historyHtml)
      setHtml(historyHtml);
    };
    displayHistory();
  }, []);
  triggerScroll()
  return (
    <div>
      <div dangerouslySetInnerHTML={{ __html: html }} />
    </div>
  );
};

export default History;
