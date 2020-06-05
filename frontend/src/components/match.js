import React, { useEffect, useState } from "react";

import {
  Container,
  Header,
  Divider,
  Segment,
  Responsive,
  Dimmer,
  Loader,
  Accordion,
  Label,
  Message
} from "semantic-ui-react";
import Innings from "./innings";
import MatchInfo from "./matchInfo"

function Match(props) {
 
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
  useEffect(() => {
   
    fetch('https://73623e19a154.ngrok.io/match_data/' + props.match.params.id)
    //fetch('http://127.0.0.01:5222/match_data/' + props.match.params.id)
      .then(response => {
        return response.json();
        //response.json();
      })
      .then(data => {
       
       
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
        setToss(toss)
       
        if (data.running_innings !== 0) {
          setInnings2State(data, innings1_team, innings2_team)
         
        }
        else {
          setInnings1State(data, innings1_team, innings2_team)
        }

     //"over_status":{over_number:{ball_number:{score_type:run}}}}
        let current_batting_team = data["current_batting_team"]
        setOverStatus(data[current_batting_team].over_status[data["running_over"]])

        if ("bowling" in  data[innings2_team]){
         setLoading(false)
        }
      });
  }, []);

  const tables1 = () => (
    <div>{match.running_innings === 0 || team2Batting == null ? null : (
      <Innings match={match} fallofwickets={team2fallofwickets} batting={team2Batting} bowling={team1Bowling} name={match.innings2_team} runScored={team2runs} wicketsFallen={team2wickets} />
)}
</div>
  )

  const tables = () => (
    <div>  <Innings match={match} fallofwickets={team1fallofwickets} batting={team1Batting} bowling={team2Bowling} name={match.innings1_team} runScored={team1runs} wicketsFallen={team1wickets} />
              <Divider section />
              
       </div>

  )
  const panels = ()=>{
    return [{
    key: '1',
    title: 'Innings 1',
    content: {tables}
       
  }]
  
}

  const panels1 = ()=> {
    
    return [{
    key: `2`,
    title:'Innings 2',
    content: {tables1}
  }]
  
}


  return (

    <div>
      
      {loading ? (<Dimmer active>
        <Loader size='massive'>Loading</Loader>
      </Dimmer>) : (
          <Responsive>
            <MatchInfo toss={toss} matchNumber={match.match_number} overStatus={overStatus} status={match.status} name1={match.innings1_team} batting1={team1Batting} runScored1={team1runs} wicketsFallen1={team1wickets} name2={match.innings2_team} batting2={team2Batting} runScored2={team2runs} wicketsFallen2={team2wickets}/>
            {/* <Container textAlign="center">
              <Header>
                {match.current_batting_team} vs {match.current_bowling_team}
              </Header>
              <p>{toss}</p>
              <p>Status: {match.status} </p>
            </Container> */}
           
            <Segment>
            {/* <Accordion defaultActiveIndex={1} panels={panels()} />
            <Accordion defaultActiveIndex={1} panels={panels1()} /> */}
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
