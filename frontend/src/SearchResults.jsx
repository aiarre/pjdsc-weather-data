import { useEffect } from "react";

const OVERPASS_BASE_URL = "https://overpass-api.de/api/interpreter";

export default function SearchResults(props) {
  const { setSelectPosition, setSelectRoad, listPlace, setListPlace } = props;
  useEffect(() => {
    document.getElementById("searchInput").addEventListener("focus", () => {
      document.getElementById("searchResultsContainer").style.display = "block";
    });
  });
  return (
    <div id="searchResultsContainer">
      <p
        style={{
          textAlign: "center",
          padding: "20px 0",
          color: "gray",
          display: "none",
        }}
        id="searchLoading"
      >
        Loading...
      </p>
      <p
        style={{
          textAlign: "center",
          padding: "20px 0",
          color: "gray",
          display: "none",
        }}
        id="searchEmpty"
      >
        No search results
      </p>
      <ul id="searchResults">
        {listPlace.map((item) => {
          return (
            <div key={item?.osm_id}>
              <li
                onClick={() => {
                  document.getElementById(
                    "searchResultsContainer",
                  ).style.display = "none";
                  console.log("loc selected");
                  setSelectPosition(item);
                  fetch(`${OVERPASS_BASE_URL}`, {
                    method: "POST",
                    body: `[out:json];
                  way["name"="${item?.name}"];
                  out geom;`,
                  })
                    .then((resp) => resp.text())
                    .then((res) => JSON.parse(res))
                    .then((data) => {
                      setSelectRoad(
                        data.elements.filter((e) => e.type === "way"),
                      );
                    });
                  setListPlace([]);
                }}
              >
                {item?.display_name}
              </li>
              <hr></hr>
            </div>
          );
        })}
      </ul>
    </div>
  );
}
