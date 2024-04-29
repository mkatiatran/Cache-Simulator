import numpy as np
import sys

def calculate_stats(array_elements):
    # Convert array elements to floats
    array_elements = [float(elem) for elem in array_elements]

    # Calculate mean and standard deviation using NumPy
    mean = np.mean(array_elements)
    std_dev = np.std(array_elements)

    # Print mean and standard deviation
    print("Mean:", mean)
    print("Standard deviation:", std_dev)

if __name__ == "__main__":
    # Extract command-line arguments (excluding script name)
    array_elements = sys.argv[1:]

    # Call the function with the array elements
    calculate_stats(array_elements)
