import sys
import os
import json
from typing import Union, List

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from features.config import api_key
from features.input import get_text_from_file
from features.projection import replace_caps_and_punct
from mistralai import Mistral
from pydantic import BaseModel, Field

model = "ministral-8b-latest"
client = Mistral(api_key=api_key)

v = "01_vt"
# Read prompt from the same directory
prompt_path = os.path.join(os.path.dirname(__file__), "prompt.txt")
prompt = get_text_from_file(prompt_path, False)

# Read text from the ocr directory at the project root
texte_path = os.path.join(project_root, f"ocr/without_incomplete_entry/{v}.txt")
texte = get_text_from_file(texte_path, False)

class Intervenant(BaseModel):
    nom: str = Field(..., description="Nom (et prénom s'il existe) de l'intervenant")
    references_pages: Union[List[int], str] = Field(..., description="Liste des numéros de page où l'intervenant est référencé ou sinon <renvoi d'index>")

class IntervenantAuSenat(BaseModel):
    listes_des_intervenants: List[Intervenant] = Field(..., description="Liste de tous les intervenants avec leurs références de pages respectives")

def main():
    entries = client.chat.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": f"{prompt}"
            },
            {
                "role": "user",
                "content": texte
            },
        ],
        response_format=IntervenantAuSenat,
        max_tokens=len(texte)*2,
        temperature=0
    )
    entries_dict = json.loads(entries.choices[0].message.content)
    entry_list = IntervenantAuSenat(**entries_dict)

    output_dir = os.path.join(project_root, 'output', 'vt')
    os.makedirs(output_dir, exist_ok=True)
    # output_path = os.path.join(output_dir, f'structured{v}.json')

    with open(f"evaluations/low_without_incomplete_entry/{v}.json", 'w', encoding='utf-8') as f:
        json.dump(entry_list.model_dump(), f, ensure_ascii=False, indent=2)
    print(entries.choices[0].message.content)
    return "Success ! \n \n \n"

main()
