import React, { useState, useEffect} from 'react';
import WizardFromMD from '../../components/WizardFromMd.tsx';

export default function Lesson({ setHidePrompt , triggerScroll }: { setHidePrompt: React.Dispatch<React.SetStateAction<boolean>>; triggerScroll: () => void}) {
  const [gettingStartedContent, setGettingStartedContent] = useState<string>(''); // state to hold status message
    useEffect(() => {
      const loadLesson = async () => {
        try {
          const response = await fetch(`/static/gettingStarted/getting_started.md`);
          if (!response.ok) {
            throw new Error(`Failed to fetch getting_started markdown. Status: ${response.status}`);
          }
          const markdownText = await response.text();
          setGettingStartedContent(markdownText);
        } catch (error) {
          console.error(`Error loading getting_started.md:`, error);
        }
      };
      setHidePrompt(true);
      loadLesson();
    }, [gettingStartedContent]);
    return(
        <div>
            {gettingStartedContent && (
              <WizardFromMD mdContent={gettingStartedContent} setHidePrompt={setHidePrompt} triggerScroll={triggerScroll}/>
            )}
        </div>
    )
}