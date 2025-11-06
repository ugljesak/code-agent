import docker
import time

print("--- Docker Test Script ---")

try:
    print("Connecting to Docker daemon...")
    docker_client = docker.from_env()
    print("Connection successful.")
except Exception as e:
    print(f"\n[FATAL ERROR] Could not connect to Docker daemon.")
    print(f"Error: {e}")
    print("Please ensure Docker is running and you have permissions (sudo usermod -aG docker $USER).")
    exit()

print("\nVerifying 'python:3.11-slim' image...")
try:
    docker_client.images.get("python:3.11-slim")
    print("Image 'python:3.11-slim' is already local. Good.")
except docker.errors.ImageNotFound:
    print("Image 'python:3.11-slim' not found locally.")
    print("Starting download (this can take 5-10 minutes)...")
    try:
        docker_client.images.pull("python:3.11-slim")
        print("Download complete.")
    except Exception as e:
        print(f"\n[FATAL ERROR] Failed to pull image: {e}")
        exit()
except Exception as e:
    print(f"\n[FATAL ERROR] An unexpected error occurred: {e}")
    exit()


print("\nAttempting to run a simple 'Hello World' container...")
print("(This is the line that hangs in the agent)...")

start_time = time.time()
try:
    container_output = docker_client.containers.run(
        image="python:3.11-slim",
        command=["python", "-c", "print('Hello from Docker!')"],
        remove=True,
        stderr=True,
        stdout=True,
        detach=False
    )
    end_time = time.time()
    
    print("\n--- TEST SUCCESSFUL! ---")
    print(f"Container ran in {end_time - start_time:.2f} seconds.")
    print(f"Output: {container_output.decode('utf-8')}")

except Exception as e:
    end_time = time.time()
    print(f"\n--- TEST FAILED after {end_time - start_time:.2f} seconds ---")
    print(f"The 'containers.run' call failed with error: {e}")

print("--- End of Test ---")