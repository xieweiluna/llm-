import json
from config import args
from extracter import get_precision, extract_answer
from prompt import get_prompt, construct_input
from prediction_runner import basic_runner
from utils import write_json, print_now, load_data, print_exp, mkpath

now = print_now(1).split(' ')[0].replace('/', '-')

Result_Folder = 'results/{}'.format(now)
mkpath('results')
mkpath(Result_Folder)
mkpath(f'{Result_Folder}/gsm8k')

Decoder_Error_File = f'{Result_Folder}/{args.learning_type}-gsm8k-{args.prompt_id}-{args.engine}_deco.json'
Predict_File = f'{Result_Folder}/gsm8k/{args.learning_type}-{args.prompt_id}-{args.engine}.json'

prompt_map = {
    "101": "COT-逐步思考",
    "201": "PS-计划解决",
    "301": "PS+-变量计划",
    "302": "PS+-完整计划",
    "303": "PS+-简洁计划",
    "304": "PS+-子问题",
    "305": "PS+-完整计划",
    "306": "PS+-信息计划",
    "307": "PS+-完整计划",
    "401": "POT-编程概念"
}

def zero_shot_cot():
    correct = 0
    question, answer, ids = load_data(args)
    total = len(question)
    prompt_id = str(args.prompt_id)
    prompt_mode = prompt_map.get(prompt_id, f"Unknown Prompt ID: {prompt_id}")
    _, prompt = get_prompt()
    all_predictions = []
    for idx, element in enumerate(question):
        inputs = construct_input(prompt, element)
        try:
            get_result, pred, error_msg = basic_runner(args, inputs, args.max_length_cot)
        except Exception as e:
            decode_error_data = {
                'question': question[idx]
            }
            write_json(decode_error_data, Decoder_Error_File)
            print(
                f"Warning: an error raised when predicting (question id: {ids[idx]}). "
                f"ERROR: {getattr(e.__class__, '__name__')}:{str(e)}"
            )
            continue
        if not get_result:
            print(
                f"Warning: not get predicted result (question id: {ids[idx]})."
                f"ERROR Message: {error_msg if error_msg else None}"
            )
            continue

        if 'Therefore, the answer is' in pred or 'The answer is' in pred :
            if 'The answer is' in pred:
                pred2 = pred.split('The answer is')[-1]
            else:
                pred2 = pred.split('the answer is')[-1]
            try:
                pred_answer = extract_answer(args, pred2)
            except:
                pred_answer = None
        else:
            lower_pred = pred.lower()
            if lower_pred == "true" or lower_pred == "false":
                if lower_pred == "true":
                    pred_answer=True
                elif lower_pred == "false":
                    pred_answer=False
            print(pred_answer)
        ans = False
        if args.dataset == 'gsm8k':
            if isinstance(answer[idx], (int, float)):
                if abs(pred_answer - answer[idx]) < 1e-3:
                    correct += 1
                    ans = True
        elif args.dataset == 'mydata':
            if isinstance(answer[idx], bool):
                if pred_answer == answer[idx]:
                    correct += 1
                    ans = True
        json_data = {
            "ID": ids[idx],
            "question": question[idx],
            "chain-of-thought": pred,
            "pred": pred_answer,
            "answer": answer[idx],
            "ans": ans
        }
        write_json(json_data, Predict_File)
        all_predictions.append(json_data)

        print(
            f"correct:{correct} tested:{idx + 1} {correct / (idx + 1)} total:{len(question)}"
        )
    return correct, total, prompt_mode, all_predictions

def load_data(args):
    questions = []
    answers = []
    ids = []
    if args.dataset == 'gsm8k':
        datapath = 'dataset/gsm8k/gsm8k.json'
        with open(datapath, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            for idx, line in enumerate(json_data):
                q = line['question']
                a = float(line['answer'])
                id = f'gsm8k_{idx}'
                questions.append(q)
                answers.append(a)
                ids.append(id)
    elif args.dataset == 'mydata':
        datapath = 'sampled_news.json'
        with open(datapath, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            for idx, item in enumerate(json_data):
                q = item['question']
                a = item['answer']  # 直接使用，不转换为 float
                id = f'mydata_{idx}'
                questions.append(q)
                answers.append(a)
                ids.append(id)
    if args.test_end == 'full':
        return questions[int(args.test_start):], answers[int(args.test_start):], ids[int(args.test_start):]
    else:
        return questions[int(args.test_start):int(args.test_end)], answers[
                                                                   int(args.test_start):int(args.test_end)], ids[
                                                                                                             int(args.test_start):int(
                                                                                                                 args.test_end)]


def write_results_to_txt(filename, all_predictions, total, correct, accuracy, prompt_mode):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Prompt Mode: {prompt_mode}\n")
        f.write(f"Total Questions: {total}\n")
        f.write(f"Correct Answers: {correct}\n")
        f.write(f"Accuracy: {accuracy:.4f}\n\n")
        f.write("-- Individual Predictions --\n")
        for prediction in all_predictions:
            f.write(f"ID: {prediction['ID']}\n")
            f.write(f"Question: {prediction['question']}\n")
            f.write(f"Chain-of-thought: {prediction['chain-of-thought']}\n")
            f.write(f"Predicted Answer: {prediction['pred']}\n")
            f.write(f"True Answer: {prediction['answer']}\n")
            f.write(f"result: {prediction['ans']}\n\n")


if __name__ == '__main__':
    print_exp(args)
    correct_count, total_count, prompt_mode, all_predictions = zero_shot_cot()
    accuracy = correct_count / total_count if total_count > 0 else 0

    print("\n--- Final Results ---")
    print(f"Total Questions: {total_count}")
    print(f"Correct Answers: {correct_count}")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Prompt Mode: {prompt_mode}")

    # 确保目录被创建
    mkpath('./结果/gsm8k')
    results_file = f'./结果/{args.dataset}/results_{args.prompt_id}_short-混元.txt'
    write_results_to_txt(results_file, all_predictions, total_count, correct_count, accuracy, prompt_mode)
    print(f"\nResults written to: {results_file}")