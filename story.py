import json
from typing import Optional, TypedDict, List, Union
import uuid


class ChoiceDict(TypedDict):
  text: str


class Scene:
  def __init__(self, text, parent_choice: Union['Choice', None], child_choices: List['Choice']) -> None:
      self.text = text
      self.id = str(uuid.uuid4())
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

  def to_dict(self): # Added
    """Converts the scene and its children to a dictionary."""
    return {
      "id": self.id,
      "text": self.text,
      "child_choices": [choice.to_dict() for choice in self.child_choices]
    }



class Choice:
  def __init__(self, text: str, parent_scene: Scene, child_scene: Optional[Scene] = None) -> None:
    self.text = text
    self.parent_scene = parent_scene
    self.child_scene = child_scene
    self.id = str(uuid.uuid4())

  def to_dict(self): # Added
    """Converts the choice and its child scene to a dictionary."""
    return {
      "id": self.id,
      "text": self.text,
      "child_scene": self.child_scene.to_dict() if self.child_scene else None
    }