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

function Match(props) {
  const [reload,setReload] = useState(false)
  const [overStatus,setOverStatus] = useState({})
  const [loading, setLoading] = useState(true);
  const [match, setMatch] = useState({});
  const [team1Batting, setTeam1Batting] = useState({ "runs_scored": 0, "wickets_fallen": 0 });
  const [team1runs, setTeam1runs] = useState(0);
  const [team2runs, setTeam2runs] = useState(0);
  const [team1wickets, setTeam1wickets] = useState(0);
  const [team2wickets, setTeam2wickets] = useState(0);

  const [team1fallofwickets, setTeam1fallofwickets] = useState(0);
  const [team2fallofwickets, setTeam2fallofwickets] = useState(0);

  const [team2Batting, setTeam2Batting] = useState({ "runs_scored": 0, "wickets_fallen": 0 });
  const [team2Bowling, setTeam2Bowling] = useState({});
  const [team1Bowling, setTeam1Bowling] = useState({});
  const [toss, setToss] = useState('');

  function setInnings2State(data, innings1_team, innings2_team) {
    setTeam1Batting(data[innings1_team].batting)
    setTeam1Bowling(data[innings1_team].bowling)
    setTeam1runs(data[innings1_team].runs_scored)
    setTeam1wickets(data[innings1_team].wickets_fallen)
    setTeam1fallofwickets(data[innings1_team].fall_of_wickets)

    setTeam2runs(data[innings2_team].runs_scored)
    setTeam2wickets(data[innings2_team].wickets_fallen)
    setTeam2Batting(data[innings2_team].batting)
    setTeam2Bowling(data[innings2_team].bowling)
    setTeam2fallofwickets(data[innings2_team].fall_of_wickets)

  }
  function setInnings1State(data, innings1_team, innings2_team) {
    setTeam1Batting(data[innings1_team].batting)
    setTeam1runs(data[innings1_team].runs_scored)
    setTeam1wickets(data[innings1_team].wickets_fallen)

    setTeam2Bowling(data[innings2_team].bowling)
    setTeam1fallofwickets(data[innings1_team].fall_of_wickets)
  }
  var match_data='';
  
  useEffect(() => {
   
    fetch('https://pexabotbackend.herokuapp.com/match_data/' + props.match.params.id)
    //fetch('http://127.0.0.01:5222/match_data/' + props.match.params.id)
      .then(response => {
        return response.json();
      })
      .then(data => {

        console.log("Result from HTTP GET request")
        setResult(data)
        match_data = data;
      });
  }, [reload]);

  useEffect(() => {
    
    if(match.status!=="end"){
    const socket = io('https://pexabotbackend.herokuapp.com');
    socket.on('connect', function(){
        console.log("connected...!")
        // if(match_data["status"]=="end"){
        //   socket.disconnect() ;
        //   console.log("Disconnected as match ended...!")
        // }
    });
    socket.on('live',function(data) {
      console.log("Result from WEBSOCKET request",data)
      console.log(typeof data)
      if (JSON.parse(data)==null || match_data["status"]=="end"){
        socket.disconnect();
        console.log("Disconnected as match ended...!")
        setReload(true)
      }
      else{
      setResult(JSON.parse(data));
      }
      
    });
  }
}, []);

  

  const setResult =(data)=>{
    console.log('Received a message from the server!',data);
    setMatch(data);
    let innings1_team = data.innings1_team
    let innings2_team = data.innings2_team
   
    let toss = ''
    if (data.toss[1] === 'batting') {
      toss = data.toss[0] + ' won the toss and chose to bat'
    }
    else {
      toss = data.toss[0] + ' won the toss and chose to bowl'
    }
    if (data.running_innings !== 0) {
      setInnings2State(data, innings1_team, innings2_team)
     
    }
    else {
      setInnings1State(data, innings1_team, innings2_team)
    }

    let current_batting_team = data["current_batting_team"]
    setToss(toss)
    if ("over_status" in data[current_batting_team]){
    setOverStatus(data[current_batting_team].over_status[data["running_over"]])
    }
    if ("bowling" in  data[innings2_team]){
     setLoading(false)
    }
  }

  return (

    <div>
      
      {loading ? (<Dimmer active>
        <Loader size='massive'>Loading</Loader>
      </Dimmer>) : (
          <Responsive>
            <Segment>
            <MatchInfo toss={toss} matchNumber={match.match_number} overStatus={overStatus} status={match.status} name1={match.innings1_team} batting1={team1Batting} runScored1={team1runs} wicketsFallen1={team1wickets} name2={match.innings2_team} batting2={team2Batting} runScored2={team2runs} wicketsFallen2={team2wickets}/>
              <Innings match={match} fallofwickets={team1fallofwickets} batting={team1Batting} bowling={team2Bowling} name={match.innings1_team} runScored={team1runs} wicketsFallen={team1wickets} />
              <Divider section />
              {match.running_innings === 0 || team2Batting == null ? null : (
                <Innings match={match} fallofwickets={team2fallofwickets} batting={team2Batting} bowling={team1Bowling} name={match.innings2_team} runScored={team2runs} wicketsFallen={team2wickets} />
              )}
            </Segment>
          </Responsive>
        )}
    </div>


  );
}

export default Match;
