import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import {UserData} from "../types/types.tsx"
import { useApiUrl } from "./baseUrlContext.tsx";

const UserContext = createContext<UserData | null>(null);

interface UserProviderProps {
    children: ReactNode;
}

export function UserProvider({ children }: UserProviderProps) {
  const [user, setUser] = useState<UserData | null>(null);
  const url=useApiUrl()("/v2/user")
  console.log("UserProvider:: url=",url)
  useEffect(() => {
    fetch(url)
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
