from pathlib import Path
from llm_stuff import data_handler, markdown_rag, teacher_agent
import os
from json import loads

QUESTIONS_PROMPT = """
Based on the provided learning materials, generate exactly {questions_amount} multiple-choice questions.

Return ONLY a valid JSON array.

[
  {{
    "question": "Question text",
    "answers": [
      {{
        "content": "Answer A",
        "correct": true
      }},
      {{
        "content": "Answer B",
        "correct": false
      }},
      {{
        "content": "Answer C",
        "correct": false
      }},
      {{
        "content": "Answer D",
        "correct": false
      }}
    ],
    "image": null
  }}
]

Learning materials:

{materials}
"""

def check_output(to_check:str) -> bool:

    try:
        data = loads(to_check)
    except:
        return False
    
    if "question" in data and\
        "answers" in data:

        if len(data['answers']) == 4:
            return True
        
    return False

def parse_json(text:str) -> str:
    
    if 'json' in text:
        
        text = text.strip()[text.index('json')+3:].removesuffix('```')

    return text


def generate(path:Path) -> list:

    dl = data_handler.Data_Loader()

    documets = dl.load(path)

    print('Materials loaded!')

    db_path = f'./{os.path.dirname(path).split("/")[-1]}_db/'

    db = markdown_rag.Knowlage_Base(path=db_path)

    print('db_created!')

    db.load_documents(documets)

    ta = teacher_agent.Teacher_Agent()

    ta.add_knowlage_base(db)

    questions = []

    i = 0

    for document in documets:
        
        print(f'{i}/{len(documets)} document {document.metadata['source']} are being processed now!')
        i += 1

        response = None

        exit_loop = 0

        while not check_output(response):

            response = parse_json(ta.ask(QUESTIONS_PROMPT.format(
                materials = document.page_content,
                questions_amount = (len(document.page_content)//100)+1
            ),False)['messages'][-1].content)

            print(response)

            exit_loop += 1

            if exit_loop >= 3:
              
              print(f'{i}/{len(documets)} document {document.metadata['source']} was not processed succesfully!')
              break


        if exit_loop < 3:

            addition = loads(response)
            questions = questions + addition
            print(f'{i}/{len(documets)} document {document.metadata['source']} are processed succesfully!\n{len(addition)} questions are added!')

    print('DONE!')
    return questions

        

        




