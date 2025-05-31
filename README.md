# OpenRouter Captcha Bypass

This project is a CLI tool for testing various types of captchas including puzzle, text, complicated text, and reCAPTCHA using Python and Selenium. The tool also uses OpenRouter API to help solve the captchas.

## Prerequisites

- Python 3.11+
- Firefox Browser
- OpenRouter Account for API

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/jawynn/openrouter-captcha-bypass.git
   cd openrouter-captcha-bypass
   ```

2. Install uv and restart shell:

   ```sh
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

3. Copy a example `.env` file:

   ```sh
   cp .env.example .env
   ```

4. Install with uv:

   ```sh
   uv sync
   ```

## Usage

Run the CLI tool with the desired captcha type:

```sh
uv run python main.py [--img IMG] [captcha_type]
```

where `[captcha_type]` can be one of: `puzzle`, `text`, `complicated_text`, `recaptcha` and `img` the path to image

Example:

```sh
uv run main.py --img captcha_image.png text
```

## Captcha Types

- `text`: Tests simple text captchas.
- `complicated_text`: Tests complicated text captchas.
- `recaptcha`: Tests Google's reCAPTCHA.
- `puzzle`: Tests puzzle captchas.

