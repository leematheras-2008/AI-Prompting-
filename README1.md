## README: Company Policy Assistant — Simple RAG in Google Colab

This project implements a plain Retrieval-Augmented Generation (RAG) assistant for company policies within a Google Colab environment. It avoids complex agents or tool-calling, focusing on a straightforward three-step process: **retrieve** relevant PDF chunks, **augment** a prompt with these chunks, and **generate** an answer using a Hugging Face model.

### Key Features

*   **Local Execution**: Everything runs locally within your Colab session. Both the embedding model and the answer-writing LLM (`Qwen/Qwen2.5-1.5B-Instruct`) are hosted directly, eliminating the need for external API keys or services.
*   **PDF Support**: Reads company policy documents from a PDF file. Includes an OCR fallback mechanism using Tesseract for scanned pages to ensure comprehensive text extraction.
*   **FAISS Vector Store**: Utilizes FAISS for efficient similarity search of document chunks, creating a searchable database (`faiss_index/`).
*   **Streamlit UI**: Provides an interactive chat interface built with Streamlit, allowing users to ask questions and receive policy-based answers.
*   **Cloudflared Tunnel**: Uses Cloudflare's quick tunnel for exposing the Streamlit application, offering a direct and stable public URL.

### How it Works (RAG Flow)

1.  **Retrieve**: When a user asks a question, the system searches the `faiss_index/` (created from your policy PDF) for the most relevant document chunks.
2.  **Augment**: The top 3 matching chunks are then incorporated into the prompt that is sent to the LLM.
3.  **Generate**: The local Hugging Face LLM processes the augmented prompt. It is instructed to use the provided policy text if relevant, and to fall back to its general knowledge for questions outside the policy scope.

### Setup and Usage

To get this assistant up and running, follow these steps in order within your Google Colab notebook:

1.  **Install Dependencies**: Execute the first code cell to install all necessary Python packages (e.g., `streamlit`, `langchain-community`, `pypdf`, `pytesseract`, `transformers`) and system tools (`tesseract-ocr`, `poppler-utils`).

    ```python
    !pip install streamlit langchain-community langchain-text-splitters langchain-huggingface faiss-cpu pypdf pdf2image pytesseract transformers torch accelerate --quiet
    !apt-get -qq install -y tesseract-ocr poppler-utils
    ```

2.  **Upload Your Policy PDF**: Run the cell that opens a file picker (`from google.colab import files; uploaded = files.upload()`). Upload your `company_policy.pdf`. If your file has a different name, either rename it or update the `PDF_FILE` variable in `build_index.py`.

3.  **Write `build_index.py`**: The content of `build_index.py` is provided in a cell. This script is responsible for reading the PDF, performing OCR if needed, splitting text into chunks, embedding them, and saving the FAISS index. Run the `%%writefile` cell to create this script.

    ```python
    %%writefile build_index.py
    # ... (script content)
    ```

4.  **Build the Vector Database**: Execute the `build_index.py` script. This is a one-time process or whenever your PDF policy changes. It will create the `faiss_index/` directory.

    ```python
    !python build_index.py
    ```

5.  **Write `app.py`**: The Streamlit application logic is contained in `app.py`. This includes loading the vector database and the local LLM, defining the RAG steps, and setting up the chat interface. Run the `%%writefile` cell to create this script.

    ```python
    %%writefile app.py
    # ... (script content)
    ```

6.  **Launch Streamlit in the Background**: Start the Streamlit app. The first time, the LLM will download (a few GB), which can take a few minutes.

    ```python
    !streamlit run app.py &>/content/logs.txt &
    ```

7.  **Download Cloudflared**: Fetch the Cloudflare tunnel tool.

    ```python
    !wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O cloudflared
    !chmod +x cloudflared
    ```

8.  **Launch Tunnel and Get Link**: Start the Cloudflare tunnel and retrieve your public URL to access the Streamlit app. Click the `https://....trycloudflare.com` link to open the chat interface.

    ```python
    import re, subprocess, time
    # ... (code to launch tunnel and print URL)
    ```

### Performance Notes

*   **CPU Runtime**: On a free Colab CPU runtime, answers can take 30–90 seconds, especially for the first query as the LLM loads.
*   **GPU Runtime**: For significantly faster responses, switch your Colab runtime to a T4 GPU (`Runtime -> Change runtime type`) and re-run all cells from the top.

### Troubleshooting

*   **"Couldn't find the 'faiss_index' folder"**: This means Cell 4 didn't run successfully, or the runtime restarted. Re-run Cells 3–4.
*   **`Failed to fetch dynamically imported module`**: Ensure you are using the newest `trycloudflare.com` link and hard-refresh your browser (Ctrl/Cmd+Shift+R).
*   **Tunnel link doesn't load**: Streamlit might still be starting. Wait ~10 seconds and retry, or check `/content/logs.txt` using `!cat /content/logs.txt`.
*   **New tunnel URL each time**: This is expected. Re-run Cell 8 whenever you restart Streamlit to get a new link.
*   **Slow answers/app looks frozen**: This is normal for a free CPU runtime. Consider switching to a T4 GPU.
*   **"Out of memory" / session crashes**: Restart your Colab runtime (`Runtime -> Restart session`) and re-run from Cell 1. A GPU runtime usually offers more memory headroom.
