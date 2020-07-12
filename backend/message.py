import json
from pydialogflow_fulfillment import TelegramKeyboardButtonResponse

class Message:

    @staticmethod
    def scoring_custom_payload(match_info):
      print("******start of scoring_custom_payload")
      output_payload = []
      current_batting_team = match_info["current_batting_team"]
      runs_scored = match_info["runs_scored"]
      wickets_fallen = match_info["wickets_fallen"]
      running_over = match_info["running_over"]
      ball_number = match_info["ball_number"]
      strike_batsman = match_info["strike_batsman"]
      non_strike_batsman = match_info["non_strike_batsman"]
      over_status = match_info["over_status"]
      strike_batsman_runs = match_info['strike_batsman_runs']
      non_strike_batsman_runs = match_info['non_strike_batsman_runs']
      strike_batsman_balls = match_info['strike_batsman_balls']
      non_strike_batsman_balls = match_info['non_strike_batsman_balls']

      output_payload.append([{"text":current_batting_team+":"+str(runs_scored)+"/"+str(wickets_fallen)+" ("+str(running_over)+"."+str(ball_number)+" overs)"}])
      output_payload.append([{"text":strike_batsman +" "+str(strike_batsman_runs)+"("+str(strike_batsman_balls)+")"},{"text":non_strike_batsman +" "+str(non_strike_batsman_runs)+"("+str(non_strike_batsman_balls)+")"}])
      this_over = ''
      print(over_status)
      
      if over_status !=None:
        for ball in over_status:
          print("$$$$$$")
          print(ball)
          for x in over_status[ball]:
            print(x)
            if "run" in x:
              this_over+=str(x["run"])+"  "
            elif "wide" in x:
              this_over+=str(x["wide"])+"Wd  "
            elif "noball" in x:
              this_over+=str(x["noball"])+"Nb  "
            elif "out" in x:
              this_over+="W  "
          print("$$$$$$")
      print(this_over)

      if this_over != '':
          output_payload.append([{"text":"This over: "+this_over}])
      else:
          output_payload.append([{"text":"This over:"}])

      print(output_payload)
      
      output_payload.append( [
          {
            "text": "0"
          },
          {
           
            "text": "1"
          },
          {
           
            "text": "2"
          },
          {
            "text":"undo"
          }
        ])
      output_payload.append( [
          {
           
            "text": "3"
          },
          {
          
            "text": "4"
          },
          {
          
            "text": "5"
          },
          {
            "text": "6"
          
          }
        ])

      output_payload.append([
          {
           
            "text": "out"
          },
           {
            "text": "strike change"
           
          }
         
       ])
      output_payload.append([
          {
           
            "text": "wide"
          }
        ])
      output_payload.append(
        [
          {
           
            "text": "no ball"
          }
        ])
      
      print("****** end of scoring_custom_payload")
      return output_payload

    @staticmethod
    def empty_keyboard_button():
      return [{
                    
                    "text": "",
                    "callback_data": "" 
                }]
                
    @staticmethod
    def ball_update_custom_keyboard():
      return  [
        [
          {
            "text": "0"
          },
          {
            "text": "1"
          },
          {
            "text": "2"
          },
          {
            "text": "undo"
          }
        ],
        [
          {
            "text": "3"
          },
          {
            "text": "4"
          },
          {
            "text": "5"
          },
          {
            "text": "6"
          }
        ],
        [
          {
            "text": "out"
          },
           {
            "text": "strike change"
           
          },
         
        ],
        [
          {
            "text": "wide"
          }
        ],
        [
          {
            "text": "no ball"
          }
        ]

      ]

    @staticmethod
    def match_start_group_payload(scoreboard_url,team1,team2,match_id):
      return  team1+" vs "+team2 +"\nscorer:"+match_id+"\n\nLive score: "+scoreboard_url
                    
               
    @staticmethod
    def match_start_payload(scoreboard_url,team1):
      return { "fullfillmentText":'user_detail', "fulfillmentMessages": [
                {
                "text": {
                    "text": [
                           "Match init success in database!\nLive score: "+scoreboard_url+"\n\nPlayer names of "+ team1 +"? (space separated usernames, team should have atleast 2 players)"
                        ]
                    }
                    }
                ]
               }
        
    @staticmethod
    def general_message(message):
        return { "fullfillmentText":'user_detail', "fulfillmentMessages": [
                {
                "text": {
                    "text": [
                          message
                        ]
                    }
                    }
                ],
               }


    @staticmethod
    def bowler_ask_payload(bolwer_list):
        calback =[{
                   
                    "text": "",
                     "callback_data": "" 
                }]
        out = {"payload":{
  "telegram": {
    "text": "Next bowler?",
    "reply_markup": {
      "keyboard": [
        ]
    }
    
  
}},
"platform":"TELEGRAM"
}
        for x in bolwer_list:
            calback[0]['text'] = x
            calback[0]['callback_data'] = x
            out['payload']['telegram']['reply_markup']['keyboard'].append(calback)
            calback =[{
                    
                    "text": "",
                    "callback_data": "" 
                }]

        return out

    @staticmethod
    def end_match_payload():
        return { "fullfillmentText":'user_detail', "fulfillmentMessages": [
                {
                "text": {
                    "text": [
                           "Match ended"
                        ]
                    }
                    }
                ],
                "outputContexts": [
      
    ]}
    @staticmethod
    def get_resume_payload():
        return json.dumps({"fullfillmentText":'valid',
    "fulfillmentMessages": [
      {
        "text": {
          "text": [
            "Match is On!"
          ]
        }
      }
    ]
  })

    @staticmethod
    def get_match_pause_payload(username):
        return {"fullfillmentText":'valid',
    "fulfillmentMessages": [
      {
        "text": {
          "text": [
            "Match paused! \nType 'Resume @"+username+"'"
          ]
        }
      }
    ],
    "outputContexts":[]
  }
    @staticmethod
    def exit_payload():
        return {
    "fulfillmentMessages": [
      {
        "text": {
          "text": [
            "Have a great day!"
          ]
        }
      }
    ],
    "outputContexts": [
      
    ]
  }
    @staticmethod
    def get_invalid_request_payload():
        return {"fullfillmentText":'invalid',"fulfillmentMessages": [
             {
              "text": {
                   "text": [
                        "Invalid request"
                      ]
                   }
                }
              ]}

    @staticmethod
    def get_update_match_document_payload(current_batting_team,running_over,ball_number,runs_scored,strike_batsman,non_strike_batsman,current_bowler):
        return {"fullfillmentText":'Next?',"fulfillmentMessages": [
                {
                "text": {
                    "text": [
                            "Team:"+current_batting_team+" Total: "+str(runs_scored)+"\nBall:"+str(running_over)+"."+str(ball_number)+ " recorded,"+
                            "\nBatsmen:"+strike_batsman+"(*), " +non_strike_batsman+"\nBowler:"+current_bowler+"\nwhat happened on the next ball?"
                        ]
                    }
                    }
                ]}
    @staticmethod
    def get_user_stats_payload(user_detail):
        return { "fullfillmentText":'user_detail', "fulfillmentMessages": [
                {
                "text": {
                    "text": [
                            "username:"+user_detail['user_id']+"\nruns:" + str(user_detail['batting']['runs'])+"\nballs:" + str(user_detail['batting']['balls']) +\
                            "\navg:"+str(user_detail['batting']['avg'])+"\nstrike rate:"+str(user_detail['batting']['strike_rate'])+"\n6s:"+str(user_detail['batting']['6s'])+"\n4s:"+str(user_detail['batting']['4s'])
                        ]
                    }
                    }
                ]}
    @staticmethod
    def next_bowler_ask_payload(current_batting_team,running_over,ball_number,runs_scored,wickets_fallen,strike_batsman,non_strike_batsman):
        
        return {"fullfillmentText":'what happened on ball 2?',"fulfillmentMessages": [
                {
                "text": {
                    "text": [
                            "Team: "+current_batting_team+"\nTotal: "+str(runs_scored)+"/"+str(wickets_fallen)+"\nOvers: "+str(running_over+1)
                        ]
                    }
                    }
                ]}
      
    @staticmethod
    def new_innings_payload():
        return { "fullfillmentText":'user_detail', "fulfillmentMessages": [
                {
                "text": {
                    "text": [
                           "Innings over!\n\nType 'change'\nAnd then Opening batsmen of second Innings? player1 and player2"
                        ]
                    }
                    }
                ]}
    

    @staticmethod
    def next_batsman_ask_payload():
         return { "fullfillmentText":'user_detail', "fulfillmentMessages": [
                {
                "text": {
                    "text": [
                           "Next batsman?"
                        ]
                    }
                    }
                ]}