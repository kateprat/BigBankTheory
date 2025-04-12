"""
Game Player module for client verification simulation.
Handles the client data processing workflow with GameClient integration.
"""

import os
import shutil
import time
from typing import Dict, Any, Optional

from game_client import GameClient
from classifier import Classifier
import utils


class GamePlayer:
    """
    Handles the game flow for client verification, processing client data
    and making classification decisions.
    """

    def __init__(self):
        """Initialize the game player with required components and directories."""
        self.game_client = GameClient()
        self.classifier = Classifier()

        # Define working directories
        self.tmp_dir = "tmp_client/"
        self.false_neg_dir = "false_negative_client/"
        self.false_pos_dir = "false_positive_client/"

        # Ensure directories exist
        for directory in [self.tmp_dir, self.false_neg_dir, self.false_pos_dir]:
            os.makedirs(directory, exist_ok=True)

    def play(self) -> int:
        """
        Run the game loop, processing clients and submitting decisions.
        Returns the final score achieved.
        """
        if not self.game_client.start_game():
            print("Failed to start game")
            return 0

        success = True
        score = 0

        while success:
            # Get and process client data
            client_data = self.game_client.get_client_data()
            self.save_data(client_data)

            # Make classification decision
            decision = self.classifier.classify(client_path=self.tmp_dir)
            success = self.game_client.post_decision(decision=decision)

            if success:
                # Continue to next client
                score = self.game_client.get_score()
                self._cleanup_tmp_dir()
                time.sleep(0.5)
            else:
                # Game ended, save the failed client data
                target_dir = self.false_pos_dir if decision else self.false_neg_dir
                self._archive_failed_client(target_dir)
                print(
                    f"Game ended. Decision was {'correct' if not decision else 'incorrect'}"
                )

        return score

    def save_data(self, client_data: Dict[str, Any]) -> None:
        """
        Save client data files to the temporary directory.

        Args:
            client_data: Dictionary containing base64-encoded client documents
        """
        try:
            utils.save_passport_image(client_data, self.tmp_dir)
            utils.save_docx_file(client_data, self.tmp_dir)
            utils.save_pdf_file(client_data, self.tmp_dir)
            utils.save_description_txt(client_data, self.tmp_dir)
        except Exception as e:
            print(f"Error saving client data: {e}")

    def _cleanup_tmp_dir(self) -> None:
        """Remove temporary directory contents."""
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)
            os.makedirs(self.tmp_dir, exist_ok=True)

    def _archive_failed_client(self, target_dir: str) -> None:
        """
        Move failed client data to appropriate directory for later analysis.

        Args:
            target_dir: Directory to store the failed client data
        """
        try:
            # Find next available client number
            existing_clients = [
                name
                for name in os.listdir(target_dir)
                if os.path.isdir(os.path.join(target_dir, name))
                and name.startswith("client_")
            ]

            if existing_clients:
                client_nums = [
                    int(client.split("_")[1])
                    for client in existing_clients
                    if client.split("_")[1].isdigit()
                ]
                next_num = max(client_nums, default=0) + 1
            else:
                next_num = 1

            # Move client data to archive directory
            new_client_dir = f"client_{next_num}"
            dest_path = os.path.join(target_dir, new_client_dir)

            if os.path.exists(self.tmp_dir):
                shutil.move(self.tmp_dir, dest_path)
                print(f"Archived failed client to {dest_path}")

                # Recreate empty tmp directory
                os.makedirs(self.tmp_dir, exist_ok=True)
        except Exception as e:
            print(f"Error archiving failed client: {e}")


if __name__ == "__main__":
    game_player = GamePlayer()
    final_score = game_player.play()
    print(f"Game completed with score: {final_score}")
