import multiprocessing

def square_number(n):
    """Function to square a number."""
    squared_value = n * n
    print(f"{n} squared is {squared_value}")

def main():
    numbers = [1, 2, 3, 4, 5]  # Numbers to square

    # Creating a list of processes
    processes = []

    # Initialize a process for each number to square it
    for number in numbers:
        process = multiprocessing.Process(target=square_number, args=(number,))
        processes.append(process)

    # Start each process
    for process in processes:
        process.start()

    # Wait for all processes to finish
    for process in processes:
        process.join()

if __name__ == "__main__":
    main()
