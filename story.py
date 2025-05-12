import json
from typing import Optional, TypedDict, List, Union


class ChoiceDict(TypedDict):
  text: str


class Scene:
  def __init__(self, text, parent_choice: Union['Choice', None], child_choices: List['Choice']) -> None:
      self.text = text
      self.child_choices = child_choices
      self.parent_choice = parent_choice

  def __str__(self) -> str:
      return json.dumps({
          "text": self.text,
          "choices": [{"text": choice.text for choice in self.child_choices}]
      })

  def __repr__(self) -> str:
      return self.__str__()

  @staticmethod
  def build_scene(text, parent_choice: Union['Choice', None], child_choices: List[ChoiceDict]):
    scene = Scene(text, parent_choice, [])
    for choice in child_choices:
      scene.child_choices.append(Choice(choice["text"], scene))
    return scene



class Choice:
  def __init__(self, text: str, parent_scene: Scene, child_scene: Optional[Scene] = None) -> None:
     self.text = text
     self.parent_scene = parent_scene
     self.child_scene = child_scene