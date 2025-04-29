import { useEffect, useState } from 'react';

const Help = ({ args }: { args: string[]}) => {
  const [html, setHtml] = useState<string>('');
  console.log("Help:: args=",args)
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

  return (
    <div>
      <div dangerouslySetInnerHTML={{ __html: html }} />
    </div>
  );
};

export default Help;
