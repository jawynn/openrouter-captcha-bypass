import argparse
import base64
import os
import time
import random
import re
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from openai import OpenAI

load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))


def average_of_array(arr):
    if not arr:
        return 0  # Handle edge case of empty array
    sum_elements = sum(arr)
    average = sum_elements / len(arr)
    return average - 5


def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def ask_recaptcha_to_chatgpt(image_path):
    client = OpenAI(
        base_url=os.getenv("OPENROUTER_API_BASE_URL"),
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )
    base64_image = encode_image_to_base64(image_path)
    short_prompt = (
        "You are an object detection assistant. Understand what is asked on the top instruction of the "
        "image. For Example if instruction says select all squares with motorcycle. There are 16 squares "
        "give number for each square 0 to 15. The numbers starts from top left to right. Then answer only "
        "with the square numbers like 1-3-5-6."
        "Understand the instruction and give me the highest probability squares as answer. Give only the correct square numbers."
    )
    response = client.chat.completions.create(
        model=os.getenv("CAPTHA_MODEL"),
        messages=[
            {"role": "system", "content": short_prompt},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                    }
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


def ask_text_to_chatgpt(image_path):
    client = OpenAI(
        base_url=os.getenv("OPENROUTER_API_BASE_URL"),
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )
    base64_image = encode_image_to_base64(image_path)
    short_prompt = "Act as a blind person assistant. Read the text from the image and give me only the text answer."
    response = client.chat.completions.create(
        model=os.getenv("CAPTHA_MODEL"),
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


def ask_slide_to_chatgpt(image_path):
    client = OpenAI(
        base_url=os.getenv("OPENROUTER_API_BASE_URL"),
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )
    base64_image = encode_image_to_base64(image_path)
    short_prompt = (
        "There is an slider button in the page and there is an empty gray space on puzzle. You should give "
        "give me how many pixels should i slide to complete the puzzle. You can simulate the slider for "
        "the exact fit before giving the answer.The total width is 210 pixels."
        "Give me only number of pixels in integer 50 up to 210 pixels."
    )
    response = client.chat.completions.create(
        model=os.getenv("CAPTHA_MODEL"),
        messages=[
            {"role": "system", "content": short_prompt},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                    }
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


def puzzle_test(driver):
    driver.get("https://2captcha.com/demo/geetest")
    time.sleep(5)
    button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "geetest_radar_tip"))
    )
    button.click()
    box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "geetest_embed"))
    )
    time.sleep(1)
    box.screenshot("geetest_box.png")
    time.sleep(1)
    all_results = []
    while True:
        slider = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "geetest_slider_button"))
        )
        time.sleep(2)
        action = ActionChains(driver)
        input_string = ask_slide_to_chatgpt("geetest_box.png")
        numbers = re.findall(r"\d+", input_string)
        if numbers:
            result = int(numbers[0])
        else:
            result = 0
        if result < 110:
            result = 90
        all_results.append(result)
        action.click_and_hold(slider).perform()
        time.sleep(random.uniform(0.8, 1.2))
        total_offset = average_of_array(all_results)
        num_steps = 5
        step_offset = total_offset / num_steps
        for _ in range(num_steps):
            action.move_by_offset(step_offset, 0).perform()
            time.sleep(random.uniform(0.05, 0.1))
        action.release().perform()


def complicated_text_test(driver):
    driver.get("https://2captcha.com/demo/mtcaptcha")
    time.sleep(5)
    iframe = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "mtcaptcha-iframe-1"))
    )
    iframe.screenshot("captcha_image.png")
    response = ask_text_to_chatgpt("captcha_image.png")

    print(response)
    driver.switch_to.frame(iframe)
    input_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CLASS_NAME, "mtcap-noborder.mtcap-inputtext.mtcap-inputtext-custom")
        )
    )
    input_field.send_keys(response)
    time.sleep(2)
    driver.switch_to.default_content()
    submit_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (
                By.CLASS_NAME,
                "_actionsItem_1f3oo_41._buttonPrimary_d46vc_44._button_d46vc_1._buttonMd_d46vc_34",
            )
        )
    )
    submit_button.click()


def text_test(driver):
    driver.get("https://2captcha.com/demo/normal")
    time.sleep(5)
    captcha_image = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "_captchaImage_rrn3u_9"))
    )

    time.sleep(2)
    captcha_image.screenshot("captcha_image.png")
    response = ask_text_to_chatgpt("captcha_image.png")

    print(response)

    input_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "_inputInner_ws73z_12"))
    )
    input_field.send_keys(response)
    submit_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (
                By.CLASS_NAME,
                "_actionsItem_1f3oo_41._buttonPrimary_d46vc_44._button_d46vc_1._buttonMd_d46vc_34",
            )
        )
    )
    submit_button.click()
    time.sleep(5)
    driver.quit()


def recaptcha_test(driver):
    driver.get("https://patrickhlauke.github.io/recaptcha/")

    def handle_recaptcha():
        number_of_challenges = 0
        recaptcha_frame = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//iframe[@title='reCAPTCHA']"))
        )
        recaptcha_frame.screenshot("recaptcha_checkbox.png")
        driver.switch_to.frame(recaptcha_frame)
        checkbox = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "recaptcha-checkbox-border"))
        )
        checkbox.click()
        driver.switch_to.default_content()
        time.sleep(2)
        array = []
        while True:
            try:
                challenge_iframe = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "//iframe[contains(@title, 'recaptcha challenge expires in two minutes')]",
                        )
                    )
                )
                number_of_challenges += 1
                filename = "recaptcha_challenge_" + str(number_of_challenges) + ".png"
                challenge_iframe.screenshot(filename)
                answer = ask_recaptcha_to_chatgpt(filename)
                if "," in answer:
                    array = answer.split(", ")
                elif "-" in answer:
                    array = answer.split("-")
                driver.switch_to.frame(challenge_iframe)
                table = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, "rc-imageselect-table-33")
                    )
                )
                time.sleep(1)
                all_images = table.find_elements(By.CLASS_NAME, "rc-image-tile-33")
                for each_element in array:
                    all_images[int(each_element)].click()
                submit_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "recaptcha-verify-button"))
                )
                submit_button.click()
                driver.switch_to.default_content()
                time.sleep(5)
                if (
                    len(
                        driver.find_elements(
                            By.CLASS_NAME, "recaptcha-checkbox-checkmark"
                        )
                    )
                    != 0
                ):
                    break
            except Exception as ex:
                print(ex)

    handle_recaptcha()
    time.sleep(5)
    driver.quit()


def main():
    parser = argparse.ArgumentParser(description="Test various captcha types.")
    parser.add_argument(
        "captcha_type",
        choices=["puzzle", "text", "complicated_text", "recaptcha"],
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
        elif args.captcha_type == "puzzle":
            response = ask_slide_to_chatgpt(args.img)
            print(f"AI Response for puzzle captcha: {response}")
        elif args.captcha_type == "recaptcha":
            response = ask_recaptcha_to_chatgpt(args.img)
            print(f"AI Response for recaptcha: {response}")
        else:
            print("Unsupported captcha type for --img argument.")
        return  # Exit after processing image

    service = FirefoxService(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service)
    try:
        if args.captcha_type == "puzzle":
            puzzle_test(driver)
        elif args.captcha_type == "text":
            text_test(driver)
        elif args.captcha_type == "complicated_text":
            complicated_text_test(driver)
        elif args.captcha_type == "recaptcha":
            recaptcha_test(driver)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
