import { useRef, useEffect } from "react";
import leaflet from "leaflet";

export default function Map(props) {
  const mapRef = useRef();
  const roadLinesRef = useRef([]);
  const { selectPosition, selectRoad } = props;

  function onLocationFound(e) {
    console.log("location found");
    var radius = e.accuracy;

    leaflet.marker(e.latlng).addTo(mapRef.current);
    leaflet.circle(e.latlng, radius).addTo(mapRef.current);
  }

  function onLocationError(e) {
    alert(e.message);
  }

  function hideSearchResults() {
    document.getElementById("searchResultsContainer").style.display = "none";
  }

  // renders the map
  useEffect(() => {
    mapRef.current = leaflet
      .map("map", { zoomControl: false })
      .setView([12.87, 121.77], 6)
      // .fitWorld()
      .on("locationfound", onLocationFound)
      .on("locationerror", onLocationError)
      .on("click", hideSearchResults)
      .locate({ setView: true, maxZoom: 20 });
    leaflet
      .tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: "© OpenStreetMap",
      })
      .addTo(mapRef.current);
  }, []);

  // runs when the user selects a road to check flood severity
  useEffect(() => {
    if (selectPosition && selectRoad) {
      mapRef.current.flyTo([selectPosition?.lat, selectPosition?.lon], 16);

      if (roadLinesRef.current) {
        roadLinesRef.current.forEach((line) =>
          mapRef.current.removeLayer(line),
        );
        roadLinesRef.current = [];
      }
      for (const way of selectRoad) {
        const coords = way.geometry.map((p) => leaflet.latLng(p.lat, p.lon));
        const polyline = leaflet
          .polyline(coords, { color: "red" })
          .addTo(mapRef.current);
        roadLinesRef.current.push(polyline);
      }
    }
  }, [selectPosition, selectRoad]);

  return <div id="map" ref={mapRef}></div>;
}
