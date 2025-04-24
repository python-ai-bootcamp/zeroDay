import React, { useState, useEffect} from 'react';
import {AssignmentStatus} from '../types'; // import AssignmentStatus type
import WizardFromMD from '../../components/WizardFromMd';
import { useUser } from '../../hooks/userContext'; 



export default function Lesson({ setHidePrompt }: { setHidePrompt: React.Dispatch<React.SetStateAction<boolean>>}) {
  const [status, setStatus] = useState<AssignmentStatus | null>(null); // state to hold status message
  const [lessonContent, setLessonContent] = useState<string>(''); // state to hold status message
  const user = useUser();

  useEffect(() => {

      const fetchStatus = async () => {
        try {
          const response = await fetch(`http://127.0.0.1:8000/v2/assignments/current_state?hacker_id=${user["hacker_id"]}`); // replace with your actual endpoint
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

      fetchStatus();
    
  }, []);

  useEffect(() => {
    const loadLesson = async () => {
      if (!status?.assignment_id) return;

      try {
        const lessonMarkdown = await import(`../../assets/lesson_${status.assignment_id}.md?raw`);
        setLessonContent(lessonMarkdown.default);
      } catch (error) {
        console.error(`Error loading lesson_${status.assignment_id}.md:`, error);
      }
    };

    loadLesson();
  }, [status]);

    return(
        <div>
            {lessonContent && (
              <WizardFromMD mdContent={lessonContent} setHidePrompt={setHidePrompt} />
            )}
        </div>
    )
}