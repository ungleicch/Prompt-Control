from flask import Flask, request, jsonify, render_template
import json
import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import time
import re
import difflib
from flask import send_from_directory
from data import SUBMISSIONS_FILE, MODEL_NAME, PROFILE_DIR, IMAGE_DIR, DEFAULT_PROFILE
from get_stuff import get_profiles, save_profile, load_data, save_data, load_profile, load_model
from calc import preprocess_input, process_response, generate_response

app = Flask(__name__)


@app.route('/profile/update_realtime', methods=['POST'])
def update_profile_realtime():
    data = request.json
    profile_name = data.get('profile_name')

    if not profile_name:
        return jsonify({"error": "Profile name required"}), 400

    profile = load_profile(profile_name)
    if profile:
        profile.update(data)  # Merge updated fields into profile
        save_profile(profile_name, profile)
        return jsonify({"message": "Profile updated successfully"})
    return jsonify({"error": "Profile not found"}), 404





@app.route('/profiles', methods=['GET'])
def list_profiles():
    profiles = [f.replace('.json', '') for f in os.listdir(PROFILE_DIR) if f.endswith('.json')]
    return jsonify(profiles)



@app.route('/profile/load', methods=['POST'])
def load_selected_profile():
    data = request.json
    profile_name = data.get('profile_name')
    profile = load_profile(profile_name)

    if not profile:
        return jsonify({"error": "Profile not found"}), 404

    # Ensure the image path is properly formatted
    profile['image'] = f"{profile.get('image', 'default.jpg')}"

    return jsonify(profile)



@app.route('/profile/save', methods=['POST'])
def save_selected_profile():
    data = request.json
    profile_name = data.get('profile_name')

    # Remove profile_name key before saving to file
    if 'profile_name' in data:
        del data['profile_name']

    save_profile(profile_name, data)
    return jsonify({"message": f"Profile '{profile_name}' saved successfully!"})

@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    file_path = os.path.join(IMAGE_DIR, file.filename)
    file.save(file_path)
    
    return jsonify({"message": "Image uploaded successfully", "filename": file.filename})


@app.route('/image/<filename>')
def get_image(filename):
    return send_from_directory(IMAGE_DIR, filename)




    
if not os.path.exists(SUBMISSIONS_FILE):
    save_data([], SUBMISSIONS_FILE)


model, tokenizer = load_model()

# Preprocess input for AI model


@app.route('/profile/create', methods=['POST'])
def create_profile():
    data = request.form
    profile_name = data.get('name').strip()
    
    if not profile_name:
        return jsonify({"error": "Profile name is required"}), 400
    
    profile_filename = profile_name + '.json'
    profile_path = os.path.join(PROFILE_DIR, profile_filename)

    # Handle image upload
    if 'image' in request.files:
        image_file = request.files['image']
        image_filename = f"{profile_name}.jpg"
        image_file.save(os.path.join(IMAGE_DIR, image_filename))
    else:
        image_filename = "default.jpg"

    new_profile = {
        "name": profile_name,
        "image": image_filename,
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
        "num_return_sequences": 1
    }

    with open(profile_path, 'w') as file:
        json.dump(new_profile, file, indent=4)

    return jsonify({"message": f"Profile '{profile_name}' created successfully!", "profile": new_profile})



@app.route('/profile/switch', methods=['POST'])
def switch_profile():
    data = request.json
    profile_name = data.get('profile_name') + '.json'
    if os.path.exists(os.path.join(PROFILE_DIR, profile_name)):
        profile = load_profile(profile_name)
        return jsonify(profile)
    return jsonify({"error": "Profile not found"}), 404


@app.route('/profile/update_vars', methods=['POST'])
def update_profile_vars():
    data = request.json
    profile_name = data.get('profile_name') + '.json'
    new_vars = data.get('vars', {})
    if os.path.exists(os.path.join(PROFILE_DIR, profile_name)):
        profile = load_profile(profile_name)
        profile['vars'].update(new_vars)
        save_profile(profile_name, profile)
        return jsonify({"message": "Profile updated", "profile": profile})
    return jsonify({"error": "Profile not found"}), 404


# Detect repeated prompt text and <thinking> parts in AI response


@app.route('/profile/image', methods=['POST'])
def update_profile_image():
    data = request.json
    profile_name = data.get('profile_name') + '.json'
    image_path = data.get('image')
    if os.path.exists(os.path.join(PROFILE_DIR, profile_name)):
        profile = load_profile(profile_name)
        profile['image'] = image_path
        save_profile(profile_name, profile)
        return jsonify({"message": "Profile image updated", "profile": profile})
    return jsonify({"error": "Profile not found"}), 404



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    result = generate_response(data, model, tokenizer)

    submission_entry = {
        "model_used": data.get("name", "Unknown Model"),  # Get the model name
        "user_input": result["user_input"],
        "final_prompt": result["final_prompt"],
        "ai_response": result["ai_response"],
        "repeated": result["repeated"],
        "original_response": result["original_response"],
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    submissions = load_data(SUBMISSIONS_FILE, [])
    submissions.append(submission_entry)
    save_data(submissions, SUBMISSIONS_FILE)

    return jsonify({
        "message": "Data submitted successfully!",
        "generated_response": result["ai_response"],
        "repeated": result["repeated"]
    })


@app.route('/load', methods=['GET'])
def load_default_profile():
    profiles = get_profiles()
    if profiles:
        profile = load_profile(profiles[0])  # Load first profile as default
        return jsonify(profile)
    return jsonify(DEFAULT_PROFILE)

@app.route('/get_submissions', methods=['GET'])
def get_submissions():
    submissions = load_data(SUBMISSIONS_FILE, [])
    return jsonify(submissions)

if __name__ == '__main__':
    app.run(debug=True, port=5001)