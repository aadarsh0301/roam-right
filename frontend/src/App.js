import React, { useState } from "react";
import RoamRight from "./components/RoamRight";

function App() {
  return (
      <div
          style={{
              backgroundColor: "#121212",
              width: "100vw",
              height: "100vh",
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
          }}
      >
          <RoamRight/>
      </div>

  );
}

export default App;
