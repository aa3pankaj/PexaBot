import React from "react";
import {
  Table
} from "semantic-ui-react";

function BatsmanTable(props) {

  return (
    
    <Table inverted unstackable>
      <Table.Header>
        <Table.Row>
          <Table.HeaderCell>Batsman Name</Table.HeaderCell>
          <Table.HeaderCell>R</Table.HeaderCell>
          <Table.HeaderCell>B</Table.HeaderCell>
          <Table.HeaderCell>4s</Table.HeaderCell>
          <Table.HeaderCell>6s</Table.HeaderCell>
          <Table.HeaderCell>SR</Table.HeaderCell>
        </Table.Row>
      </Table.Header>
      <Table.Body>
       {props.data}
      </Table.Body>
    </Table>
  );
}

export default BatsmanTable;
