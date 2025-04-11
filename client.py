import requests
import os
import logging
import time
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GameClient:
    def __init__(self):
        self.api_key = os.getenv("API_KEY")
        self.player_name = os.getenv("PLAYER_NAME", "DefaultPlayer")
        self.base_url = "https://hackathon-api.mlo.sehlat.io"
        self.session_data = {}

        self.headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key
        }

    def start_game(self):
        url = f"{self.base_url}/game/start"
        payload = {"player_name": self.player_name}

        try:
            logging.info("Starting the game...")
            response = requests.post(url, json=payload, headers=self.headers)
            logging.info(f"Status code: {response.status_code}")

            if response.text.strip():
                try:
                    data = response.json()

                    if all(key in data for key in ["message", "session_id", "player_id", "client_id", "client_data", "score"]):
                        self.session_data = data
                        logging.info(f"Message: {data["message"]}")
                        return True
                    else:
                        logging.warning("Invalid response structure.")
                        return False
                except ValueError:
                    logging.error("Response is not valid JSON.")
                    logging.debug(f"Response Text: {response.text}")
                    return False
            else:
                logging.warning("Empty response body.")
                return False

        except requests.RequestException as e:
            logging.error(f"An error occurred: {e}")
            return False

    def post_decision(self, decision : bool):
        if not self.session_data:
            logging.error("No game session available. Please start the game first.")
            return False

        url = f"{self.base_url}/game/decision"
        str_decision = "Accept" if decision else "Reject"
        
        payload = {
            "decision": str_decision,
            "session_id": self.get_session_id(),
            "client_id": self.get_client_id()
        }

        try:
            logging.info(f"Posting decision: {decision}")
            response = requests.post(url, json=payload, headers=self.headers)
            logging.info(f"Status code: {response.status_code}")

            if response.text.strip():
                try:
                    data = response.json()
                    status = data.get("status", "gameover")

                    if status == "active":
                        self.session_data["score"] = data["score"]
                        self.session_data["client_id"] = data["client_id"]
                        self.session_data["client_data"] = data["client_data"]
                        logging.info(f"Decision posted successfully: {status}")
                        return True
                    else:
                        logging.warning(f"Game over.")
                        return False
                except ValueError:
                    logging.error("Response is not valid JSON.")
                    logging.debug(f"Response Text: {response.text}")
                    return False
            else:
                logging.warning("Empty response body when posting decision.")
                return False

        except requests.RequestException as e:
            logging.error(f"An error occurred while posting decision: {e}")
            return False

    def get_session_id(self):
        return self.session_data.get("session_id")

    def get_player_id(self):
        return self.session_data.get("player_id")
    
    def get_client_id(self):
        return self.session_data.get("client_id")
    
    def get_client_data(self):
        return self.session_data.get("client_data")

    def get_score(self):
        return self.session_data.get("score", 0)

if __name__ == "__main__":
    gc = GameClient()

    if gc.start_game():
        logging.info(f"Game started. Session ID: {gc.get_session_id()}, Player ID: {gc.get_player_id()}")
        
        decision = True
        while 1 :
            success = gc.post_decision(decision=decision)
            if not success:
                break
            
            time.sleep(1.5)
