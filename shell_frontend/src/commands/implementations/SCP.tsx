import React, { useState, useRef, useEffect} from 'react';
import JSZip from 'jszip';
import { useApiUrl } from "../../hooks/baseUrlContext.tsx";
import StatusAssignment from './StatusAssignment.tsx';
declare module 'react' {
  interface InputHTMLAttributes<T> extends React.HTMLAttributes<T> {
    webkitdirectory?: string;
    directory?: string;
  }
}
export default function SCP({ args, setHidePrompt, triggerScroll }: { args: string[]; setHidePrompt: React.Dispatch<React.SetStateAction<boolean>>; triggerScroll: ()=>void }) {
    setHidePrompt(true);
    const [packingProgressDisplay, setPackingProgressDisplay] = useState<number>(-1); // state to hold scp content
    const [uploadProgressDisplay, setUploadProgressDisplay] = useState<number>(-1); // state to hold scp content
    const [testingProgressDisplay, setTestingProgressDisplay] = useState<number>(-1); // state to hold scp content
    const [canSubmit, setCanSubmit] = useState<string>(""); // state to hold scp content
    const [cantSubmitExplenation, setCantSubmitExplenation] = useState<string>(""); // state to hold scp content
    const fileInputRef = useRef<HTMLInputElement>(null);
    const current_status_url=useApiUrl()("/v2/assignments/current_state")
    const submit_assignment_url_template=useApiUrl()("/v2/assignments/$${{ASSIGNMENT_ID}}$$/submission")
    const test_status_url=useApiUrl()("/v2/assignments/submission/test_status")
    const check_if_user_viewed_lesson_url=useApiUrl()("/v2/analytics/event/assignment_start_time")
    const isPackingComplete = useRef<boolean>(false);
    const isUploadComplete = useRef<boolean>(false);
    const maxNotBreached = useRef<boolean>(true);
    const [isTestingComplete, setIsTestingComplete] = useState<boolean>(false);
    const asyncWait = function wait(ms:number) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

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
        
        const pollPacking = async (current: number) => {
          setPackingProgressDisplay(current);
          console.log(`pollPacking called with ${current}`);
          await asyncWait(1000)
          if (!(isPackingComplete.current)) {
              setPackingProgressDisplay(current + 1);
              await pollPacking(current + 1);
          } else {
              console.log("Packing completed!");
              setHidePrompt(false);
          }
        };
        pollPacking(0);

        const blob = await createZip(files)
        isPackingComplete.current=true;

        const formData = new FormData();
        formData.append('zip_file', blob, 'directory.zip');
        
        try {
            const user_status_res= await fetch(current_status_url)
              .then(res=>res.json())
            //if(user_status_res.submission_id>user_status_res.max_submission_id){
            //  console.log(`Used exceeded max submissions allowed for this task (submission_attempts=${user_status_res.submission_id-1}, max_allowed=${user_status_res.max_submission_id})`)
            //  isUploadComplete.current=true
            //  setIsTestingComplete(true)
            //  maxNotBreached.current=false
            //  setHidePrompt(false);
            //  triggerScroll();
            //}else{
              const submit_assignment_url=submit_assignment_url_template.replace("$${{ASSIGNMENT_ID}}$$",user_status_res.assignment_id)
              console.log("submitting file to following url::", submit_assignment_url)
              const res = await fetch(submit_assignment_url, {
                  method: 'POST',
                  body: formData,
              });
      
              const result = await res.json();
              console.log('Upload successful:', result);
              isUploadComplete.current=true
            //}
        } catch (error) {
            console.error('Upload failed:', error);
        }
    };

    const isTestingCompleted = async function(){
        const test_status_res=await fetch(test_status_url)
          .then(res=>res.json())
          .then(resBody=>resBody.status)
        if (test_status_res!="IN_PROGRESS"){
            setIsTestingComplete(true)
            return true
        }else{
            return false
        }        
    }

    const triggerDirectoryPicker = async () => {
        
        if (fileInputRef.current) {
            fileInputRef.current.click();
        }
        const pollPackingNoUiModification = async (current: number) => {
          console.log(`pollPackingNoUiModification called with ${current}`);
          await asyncWait(1000)
          if (!(isPackingComplete.current)) {
              await pollPackingNoUiModification(current + 1);
          } else {
              console.log("Packing completed!");
              setHidePrompt(false);
          }
        };
        const pollUpload = async (current: number) => {
            setUploadProgressDisplay(current);
            console.log(`pollUpload called with ${current}`);
            await asyncWait(75)
            if (!(isUploadComplete.current)) {
                setUploadProgressDisplay(current + 1);
                await pollUpload(current + 1);
            } else {
                console.log("Packing completed!");
                setHidePrompt(false);
            }
        };
        const pollTesting = async (current: number) => {
            setTestingProgressDisplay(current);
            console.log(`pollTesting called with ${current}`);
            const completed = await isTestingCompleted();            
            //await asyncWait(125)     
            await asyncWait(1500)
            if (!completed) {
                setTestingProgressDisplay(current + 1);
                await pollTesting(current + 1);
            } else {
                console.log("Packing completed!");
                setHidePrompt(false);
            }
        };   
        await pollPackingNoUiModification(0);
        setHidePrompt(true);
        triggerScroll();
        await pollUpload(0);
        setHidePrompt(true);
        triggerScroll();
        await pollTesting(0);
        setHidePrompt(false);
        triggerScroll();
    };

    const triggerBlockSubmission =  () => {
      console.log("USER CANNOT SUBMIT BECAUSE HE DID NOT VIEW ASSIGNMENT YET")
      setHidePrompt(false);
      triggerScroll();
    }

    useEffect(() => {
        fetch(check_if_user_viewed_lesson_url)
          .then(res=>res.json())
          .then(resBody=>{
            if (resBody.status=="OK"){
              fetch(current_status_url)
                .then(res=>res.json())
                .then(res_body=>{
                  if(res_body.submission_id>res_body.max_submission_id){
                    console.log(`User exceeded max submissions allowed for this task (submission_attempts=${res_body.submission_id-1}, max_allowed=${res_body.max_submission_id})`)
                    isUploadComplete.current=true
                    setIsTestingComplete(true)
                    maxNotBreached.current=false
                    setHidePrompt(false);
                    triggerScroll();
                  }else{
                    setCanSubmit("Please Select Assignment Files For Upload...")
                    triggerDirectoryPicker();
                  }                
                })
            }else{
              setCanSubmit("ERROR:: User Can Not Submit Assignment Before Viewing Lesson")
              setCantSubmitExplenation("Please execute 'lesson' command.\nOnce finished going over learning matirial, execute 'assignment' command.\nThen Try submitting using 'scp' command again.")
              triggerBlockSubmission();
              setHidePrompt(false);
              triggerScroll();
            }
          })
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
        <div>{(!cantSubmitExplenation)?(canSubmit):(<div><pre className="text-red-500">{canSubmit}</pre><pre>{cantSubmitExplenation}</pre></div>)}</div>
        {(packingProgressDisplay!=-1)?<div>Assignment Packing in Progress:: <pre style={{ display: 'inline' }}>{".".repeat(packingProgressDisplay).match(/.{1,120}/g)?.join("\n")}</pre>{(isPackingComplete.current)?<label> [ COMPLETE ]</label>:null}</div>:null}
        {(uploadProgressDisplay!=-1)?<div>Assignment Upload in Progress::   <pre style={{ display: 'inline' }}>{".".repeat(uploadProgressDisplay).match(/.{1,120}/g)?.join("\n")}</pre>{(isUploadComplete.current)?<label> [ COMPLETE ]</label>:null}</div>:null}
        {(testingProgressDisplay!=-1)?<div>Assignment Testing in Progress:: <pre style={{ display: 'inline' }}>{".".repeat(testingProgressDisplay).match(/.{1,120}/g)?.join("\n")}</pre>{(isTestingComplete)?<label> [ COMPLETE ]</label>:null}</div>:null}
        {(isTestingComplete&&maxNotBreached.current)?<StatusAssignment triggerScroll={triggerScroll}/>:null}
        {(isTestingComplete&&(!(maxNotBreached.current)))?<div className="text-red-500">ERROR:: User breached max allowed submissions for assignment (execute 'status' command for details)</div>:null}
      </div>

    );
}