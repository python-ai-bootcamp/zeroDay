import { useState, useEffect } from 'react';
import { marked } from 'marked';

const useMarkdown = (filePath:string) => {
  const [content, setContent] = useState('');

  useEffect(() => {
    const fetchMarkdown = async () => {
      try {
        const response = await fetch(filePath); // Fetch the markdown file from the provided path
        const text = await response.text();
        const html_result = marked.parse(text);
        if (html_result instanceof Promise) {
          html_result.then(setContent);
        } else {
          setContent(html_result);
        }
      } catch (error) {
        console.error('Error loading markdown:', error);
      }
    };

    fetchMarkdown();
  }, [filePath]);

  return content;
};

export default useMarkdown;
