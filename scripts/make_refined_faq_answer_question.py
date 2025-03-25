import pickle
import json

def generate_refined_jsonl(data, output_file="faq_answer_question_pair.jsonl"):
    with open(output_file, 'w', encoding='utf-8') as f:
        for key, value in data.items():
            divided_value = value.split("\n\n\n위 도움말이 도움이 되었나요?")[0] #delete un-useful data
            question = f"{key}"
            completion = f" {divided_value}"
            json.dump({"question": question, "answer": completion}, f, ensure_ascii=False)
            f.write('\n')

    print(f"[✔] created jsonl file: {output_file}")

with open('final_result.pkl', 'rb') as f:
    data = pickle.load(f)

generate_refined_jsonl(data)