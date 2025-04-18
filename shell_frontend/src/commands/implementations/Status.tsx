import React, { useState, useEffect} from 'react';
import {AssignmentStatus} from '../types'; // import AssignmentStatus type


export default function Status() {
    const [status, setStatus] = useState<AssignmentStatus | null>(null); // state to hold status message

  useEffect(() => {

      const fetchStatus = async () => {
        try {
          const response = await fetch('http://127.0.0.1:8000/v2/assignments/current_state?hacker_id=5r4xxv'); // replace with your actual endpoint
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