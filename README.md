# README: Prompt to Picture — Text-to-Image Generator

This project provides a fully local text-to-image generator using a small, fast Stable Diffusion model (`SD-Turbo`) directly within Google Colab. There's no need for API keys or external accounts.

## Features

*   **Local Execution**: Runs entirely on your Colab GPU, without relying on external APIs.
*   **Fast Generation**: Utilizes `SD-Turbo`, a distilled model designed for rapid image generation in just 1-4 steps.
*   **Streamlit Interface**: Provides an interactive web UI for entering prompts, adjusting generation parameters, and downloading images.
*   **Cloudflare Tunneling**: Makes the local Streamlit app accessible via a public URL.

## Requirements

*   **GPU Runtime**: This notebook *requires* a T4 GPU runtime. To enable it, go to **Runtime → Change runtime type → T4 GPU**, then **Runtime → Restart session**.

## Setup and Usage

Follow these steps to set up and run the text-to-image generator:

1.  **Install Dependencies**: The first code cell (`!pip install ...`) installs all necessary Python libraries.
2.  **Verify GPU**: The second code cell (`import torch...`) checks for GPU availability. If a GPU is not detected, follow the instructions to change your runtime type.
3.  **Write `app.py`**: The `%%writefile app.py` cell creates the Streamlit application file. This is the core of the web interface.
4.  **Launch Streamlit**: The `!streamlit run app.py &>/content/logs.txt &` command starts the Streamlit application in the background.
5.  **Download `cloudflared`**: The `!wget ...` and `!chmod ...` commands download and make the Cloudflare tunnel client executable.
6.  **Launch Tunnel and Get Link**: The final Python cell (`import re, subprocess, time...`) starts the Cloudflare tunnel and prints a public `https://....trycloudflare.com` URL. Click this link to open the Streamlit application in your browser.

## Troubleshooting

*   **"No GPU detected"**: Ensure you have selected a T4 GPU runtime as described in the Requirements section.
*   **Slow Generation or Out of Memory**: Try lowering the "Steps" slider in the Streamlit app, or restart your runtime to clear GPU memory.
*   **Solid Black Image**: The safety filter might have incorrectly flagged your prompt. Try rephrasing it slightly.
*   **Tunnel link doesn't load**: Wait a few seconds for Streamlit to start, then re-run the "Launch the tunnel" cell. You can check `/content/logs.txt` for errors.
*   **New tunnel URL each time**: This is expected. Re-run the "Launch the tunnel" cell whenever you restart Streamlit to get the latest URL.
