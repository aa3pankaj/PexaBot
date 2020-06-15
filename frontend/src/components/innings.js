import React, { useEffect, useState } from "react";
import {  Header } from "semantic-ui-react";
import BatsmanTable from "./batsmanTable";
import BowlerTable from "./bowlerTable";
import {
  Table
} from "semantic-ui-react";


function Innings({match,fallofwickets,batting,bowling,name,runScored,wicketsFallen}) {

  const [battingRows, setBattingRows] = useState([]);
  const [bowlingRows, setBowlingRows] = useState([]);
  const [fallOfWickets, setFallOfWickets] = useState();
  const createFallOfWickets = (data) => {
    return (
    <Table.Row>
      <Table.Cell>{data}</Table.Cell>
    </Table.Row>

    )
  }
  const createDataBatting = (name, runs, balls, fours, sixes, sr, status) => {
    if (status === true) {
      return (<Table.Row  key={name}>

        <Table.Cell positive>{name}</Table.Cell>
        <Table.Cell>{runs}</Table.Cell>
        <Table.Cell>{balls}</Table.Cell>
        <Table.Cell>{fours}</Table.Cell>
        <Table.Cell>{sixes}</Table.Cell>
        <Table.Cell>{sr}</Table.Cell>
      </Table.Row>);
    }
    else {

      return (<Table.Row key={name}>
        <Table.Cell>{name}</Table.Cell>
        <Table.Cell>{runs}</Table.Cell>
        <Table.Cell>{balls}</Table.Cell>
        <Table.Cell>{fours}</Table.Cell>
        <Table.Cell>{sixes}</Table.Cell>
        <Table.Cell>{sr}</Table.Cell>
      </Table.Row>);

    }

  }

  const createDataBowling = (name, balls, runs, wickets, wides, noballs, er) => {

    return (<Table.Row key={name}>
      <Table.Cell >{name}</Table.Cell>
      <Table.Cell>{balls}</Table.Cell>
      <Table.Cell>{runs}</Table.Cell>
      <Table.Cell>{wickets}</Table.Cell>
      <Table.Cell>{wides}</Table.Cell>
      <Table.Cell>{noballs}</Table.Cell>
      <Table.Cell>{er}</Table.Cell>
    </Table.Row>);

  }
  useEffect(() => {
    console.log("useEffect of innings");

    var dataArray = []

    // let batting = props.batting;

    Object.keys(batting).map((key) => {
      //console.log(key)
      let row = createDataBatting(key, batting[key].runs, batting[key].balls, batting[key]['4s'], batting[key]['6s'], batting[key].strike_rate, batting[key].status)
      dataArray.push(row);
    });

    setBattingRows(dataArray)
    dataArray = []
    // let bowling = props.bowling;
    console.log("nowling=",bowling)
    Object.keys(bowling).map((key) => {
      // console.log(key)
      let row = createDataBowling(key, bowling[key].balls, bowling[key].runs, bowling[key].wickets, bowling[key].wides, bowling[key].noballs, bowling[key].economy_rate)
      dataArray.push(row);
    });
    setBowlingRows(dataArray)
    var fallOfWickets = ''
    var wicket_fallen = 1


    console.log(typeof fallofwickets)

    if (typeof fallofwickets != 'undefined' && typeof fallofwickets != 'number' ) {
      const items = fallofwickets.map((item, key) => {
        console.log(item.team_score)
        fallOfWickets = fallOfWickets + (item.team_score + "/" + wicket_fallen + " (" + item.batsman + ", " + item.over_number + "." + item.ball_number +
          " over), ")
        console.log(fallOfWickets)
        wicket_fallen = wicket_fallen + 1
      });
      console.log(fallOfWickets)
      let row = createFallOfWickets(fallOfWickets);
      setFallOfWickets(row)
    }

  }, []);

  return (

    <div>
      <Header as='h4' attached="top" block >
      {name} 
  </Header>
      <BatsmanTable data={battingRows} />
      <Table >
        <Table.Header>
          <Table.Row>
            <Table.HeaderCell>Fall of wickets</Table.HeaderCell>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {fallOfWickets}
        </Table.Body>
      </Table>
      <BowlerTable data={bowlingRows} />
    </div>
  );
}

export default Innings;
