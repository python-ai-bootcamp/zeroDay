// commandRegistry.ts
import { CommandExecutor } from './types';
import Help from './implementations/Help';
import Status from './implementations/Status'; // import Status component
import GettingStarted from '../assets/getting_started.md?raw'; // import getting started markdown
import WizardFromMd from '../components/WizardFromMd';
import Lesson from './implementations/Lesson'; // import Lesson component
import Assignment from './implementations/Assignment'; // import Assignment component
import SCP from './implementations/SCP'; // import SCP component


const commandRegistry: Record<string, CommandExecutor> = {
  help: (_args, _setHistory) => {
    return <Help />;
  },
  getting_started: (_args, _setHistory, _setHidePrompt, _hidePrompt) => {

    return <WizardFromMd mdContent={GettingStarted} setHidePrompt={_setHidePrompt} />
  },
  clear: (_args, setHistory) => {
    setHistory([]); // clear history
    return; // no JSX returned
  },
  echo: (args, _setHistory) => {
    const text = args.join(' '); // join arguments with space
    return <div>{text}</div>; // return JSX element with text
  },
  status: (_args, _setHistory) => {
    return <Status />; // return Status component
  },
  lesson: (_args, _setHistory, _setHidePrompt) => {
    return <Lesson setHidePrompt={_setHidePrompt}/>; // placeholder for lesson command
  },
  assignment: (_args, _setHistory, _setHidePrompt) => {
    return <Assignment setHidePrompt={_setHidePrompt}/>; // placeholder for lesson command
  },
  scp: (_args, _setHistory) => {
    console.log('scp command executed with args:', _args); // log scp command execution
    return <SCP args={_args} />; // return SCP component with args


  }
};

export default commandRegistry;
