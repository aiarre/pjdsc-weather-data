// import "./App.css";
import { useState } from "react";
import Map from "./Map";
import SearchBox from "./SearchBox";

export default function App() {
  const [selectPosition, setSelectPosition] = useState();
  const [selectRoad, setSelectRoad] = useState([]);
  return (
    <>
      <Map selectPosition={selectPosition} selectRoad={selectRoad} />
      <SearchBox
        selectPosition={selectPosition}
        setSelectPosition={setSelectPosition}
        selectRoad={selectRoad}
        setSelectRoad={setSelectRoad}
      />
      <div id="legendContainer">
        <h3>Legend</h3>
        <div>
          <h3>
            <span class="dot" style={{ backgroundColor: "red" }} />
            {"  "}Severe
          </h3>
        </div>
        <h3>
          <span class="dot" style={{ backgroundColor: "orange" }} />
          {"  "}Moderate
        </h3>
        <h3>
          <span class="dot" style={{ backgroundColor: "yellow" }} />
          {"  "}Light
        </h3>
        <h3>
          <span class="dot" style={{ backgroundColor: "green" }} />
          {"  "}No Flood
        </h3>
      </div>
    </>
  );
}
