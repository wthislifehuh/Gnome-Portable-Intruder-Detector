import os

# Print the current working directory
print("Current Directory:", os.getcwd())

# Change to a new directory, replace 'new_directory_path' with your desired path
new_directory_path = '/path/to/new/directory'
os.chdir(new_directory_path)

# Print the new current working directory to confirm the change
print("New Directory:", os.getcwd())
