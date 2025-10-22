import { useEffect, useState } from "react";

export default function useGeolocation() {
  const [position, setPosition] = useState({
    latitude: 14.6,
    longitude: 121.07,
  });

  useEffect(() => {
    const geo = navigator.geolocation;

    const watcher = geo.watchPosition(onSuccess, onError);
    function onSuccess(position) {
      setPosition({
        latitude: position.coords.latitude,
        longitude: position.coords.longitude,
      });
    }

    function onError(error) {
      if (error.code === 1) {
        alert(error.message);
      } else {
        alert(error.message);
      }
    }

    return () => geo.clearWatch(watcher);
  }, []);

  return position;
}
