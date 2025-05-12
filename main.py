from chatbot import ChatBot, generate_description, generate_story_metadata
from parse_arguments import parse_args
import logging
from story import Scene, Choice


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger(__name__)

args = parse_args()

light_weight_chatbot = ChatBot("Qwen/Qwen3-1.7B")
chatbot = ChatBot("Qwen/Qwen3-4B")

# --leaf-probabilities
choices_probabilities = args.leaf_probabilities
choices_probabilities = [tuple(map(float, choice.split(':'))) for choice in choices_probabilities]
choices_probabilities = {int(k): v for k, v in choices_probabilities}
choices_probabilities[1] = 1 - sum(choices_probabilities.values())
logger.info("Choices Probabilities: %s", choices_probabilities)

description = args.description
if description is None:
    logger.info("No description provided. Generating our own...")
    description = generate_description(light_weight_chatbot)

logger.info("Description: %s", description)
story_metadata = generate_story_metadata(chatbot, description)
logger.info("Story Metadata: %s", story_metadata)


first_introduction_scene = Scene.build_scene(
    text=story_metadata['first_introduction_scene']['text'],
    parent_choice=None,
    child_choices=[{"text": story_metadata['first_introduction_scene']['choice']}]
)

