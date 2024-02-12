from concurrent.futures import ThreadPoolExecutor

# Define a function that you want to run in parallel
def task(n):
    # Your task logic here
    print(f"Executing task {n}")
    return n * 2  # Example operation

# Number of tasks you want to run in parallel
tasks = [1, 2, 3, 4, 5, 6]

# Use ThreadPoolExecutor to execute tasks in parallel
with ThreadPoolExecutor(max_workers=5) as executor:
    # Submit tasks to the executor
    futures = [executor.submit(task, n) for n in tasks]

    # Retrieve the results (if needed)
    results = [future.result() for future in futures]
    print(f"Results: {results}")

# This code will execute the `task` function in parallel for each element in `tasks`.
