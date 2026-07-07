from learning_resources_generator import questions
from json import dumps

if __name__ == '__main__':

    data = questions.generate('./test_data/')

    with open('./testowe.json','w+',encoding="UTF-8") as file:

        file.write(dumps(data,indent=4))