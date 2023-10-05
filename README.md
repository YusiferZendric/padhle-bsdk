# Reddit Goal Management Bot

This bot is designed to help Reddit users manage their study goals on the `jeeneetards` subreddit. The bot provides several functionalities, including setting goals, updating them, viewing progress, adding new goals, removing existing goals, and displaying the time remaining for major events.

## Features:

1. **Set Goals**: Users can define and set their study goals.
2. **Update Goals**: Users can update their progress on the goals they've set.
3. **View Goals**: Users can view their goals and the progress they've made.
4. **Add Goals**: Users can add more tasks to their existing goals.
5. **Remove Goals**: Users can remove specific tasks from their existing goals.
6. **Time Remaining**: The bot can display the time remaining for major events like JEE and NEET exams.

## Dependencies:

- `praw`: Reddit API wrapper for Python.
- `random`: For random operations.
- `os`: For OS-level operations.
- `datetime`: To handle date and time operations.
- `PIL (Pillow)`: For image processing tasks.
- `imgurpython`: To upload images to Imgur.
- `textwrap`: For text formatting.
- `re`: Regular expression operations.
- `sqlite3`: For database operations.
- `json`: For encoding and decoding JSON formatted data.

## How it works:

The bot continuously monitors the `jeeneetards` subreddit for new comments. When it finds a comment with a specific command (like `u/padhle-bsdkk setgoal`), it processes the command and replies to the user's comment with the appropriate response.

## Setup:

1. Make sure you have all the required dependencies installed.
2. Set up the SQLite database by running the `setup_database` method.
3. Start the bot by executing the script.

## Notes:

- Ensure that you have set the correct API keys and credentials for both Reddit and Imgur.
- The bot uses SQLite to manage and store user goals and progress.
- It's recommended to run the bot continuously for real-time responses.

## Disclaimer:

Please keep your API keys and credentials secure. The ones provided in the code are placeholders and should be replaced with your own.
