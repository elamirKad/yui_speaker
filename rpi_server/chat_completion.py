import requests


class TaggerBot:
    def __init__(self, tag_mapping):
        self.tag_mapping = tag_mapping

    def analyze_text(self, text):
        text_lower = text.lower()
        for phrase, tag in self.tag_mapping.items():
            if any(keyword in text_lower for keyword in phrase):
                return f"tag: {tag}"
        return "tag: unknown"


def send_message_to_remote_server(url, headers, character, user_message, history):
    history.append({"role": "user", "content": user_message})
    data = {
        "mode": "chat",
        "character": character,
        "messages": history
    }

    try:
        response = requests.post(url, headers=headers, json=data, verify=False)
        if response.status_code == 200:
            assistant_message = response.json()['choices'][0]['message']['content']
            history.append({"role": "assistant", "content": assistant_message})
            return assistant_message, history
        else:
            return f"Error: Received a non-200 response code: {response.status_code}", history
    except Exception as e:
        return f"An error occurred: {e}", history


def get_answer(user_message, history=None):
    if history is None:
        history = []
    url = "http://100.101.173.98:5000/v1/chat/completions"
    headers = {
        "Content-Type": "application/json"
    }
    character = "Yui"

    response, updated_history = send_message_to_remote_server(url, headers, character, user_message, history)
    # print("Response:", response)
    # print("Conversation History:", updated_history)

    custom_tags = {
        ("happy", "hehe"): "hehe",
        ("sad", "heartbroken"): "heartbroken",
        ("confused", "baffling", "puzzled"): "confused",
        ("love", "peace"): "love",
        ("angry", "mad", "furious"): "angry",
        ("excited", "thrilled", "eager"): "excited",
    }
    tags_text = ", ".join([tag for tags in custom_tags.keys() for tag in tags])
    # print("Tags:", tags_text)
    tagger_bot = TaggerBot(custom_tags)

    tag, _ = send_message_to_remote_server(url, headers, "TaggerBot", f"You: Categorize this text: ```{response}```. Use next tags: {tags_text}\n\n TaggerBot: tag: ", [{"role": "user", "content": f"You: Categorize this text: ```Just booked my dream vacation, I can hardly wait!```. Use next tags: {tags_text}\n\n TaggerBot: tag: "}, {"role": "assistant", "content": "hehe"}])
    # print(tag)
    # print(tagger_bot.analyze_text(tag))

    return {"response": response, "tag": tagger_bot.analyze_text(tag), "history": updated_history}
