import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './styles/index.css'
import AutoClipboard from './components/Clipboard.tsx'
import Terminal from './components/Terminal.tsx'
import { UserProvider } from './hooks/userContext';
import { AuthKeyProvider } from './hooks/authKeyContext';
import { ApiUrlProvider } from './hooks/baseUrlContext.tsx';


createRoot(document.getElementById('root')!).render(
  <StrictMode>
    {/* IMPORTANT NOTE:: rmemeber to change to 5r4xxv before commiting so micha won't suffer the consequence of tal using concurrency_user_2*/}
    <AuthKeyProvider value="concurrency_user_2">
      <ApiUrlProvider baseUrl="http://127.0.0.1:8000">
        <UserProvider>
          <AutoClipboard />
          <Terminal />
        </UserProvider>
      </ApiUrlProvider>
    </AuthKeyProvider>
  </StrictMode>,
)
