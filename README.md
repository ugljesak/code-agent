# LLM Code Repair Agent (HumanEvalFix)

This project implements an AI agent using **LangGraph** to automatically fix buggy Python code. The agent operates in a **ReAct-style** (Reason-Act) loop, using a sandboxed **Docker** container to safely execute and test its proposed fixes.

The agent's performance is benchmarked against the `bigcode/humanevalpack` dataset, reporting the final **`pass@1`** metric.

## 🚀 Features

* **Agentic Framework**: Built with **LangGraph** for robust, stateful agent execution.
* **ReAct Logic**: The agent can reason, act (run code), and observe results iteratively to solve complex bugs.
* **Sandboxed Execution**: Uses **Docker** to safely execute all LLM-generated code.
* **Local LLM Support**: Configured to run with **Ollama** (e.g., `qwen3:0.6b`, `qwen2:0.5b`) for local, free inference.
* **Evaluation Harness**: Includes the `src/eval.py` script to run the agent against the benchmark.

---

## 🛠️ How to Run the Evaluation

Running this project requires three main services to be active simultaneously:
1.  The **Docker Service** (for running code)
2.  The **Ollama Service** (for the LLM)
3.  The **Python Evaluation Script** (for the agent logic)

We strongly recommend using **three separate terminals** for this setup.

### Step 1: Prerequisites

Ensure you have the following installed:
* Python 3.10+
* [Docker Desktop (or Docker Engine on Linux)](https://www.docker.com/products/docker-desktop/)
* [Ollama](https://ollama.com/)

### Step 2: Project Setup (Terminal 1)

This is your main terminal for running the Python script.

1.  **Activate Environment:** (Assuming you have a `venv` setup)
    ```bash
    source venv/bin/activate
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Step 3: Start Services (Terminals 2 & 3)

#### Terminal 2: Start the Docker Service (Sandbox)

1.  **Start Docker:** Ensure the Docker daemon is running (via the Desktop app or `sudo systemctl start docker` on Linux).
2.  **Pull the Sandbox Image:** Pre-download the required image to prevent startup hangs:
    ```bash
    docker pull python:3.11-slim
    ```

#### Terminal 3: Start the Ollama Server (LLM)

1.  **Run the Ollama Server:**
    ```bash
    ollama serve
    ```
    (Leave this terminal running in the background)

2.  **Pull Your Model:** Pull the model specified in your `src/config.py` (e.g., `qwen3:0.6b`):
    ```bash
    ollama pull qwen3:0.6b
    ```

### Step 4: Run the Evaluation (Back in Terminal 1)

With Docker and the local Ollama server running, your script should now execute without network errors.

1.  **Run the Script:**
    ```bash
    python -m src.eval
    ```

The agent's steps will be printed live to the console using `graph.stream()`.

---

## ⚙️ Configuration

The agent's behavior is controlled by **`src/config.py`**:

| Variable | Description | Example Value |
| :--- | :--- | :--- |
| `MODEL_NAME` | The **exact** Ollama model name to use. | `"qwen2:0.5b"` |
| `OLLAMA_BASE_URL` | The endpoint for your Ollama server. | `"http://localhost:11434"` |
| `AGENT_MAX_ITERATIONS` | Max steps (Reason -> Act -> Observe) before the agent gives up. | `8` |
| `EVAL_SAMPLE_SIZE` | Number of problems to run. Set to `None` for the full benchmark. | `1` or `10` |

## 📊 Viewing Results

All evaluation outputs are saved in the `/results` directory:

* **`results/results.json`**: A detailed log of every problem and the agent's actions.
* **`results/report.md`**: A summary of the final `pass@1` score.
* **`results/agent_graph.png`**: A visualization of the agent's internal logic graph.