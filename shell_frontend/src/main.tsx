import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './styles/index.css'
import AutoClipboard from './components/Clipboard.tsx'
import Terminal from './components/Terminal.tsx'
import { UserProvider } from './hooks/userContext';
import { AuthKeyProvider, useHackerId } from './hooks/authKeyContext';
import { ApiUrlProvider } from './hooks/baseUrlContext.tsx';
import MatrixScreen from './components/MatrixScreen.tsx';
import ZeroDayAscii from './components/AsciArtLogo.tsx';

const AppRouter = () => {
  const hackerId = useHackerId();
  return (
    <>
      {hackerId === "" && <MatrixScreen />}
      {hackerId === "" && <ZeroDayAscii />} 
      <Terminal />
    </>
  );
};
createRoot(document.getElementById('root')!).render(
  <StrictMode>
    {/* IMPORTANT NOTE:: rmemeber to change to 5r4xxv before commiting so micha won't suffer the consequence of tal using concurrency_user_2*/}
    <AuthKeyProvider value="concurrency_user_2">
      <ApiUrlProvider baseUrl="http://127.0.0.1:8000">
        <UserProvider>
          <AutoClipboard />
          <AppRouter />
        </UserProvider>
      </ApiUrlProvider>
    </AuthKeyProvider>
  </StrictMode>,
)
