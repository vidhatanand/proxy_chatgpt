# proxy_chatgpt

A Python package (macOS-only) that uses AppleScript automation of Safari/Chrome to interact with ChatGPT-like services.

## Installation

```bash
git clone git@github.com:vidhatanand/proxy_chatgpt.git
cd proxy_chatgpt
pip install .


### Quick API demo (macOS)

```bash
# 1. install core lib + API extras
pip install .[api]

# 2. launch the façade
uvicorn openai_compat:app --host 0.0.0.0 --port 8000
