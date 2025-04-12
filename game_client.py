import os
import time
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class GameClient:
    def __init__(self):
        self.api_key = os.getenv("API_KEY")
        self.player_name = os.getenv("PLAYER_NAME", "DefaultPlayer")
        self.base_url = "https://hackathon-api.mlo.sehlat.io"
        self.session_data = {}

        self.headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key,
        }

    def start_game(self):
        url = f"{self.base_url}/game/start"
        payload = {"player_name": self.player_name}

        try:
            logging.info("Starting the game...")
            response = requests.post(url, json=payload, headers=self.headers)

            if not response.text.strip():
                logging.warning("Empty response body.")
                return False

            data = response.json()
            required_keys = {
                "message",
                "session_id",
                "player_id",
                "client_id",
                "client_data",
                "score",
            }

            if not required_keys.issubset(data):
                logging.warning("Invalid response structure.")
                return False

            self.session_data = data
            logging.info(f"Message: {data['message']}")
            return True

        except ValueError:
            logging.error("Invalid JSON response.")
            logging.debug(f"Response text: {response.text}")
        except requests.RequestException as e:
            logging.error(f"Request error: {e}")

        return False

    def post_decision(self, decision: bool):
        if not self.session_data:
            logging.error("Game not started.")
            return False

        url = f"{self.base_url}/game/decision"
        payload = {
            "decision": "Accept" if decision else "Reject",
            "session_id": self.get_session_id(),
            "client_id": self.get_client_id(),
        }

        try:
            logging.info(f"Posting decision: {payload['decision']}")
            response = requests.post(url, json=payload, headers=self.headers)

            if not response.text.strip():
                logging.warning("Empty response body.")
                return False

            data = response.json()
            if data.get("status") == "active":
                self.session_data.update(
                    {
                        "score": data["score"],
                        "client_id": data["client_id"],
                        "client_data": data["client_data"],
                    }
                )
                logging.info("Decision accepted.")
                return True

            logging.warning("Game over.")
            return False

        except ValueError:
            logging.error("Invalid JSON response.")
            logging.debug(f"Response text: {response.text}")
        except requests.RequestException as e:
            logging.error(f"Request error: {e}")

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
        logging.info(
            f"Session ID: {gc.get_session_id()} | Player ID: {gc.get_player_id()}"
        )

        decision = True
        while gc.post_decision(decision):
            time.sleep(1.0)
