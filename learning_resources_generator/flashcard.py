from llm_stuff.teacher_agent import Teacher_Agent
from learning_resources_generator.util import parse_json
from json import loads

FLASHCARDS_PROMPT = """
Based on the provided learning materials, generate flashcards.

Return ONLY a valid JSON array.

{{
    "head 1":"back 1",
    "head 2":"back 2",
    ...
}}

Learning materials:

{materials}
"""

def check_output(to_check:str) -> bool:

    try:
        data = loads(to_check)
    except:
        return False
        
    return isinstance(data,dict)

def generate(documents:list,agent:Teacher_Agent) -> list:

    flashcards = []

    i = 0

    for document in documents:
        
        print(f'{i}/{len(documents)} document {document.metadata['source']} are being processed now!')
        i += 1

        response = None

        exit_loop = 0

        while not check_output(response):

            response = parse_json(agent.ask(FLASHCARDS_PROMPT.format(
                materials = document.page_content,
            ),False)['messages'][-1].content)

            print(response)

            exit_loop += 1

            if exit_loop >= 3:
              
              print(f'{i}/{len(documents)} document {document.metadata['source']} was not processed succesfully!')
              break


        if exit_loop < 3:

            addition = loads(response)
            flashcards = flashcards + addition
            print(f'{i}/{len(documents)} document {document.metadata['source']} are processed succesfully!\n{len(addition)} flashcards are added!')

    print('DONE!')
    return flashcards

        

        




