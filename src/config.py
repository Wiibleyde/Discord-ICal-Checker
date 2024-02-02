import yaml
import os

class Config:
    def __init__(self, path:str='config.yaml'):
        self.default = {
            'bot_token': 'YOUR_BOT_TOKEN',
            'calendar_url': 'YOUR_CALENDAR_URL',
        }
        self.path = path
        self.config = self.load_config()

    def load_config(self):
        if not os.path.exists(self.path):
            self.create_config()
        with open(self.path, "r") as f:
            return yaml.load(f, Loader=yaml.FullLoader)

    def create_config(self):
        with open(self.path, "w") as f:
            yaml.dump(self.default, f, default_flow_style=False)

    def save_config(self):
        with open(self.path, "w") as f:
            yaml.dump(self.config, f, default_flow_style=False)

    def get(self, key):
        return self.config[key]
    
    def set(self, key, value):
        self.config[key] = value
        self.save_config()

    def __getitem__(self, key):
        return self.config[key]
    
    def __setitem__(self, key, value):
        self.config[key] = value
        self.save_config()