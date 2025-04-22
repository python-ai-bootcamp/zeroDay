import React, { useState, useRef, useEffect} from 'react';
import JSZip from 'jszip';

export default function SCP({ args }: { args: string[]}) {

    const [scpContent, setScpContent] = useState<string>(''); // state to hold scp content
    const fileInputRef = useRef<HTMLInputElement>(null);
    
    const handleDirectoryPick = async () => {
      try {
        const dirHandle = await window.showDirectoryPicker();
        const files: File[] = [];
    
        for await (const [name, handle] of dirHandle.entries()) {
          if (handle.kind === 'file') {
            const file = await handle.getFile();
            file.webkitRelativePath = name; // optional: mimic relative path
            files.push(file);
          }
        }
    
        handleDirectoryUpload(files as any); // pass as FileList-like
      } catch (err) {
        console.error('User cancelled or error occurred:', err);
      }
    };

    const handleDirectoryUpload = async (files: FileList | null) => {
        if (!files) return;
        
        const zip = new JSZip();
        
        // Validate and add files to zip
        for (const file of Array.from(files)) {
          // Add any validation here, e.g., file.type, name, size, etc.
          zip.file(file.webkitRelativePath, file);
        }
    
        const blob = await zip.generateAsync({ type: 'blob' });
    
        // Upload the zip to your backend
        const formData = new FormData();
        formData.append('file', blob, 'directory.zip');
    
        try {
          const res = await fetch('http://localhost:8000/upload', {
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
        onChange={(e) => handleDirectoryPick(e.target.files)}
      />
    </div>

    );
}