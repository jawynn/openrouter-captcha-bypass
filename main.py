import argparse
import base64
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))

# Проверка наличия необходимых переменных окружения
openrouter_base_url = os.getenv("OPENROUTER_API_BASE_URL")
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
captcha_model = os.getenv("CAPTHA_MODEL").split("#")[0].strip().strip('"')

if not openrouter_base_url:
    print(
        "Ошибка: Переменная окружения OPENROUTER_API_BASE_URL не установлена. Пожалуйста, проверьте ваш файл .env."
    )
    exit(1)
if not openrouter_api_key:
    print(
        "Ошибка: Переменная окружения OPENROUTER_API_KEY не установлена. Пожалуйста, проверьте ваш файл .env."
    )
    exit(1)
if not captcha_model:
    print(
        "Ошибка: Переменная окружения CAPTHA_MODEL не установлена. Пожалуйста, проверьте ваш файл .env."
    )
    exit(1)




def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def ask_text_to_chatgpt(image_path):
    client = OpenAI(
        base_url=os.getenv("OPENROUTER_API_BASE_URL"),
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )
    base64_image = encode_image_to_base64(image_path)
    short_prompt = "Act as a blind person assistant. Read the text from the image and give me only the text answer."
    response = client.chat.completions.create(
        model=captcha_model,
        messages=[
            {"role": "system", "content": [{"type": "text", "text": short_prompt}]},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                    },
                    {
                        "type": "text",
                        "text": "Understand what is asked on the top instruction of the image. Give me the only correct squares with highest probability",
                    },
                ],
            },
        ],
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    return response.choices[0].message.content


def main():
    parser = argparse.ArgumentParser(description="Test various captcha types.")
    parser.add_argument(
        "captcha_type",
        choices=["text", "complicated_text"],
        help="Specify the type of captcha to test",
    )
    parser.add_argument(
        "--img",
        type=str,
        help="Path to a local image file to use instead of capturing from browser.",
    )
    args = parser.parse_args()

    if args.img:
        # If --img is provided, bypass Selenium and directly call AI functions
        if args.captcha_type == "text":
            response = ask_text_to_chatgpt(args.img)
            print(f"AI Response for text captcha: {response}")
        elif args.captcha_type == "complicated_text":
            response = ask_text_to_chatgpt(
                args.img
            )  # Assuming ask_text_to_chatgpt can handle complicated_text
            print(f"AI Response for complicated_text captcha: {response}")
        else:
            print("Unsupported captcha type for --img argument.")
        return  # Exit after processing image
    else:
        print(
            "Error: --img flag is required as browser functionality has been removed."
        )
        parser.print_help()
        return


if __name__ == "__main__":
    main()
