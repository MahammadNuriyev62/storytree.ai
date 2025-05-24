import torch
from transformers import AutoModelForCausalLM, AutoTokenizer 
import re
import json

class ChatBot:
    def __init__(self, model_name="Qwen/Qwen3-0.6B"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto", torch_dtype=torch.bfloat16)

    def prompt(self, messages):
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )

        inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)
        response_ids = self.model.generate(**inputs, max_new_tokens=2048)[0][len(inputs.input_ids[0]):].tolist()
        response = self.tokenizer.decode(response_ids, skip_special_tokens=True)

        return response


def generate_description(chatbot: ChatBot):
    description = chatbot.prompt([
        {"role": "system", "content": "You're best story teller."},
        {"role": "user", "content": "Give me 2-3 sentence story description"},
        {"role": "assistant", "content": "In the darkest depths of the ocean, Iroh the Diver stumbles upon the ruins of a long-lost civilization and unearths secrets guarded for millennia. Joined by mythical beings and a legendary captain, he must navigate ancient magic, monstrous guardians, and mysterious alliances to uncover the truth of Atlantis."},
        {"role": "user", "content": "Give me another 2-3 sentence story description"},
    ])
    return description

story_example = {
    "title": "Deep under ocean",
    "description": "Story about a deep-sea diver who discovers an ancient civilization and meets interesting creatures.",
    "characters": [
        {
            "name": "Iroh the Diver",
            "role": "Diver",
            "traits": ["brave", "curious", "adventurous"],
            "description": "A skilled diver who is determined to explore the depths of the ocean and uncover its secrets.",
            "isMain": True
        },
        {
            "name": "Captain Nemo",
            "role": "Captain of the Nautilus",
            "traits": ["brave", "adventurous", "intelligent"],
            "description": "A legendary captain who has explored the ocean for years and knows its secrets. Not a normal human anymore.",
            "isMain": False
        },
        {
            "name": "Maria",
            "role": "Former Queen of Atlantis",
            "traits": ["wise", "mysterious", "elegant", "sexy", "passionate"],
            "description": "The former queen of Atlantis who has been transformed into a mermaid. She is wise and mysterious, with a deep connection to the ocean.",
            "isMain": False
        },
        {
            "name": "Monster of the Deep",
            "role": "Guardian of Atlantis",
            "traits": ["fearsome", "ancient", "powerful", "dangerous"],
            "description": "A fearsome creature that guards the entrance to Atlantis. It is ancient and powerful, with a deep connection to the ocean.",
            "isMain": False
        }
    ],
    "worldview": {
        "setting": "The story takes place in the depths of the ocean, where Iroh discovers an ancient civilization and meets interesting creatures.",
        "timePeriod": "Modern day",
        "technologyLevel": "Advanced technology for diving and exploration, but the civilization is ancient.",
        "magicSystem": "The ocean has its own magic, with creatures and phenomena that defy explanation. The civilization has its own ancient magic that is tied to the ocean."
    },
    "themes": [
        "Exploration",
        "Adventure",
        "Discovery",
        "Mystery",
        "Transformation"
    ],
    "first_introduction_scene": {
        "text": "Iroh the Diver is preparing for his dive into the depths of the ocean. He is excited and nervous, knowing that he is about to embark on an adventure of a lifetime.",
        "choice": "Dive into the ocean"
    }
}

def generate_story_metadata(chatbot: ChatBot, description: str):
    story_metadata = chatbot.prompt([
        {"role": "system", "content": "You only output valid JSON."},
        {"role": "user", "content": "Output the complete json (ONLY JSON) for interactive story quest with the following description: In the darkest depths of the ocean, Iroh the Diver stumbles upon the ruins of a long-lost civilization and unearths secrets guarded for millennia. Joined by mythical beings and a legendary captain, he must navigate ancient magic, monstrous guardians, and mysterious alliances to uncover the truth of Atlantis."},
        {"role": "assistant", "content": json.dumps(story_example)},
        {"role": "user", "content": f"Output the complete json for interactive story quest with the following description: {description}"},
    ])

    try:
        return json.loads(story_metadata)
    except:
        try:
            return dict(story_metadata)
        except:
            return story_metadata
