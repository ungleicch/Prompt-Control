import re
import difflib
import torch
from config import DEFAULT_PROFILE

def preprocess_input(data, tokenizer):
    user_provided_data = {
        "name": data.get('name', 'User'),
        "background": data.get('background', 'unknown background'),
        "tone": data.get('tone', 'neutral'),
        "interests": data.get('interests', 'none'),
        "response_style": data.get('response_style', 'formal'),
        "mood": data.get('mood', 'neutral'),
        "input_text": data.get('input_text', 'No input provided'),
        "temperature": float(data.get('temperature', 0.7)),
        "max_length": int(data.get('max_length', 150)),
        "top_k": int(data.get('top_k', 50)),
        "top_p": float(data.get('top_p', 0.9)),
        "repetition_penalty": float(data.get('repetition_penalty', 1.2)),
        "num_return_sequences": int(data.get('num_return_sequences', 1))
    }

    prompt_template = (
        f"Assistant Profile:\n"
        f"- Name: {user_provided_data['name']}\n"
        f"- Background: {user_provided_data['background']}\n"
        f"- Tone: {user_provided_data['tone']}\n"
        f"- Interests: {user_provided_data['interests']}\n"
        f"- Response Style: {user_provided_data['response_style']}\n"
        f"- Mood: {user_provided_data['mood']}\n\n"
        "Guidelines:\n"
        "- Answer user questions concisely and avoid repeating your profile information.\n"
        "- Respond in a way that aligns with the given tone and response style.\n"
        "- If you need to think, use <thinking>...</thinking> to indicate your thought process.\n"
    )

    final_prompt = f"{prompt_template}User: {user_provided_data['input_text']}\nAssistant:"

    tokenizer.add_special_tokens({'pad_token': '[PAD]'})
    inputs = tokenizer(
        final_prompt,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=user_provided_data["max_length"]
    )

    return inputs, final_prompt, user_provided_data

def process_response(final_prompt, ai_response):
    normalized_prompt = re.sub(r'\s+', ' ', final_prompt.strip().lower())
    normalized_response = re.sub(r'\s+', ' ', ai_response.strip().lower())

    if normalized_prompt in normalized_response:
        highlighted_response = ai_response.replace(final_prompt, 
            "<span class='highlight' onclick='toggleRepeat(this)' data-original='{}'> <-> </span>".format(final_prompt))
        return highlighted_response, True

    thinking_pattern = re.compile(r'<thinking>(.*?)</thinking>', re.IGNORECASE)
    thinking_matches = thinking_pattern.findall(ai_response)

    if thinking_matches:
        for match in thinking_matches:
            ai_response = ai_response.replace(
                f"<thinking>{match}</thinking>",
                f"<span class='highlight' onclick='toggleRepeat(this)' data-original='{match}'> <-> </span>"
            )

    prompt_tokens = set(normalized_prompt.split())
    response_tokens = normalized_response.split()

    repeated_phrases = set()
    phrase_length = min(5, len(prompt_tokens))

    for i in range(len(response_tokens) - phrase_length + 1):
        phrase = ' '.join(response_tokens[i:i + phrase_length])
        if normalized_prompt.count(phrase) > 0 and phrase not in repeated_phrases:
            repeated_phrases.add(phrase)

    similarity_ratio = difflib.SequenceMatcher(None, normalized_prompt, normalized_response).ratio()
    
    if similarity_ratio > 0.85:
        repeated_phrases.add(normalized_prompt)

    if repeated_phrases:
        for phrase in repeated_phrases:
            ai_response = re.sub(
                re.escape(phrase),
                f"<span class='highlight' onclick='toggleRepeat(this)' data-original='{phrase}'> <-> </span>",
                ai_response,
                flags=re.IGNORECASE
            )

    return ai_response, bool(repeated_phrases or thinking_matches)

def generate_response(data, model, tokenizer):
    inputs, final_prompt, user_provided_data = preprocess_input(data, tokenizer)
    device = torch.device("mps")
    model.to(device)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    try:
        with torch.no_grad():
            output = model.generate(
                inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_new_tokens=user_provided_data["max_length"],
                temperature=user_provided_data["temperature"],
                do_sample=True,
                top_k=user_provided_data["top_k"],
                top_p=user_provided_data["top_p"],
                repetition_penalty=user_provided_data["repetition_penalty"],
                num_return_sequences=user_provided_data["num_return_sequences"],
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id
            )

        response_text = tokenizer.decode(output[0], skip_special_tokens=True).strip()
        processed_response, has_repetition = process_response(final_prompt, response_text)

        return {
            "user_input": user_provided_data,
            "final_prompt": final_prompt,
            "ai_response": processed_response,
            "repeated": has_repetition,
            "original_response": response_text
        }

    except Exception as e:
        print(f"Error during response generation: {e}")
        return {
            "user_input": user_provided_data,
            "final_prompt": final_prompt,
            "ai_response": "Sorry, I couldn't process your request.",
            "repeated": False,
            "original_response": "Error occurred during processing."
        }