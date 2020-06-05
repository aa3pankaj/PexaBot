import React from "react";
import Match from "./components/match";
import { Router, Route, Switch } from "react-router";
import MatchInfo from './components//matchInfo'
export default function App() {
  return (
   
    <div>
      {/* <MatchInfo /> */}
      <Route path="/match/:id" component={Match}/>
    </div>
  
  );
}
