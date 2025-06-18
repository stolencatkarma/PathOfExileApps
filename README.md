# Path of Exile Apps

This project provides a framework for developing various Path of Exile related applications as plugins. It now includes a basic GGPK file parser to extract game data.

## Setup

1.  **Clone the repository (or download the files) to `C:\test\PathOfExileApps`**.

2.  **GGPK File Path**: Before running, you may need to update the path to your `Content.ggpk` file inside `src/main.py`. The default path is set to `C:\Program Files (x86)\Grinding Gear Games\Path of Exile\Content.ggpk`.

    ```python:C:\test\PathOfExileApps\src\main.py
    # in main()
    ggpk_file_path = "C:\\Program Files (x86)\\Grinding Gear Games\\Path of Exile\\Content.ggpk" # IMPORTANT: USER MUST CHANGE THIS if the path is different
    ```

3.  **Data Files**: This application is intended to work with data files (`.dat`) from Path of Exile's `Content.ggpk` file. The `ggpk_parser.py` is a work in progress and does not yet extract these files.

## Running the Application

The application will first attempt to parse the `Content.ggpk` file, then it will load the plugins from the `plugins` directory and execute their `run` function.

To run the application, navigate to the `src` directory and run `main.py`:

```bash
cd C:\test\PathOfExileApps\src
python main.py
```

## Plugins

## Project Structure

- `ggpk_parser.py`: A script to parse the `Content.ggpk` file. **This is a work in progress.**
- `src/main.py`: The main entry point of the application.
- `plugins/`: Contains individual plugin folders.

## Plugins

Plugins are located in the `plugins` directory. Each plugin should be in its own subdirectory and contain an `__init__.py` file with a `run()` function.

### Random Build Generator Plugin

This plugin generates a random Path of Exile build. It's a placeholder and needs actual `.dat` file parsing logic to be fully functional.

### Build Archetype Combiner Plugin

This plugin combines major and minor build elements to suggest new build archetypes, based on the theory that you can excel at 2 major and 1 minor aspect in the game. It uses placeholder data and will need actual `.dat` file parsing to be fully functional.
