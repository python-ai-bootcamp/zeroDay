import React, { useState, useEffect} from 'react';
import {AssignmentStatus} from '../types'; // import AssignmentStatus type
import WizardFromMD from '../../components/WizardFromMd';
import { useApiUrl } from "../../hooks/baseUrlContext.tsx";


export default function Assignment({ setHidePrompt , triggerScroll }: { setHidePrompt: React.Dispatch<React.SetStateAction<boolean>>; triggerScroll: () => void}) {
  const [status, setStatus] = useState<AssignmentStatus | null>(null); 
  const [assignmentContent, setAssignmentContent] = useState<string>(''); 
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

      fetchStatus();
    
  }, []);

  useEffect(() => {
    if (!status?.assignment_id) return;
    const loadAssignment = async () => {
      try {
        const response = await fetch(`/static/assignment/${status.assignment_id}/assignment_${status.assignment_id}.md`);
        if (!response.ok) {
          throw new Error(`Failed to fetch assignment markdown. Status: ${response.status}`);
        }
        const markdownText = await response.text();
        setAssignmentContent(markdownText);
      } catch (error) {
        console.error(`Error loading assignment markdown:`, error);
      }
    };
    const downloadAssignmentZip = () => {
        try{
            const link = document.createElement("a");
            link.href = `/static/assignment/${status.assignment_id}/assignment_${status.assignment_id}.zip`;
            link.download = `assignment_${status.assignment_id}.zip`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }catch (error) {
            console.error(`Error downloading assignment_${status.assignment_id}.md:`, error);
          }
      };

    loadAssignment();
    downloadAssignmentZip();
  }, [status]);


    return(
        <div>
            {assignmentContent && (
              <WizardFromMD mdContent={assignmentContent} setHidePrompt={setHidePrompt} triggerScroll={triggerScroll}/>
            )}
        </div>
    )
}