import React, { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import rehypeRaw from "rehype-raw";

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

export default function WizardFromMD({ mdContent, setHidePrompt, triggerScroll }: { mdContent: string; setHidePrompt: React.Dispatch<React.SetStateAction<boolean>> ; triggerScroll: () => void}) {
  const pages = splitMarkdownIntoPages(mdContent);
  const [currentPage, setCurrentPage] = useState(0);
  const [isComplete, setIsComplete] = useState(false); // Track completion status
  
  useEffect(() => {
    const handleKey = () => {
      if (currentPage < pages.length - 1) {
        setCurrentPage(prev => Math.min(prev + 1, pages.length - 1));
        setHidePrompt(true); // Hide prompt when moving to the next page
      } else {
        setIsComplete(true); // Set completion to true when the wizard is finished
        setHidePrompt(false); // Show prompt again after completion
      }
      triggerScroll()
    };

    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [currentPage, pages.length]);

  const page = pages[currentPage];

  if (isComplete){
    triggerScroll()
    return null; // 🔥 Early return if complete
  }

  return (
    <div className="w-full bg-black text-green-500 px-10 py-4 overflow-y-auto">
      <div className="text-sm font-mono space-y-2">
        <div className="text-gray-200 font-bold">{page.title}</div>
        <div className="prose prose-invert max-w-full text-left">
          <ReactMarkdown rehypePlugins={[rehypeRaw]}>{page.content}</ReactMarkdown>
        </div>
        <div className="text-gray-400">Press any key to continue...</div>
      </div>
    </div>
  );
}
