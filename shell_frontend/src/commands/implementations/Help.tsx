
import { marked } from 'marked';
import helpMarkdown from '../../assets/help.md?raw'; // <- THIS IS KEY

const Help = () => {
  const html = marked.parse(helpMarkdown); // convert markdown to HTML

  return (
    <div>
      <div dangerouslySetInnerHTML={{ __html: html }} />
    </div>
  );
};

export default Help;
