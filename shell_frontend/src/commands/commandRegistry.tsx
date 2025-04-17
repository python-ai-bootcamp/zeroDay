// commandRegistry.ts
import { CommandExecutor } from './types';
import Help from './implementations/Help';
import GettingStarted from '../assets/getting_started.md?raw'; // import getting started markdown
import WizardFromMd from '../components/WizardFromMd';

const commandRegistry: Record<string, CommandExecutor> = {
  help: (_args, _setHistory) => {
    return <Help />;
  },
  getting_started: (_args, _setHistory) => {
    return <WizardFromMd mdContent={GettingStarted}/>; // return JSX element for getting started
  },
  clear: (_args, setHistory) => {
    setHistory([]); // clear history
    return; // no JSX returned
  },
  echo: (args, _setHistory) => {
    const text = args.join(' '); // join arguments with space
    return <div>{text}</div>; // return JSX element with text
  }
};

export default commandRegistry;
