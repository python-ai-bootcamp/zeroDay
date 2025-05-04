import React, { useState, useEffect} from 'react';
import {AssignmentStatus} from '../types'; // import AssignmentStatus type
import WizardFromMD from '../../components/WizardFromMd';
import { useApiUrl } from "../../hooks/baseUrlContext.tsx";

export default function Lesson({ setHidePrompt , triggerScroll }: { setHidePrompt: React.Dispatch<React.SetStateAction<boolean>>; triggerScroll: () => void}) {
  const [status, setStatus] = useState<AssignmentStatus | null>(null); // state to hold status message
  const [lessonContent, setLessonContent] = useState<string>(''); // state to hold status message
  const url=useApiUrl()("/v2/assignments/current_state")
  useEffect(() => {

      const fetchStatus = async () => {
        try {
          const response = await fetch(url); // replace with your actual endpoint
          if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
          }
          const data: AssignmentStatus = await response.json();
          console.log(data); // Log the response data
          setStatus(data);
        } catch (error) {
          console.error('Error fetching user data:', error);
        }
      };
      setHidePrompt(true);
      fetchStatus();
    
  }, []);

  useEffect(() => {
    const loadLesson = async () => {
      if (!status?.assignment_id) return;
      try {
        const response = await fetch(`/static/lesson/${status.assignment_id}/lesson_${status.assignment_id}.md`);
        if (!response.ok) {
          throw new Error(`Failed to fetch lesson markdown. Status: ${response.status}`);
        }
        const markdownText = await response.text();
        setLessonContent(markdownText);
      } catch (error) {
        console.error(`Error loading lesson_${status.assignment_id}.md:`, error);
      }
    };
    loadLesson();
  }, [status]);

    return(
        <div>
            {lessonContent && (
              <WizardFromMD mdContent={lessonContent} setHidePrompt={setHidePrompt} triggerScroll={triggerScroll}/>
            )}
        </div>
    )
}