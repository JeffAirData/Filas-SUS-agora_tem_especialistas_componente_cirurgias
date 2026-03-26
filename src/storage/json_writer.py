import json

def write_to_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

def append_to_json(data, file_path):
    try:
        with open(file_path, 'r+', encoding='utf-8') as json_file:
            existing_data = json.load(json_file)
            existing_data.append(data)
            json_file.seek(0)
            json.dump(existing_data, json_file, ensure_ascii=False, indent=4)
    except FileNotFoundError:
        write_to_json([data], file_path)