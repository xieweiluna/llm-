import time
from openai import OpenAI
import base64
import os
os.environ["HUNYUAN_API_KEY"]="请输入对应的api"


def decoder_for_hunyuan(args, input_text, max_length):
    client = OpenAI(
        api_key=base64.b64decode(os.environ["HUNYUAN_API_KEY"]).decode('utf-8'),
        base_url="https://api.hunyuan.cloud.tencent.com/v1",
    )

    # 设置温度参数
    temperature = 0.7 if args.SC and max_length != 32 else 0.0
    n = 10 if args.SC and max_length != 32 else 1

    try:
        completion = client.chat.completions.create(
            model="hunyuan-pro",
            messages=[
                {
                    "role": "user",
                    "content": input_text,
                }
            ],
            max_tokens=max_length,
            temperature=temperature,
            n=n,
            extra_body={
                "enable_enhancement": True,
            },
        )

        if max_length == 32 or not args.SC:
            return completion.choices[0].message.content
        elif max_length != 32 and args.SC:
            responses = []
            for choice in completion.choices:
                responses.append(choice.message.content)
            return responses
        else:
            raise NotImplementedError(f'Unhandled case for model configuration')

    except Exception as e:
        raise e


def basic_runner(args, inputs, max_length, max_retry=3):
    retry = 0
    get_result = False
    pred = [] if args.SC else ''
    error_msg = ''
    while not get_result and retry < max_retry:

        try:
            pred = decoder_for_hunyuan(args, inputs, max_length)
            get_result = True
        except Exception as e:
            retry += 1
            time.sleep(args.api_time_interval)
            error_msg = str(e)

            if retry >= max_retry:
                break

    return get_result, pred, error_msg