// commandRegistry.ts
import { CommandExecutor } from './types';
import Help from './implementations/Help';
import Status from './implementations/Status'; // import Status component
import StatusAssignment from './implementations/StatusAssignment'; // import Status component
import GettingStarted from './implementations/GettingStarted'
import Lesson from './implementations/Lesson'; // import Lesson component
import Assignment from './implementations/Assignment'; // import Assignment component
import SCP from './implementations/SCP'; // import SCP component
import History from './implementations/History';
import GetSystemInfo from './implementations/GetSystemInfo.tsx'; 


const commandRegistry: Record<string, CommandExecutor> = {
  help: (_args, _triggerScroll, _setHistory) => {
    return <Help triggerScroll={_triggerScroll}/>;
  },
  getting_started: (_args, _triggerScroll, _setHistory, _setHidePrompt) => {
    return <GettingStarted setHidePrompt={_setHidePrompt} triggerScroll={_triggerScroll}/>;
  },
  clear: (_args, _triggerScroll, setHistory) => {
    setHistory([]); // clear history
    return; // no JSX returned
  },
  echo: (args, _triggerScroll, _setHistory) => {
    const text = args.join(' '); // join arguments with space
    return <div>{text}</div>; // return JSX element with text
  },
  status: (_args, _triggerScroll, _setHistory) => {
    return <Status triggerScroll={_triggerScroll}/>; // return Status component
  },
  status_assignment: (_args, _triggerScroll, _setHistory) => {
    return <StatusAssignment triggerScroll={_triggerScroll}/>; // return Status component
  },
  lesson: (_args, _triggerScroll, _setHistory, _setHidePrompt) => {
    return <Lesson setHidePrompt={_setHidePrompt} triggerScroll={_triggerScroll}/>; // placeholder for lesson command
  },
  assignment: (_args, _triggerScroll, _setHistory, _setHidePrompt) => {
    return <Assignment setHidePrompt={_setHidePrompt} triggerScroll={_triggerScroll}/>; // placeholder for lesson command
  },
  scp: (_args, _triggerScroll, _setHistory, _setHidePrompt) => {
    console.log('scp command executed with args:', _args); // log scp command execution
    return <SCP args={_args} setHidePrompt={_setHidePrompt} triggerScroll={_triggerScroll}/>; // return SCP component with args
  },
  history: (_args, _triggerScroll, _setHistory, _setHidePrompt, _currentHistory) => {
    console.log("history command received following array::\n",_currentHistory)
    return <History args={_currentHistory} triggerScroll={_triggerScroll}/>; // print history
  },
  get_system_info: (_args, _triggerScroll, _setHistory, _setHidePrompt, _currentHistory) => {
    console.log("history command received following array::\n",_currentHistory)
    return <GetSystemInfo setHidePrompt={_setHidePrompt} triggerScroll={_triggerScroll}/>; // print history
  }
};

export default commandRegistry;
