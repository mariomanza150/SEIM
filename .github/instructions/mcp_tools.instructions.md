---
applyTo: '**'
---
Here are the available tools and functions you can use:

1. **list_files**  
   - Lists files in a specified directory  
   - Parameters: `path` (directory path)

2. **create_file**  
   - Creates a new file with specified content  
   - Parameters: `path`, `content`

3. **edit_file**  
   - Edits an existing file (overwrites content)  
   - Parameters: `path`, `content`

4. **insert_edit_into_file**  
   - Inserts/edit content into a file (avoids repeating existing code)  
   - Parameters: `path`, `content`, `insert_after` (optional)

5. **read_file**  
   - Reads and returns the content of a file  
   - Parameters: `path`

6. **delete_file**  
   - Deletes a specified file  
   - Parameters: `path`

7. **mkdir**  
   - Creates a new directory  
   - Parameters: `path`

8. **rmdir**  
   - Removes an empty directory  
   - Parameters: `path`

9. **move_file**  
   - Moves a file to a new location  
   - Parameters: `source`, `destination`

10. **copy_file**  
    - Copies a file to a new location  
    - Parameters: `source`, `destination`

11. **search_files**  
    - Searches for files matching a pattern  
    - Parameters: `path`, `pattern`

12. **execute_command**  
    - Executes a shell command  
    - Parameters: `command`

13. **get_current_directory**  
    - Returns the current working directory  

14. **set_working_directory**  
    - Changes the working directory  
    - Parameters: `path`

15. **get_file_metadata**  
    - Retrieves metadata (size, permissions, etc.) for a file  
    - Parameters: `path`

Let me know which tool you'd like to use!