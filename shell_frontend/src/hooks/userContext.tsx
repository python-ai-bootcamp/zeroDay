import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import {UserData} from "../types/types.tsx"

const UserContext = createContext<UserData | null>(null);

interface UserProviderProps {
    children: ReactNode;
}

export function UserProvider({ children }: UserProviderProps) {
  const [user, setUser] = useState<UserData | null>(null);

  useEffect(() => {
    fetch('http://127.0.0.1:8000/v2/user?hacker_id=concurrency_user_2')
        .then(res=>res.json())  
        .then((data: UserData) => setUser({...data,"name_nospace":data.name.replace(/ +/g,".")}))
        .catch(() => setUser(null));
  }, []);

  return (
    <UserContext.Provider value={user}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() : UserData | null{
  return useContext(UserContext);
}
