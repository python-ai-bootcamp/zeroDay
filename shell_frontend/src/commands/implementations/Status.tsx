import { useState, useEffect} from 'react';
import {AssignmentStatus} from '../types'; // import AssignmentStatus type
import { useApiUrl } from "../../hooks/baseUrlContext.tsx";

export default function Status({triggerScroll}: { triggerScroll: () => void}) {
  const [status, setStatus] = useState<AssignmentStatus | null>(null); // state to hold status message
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
          triggerScroll();
        } catch (error) {
          console.error('Error fetching user data:', error);
        }
      };

      fetchStatus();
    
  }, []);
    return(
        <div>
    {status && (
      <div>
        <p>Assignment ID: {status.assignment_id}</p>
        <p>Submission ID: {status.submission_id}</p>
        <p>Max Submission ID: {status.max_submission_id}</p>
      </div>
    )}
  </div>
    )
}