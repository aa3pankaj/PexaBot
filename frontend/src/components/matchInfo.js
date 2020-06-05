import React ,{useEffect} from "react";
import {
    Grid, Placeholder, Segment, Button,
    Divider,
    Header,
    Label,
    Container,
    List
}
    from "semantic-ui-react";

function MatchInfo({toss, matchNumber, overStatus, status, name1,batting1,runScored1,wicketsFallen1,name2,batting2,runScored2,wicketsFallen2}) {
    const createBallStatus = (type) => {
        var dataArray = []
        

        if("run" in type){
             if (type.run==6 || type.run==4){
                dataArray.push(<Label color ="blue" size="large" as='a'>{type.run}</Label>);

             }
             
             else {
                dataArray.push(<Label  size="large" as='a'>{type.run}</Label>);

             }
        }

        if("out" in type){
            dataArray.push(<Label color="red" size="large" as='a'>W</Label>);

        }

        if("wide" in type){
           
            dataArray.push(<Label color="grey" size="large" as='a'>{type.wide}Wd</Label>);

        }
        if ("noball" in type){
            dataArray.push(<Label color="grey" size="large" as='a'>{type.noball}N</Label>);

        }

        return dataArray;
       
    }

    const createOverStatus=()=>{

        var dataArray = []

        Object.keys(overStatus).map((key) => {

            let ball = createBallStatus(overStatus[key])
            dataArray.push(ball);
       }

       );

       return dataArray;
        
    }
    useEffect(()=>{

        // console.log("pa"+status+"pa")
        // if(status=='live'){
        //     console.log("live hai be")
        // }
        // console.log("wanta")
        // console.log(overStatus)
        // Object.keys(overStatus).map((key) => {

        console.log(runScored2+"/"+wicketsFallen2)
        // }

        // );

        

    });
    return ( 
        <Container style={{ margin: 20 }}>
        <Grid columns={1} unstackable>
            <Grid.Column>
           <Segment raised>
            {status==="live"?(<Label as='a' color='red' ribbon> Live </Label> ):(<Label as='a' color='green' ribbon> Ended </Label> )}
            <Grid columns={1} unstackable textAlign='center'>
              
                <Grid.Row verticalAlign='middle'>
                    <Grid.Column>
                    {/* <List size="medium">
                        <List.Item> Match #{matchNumber} Internal</List.Item>
                        <List.Item>{toss}</List.Item>
            
                    </List> */}
                        <Header as="h5" color="grey">
                            Match #{matchNumber} Internal
                            <Header as="h5" color="grey">{toss}</Header>
                        </Header>
                        
                      
                    </Grid.Column>
                 
                </Grid.Row>
               
            </Grid>
            <Grid columns={2} unstackable textAlign='center'>

                <Grid.Row verticalAlign='middle'>
                    <Grid.Column>
                   
                    <Header as="h2" color="blue">{name1}
                    <Header color="blue" as="h5">  {runScored1}/{wicketsFallen1} </Header>
                    
                    </Header>
                    
                    </Grid.Column>
                    
                    <Grid.Column>
                        <Header as="h2"  color="blue">{name2}
                        
                        <Header color="blue" as="h5"> {runScored2}/{wicketsFallen2}</Header>
                        
                        </Header>
                       
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
      </Container>
    
    );
}

export default MatchInfo;
