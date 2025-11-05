import json
from datasets import load_dataset
from tqdm import tqdm

from src.agent import *
from src.tools import run_python_code
from src import config

def load_data(sample_size: int = None):
    
    print("Loading 'bigcode/humanevalpack' dataset...")
    try:
        ds = load_dataset("bigcode/humanevalpack", "python", split="test")
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return None

    print(f"Found {len(ds)} Python problems in the test split.")

    if sample_size:
        print(f"Taking a subsample of {sample_size} problems.")
        ds = ds.select(range(sample_size))

    return ds

def create_problem_prompt(problem: dict) -> str:
    """
    Formats the dataset problem into a prompt for the agent.
    """
    return f"""Here is the buggy Python function:

```python
{problem['buggy_solution']}
```

Here is the test code that checks the function:

```python
{problem['test']}
```

Please analyze the bug, fix the function, and provide ONLY the complete, corrected Python function in a single code block.
"""

def check_solution(fixed_code: str, test_code: str) -> tuple[bool, str]:
    if not fixed_code:
        return False, "Agent did not provide any code."
    
    result = run_python_code(f"{fixed_code}\n{test_code}")
    print(result)
    if "Success" in result:
        return True, "Passed"
    return False, result


def main():

    print("--- 🚀 Starting HumanEvalFix Agent Evaluation ---")
    
    print("Initializing agent graph...")
    try:
        agent = create_agent()
    except Exception as e:
        print(f"Failed to create agent: {e}")
        return

    dataset = load_data(sample_size=config.EVAL_SAMPLE_SIZE)
    if dataset is None:
        return
        
    evaluation_results = []
    pass_count = 0

    print(f"\nRunning evaluation on {len(dataset)} problems...")
    
    for problem in tqdm(dataset, desc="Evaluating Problems"):
        
        problem_prompt = create_problem_prompt(problem)
        response = run_agent(agent, problem_prompt)        
        
        fixed_code = parse_final_code(response)
        passed, check_result = check_solution(fixed_code, problem['test'])
        
        if passed:
            pass_count += 1
            
        evaluation_results.append({
            "task_id": problem['task_id'],
            "passed": passed,
            "buggy_code": problem['buggy_solution'],
            "fixed_code": fixed_code,
            "agent_final_response": response,
            "check_result": check_result
        })

    if len(dataset) == 0:
        print("No problems were evaluated.")
        return

    pass_at_1 = (pass_count / len(dataset)) * 100

    print("\n--- ✅ Evaluation Complete ---")
    print(f"\nModel: {config.MODEL_NAME}")
    print(f"Total Problems: {len(dataset)}")
    print(f"Problems Passed: {pass_count}")
    print(f"\npass@1 Score: {pass_at_1:.2f}%")
    
    results_path = "results/results.json"
    print(f"\nSaving detailed results to {results_path}...")
    
    import os
    os.makedirs("results", exist_ok=True)
    
    with open(results_path, "w") as f:
        json.dump(evaluation_results, f, indent=2)
        
    with open("results/report.md", "w") as f:
        f.write(f"Evaluation Report:\n\n")
        f.write(f"  Model: `{config.MODEL_NAME}`\n")
        f.write(f"  Problems: `{len(dataset)}`\n")
        f.write(f"  Passed: `{pass_count}`\n")
        f.write(f"  pass@1: `{pass_at_1:.2f}%`\n")

    print("Done.")


if __name__ == "__main__":
    main()

