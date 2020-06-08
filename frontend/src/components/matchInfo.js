import React from "react";
import {
    Grid, Segment,
    Divider,
    Header,
    Label,
    Container,
    Card
}
    from "semantic-ui-react";

function MatchInfo({ toss, matchNumber, overStatus, status, name1, batting1, runScored1, wicketsFallen1, name2, batting2, runScored2, wicketsFallen2 }) {
    const createBallStatus = (type) => {
        var dataArray = []

        if ("run" in type) {
            if (type.run === 6 || type.run === 4) {
                dataArray.push(<Label key='run' color="blue" size="large" as='a'>{type.run}</Label>);

            }

            else {
                dataArray.push(<Label key='run' size="large" as='a'>{type.run}</Label>);

            }
        }

        else if ("out" in type) {
            dataArray.push(<Label key='out' color="red" size="large" as='a'>W</Label>);

        }

        else if ("wide" in type) {

            dataArray.push(<Label key='wide' color="grey" size="large" as='a'>{type.wide}Wd</Label>);

        }
        else if ("noball" in type) {
            dataArray.push(<Label key='noball' color="grey" size="large" as='a'>{type.noball}N</Label>);

        }

        return dataArray;

    }

    const createOverStatus = () => {

        var dataArray = []

        // Object.keys(overStatus).map((key) => {

        //     let ball = createBallStatus(overStatus[key])
        //     dataArray.push(ball);
        // }

        // );

        Object.keys(overStatus).map((key) => {
            overStatus[key].map((val)=>{
                let ball = createBallStatus(val)
                dataArray.push(ball);
            })
            
           
        }

        );

        return dataArray;

    }

    return (
        <Card raised fluid >
            <Grid columns={1} unstackable>
                <Grid.Column>
                    <Segment inverted raised>
                        {status === "live" ? (<Label as='a' color='red' ribbon> Live </Label>) : (<Label as='a' color='green' ribbon> {status} </Label>)}
                        <Grid columns={1} unstackable textAlign='center'>
                            <Grid.Row verticalAlign='middle'>
                                <Grid.Column>
                                    <Header as="h5" color="grey">
                                        Match #{matchNumber} Internal 
                                    </Header>
                                    {toss}
                                </Grid.Column>
                            </Grid.Row>
                        </Grid>
                        <Grid columns={2} unstackable textAlign='center'>

                            <Grid.Row verticalAlign='middle'>
                                <Grid.Column>

                                    <Header as="h2" color="blue">{name1}</Header>
                                    {runScored1}/{wicketsFallen1}
                                </Grid.Column>

                                <Grid.Column>
                                    <Header as="h2" color="blue">{name2} </Header>

                                    {runScored2}/{wicketsFallen2}

                                </Grid.Column>
                            </Grid.Row>
                        </Grid>
                        <Divider />

                        <Grid columns={1} unstackable textAlign='center'>
                            <Grid.Row verticalAlign='middle'>
                                <Grid.Column>


                                    <Label.Group circular>

                                        {createOverStatus()}
                                    </Label.Group>
                                </Grid.Column>
                            </Grid.Row>
                        </Grid>
                        <Divider />
                    </Segment>
                </Grid.Column>
            </Grid>
        </Card>

    );
}

export default MatchInfo;
