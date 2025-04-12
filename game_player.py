from client import GameClient
from classifier import Classifier
import utils
import shutil
import os

class GamePlayer :
    def __init__(self) :
        self.game_client = GameClient()
        self.classifier = Classifier()
        
        self.tmp_dir = "tmp_client/"
        self.false_neg_dir = "false_negative_client/"
        self.false_pos_dir = "false_positive_client/"
    
    def play(self) :
        if not self.game_client.start_game() :
            return
        
        success = True
        score = 0
        
        while success :
            client_data = self.game_client.get_client_data()
            self.save_data(client_data=client_data)
            
            decision = self.classifier.classify(client_path=self.tmp_dir)
            success = self.game_client.post_decision(decision=decision)
            
            if success :
                score = self.game_client.get_score()
                shutil.rmtree(self.tmp_dir)
            else :
                dir_name = self.false_pos_dir if decision else self.false_neg_dir
                self.move_client(dir_name)
                
        print(f"Score = {score}")
        
    def save_data(self, client_data):
        utils.save_passport_image(client_data, self.tmp_dir)
        utils.save_docx_file(client_data, self.tmp_dir)
        utils.save_pdf_file(client_data, self.tmp_dir)
        utils.save_description_txt(client_data, self.tmp_dir)
        
    def move_client(self, into_dir) :
        os.makedirs(into_dir, exist_ok=True)

        existing = [name for name in os.listdir(into_dir) 
                    if os.path.isdir(os.path.join(into_dir, name)) 
                    and name.startswith("client_")]
        nums = [int(e.split("_")[1]) for e in existing]
        next_num = str(max(nums, default=0) + 1)
        
        new_name = f"client_{next_num}"
        dest_path = os.path.join(into_dir, new_name)

        shutil.move(self.tmp_dir, dest_path)
        


if __name__ == "__main__" :
    gp = GamePlayer()
    gp.play()