import React, { useState, useRef, useEffect} from 'react';
import JSZip from 'jszip';
import { useApiUrl } from "../../hooks/baseUrlContext.tsx";

export default function SCP({ args }: { args: string[]}) {

    const [scpContent, setScpContent] = useState<string>(''); // state to hold scp content
    const fileInputRef = useRef<HTMLInputElement>(null);
    const current_status_url=useApiUrl()("/v2/assignments/current_state")
    const submit_assignment_url_template=useApiUrl()("/v2/assignments/$${{ASSIGNMENT_ID}}$$/submission")
    

    async function createZip(files: FileList) { // will return only the subdirectory under assignment folder and not the top folder itself
        const zip = new JSZip();
        for (const file of files) {
            const relativePath = file.webkitRelativePath || file.name;
            const pathParts = relativePath.split('/');
            if (pathParts.length > 1) {
                const subfolderPath = pathParts.slice(1).join('/');
                const content = await file.arrayBuffer();
                zip.file(subfolderPath, content);
            }
        }
        const zipData = await zip.generateAsync({ type: "blob" });
        return zipData;
    }

    const handleDirectoryUpload = async (files: FileList | null) => {
        if (!files) return;

        const blob = await createZip(files)

        const formData = new FormData();
        formData.append('zip_file', blob, 'directory.zip');
        
        try {
          const user_status_res= await fetch(current_status_url)
            .then(res=>res.json())
          const submit_assignment_url=submit_assignment_url_template.replace("$${{ASSIGNMENT_ID}}$$",user_status_res.assignment_id)
          console.log("submitting file to following url::", submit_assignment_url)
          const res = await fetch(submit_assignment_url, {
            method: 'POST',
            body: formData,
          });
    
          const result = await res.json();
          console.log('Upload successful:', result);
          setScpContent('Upload successful!');
        } catch (error) {
          console.error('Upload failed:', error);
          setScpContent('Upload failed.');
        }
      };
    const triggerDirectoryPicker = () => {
        if (fileInputRef.current) {
          fileInputRef.current.click();
        }
      };

  useEffect
  (() => {
    triggerDirectoryPicker()
  }, [args]);

    return (
      <div>
        <input
          type="file"
          ref={fileInputRef}
          style={{ display: 'none' }}
          webkitdirectory="true"
          directory=""
          multiple
          onChange={(e) => handleDirectoryUpload(e.target.files)}
        />
      </div>

    );
}