import React, { useEffect, useState } from "react";

import {
  Divider,
 
  Responsive,
  Dimmer,
  Loader,
  Card,Grid,
  Segment,
  Table,
  Label,
  Header,
  Checkbox,
  Button,

  Container

} from "semantic-ui-react";


function Scoring() {
  

  return (
    
    <Segment>
    <Card raised fluid >
    <Grid columns={1} unstackable>
     <Grid.Column>
                              <Segment raised>
                                              {/* <Label as='a' color='red' ribbon> Live </Label> */}
                                              
                                              <Grid columns={2} unstackable textAlign='center'>

                                                  <Grid.Row verticalAlign='middle'>
                                                      <Grid.Column>

                                                          <Header as="h2" color="blue">Oracle</Header>
                                                          343/9 (23 overs)
                                                      </Grid.Column>

                                                      <Grid.Column>
                                                          <Header as="h2" color="blue">CRR </Header>

                                                          8.80

                                                      </Grid.Column>
                                                  </Grid.Row>
                                                 </Grid>
                                            <Divider />

                                              <Grid columns={1} unstackable textAlign='center'>
                                                  <Grid.Row verticalAlign='middle'>
                                                      <Grid.Column>


                                                          <Label.Group circular>

                                                          <Label key='run' color="blue" size="large" as='a'>4</Label>
                                                          <Label key='run' color="red" size="large" as='a'>W</Label>
                                                          <Label key='run' color="blue" size="large" as='a'>6</Label>
                                                          <Label key='run'  size="large" as='a'>1</Label>
                                                          <Label key='run'  size="large" as='a'>2</Label>
                                                          <Label key='run'  size="large" as='a'>1</Label>

                                                          </Label.Group>
                                                      </Grid.Column>
                                                  </Grid.Row>
                                              </Grid>
                          <Divider />
                                      <Grid columns={1} unstackable textAlign='center'>
                                          <Grid.Row verticalAlign='middle'>
                                              <Grid.Column>

                                              <Table unstackable>
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
                                                                  <Table.Row>
                                                                  <Table.Cell >Pankaj</Table.Cell>
                                                                  <Table.Cell>34</Table.Cell>
                                                                  <Table.Cell>32</Table.Cell>
                                                                  <Table.Cell>2</Table.Cell>
                                                                  <Table.Cell>4</Table.Cell>
                                                                  <Table.Cell>3</Table.Cell>
                                                                
                                                                </Table.Row>
                                                                <Table.Row>
                                                                  <Table.Cell>Ankur</Table.Cell>
                                                                  <Table.Cell>34</Table.Cell>
                                                                  <Table.Cell>32</Table.Cell>
                                                                  <Table.Cell>2</Table.Cell>
                                                                  <Table.Cell>4</Table.Cell>
                                                                  <Table.Cell>3</Table.Cell>
                                                            
                                                                </Table.Row>
                                                      </Table.Body>
                                                  </Table>


                                                                          
                                              </Grid.Column>
                                          </Grid.Row>
                                      </Grid>

                                      <Grid columns={1} unstackable textAlign='center'>
                                          <Grid.Row verticalAlign='middle'>
                                              <Grid.Column>

                                              <Table unstackable>
                                                          <Table.Header>
                                                            <Table.Row>
                                                              <Table.HeaderCell>Bowler Name</Table.HeaderCell>
                                                              <Table.HeaderCell>R</Table.HeaderCell>
                                                              <Table.HeaderCell>B</Table.HeaderCell>
                                                              <Table.HeaderCell>4s</Table.HeaderCell>
                                                              <Table.HeaderCell>6s</Table.HeaderCell>
                                                              <Table.HeaderCell>SR</Table.HeaderCell>
                                                            </Table.Row>
                                                          </Table.Header>
                                                          <Table.Body>
                                                                  <Table.Row>
                                                                  <Table.Cell >Pankaj</Table.Cell>
                                                                  <Table.Cell>34</Table.Cell>
                                                                  <Table.Cell>32</Table.Cell>
                                                                  <Table.Cell>2</Table.Cell>
                                                                  <Table.Cell>4</Table.Cell>
                                                                  <Table.Cell>3</Table.Cell>
                                                                
                                                                </Table.Row>
                                                               
                                                      </Table.Body>
                                                  </Table>


                                                                          
                                              </Grid.Column>
                                          </Grid.Row>
                                      </Grid>

                                      </Segment>
                                      </Grid.Column>
                                      </Grid>
                                      </Card>
                                     

                                        <Grid columns={4} unstackable textAlign='center'>
                                                      <Grid.Row verticalAlign='middle'>
                                                          <Grid.Column>
                                                          <Checkbox label='Wide' />                     
                                                          </Grid.Column>
                                                          <Grid.Column>
                                                          <Checkbox label='Noball' />                     
                                                          </Grid.Column>
                                                          <Grid.Column>
                                                          <Checkbox label='Byes' />                     
                                                          </Grid.Column>
                                                          <Grid.Column>
                                                          <Checkbox label='Leg Byes' />                     
                                                          </Grid.Column>
                                                      </Grid.Row>
                                                      <Grid.Row verticalAlign='middle'>
                                                          <Grid.Column>
                                                          <Checkbox label='Out' />                     
                                                          </Grid.Column>
                                                              
                                                          <Grid.Column>
                                                          <Button>Swap</Button>    
                                                          </Grid.Column>
                                                          <Grid.Column>
                                                          <Button>Retire</Button>                
                                                          </Grid.Column>
                                                          <Grid.Column>
                                                          <Button>Undo</Button>             
                                                          </Grid.Column>
                                                        
                                                      </Grid.Row>
                                        </Grid>
                            <Container>
                                   
                            <Grid columns={4} unstackable textAlign='center'>
                                                      <Grid.Row verticalAlign='middle'>
                                                          <Grid.Column>
                                                          <Button circular fluid size="large">0</Button>               
                                                          </Grid.Column>
                                                          <Grid.Column>
                                                          <Button circular fluid size="large">1</Button>                     
                                                          </Grid.Column>
                                                          <Grid.Column>
                                                          <Button circular fluid size="large">2</Button>     
                                                          </Grid.Column>
                                                          <Grid.Column>
                                                          <Button circular fluid size="large">3</Button>     
                                                          </Grid.Column>
                                                      </Grid.Row>
                                                      <Grid.Row verticalAlign='middle'>
                                                          <Grid.Column>
                                                          <Button circular fluid size="large">4</Button>                 
                                                          </Grid.Column>
                                                          <Grid.Column>
                                                          <Button circular fluid size="large">5</Button>     
                                                          </Grid.Column>
                                                          <Grid.Column>
                                                          <Button circular fluid size="large">6</Button>           
                                                          </Grid.Column>
                                                          <Grid.Column>
                                                          <Button circular fluid size="large">-</Button>          
                                                          </Grid.Column>
                                                        
                                                      </Grid.Row>
                                        </Grid>



                            </Container>
           
        
                                        </Segment>
   

 


  );
}

export default Scoring;
