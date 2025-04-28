
import { marked } from 'marked';
import { useEffect, useState } from 'react';

const Help = () => {
  const [html, setHtml] = useState<string>('');
  useEffect(() => {
    const fetchHelpMarkdown = async () => {
      const response = await fetch('/static/help/Help.md');
      const markdownText = await response.text();
      setHtml(marked.parse(markdownText, { async: false }));
    };

    fetchHelpMarkdown();
  }, []);

  return (
    <div>
      <div dangerouslySetInnerHTML={{ __html: html }} />
    </div>
  );
};

export default Help;
