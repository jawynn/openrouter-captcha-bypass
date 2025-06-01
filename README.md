# OpenRouter Captcha Bypass

This project is a CLI tool for testing various types of captchas including puzzle, text, complicated text, and reCAPTCHA using Python and Selenium. The tool also uses OpenRouter API to help solve the captchas.

## Prerequisites

- Git
- Curl
- OpenRouter API key

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/jawynn/openrouter-captcha-bypass.git
   cd openrouter-captcha-bypass
   ```

2. Install uv and restart shell:
   MacOS and Linux

   ```sh
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
   Windows
   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

3. Copy a example `.env` file and insert your OpenRouter API key :

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

where `[captcha_type]` can be one of: `text`, `complicated_text`

Example:

```sh
uv run main.py --img /path/to.png text
```

## Captcha Types

- `text`: Tests simple text captchas.
- `complicated_text`: Tests complicated text captchas.


