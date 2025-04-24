import { createContext, useContext, ReactNode } from 'react';
import { useHackerId } from './authKeyContext';

type ApiUrlContextType = (endpoint: string) => string;

const ApiUrlContext = createContext<ApiUrlContextType | null>(null);

interface ApiUrlProviderProps {
  baseUrl: string;
  children: ReactNode;
}

export const ApiUrlProvider = ({ baseUrl, children }: ApiUrlProviderProps) => {
  const hackerId = useHackerId();

  const getApiUrl = (endpoint: string) => {
    const sep = endpoint.includes('?') ? '&' : '?';
    const hacker_id_authentication= hackerId==""? "": `${sep}hacker_id=${encodeURIComponent(hackerId)}`
    return `${baseUrl}${endpoint}${hacker_id_authentication}`;
  };

  return (
    <ApiUrlContext.Provider value={getApiUrl}>
      {children}
    </ApiUrlContext.Provider>
  );
};

export const useApiUrl = (): ApiUrlContextType => {
  const context = useContext(ApiUrlContext);
  if (!context) throw new Error('useApiUrl must be used within an ApiUrlProvider');
  return context;
};