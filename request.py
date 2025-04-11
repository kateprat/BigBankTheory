import requests
import base64

start_url = "https://hackathon-api.mlo.sehlat.io/game/start"
decision_url = "https://hackathon-api.mlo.sehlat.io/game/decision"


API_KEY = "8Uy75OhFF7FGJPIv2Ae_gtFdoCwpRo8VBQvzZrmrfc4"

headers = {
    "X-Api-Key": "8Uy75OhFF7FGJPIv2Ae_gtFdoCwpRo8VBQvzZrmrfc4",
    "accept": "application/json",
    "Content-Type" : "application/json"
}

start_payload = {
  "player_name": "BigBank Theory"
}


# Send the POST request
response = requests.post(start_url, json=start_payload, headers=headers)

if response.status_code == 200:
    data = response.json()  
    client_id = data.get("client_id")  
    session_id = data.get("session_id")
    score = data.get("score")
    documents = data.get("client_data", {})

    # if 'passport' in documents:
    #     with open("passport.png", "wb") as file:
    #         file.write(base64.b64decode(documents['passport']))

    # if 'profile' in documents:
    #     with open("profile.docx", "wb") as file:
    #         file.write(base64.b64decode(documents['profile']))

    # if 'account' in documents:
    #     with open("account_opening_form.pdf", "wb") as file:
    #         file.write(base64.b64decode(documents['account']))

    # if 'description' in documents:
    #     with open("description.txt", "wb") as file:
    #         file.write(base64.b64decode(documents['description']))

    # print(f"Client ID: {client_id}")
    # print(f"Session ID: {session_id}")
    # print(f"score: {score}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)

while True: 
    decision_payload = {
        "decision" : "Accept", 
        "session_id": session_id, 
        "client_id" : client_id
    }

    response = requests.post(decision_url, json=decision_payload, headers=headers)

    if response.status_code == 200:
        
        data = response.json()  
        score_after = data.get("score")

        client_id = data.get("client_id")  
        print(f"Client ID: {client_id}")
        print(f"score after decision: {score_after}")

        if data.get("status") == "gameover" : 

            documents = data.get("client_data", {})

            if 'passport' in documents:
                with open("passport.png", "wb") as file:
                    file.write(base64.b64decode(documents['passport']))

            if 'profile' in documents:
                with open("profile.docx", "wb") as file:
                    file.write(base64.b64decode(documents['profile']))

            if 'account' in documents:
                with open("account_opening_form.pdf", "wb") as file:
                    file.write(base64.b64decode(documents['account']))

            if 'description' in documents:
                with open("description.txt", "wb") as file:
                    file.write(base64.b64decode(documents['description']))

            break
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        break