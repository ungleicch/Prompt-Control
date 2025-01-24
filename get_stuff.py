import json
import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from config import PROFILE_DIR, DEFAULT_PROFILE, MODEL_NAME

def get_profiles():
    profiles = [f for f in os.listdir(PROFILE_DIR) if f.endswith('.json')]
    return profiles if profiles else None

def save_profile(profile_name, profile_data):
    profile_path = os.path.join(PROFILE_DIR, profile_name + '.json')
    for key, value in profile_data.items():
        if value == "undefined":
            profile_data[key] = ""
    with open(profile_path, 'w') as file:
        json.dump(profile_data, file, indent=4)

def load_data(filename, default_value=None):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            try:
                return json.load(file) or default_value
            except json.JSONDecodeError:
                return default_value
    return default_value

def save_data(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def load_profile(profile_name):
    profile_path = os.path.join(PROFILE_DIR, profile_name + '.json')
    if os.path.exists(profile_path):
        with open(profile_path, 'r') as file:
            profile = json.load(file)
            profile['image'] = profile.get('image', 'default.jpg')
            return profile
    return DEFAULT_PROFILE

def load_model():
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME, 
            device_map="mps", 
            torch_dtype=torch.bfloat16
        ).to("mps")
        return model, tokenizer
    except Exception as e:
        raise RuntimeError(f"Model loading failed: {e}")