import json
import logging
from collections import Counter

from config import args
from extracter import get_precision, extract_answer
from prompt import get_prompt, construct_input
from prediction_runner import basic_runner
from utils import write_json, print_now, load_data, print_exp, mkpath

now = print_now(1).split(' ')[0].replace('/', '-')

Result_Folder = 'result/{}'.format(now)
mkpath('result')
mkpath(Result_Folder)
mkpath(f'{Result_Folder}/{args.dataset}')

Log_Folder = 'log/{}'.format(now)
mkpath('log')
mkpath(Log_Folder)
mkpath(f'{Log_Folder}/{args.dataset}')


Decoder_Error_File = f'{Result_Folder}/{args.learning_type}-{args.dataset}-{args.prompt_id}-{args.engine}-SC-{args.SC}_deco.json'
Predict_File = f'{Result_Folder}/{args.dataset}/{args.learning_type}-{args.prompt_id}-{args.engine}-SC-{args.SC}.json'
Log_File = f'{Log_Folder}/{args.dataset}/{args.learning_type}-{args.prompt_id}-{args.engine}-SC-{args.SC}.log'

# logging.basicConfig(filename=Log_File)
formatter = logging.Formatter('%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')
sh = logging.StreamHandler()
fh = logging.FileHandler(filename=Log_File)
fh.setFormatter(formatter)
sh.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(fh)
logger.addHandler(sh)


def zero_shot_cot():
    correct = 0
    question, answer, ids = load_data(args)
    total = len(question)  # 获取题目总数
    _, prompt = get_prompt()
    for idx, element in enumerate(question):
        # --test_star 100 从100开始测试
        # --test_end 100 只测前100个
        # --test_star 100 --test_end 200 从100开始测试，到200结束
        inputs = construct_input(prompt, element)
        try:
            get_result, pred, error_msg = basic_runner(args, inputs, args.max_length_cot)
        except Exception as e:
            decode_error_data = {
                'question': question[idx]
            }
            write_json(decode_error_data, Decoder_Error_File)
            logger.warning(
                f"an error raised when predicting (question id: {ids[idx]}). "
                f"ERROR: {getattr(e.__class__, '__name__')}:{str(e)}"
            )
            break
            continue
        if not get_result:
            logger.warning(
                f"not get predicted result (question id: {ids[idx]})."
                f"ERROR Message: {error_msg if error_msg else None}"
            )
            continue

        if 'Therefore, the answer is' in pred or 'The answer is' in pred:
            if 'The answer is' in pred:
                pred2 = pred.split('The answer is')[-1]
            else:
                pred2 = pred.split('the answer is')[-1]
            try:
                pred_answer = extract_answer(args, pred2)
            except:
                pred_answer = None
        else:
            inputs2 = inputs + pred + ' ' + args.direct_answer_trigger_for_direct
            try:
                get_result, pred3, error_msg = basic_runner(args, inputs2, 32)
            except Exception as e:
                decode_error_data = {
                    'question': question[idx]
                }
                write_json(decode_error_data, Decoder_Error_File)
                logger.warning(
                    f"an error raised when predicting (question id: {ids[idx]}). "
                    f"ERROR: {getattr(e.__class__, '__name__')}:{str(e)}"
                )
                continue
            if not get_result:
                logger.warning(
                    f"not get predicted result (question id: {ids[idx]})."
                    f"ERROR Message: {error_msg if error_msg else None}"
                )
                continue
            try:
                pred_answer = extract_answer(args, pred3)
            except:
                pred_answer = None
        ans = False
        if pred_answer is not None:
            if args.dataset.lower() in ["svamp", "gsm8k", "multiarith", "addsub", "singleeq"]:
                if abs(pred_answer - answer[idx]) < 1e-3:
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
                else:
                    json_data = {
                        "ID": ids[idx],
                        "question": question[idx],
                        "chain-of-thought": pred,
                        "pred": pred_answer,
                        "answer": answer[idx],
                        "ans": ans
                    }
                    write_json(json_data, Predict_File)
            else:
                if isinstance(pred_answer, float) and isinstance(answer[idx], float):
                    precision = min(get_precision(pred_answer), get_precision(answer[idx]))
                    if round(pred_answer, precision) == round(answer[idx], precision):
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
                    else:
                        ans = False
                        json_data = {
                            "ID": ids[idx],
                            "question": question[idx],
                            "chain-of-thought": pred,
                            "pred": pred_answer,
                            "answer": answer[idx],
                            "ans": ans
                        }
                        write_json(json_data, Predict_File)
                else:
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
                    else:
                        json_data = {
                            "ID": ids[idx],
                            "question": question[idx],
                            "chain-of-thought": pred,
                            "pred": pred_answer,
                            "answer": answer[idx],
                            "ans": ans
                        }
                        write_json(json_data, Predict_File)
        else:
            json_data = {
                "ID": ids[idx],
                "question": question[idx],
                "chain-of-thought": pred,
                "pred": pred_answer,
                "answer": answer[idx],
                "ans": ans
            }
            write_json(json_data, Predict_File)

        logger.info(
            f"correct:{correct} tested:{idx + 1} {correct / (idx + 1)} total:{len(question)}"
        )
    return correct




if __name__ == '__main__':
    print_exp(args)


    alls = zero_shot_cot()

    logger.info(f"correct num: {alls}")
