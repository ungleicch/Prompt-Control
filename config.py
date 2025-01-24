# Configuration constants
DATA_FILE = 'data.json'
SUBMISSIONS_FILE = 'submissions.json'
MODEL_NAME = "mistralai/Mistral-7B-v0.1"
PROFILE_DIR = 'profiles/'
IMAGE_DIR = 'static/images/'

DEFAULT_PROFILE = {
    "name": "",
    "tone": "",
    "interests": "",
    "background": "",
    "mood": "",
    "response_style": "",
    "preferences": "",
    "input_text": "",
    "temperature": 0.7,
    "max_length": 150,
    "top_k": 50,
    "top_p": 0.9,
    "repetition_penalty": 1.2,
    "num_return_sequences": 1,
    "image": "default.jpg"
}