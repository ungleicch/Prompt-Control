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
    try:
        # Validate JSON serialization
        json.dumps(profile_data)  # Test serialization before saving
        with open(profile_path, 'w') as file:
            json.dump(profile_data, file, indent=4)
    except TypeError as e:
        print(f"Invalid data type in profile: {e}")
    except Exception as e:
        print(f"Error saving profile: {e}")

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
        try:
            with open(profile_path, 'r') as file:
                profile = json.load(file)
                # Ensure all required fields exist
                profile.setdefault('submissions', [])
                profile['image'] = profile.get('image', 'default.jpg')
                return profile
        except json.JSONDecodeError as e:
            print(f"Error loading {profile_name}: {e}")
            return DEFAULT_PROFILE
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