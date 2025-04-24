import { createContext, useContext, ReactNode } from 'react';

const HackerIdContext = createContext<string | null>(null);

export const AuthKeyProvider = ({
  children,
  value,
}: {
  children: ReactNode;
  value: string;
}) => {
  return (
    <HackerIdContext.Provider value={value}>
      {children}
    </HackerIdContext.Provider>
  );
};

export const useHackerId = () => {
  const context = useContext(HackerIdContext);
  if (context === null) {
    throw new Error('useHackerId must be used within an AuthKeyProvider');
  }
  return context;
};