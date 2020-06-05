import React from "react";
import Match from "./components/match";
import { Route } from "react-router";

export default function App() {
  return (
   
    <div>
      {/* <MatchInfo /> */}
      <Route path="/match/:id" component={Match}/>
    </div>
  
  );
}
