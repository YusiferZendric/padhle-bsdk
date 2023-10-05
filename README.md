# [u/padhle-bsdkk](https://www.reddit.com/user/padhle-bsdkk/)

A Reddit bot designed to help users manage their study goals.

## Overview

The bot listens to specific commands mentioned in the comments on the subreddit 'jeeneetards'. It allows users to set, view, update, add, and remove their study goals. Additionally, the bot can display the time remaining for certain key events and provide motivational quotes to the users.

## Commands

1. **Set Goal**:
    - Command: `u/padhle-bsdkk setgoal "TASK_DESCRIPTION [PERCENTAGE%]: ... : x hours"`
    - Sets a series of tasks and their completion targets for the user.
    - Example: 
    ```
    u/padhle-bsdkk setgoal "Complete Quantum Mechanics Chapter [30%]: Solve Thermodynamics PYQs [50%]: Watch Organic Chemistry Lectures [20%]: 8 hours"
    ```

2. **Update Goal**:
    - Command: `u/padhle-bsdkk updategoal TASK_NO. PERCENTAGE% ...`
    - Updates the progress of the tasks.
    - Example: 
    ```
    u/padhle-bsdkk updategoal 1. 15% 2. 25% 3. 10%
    ```

3. **View Goal**:
    - Command: `u/padhle-bsdkk viewgoal`
    - Displays the user's current goals and their progress.

4. **Add Goal**:
    - Command: `u/padhle-bsdkk addgoal "TASK_DESCRIPTION: x hours"`
    - Adds a new task to the user's existing goals.
    - Example: 
    ```
    u/padhle-bsdkk addgoal "Modern Physics PYQ from Marks: 0.5 hours"
    ```

5. **Remove Goal**:
    - Command: `u/padhle-bsdkk removegoal TASK_NO`
    - Removes a specific task from the user's goals based on the task number.
    - Example: 
    ```
    u/padhle-bsdkk removegoal 2
    ```

6. **Display Time Remaining**:
    - Command: `u/padhle-bsdkk time`
    - Displays the time left for certain key events (like exams) with a motivational quote.

## Features

- Uses the `praw` library to interact with Reddit.
- Uses the `sqlite3` library to manage user data in a local database.
- Uses the `imgurpython` library to upload images to Imgur.
- Uses the `PIL` library to generate images.
- Provides random motivational quotes to users.

## Usage

Simply run the script, and the bot will start listening to the commands on the specified subreddit. Ensure all necessary dependencies are installed and the SQLite database is set up.
