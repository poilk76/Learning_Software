def parse_json(text:str) -> str:
    
    if 'json' in text:
        
        text = text.strip()[text.index('json')+3:].removesuffix('```')

    return text