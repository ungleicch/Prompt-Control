# Constants
SUBMISSIONS_FILE = 'submissions.json'
MODEL_NAME = "mistralai/Mistral-7B-v0.1"
#MODEL_NAME = "llama3.2"
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

# dont want to interrupt the conversations
FORBIDDEN_PATTERNS = {
    r'\bgpt-?4\b': 'gpt4',
    r'\bgpt-?3\b': 'gpt3',
    r'\bgpt-?2\b': 'gpt2',
    r'\bdeepseek\b': 'deepseek',
    r'\bchat ?bot\b': 'chat bot',
    r'\bassista?nt\b': 'assistant',
    r'\bassiatiant\b': 'assiatiant',
    r'\bai\b': 'ai',
    r'\blanguage model\b': 'language model',
    r'\bopenai\b': 'openai',
    r'\bchatbot\b': 'chatbot',
    r'\blarge language model\b': 'large language model',
    r'\bloud\b': 'cloud',
    r'\b\\n\b': '\\n',
    r'\b\\Answer: \b': '\Answer:',
    r'\b\\\b': '\\',
    r'\bChatGPT\b': 'ChatGPT',
    r'\bChatGPT-3\b': 'ChatGPT-3',
    r'\bChatGPT-4\b': 'ChatGPT-4',
    r'\bChatGPT-3.5\b': 'ChatGPT-3',
    r'\bGPT\b': 'GPT',
    r'\bbot\b': 'bot'
}