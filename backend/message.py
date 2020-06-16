import json
from pydialogflow_fulfillment import TelegramKeyboardButtonResponse

class Message:

    @staticmethod
    def scoring_custom_payload(match_info):
      print("******start of scoring_custom_payload")
      output_payload = []
      current_batting_team = match_info["current_batting_team"]
      runs_scored = match_info["runs_scored"]
      running_over = match_info["running_over"]
      ball_number = match_info["ball_number"]
      strike_batsman = match_info["strike_batsman"]
      non_strike_batsman = match_info["non_strike_batsman"]
      over_status = match_info["over_status"]
      
      output_payload.append([{"text":current_batting_team+":"+str(runs_scored)+" ("+str(running_over)+"."+str(ball_number)+" overs)"}])
      output_payload.append([{"text":strike_batsman},{"text":non_strike_batsman}])
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
            "text": "0",
            "callback_data": 0
          },
          {
            "callback_data": 1,
            "text": "1"
          },
          {
            "callback_data": 2,
            "text": "2"
          }
        ],
        [
          {
            "callback_data": 3,
            "text": "3"
          },
          {
            "callback_data": 4,
            "text": "4"
          },
          {
            "callback_data": 5,
            "text": "5"
          },
          {
            "text": "6",
            "callback_data": 6
          }
        ],
        [
          {
            "callback_data": "out",
            "text": "out"
          },
           {
            "text": "strike change"
           
          },
         
        ],
        [
          {
            "callback_data": "wide",
            "text": "wide"
          }
        ],
        [
          {
            "callback_data": "no ball",
            "text": "no ball"
          }
        ]
      ]

    @staticmethod
    def match_start_payload(scoreboard_url,team1):
      return { "fullfillmentText":'user_detail', "fulfillmentMessages": [
                {
                "text": {
                    "text": [
                           "Match init success in database!\nLive score: "+scoreboard_url+"\n\Player names of "+ team1 +"? (space separated usernames)"
                        ]
                    }
                    }
                ],
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
        # tele_res = TelegramKeyboardButtonResponse ("pankaj")
        # print(json.dumps(tele_res.response))
        # return json.dumps(json.dumps(tele_res.response))
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
            #out['payload']['telegram']['reply_markup']['keyboard'].append(calback)
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
        return {"fullfillmentText":'what happened on ball 2?',"fulfillmentMessages": [
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
    def next_bowler_ask_payload(current_batting_team,running_over,ball_number,runs_scored,strike_batsman,non_strike_batsman):
        
        return {"fullfillmentText":'what happened on ball 2?',"fulfillmentMessages": [
                {
                "text": {
                    "text": [
                            "Team:"+current_batting_team+" Total: "+str(runs_scored)+"\nBall:"+str(running_over)+"."+str(ball_number)+ " recorded,"+
                            "\nBatsmen:"+strike_batsman+"(*), " +non_strike_batsman
                        ]
                    }
                    }
                ]}
        # return { "fullfillmentText":'user_detail', "fulfillmentMessages": [
        #         {
        #         "text": {
        #             "text": [
        #                    "enter next bowler name"
        #                 ]
        #             }
        #             }
        #         ]}
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