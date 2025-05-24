from chatbot import ChatBot, generate_description, generate_story_metadata
from parse_arguments import parse_args
import logging
import json
import random
from story import Scene
import time # Added
import os # Added

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger(__name__)

args = parse_args()

# --- ChatBot and Probabilities Setup (as before) ---
light_weight_chatbot = ChatBot("Qwen/Qwen3-1.7B")
chatbot = ChatBot("Qwen/Qwen3-4B")
_choices_probabilities = args.leaf_probabilities
_choices_probabilities = [tuple(map(float, choice.split(':'))) for choice in _choices_probabilities]
choices_probabilities = {int(k): v for k, v in _choices_probabilities}
choices_probabilities[1] = 1 - sum(choices_probabilities.values())
logger.info("Choices Probabilities: %s", choices_probabilities)
# --- Description and Metadata Setup (as before) ---
description = args.description
if description is None:
    logger.info("No description provided. Generating our own...")
    description = generate_description(light_weight_chatbot)
logger.info("Description: %s", description)
story_metadata = generate_story_metadata(chatbot, description)
logger.info("Story Metadata: %s", story_metadata)
# --- First Scene Setup (as before) ---
first_introduction_scene = Scene.build_scene(
    text=story_metadata['first_introduction_scene']['text'],
    parent_choice=None,
    child_choices=[{"text": story_metadata['first_introduction_scene']['choice']}]
)
# --- Templates (as before) ---
USER_FIRST_MESSAGE_TEMPLATE = (
  "Generate the first scene (1/{n_scene_total}) with 1 choice!"
)
USER_MESSAGE_TEMPLATE = (
  "Player proceeds with \"{choice}\". "
  "Generate next scene ({n_scene}/{n_scene_total}) with {n_choices} choice(s)!"
)
USER_FINAL_MESSAGE_TEMPLATE = (
  "Player proceeds with \"{choice}\". "
  "Generate final scene ({n_scene}/{n_scene_total}) with 1 choice to end the story!"
)

# --- Added: Story State Saving ---
STORY_STATE_FILE = "story_state.json"

def save_story_state(root_scene: Scene, current_id: str | None = None, last_added_id: str | None = None):
    """Saves the current story tree and metadata to a JSON file."""
    state = {
        "story_tree": root_scene.to_dict(),
        "metadata": {
            "current_id": current_id, # Can be scene or choice ID
            "last_added_id": last_added_id,
            "timestamp": time.time()
        }
    }
    try:
        # Write to temp and replace for atomicity (optional but safer)
        temp_file = STORY_STATE_FILE + ".tmp"
        with open(temp_file, 'w') as f:
            json.dump(state, f, indent=4)
        os.replace(temp_file, STORY_STATE_FILE)
        logger.info(f"Story state saved. Current: {current_id}, Added: {last_added_id}")
    except Exception as e:
        logger.error(f"Failed to save story state: {e}")

# --- Modified: build_story ---
def build_story(scene: Scene, n_scene_total: int, root_scene: Scene) -> None: # Pass root_scene
  messages = []
  curr_scene: Scene = scene
  while True:
    if curr_scene.parent_choice is None:
      messages = [{"role": "assistant", "content": str(curr_scene)}] + messages
      break
    messages = [
      {
        "role": "user",
        "content": USER_MESSAGE_TEMPLATE.format(
          choice=curr_scene.parent_choice.text,
          n_scene="{n_scene}",
          n_scene_total=n_scene_total,
          n_choices=len(curr_scene.child_choices),
        )
      },
      {"role": "assistant", "content": str(curr_scene)},
    ] + messages
    curr_scene = curr_scene.parent_choice.parent_scene

  messages = [
    {"role": "system", "content": (
      "You're best story teller. Given the story metadata:\n"
      f"{json.dumps(story_metadata)}\n\n"
      f"You will create a story with {n_scene_total} scenes.\n"
      "IMPORTANT: you output only valid json of the following format:\n"
      '{"text": "<scene description>", "choices": [{"text": "<choice description>"}, ...]}'
    )},
    {"role": "user", "content": USER_FIRST_MESSAGE_TEMPLATE.format(n_scene_total=n_scene_total)},
  ] + messages

  n_scene = 0
  for message in messages:
    if message["role"] == "user":
      n_scene += 1
      message["content"] = message["content"].format(n_scene=n_scene)

  if n_scene == n_scene_total:
      save_story_state(root_scene, current_id=scene.id) # Added save
      return

  n_scene = n_scene + 1

  for choice in scene.child_choices:
    save_story_state(root_scene, current_id=choice.id) # Added save + highlight choice
    time.sleep(0.5) # Added delay

    n_choices = 1
    if n_scene != n_scene_total:
      n_choices = random.choices(
        list(choices_probabilities.keys()),
        weights=list(choices_probabilities.values()),
      k=1)[0]
    curr_messages = messages + [{
      "role": "user",
      "content": USER_FINAL_MESSAGE_TEMPLATE.format(
        choice=choice.text,
        n_scene=n_scene,
        n_scene_total=n_scene_total
      )
    } if n_scene == n_scene_total else {"role": "user", "content": USER_MESSAGE_TEMPLATE.format(
      n_scene=n_scene,
      n_scene_total=n_scene_total,
      choice=choice.text,
      n_choices=n_choices
    )}]

    while True:
      save_story_state(root_scene, current_id=choice.id) # Added save (still processing choice)
      try:
        scene_string = (chatbot.prompt if n_scene < 3 else light_weight_chatbot.prompt)(curr_messages)
        logger.info(f"{scene_string = }")
        curr_messages.append({"role": "assistant", "content": scene_string})
        scene_json = json.loads(scene_string)
        logger.info(f"{n_choices = } | {n_scene = } | {scene_json = }")
        
        child_scene = Scene.build_scene(
            text=scene_json["text"],
            parent_choice=choice,
            child_choices=scene_json["choices"]
        )
        choice.child_scene = child_scene
        save_story_state(root_scene, current_id=choice.id, last_added_id=child_scene.id) # Added save + highlight new scene
        time.sleep(1) # Added delay

        build_story(child_scene, n_scene_total, root_scene) # Pass root_scene
        break
      except json.JSONDecodeError as e:
        logger.error(e)
        curr_messages.append({"role": "user", "content": f"json.JSONDecodeError: {str(e)}\nPlease output a valid json."})
        time.sleep(1) # Added delay on error


if __name__ == "__main__":
    # Ensure the state file exists initially or is cleaned
    if os.path.exists(STORY_STATE_FILE):
        os.remove(STORY_STATE_FILE)
    save_story_state(first_introduction_scene, current_id=first_introduction_scene.id) # Save initial state
    build_story(first_introduction_scene, args.n_scenes, first_introduction_scene)
    save_story_state(first_introduction_scene) # Save final state
    logger.info("Story generation complete.")