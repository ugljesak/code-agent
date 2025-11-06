from docker.errors import ContainerError, ImageNotFound, APIError
from langchain.tools import tool

@tool
def run_python_code(code: str) -> str:
    """
    Executes a string of Python code in a sandboxed Docker container.
    You MUST use this tool to test your code fixes.
    
    To test your fix, the code you provide should include:
    1. The full, corrected function.
    2. The test code (assertions) to validate the function.
    
    If the code runs successfully and all assertions pass, it will return
    an empty string or 'Success'.
    
    If the code fails (e.g., an 'AssertionError' or 'SyntaxError'), 
    it will return the full traceback from stderr.
    
    Args:
        code: The Python code string to execute.
    
    Returns:
        A string containing stdout and stderr from the execution,
        or 'Success' if execution is successful with no output.
    """
    print("First")
    try:
        import docker
        docker_client = docker.from_env()
    except APIError:
        print("Error: Docker daemon is not running.")
        print("Please start Docker Desktop and try again.")
        return "Error: Docker not working."
    print("Second")
    try:
        container = docker_client.containers.run(
            image="python:3.11-slim",
            command=["python", "-c", code],  
            remove=True,
            stderr=True,
            stdout=True,
            detach=False
        )
        
        output = container.decode('utf-8')
        
        if not output:
            return "Success: Code executed without errors and output."
        return output

    except ImageNotFound:
        return ("Error: Docker image 'python:3.11-slim' not found.\n"
                "Please run: docker pull python:3.11-slim")
    except ContainerError as e:
        return e.stderr.decode('utf-8')
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"