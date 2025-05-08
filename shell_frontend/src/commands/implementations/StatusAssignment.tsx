import { useState, useEffect} from 'react';
import {AssignmentStatus} from '../types'; // import AssignmentStatus type
import { useApiUrl } from "../../hooks/baseUrlContext.tsx";

type JSONValue =
  | string
  | number
  | boolean
  | null
  | { [key: string]: JSONValue }
  | JSONValue[];

type JsonRendererProps = {
  data: JSONValue;
  level?: number;
};

const JsonRenderer: React.FC<JsonRendererProps> = ({ data, level = 0 }) => {
  if (typeof data === 'object' && data !== null) {
    const isArray = Array.isArray(data);
    return (
      <div style={{ paddingLeft: level * 20 }}>
        {isArray ? '[' : '{'}
        {Object.entries(data).map(([key, value], index) => (
          <div key={index}>
            {!isArray && <span style={{ color: 'orange' }}>{key}: </span>}
            <JsonRenderer data={value} level={level + 1} />
          </div>
        ))}
        {isArray ? ']' : '}'}
      </div>
    );
  } else if (typeof data === 'string') {
    if(data.startsWith("http")){
    return (
        <a
          href={data}
          target="_blank"
          rel="noopener noreferrer"
          style={{ color: 'lightblue', textDecoration: 'underline' }}
        >
          {data
            .replace(/.*submitted_tasks_browser/,"open")
            .replace("/","_assignment_#")
            .replace("/","_submission_#")
            .replace("/","_task_#")
            }
        </a>
      );
    } else {
      return (
        <span style={{ color: typeof data === 'string' ? 'brown' : 'gray' }}>
          '{String(data)}'
        </span>
      ); 
    }
  } else {
    return (
      <span style={{ color: typeof data === 'number' ? 'lightgreen' : 'gray' }}>
        {String(data)}
      </span>
    );
  }
};
export default function Status({triggerScroll}: { triggerScroll: () => void}) {
  const [status, setStatus] = useState<AssignmentStatus | null>(null); // state to hold status message
  const url=useApiUrl()("/v2/assignments/submission/last_result")
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
      <JsonRenderer data={status} />
    )}
  </div>
    )
}