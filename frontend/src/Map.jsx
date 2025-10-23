import { useRef, useEffect } from "react";
import leaflet from "leaflet";
import pin from "./assets/pin.png";

var icon = leaflet.icon({
  iconUrl: pin,
  iconSize: [38, 38],
  iconAnchor: [22, 34],
  popupAnchor: [-3, -76],
});

export default function Map(props) {
  const mapRef = useRef();
  const roadLinesRef = useRef([]);
  const { selectPosition, selectRoad, severity } = props;

  function onLocationFound(e) {
    var radius = e.accuracy;

    leaflet.marker(e.latlng, { icon: icon }).addTo(mapRef.current);
    leaflet.circle(e.latlng, radius).addTo(mapRef.current);
  }

  function onLocationError(e) {
    console.log(e.message);
  }

  function hideSearchResults() {
    document.getElementById("searchResultsContainer").style.display = "none";
  }

  function colorBasedOnScore(score) {
    if (score >= 0.7) {
      return "red";
    } else if (score >= 0.4) {
      return "orange";
    } else if (score > 0) {
      return "yellow";
    } else {
      return "green";
    }
  }

  // renders the map
  useEffect(() => {
    mapRef.current = leaflet
      .map("map", { zoomControl: false })
      .setView([12.87, 121.77], 6)
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
          .polyline(coords, { color: colorBasedOnScore(severity) })
          .addTo(mapRef.current);
        roadLinesRef.current.push(polyline);
      }
    }
  }, [selectPosition, selectRoad, severity]);

  return <div id="map" ref={mapRef}></div>;
}
