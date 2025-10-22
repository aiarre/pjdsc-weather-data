import { useEffect, useState } from "react";

export default function useLocalStorage(key, initialValue) {
  const [value, setValue] = useState(() => {
    try {
      const storedValue = localStorage.getItem(key);
      console.log(storedValue);
      if (storedValue === null) return initialValue;
      return JSON.parse(storedValue);
    } catch (error) {
      console.warn(`Failed to parse localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);

  return [value, setValue];
}
