import React from "react";
import Match from "./components/match";
import { Route } from "react-router";
import Scoring from "./components/scoring.js"
export default function App() {
  return (
   
    <div>
      {/* <Scoring /> */}
      <Route path="/match/:id" component={Match}/>
    </div>
  
  );
}
