import React, { useEffect, useState } from "react";

import {
  Divider,
  Segment,
  Responsive,
  Dimmer,
  Loader
} from "semantic-ui-react";
import Innings from "./innings";
import MatchInfo from "./matchInfo"
import io from 'socket.io-client';

function MatchList() {

  const createMatchInfoList=()=>{
   
    <Segment>
    <MatchInfo toss={toss} matchNumber={match.match_number} overStatus={overStatus} status={match.status} name1={match.innings1_team}  runScored1={team1runs} wicketsFallen1={team1wickets} name2={match.innings2_team} runScored2={team2runs} wicketsFallen2={team2wickets}/>
    </Segment>


  }
  
  useEffect(() => {
    fetch('https://pexabotbackend.herokuapp.com/matches/10')
    //fetch('http://127.0.0.01:5222/match_data/' + props.match.params.id)
      .then(response => {
        return response.json();
      })
      .then(data => {
        console.log("Result from HTTP GET request")
    
      });
  }, []);


  return (
    <div>
      {loading ? (<Dimmer active>
        <Loader size='massive'>Loading</Loader>
      </Dimmer>) : (
          <Responsive>
            <Segment>
            <MatchInfo toss={toss} matchNumber={match.match_number} overStatus={overStatus} status={match.status} name1={match.innings1_team}  runScored1={team1runs} wicketsFallen1={team1wickets} name2={match.innings2_team} runScored2={team2runs} wicketsFallen2={team2wickets}/>
            </Segment>
          </Responsive>
        )}
    </div>

  );
}

export default MatchList;
