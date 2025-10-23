import { useState } from "react";
import SearchResults from "./SearchResults";
import search from "./assets/search.png";

const NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org/search?";

export default function SearchBox(props) {
  const { setSelectPosition, setSelectRoad, setSeverity } = props;
  const [searchText, setSearchText] = useState("");
  const [listPlace, setListPlace] = useState([]);

  function submitAndSearch() {
    document.getElementById("searchLoading").style.display = "block";
    document.getElementById("searchEmpty").style.display = "none";
    const params = {
      q: searchText,
      format: "json",
      addressdetails: 1,
      polygon_geojson: 0,
      category: "highway",
      countrycodes: "ph",
    };
    const queryString = new URLSearchParams(params).toString();
    const requestOptions = {
      method: "GET",
      redirect: "follow",
    };
    fetch(`${NOMINATIM_BASE_URL}${queryString}`, requestOptions)
      .then((resp) => resp.text())
      .then((result) => {
        document.getElementById("searchLoading").style.display = "none";
        const data = JSON.parse(result);
        if (data.length === 0) {
          document.getElementById("searchEmpty").style.display = "block";
        }
        setListPlace(JSON.parse(result));
      })
      .catch((e) => console.log("error: ", e));
  }

  return (
    <div id="floatingTab">
      <div style={{ display: "flex", flexDirection: "column" }}>
        <div id="searchbox">
          <div id="input">
            <input
              type="text"
              id="searchInput"
              placeholder="Enter major road here"
              value={searchText}
              onChange={(e) => {
                setSearchText(e.target.value);
              }}
            />
          </div>
          <div id="button">
            <button type="submit" onClick={submitAndSearch} id="searchButton">
              <img src={search} height={"16px"}></img>
            </button>
          </div>
        </div>
        <SearchResults
          listPlace={listPlace}
          setListPlace={setListPlace}
          setSelectPosition={setSelectPosition}
          setSelectRoad={setSelectRoad}
          setSeverity={setSeverity}
        />
      </div>
    </div>
  );
}
