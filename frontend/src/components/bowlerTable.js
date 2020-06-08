import React from "react";
import { Table } from "semantic-ui-react";

function BowlerTable(props) {
  return (
    <Table inverted unstackable>
      <Table.Header>
        <Table.Row>
          <Table.HeaderCell>Bowler</Table.HeaderCell>
          <Table.HeaderCell>B</Table.HeaderCell>
          <Table.HeaderCell>R</Table.HeaderCell>
          <Table.HeaderCell>W</Table.HeaderCell>
          <Table.HeaderCell>Wd</Table.HeaderCell>
          <Table.HeaderCell>N</Table.HeaderCell>
          <Table.HeaderCell>ER</Table.HeaderCell>
        </Table.Row>
      </Table.Header>
      <Table.Body>
        {props.data}
      </Table.Body>
    </Table>
  );
}

export default BowlerTable;
