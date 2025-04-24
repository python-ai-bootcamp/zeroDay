import React, { useState, useEffect} from 'react';
import {AssignmentStatus} from '../types'; // import AssignmentStatus type
import WizardFromMD from '../../components/WizardFromMd';
import { useApiUrl } from "../../hooks/baseUrlContext.tsx";


export default function Assignment({ setHidePrompt }: { setHidePrompt: React.Dispatch<React.SetStateAction<boolean>>}) {
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
    const loadAssignment = async () => {
      if (!status?.assignment_id) return;
      try {
        const assignmentMarkdown = await import(`../../assets/assignment_${status.assignment_id}.md?raw`);
        setAssignmentContent(assignmentMarkdown.default);
      } catch (error) {
        console.error(`Error loading assignment_${status.assignment_id}.md:`, error);
      }
    };
    const downloadAssignmentZip = () => {
        if (!status?.assignment_id) return;
        try{
            const link = document.createElement("a");
            link.href = `/assignment_${status.assignment_id}.zip`;
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
              <WizardFromMD mdContent={assignmentContent} setHidePrompt={setHidePrompt} />
            )}
        </div>
    )
}