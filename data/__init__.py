import json

next_move_dataset = []


def save_to_jsonl(data, file_path):
    with open(file_path, 'a', encoding='utf-8') as f:
        for entry in data:
            json.dump(entry, f, ensure_ascii=False)
            f.write('\n')


def save_to_json_list(data, file_path):
    with open(file_path, 'a', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
