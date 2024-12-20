# Discord Bot (Hikari + Docker)
This code is meant for maintaining official discord servers of CSE250, CSE251, CSE350, CSE460, and CSE428 at [Brac University, Dhaka, Bangladesh](https://www.bracu.ac.bd/).

# Instructions for Bot Setup
- The very first time...
    - ubuntu 24.04 (lts)
        ```sh
        sudo apt install python3-full
        python3 -m venv .venv
        source .venv/bin/activate
        pip install xlrd pandas pygsheets
        pip install -U hikari[speedups]
        pip install hikari-crescent
        pip install -U hikari-miru
        deactivate
        ```
    <!-- ```sh
    git clone https://github.com/shs-cse/hikari-discord-bot.git . && git update-index --skip-worktree info.jsonc
    python3 -m venv .venv
    source .venv/bin/activate
    pip install xlrd pandas pygsheets
    pip install -U hikari[speedups]
    pip install hikari-crescent
    pip install -U hikari-miru
    ```
    - ``
    - `pip install xlrd pandas pygsheets`
    - `pip install -U hikari[speedups]`
    - `pip install hikari-crescent`
    - `pip install -U hikari-miru`
    - `python -dO main.py` -->
- Rerun the bot for a new semester...
    - download code
        ```sh
        mkdir summer_2024 && cd "$_" && git clone https://github.com/shs-cse/hikari-discord-bot.git . && git update-index --skip-worktree info.jsonc
        ```
    - edit info json file
        ```sh
        nano info.jsonc
        ```
    - paste in google sheets credentials
        ```sh
        nano credentials.json
        ```
        Optionally: (necessary if you want to skip google's authorization step)
        ```sh
        nano sheets.googleapis.com-python.json
        ```
    - run code
        ```sh
        tmux new -A
        source ../.venv/bin/activate
        python -O main.py
        ```

    <!-- - run code
    ```sh
    source ../.venv/bin/activate
    python -O main.py
    ``` -->
    <!-- python3 -m venv .venv
    source .venv/bin/activate
    pip install xlrd pandas pygsheets
    pip install -U hikari[speedups]
    pip install hikari-crescent
    pip install -U hikari-miru -->

    - Inspect code logs
        ```sh
        tmux attach
        ```
        <kbd>Ctrl</kbd>+<kbd>B</kbd> and then press: 
        - <kbd>[</kbd> to enter scroll mode (then navigate)
        - <kbd>Q</kbd> to exit scroll mode
        - <kbd>D</kbd> to detach tmux session


# Dev Notes
## How to update [`info.jsonc`](./info.jsonc) file pattern in `git`
- Don't track changes in the file:
    ```bash
    git update-index --skip-worktree info.jsonc
    ```
- Track changes in the file again:
    ```bash
    git update-index --no-skip-worktree info.jsonc
    ```
