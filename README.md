# LLM Agent for Python Code Repair (HumanEvalFix)

This project implements an AI agent using LangGraph to automatically fix buggy Python code. The agent operates in a ReAct-style loop, using a sandboxed code interpreter to test its fixes.

The agent's performance is benchmarked against the Python subset of the HumanEvalFix dataset, reporting the `pass@1` metric.

## 🚀 Features

* **Agentic Framework**: Built with **LangGraph** for robust, stateful agent execution.
* **ReAct Logic**: The agent can reason, act (run code), and observe results iteratively.
* **Sandboxed Execution**: Uses **Docker** to safely execute all LLM-generated code, preventing any risk to your local system.
* **Evaluation Harness**: Includes a script to run the agent against HumanEvalFix and calculate the `pass@1` score.
* **Lightweight Model**: Configured to run with a small open-source model like `qwen2:0.5b` via **Ollama**.

## 🛠️ Setup Instructions

### 1. Prerequisites

You must have the following installed on your system:
* [Python 3.10+](https://www.python.org/)
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Ensure the Docker daemon is running)
* [Ollama](https://ollama.com/)

### 2. Clone & Install Dependencies

First, create the project directory and files as listed in this repository.

Then, install the required Python packages:

```bash
pip install -r requirements.txt