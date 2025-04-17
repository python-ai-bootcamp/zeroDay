import { useState, useEffect } from 'react';
import { marked } from 'marked';

const useMarkdown = (filePath) => {
  const [content, setContent] = useState('');

  useEffect(() => {
    const fetchMarkdown = async () => {
      try {
        const response = await fetch(filePath); // Fetch the markdown file from the provided path
        const text = await response.text();
        const html = marked.parse(text);
        setContent(html); // Store the HTML content
      } catch (error) {
        console.error('Error loading markdown:', error);
      }
    };

    fetchMarkdown();
  }, [filePath]);

  return content;
};

export default useMarkdown;
