import React, { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";

interface Page {
  title: string;
  content: string;
}

const splitMarkdownIntoPages = (markdown: string): Page[] => {
  const sections = markdown.split(/^# /gm).filter(Boolean);
  return sections.map(section => {
    const [titleLine, ...rest] = section.split("\n");
    return {
      title: titleLine.trim(),
      content: rest.join("\n").trim()
    };
  });
};

export default function WizardFromMD({ mdContent }: { mdContent: string }) {
  const pages = splitMarkdownIntoPages(mdContent);
  const [currentPage, setCurrentPage] = useState(0);
  const [isComplete, setIsComplete] = useState(false); // Track completion status

  useEffect(() => {
    const handleKey = () => {
      if (currentPage < pages.length - 1) {
        setCurrentPage(prev => Math.min(prev + 1, pages.length - 1));
      } else {
        setIsComplete(true); // Set completion to true when the wizard is finished
      }
    };

    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [currentPage, pages.length]);

  const page = pages[currentPage];

  return (
    <div className="w-full h-screen bg-black text-white px-10 py-4 overflow-y-auto">
      <div className="text-sm font-mono space-y-2">
        {/* Display the terminal prompt with each new line */}
        <div className="text-gray-400">
          <span className="text-green-400">root@zeroDay$</span> {page.title}
        </div>
        <div className="prose prose-invert max-w-full text-left">
          <ReactMarkdown>{page.content}</ReactMarkdown>
        </div>

        {isComplete ? (
          <div className="text-gray-400">
            <span className="text-green-400">root@zeroDay$</span> End of wizard 🎉 The wizard is now complete.
          </div>
        ) : (
          <div className="text-gray-400">
            <span className="text-green-400">root@zeroDay$</span> Press any key to continue...
          </div>
        )}
      </div>
    </div>
  );
}
