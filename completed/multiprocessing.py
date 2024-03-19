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

"""

<Configuration>
    <Appenders>
        <Console name="ConsoleAppender">
            <PatternLayout pattern="%d{HH:mm:ss.SSS} [%t] %-5level %logger{36} - %msg%n"/>
            <Filters>
                <RegexFilter regex=".*duplicate key value violates unique constraint.*" onMatch="DENY" onMismatch="NEUTRAL"/>
            </Filters>
        </Console>
    </Appenders>
    <Loggers>
        <Root level="DEBUG">
            <AppenderRef ref="ConsoleAppender"/>
        </Root>
    </Loggers>
</Configuration>
"""