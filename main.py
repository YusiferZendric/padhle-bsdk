import praw
import random
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from imgurpython import ImgurClient
import textwrap
import re
import sqlite3
import json
class RedditBot:
    def __init__(self):
        self.client_id = 'a6e933249c93935'
        self.client_secret = '772422fda828191fc3d09ffb141196b5a607f5cc'
        self.client = ImgurClient(self.client_id, self.client_secret)
        self.reddit = praw.Reddit(client_id="zzdyeGoux-tEgGejZHER5g",
                                  client_secret="wQSY0-54Gf0WbykN21bOb499_Itatg",
                                  username="padhle-bsdkk",
                                  password="P298ypcrq",
                                  user_agent="padhle-bsdkk bot by u/zendrixate")
        self.subreddit = self.reddit.subreddit('jeeneetards')
        self.processed_comments = set()
        self.setup_database()
    def simulate(self):
        print("Simulation mode...")

        # Dummy comments for simulation
        dummy_comments = [
            {"body": 'u/padhle-bsdkk updategoal 1. 100%', "author": "zendrixate", "id": "test1"},
            # {"body": "u/padhle-bsdkk stats ...", "author": "zendrixate", "id": "test2"}, # adjust as necessary
            # {"body": "u/padhle-bsdkk stats ...", "author": "zendrixate", "id": "test2"}, # adjust as necessary
            # ... Add more dummy comments here
        ]

        for comment in dummy_comments:
            try:
                author = comment['author']
            except AttributeError:
                continue

            print(f"New simulated message from {author}...")

            if "u/padhle-bsdkk time" in comment['body'].lower() and author != 'padhle-bsdkk':
                # Instead of replying to the comment, print the response.
                print("[Reply]:", self.days_hours_minutes_remaining(datetime(2024, 1, 24), 'Mains 2024'))

            if "u/padhle-bsdkk setgoal" in comment['body'].lower() and author != 'padhle-bsdkk':
                response = self.set_goal(author, comment['body'])
                print("[Reply]:", response)

            if "u/padhle-bsdkk updategoal" in comment['body'].lower() and author != 'padhle-bsdkk':
                response = self.update_goal(author, comment['body'])
                print("[Reply]:", response)

            if "u/padhle-bsdkk viewgoal" in comment['body'].lower() and author != 'padhle-bsdkk':
                response = self.view_goal(author)
                print("[Reply]:", response)

            if "u/padhle-bsdkk addgoal" in comment['body'].lower() and author != 'padhle-bsdkk':
                response = self.add_goal(author, comment['body'])
                print("[Reply]:", response)

            if "u/padhle-bsdkk removegoal" in comment['body'].lower() and author != 'padhle-bsdkk':
                response = self.remove_goal(author, comment['body'])
                print("[Reply]:", response)

            if "u/padhle-bsdkk stats" in comment['body'].lower() and author != 'padhle-bsdkk':
                response = self.display_stats(author)
                print("[Reply]:", response)

    def is_valid_command_url(self, comment, command):
        valid_url = "https://www.reddit.com/r/JEENEETards/comments/16ccs0r/so_ive_created_a_bot_out_of_boredom_padhlebsdk/?rdt=45360"
        
        # If it's a 'time' command, it can be from anywhere in the subreddit
        if command == "time":
            return comment.subreddit.display_name.lower() == "jeeneetards"
        
        # For other commands, it should be from the specific post
        return comment.permalink.startswith(valid_url)
    def setup_database(self):
        self.conn = sqlite3.connect('user_goals.db')
        self.cursor = self.conn.cursor()
        
        # Create tables if they don't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS goals (
                username TEXT PRIMARY KEY,
                goal_data TEXT,
                target_time INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS progress (
                username TEXT,
                task_description TEXT,
                target_percentage INTEGER,
                current_percentage INTEGER,
                PRIMARY KEY (username, task_description),
                FOREIGN KEY (username) REFERENCES goals(username)
            )
        ''')
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS stats (
            username TEXT PRIMARY KEY,
            challenges_taken INTEGER DEFAULT 0,
            challanges_finished INTEGER DEFAULT 0,
            streak INTEGER DEFAULT 0,
            hours_studied REAL DEFAULT 0.0
        )
        ''')
        self.conn.commit()
        
        # Check if the timestamp column exists and add if it doesn't
        self.cursor.execute("PRAGMA table_info(goals)")
        columns = [column[1] for column in self.cursor.fetchall()]
        if "timestamp" not in columns:
            self.cursor.execute('''
                ALTER TABLE goals ADD COLUMN timestamp DATETIME DEFAULT CURRENT_TIMESTAMP;
            ''')
        
        self.conn.commit()

    def set_goal(self, author, command_text):
        # Extracting goal data
        goal_data_match = re.search(r'"(.*?)"', command_text)
        if not goal_data_match:
            return """*Invalid goal format*. 
            **Dummy Example**: 
            ```
            u/padhle-bsdkk setgoal "Complete Quantum Mechanics Chapter [30%]: Solve Thermodynamics PYQs [50%]: Watch Organic Chemistry Lectures [20%]: 8 hours"
            ```
            **Syntax**: <task1> [percentage%]: <task2> [percentage%]... <taskn> [percentage%]: x hours (keep in hours. for 30 minutes: 0.5 hours)
            """
        goal_data_str = goal_data_match.group(1)
        tasks = goal_data_str.split(":")
        
        # Last item is the target time
        target_time_str = tasks[-1].strip().split()[0]
        
        try:
            target_time = round(float(target_time_str),2) * 3600  # Convert hours to seconds
        except Exception as e:
            return f"""*{e}*. 
            **Dummy Example**: 
            ```
            u/padhle-bsdkk setgoal "Complete Quantum Mechanics Chapter [30%]: Solve Thermodynamics PYQs [50%]: Watch Organic Chemistry Lectures [20%]: 8 hours"
            ```
            **Syntax**: <task1> [percentage%]: <task2> [percentage%]... <taskn> [percentage%]: x hours (keep in hours. for 30 minutes: 0.5 hours)
            """
        self.cursor.execute('''
            SELECT goal_data, target_time
            FROM goals
            WHERE username = ?
        ''', (author,))
        existing_goals = self.cursor.fetchone()
        if existing_goals:
            existing_goal_data, existing_target_time = existing_goals
            tasks = json.loads(existing_goal_data) + tasks[:-1]
            target_time += existing_target_time
        # Storing goal data
        current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute('''
            INSERT OR REPLACE INTO goals (username, goal_data, target_time, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (author, json.dumps(tasks[:-1]), target_time, current_timestamp))
        
        # Storing individual tasks and their target percentages
        totalPercentage = []
        for task in tasks[:-1]:
            task_description, percentage_str = task.rsplit('[', 1)
            target_percentage = int(percentage_str.split('%')[0])
            # Extract the tasks and the target_time_str
            tasks, target_time_str = goal_data_str.rsplit(":", 1)
            tasks = tasks.split(":")
            tasks.append(target_time_str.split()[-2])  # Append the task before the target_time_str

            # Other processing for target_time remains unchanged...

            # Storing individual tasks and their target percentages
            totalPercentage = []
            for task in tasks[:-1]:  # Now it correctly includes all tasks
                task_description, percentage_str = task.rsplit('[', 1)
                target_percentage = int(percentage_str.split('%')[0])
                totalPercentage.append(target_percentage)

        if sum(totalPercentage) != 100:
            return f"""*Current Percentage: {totalPercentage}\nTotal percentage of all Tasks should be 100. Eg: 30 50 20*. 
                **Dummy Example**: 
                ```
                u/padhle-bsdkk setgoal "Complete Quantum Mechanics Chapter [30%]: Solve Thermodynamics PYQs [50%]: Watch Organic Chemistry Lectures [20%]: 8 hours"
                ```
                **Syntax**: <task1> [percentage%]: <task2> [percentage%]... <taskn> [percentage%]: x hours (keep in hours. for 30 minutes: 0.5 hours)
                """
        else:
            for task in tasks[:-1]:
                task_description, percentage_str = task.rsplit('[', 1)
                target_percentage = int(percentage_str.split('%')[0])
                self.cursor.execute('''
                    INSERT OR REPLACE INTO progress (username, task_description, target_percentage, current_percentage)
                    VALUES (?, ?, ?, 0)
                ''', (author, task_description.strip(), target_percentage))
        
        self.conn.commit()
        self.cursor.execute('''
            INSERT OR IGNORE INTO stats (username, challenges_taken)
            VALUES (?, 0)
        ''', (author,))
        self.cursor.execute('''
            UPDATE stats
            SET challenges_taken = challenges_taken + 1
            WHERE username = ?
        ''', (author,))

        self.conn.commit()
        return f"Goal set for {author}. I'll remind you in {target_time_str.strip()}!"

    def give_random_quote(self):
        with open("quotes.txt", 'r') as file:
            return random.choice(file.readlines()).strip()
    def update_goal(self, author, command_text):
        # Extracting task updates
        hours_studied = 0
        updates = re.findall(r'(\d+)\.\s*(\d+)%', command_text)
        if not updates:
            return """*Invalid Update Format*
            **Dummy Example**: 
                ```
                u/padhle-bsdkk updategoal 1. 15% 2. 25% 3. 10%
                ```
            **Syntax**: <task no> <percentage completed out of 100 of that particular task>% ...        
            """
        
        # Update the progress in the database
        for task_num, percentage in updates:
            try:
                task_num = int(task_num)
                percentage = int(percentage)
            except ValueError:
                continue

            # Fetch the task description and target_percentage based on the task number
            self.cursor.execute('''
                SELECT task_description, target_percentage, current_percentage
                FROM progress
                WHERE username = ?
                ORDER BY task_description ASC
                LIMIT 1 OFFSET ?
            ''', (author, task_num - 1))
            result = self.cursor.fetchone()
            if not result:
                continue
            task_description, task_target_percentage,current_percentage = result
            percentage = percentage-current_percentage 
            # Calculate the effective progress
            effective_progress = (percentage / 100) * task_target_percentage

            # Update the current percentage for the task with the effective progress
            self.cursor.execute('''
                UPDATE progress
                SET current_percentage = ?
                WHERE username = ? AND task_description = ?
            ''', (effective_progress, author, task_description))
            self.cursor.execute('''SELECT target_time FROM goals WHERE username = ?''', (author,))
            total_time = self.cursor.fetchone()
            if total_time:
                total_time = total_time[0]
                hours_studied += (effective_progress / 100) * (total_time / 3600)  # Convert total_time from seconds to hours

        self.conn.commit()

        self.cursor.execute('''
            SELECT current_percentage, target_percentage
            FROM progress
            WHERE username = ?
        ''', (author,))
        

        results = self.cursor.fetchall()
        print(results)
        if not results:
            return "No goals found for the user."

        progress_messages = []
        total_progress = 0
        total_target = 0
        for current, target in results:
            progress_messages.append(f"{current:.2f}/{target}")
            total_progress += current
            total_target += target

        overall_percentage = (total_progress / total_target) * 100
        progress_summary = ", ".join(progress_messages)
        self.cursor.execute('''
            UPDATE stats
            SET hours_studied = hours_studied + ?
            WHERE username = ?
        ''', (hours_studied, author))
        self.cursor.execute('''
            SELECT hours_studied
            FROM stats
            WHERE username = ?
        ''', (author,))
        self.conn.commit()
        if round(overall_percentage) == 100:
            # Display congratulatory message
            response = "Congrats! You have finished your challenge."
            
            # Increment the challanges_finished by 1
            self.cursor.execute('''
                UPDATE stats
                SET challanges_finished = challanges_finished + 1
                WHERE username = ?
            ''', (author,))

            # Remove the user's data from goals and progress tables
            self.cursor.execute('DELETE FROM goals WHERE username = ?', (author,))
            self.cursor.execute('DELETE FROM progress WHERE username = ?', (author,))
        else:
            response = f"Updated your goals, {author}. Your progress: {progress_summary}. Overall: {overall_percentage:.2f}% of your total goals!"
    
        self.conn.commit()
        return response

    def view_goal(self, author):
        self.cursor.execute('''
            SELECT task_description, target_percentage, current_percentage
            FROM progress
            WHERE username = ?
        ''', (author,))
        tasks = self.cursor.fetchall()

        if not tasks:
            return "No goals found for the user."

        # Fetch the target_time from the goals table
        self.cursor.execute('''
            SELECT target_time
            FROM goals
            WHERE username = ?
        ''', (author,))
        target_time = self.cursor.fetchone()
        if not target_time:
            return "No target time found for the user."
        target_time = target_time[0] / 3600  # Convert seconds to hours

        # Calculate elapsed time
        current_time = datetime.now()
        # Assuming you store the start time in the goals table when setting goals
        self.cursor.execute('''
            SELECT MAX(timestamp)
            FROM goals
            WHERE username = ?
        ''', (author,))
        goal_timestamp = self.cursor.fetchone()[0]
        goal_datetime = datetime.strptime(goal_timestamp, '%Y-%m-%d %H:%M:%S')
        difference = current_time - goal_datetime
        elapsed_time = (difference.days * 24) + (difference.seconds / 3600)

        print("Most Recent Goal Timestamp:", goal_timestamp)
        print("Current Timestamp:", current_time)
        print("Calculated Elapsed Time:", elapsed_time)
        # Create a table-like structure for the goals
        
        table = "Your Goals:\n\n"
        table += "| Task No. | Task Description | Share % | Completed % |\n"
        table += "|----------|------------------|----------|-------------|\n"
        totalidx = 0
        totalcurrent = 0

        def get_larger_root(a, b, c):
            root1 = (-b + (b**2 - 4*a*c)**0.5) / (2*a)
            root2 = (-b - (b**2 - 4*a*c)**0.5) / (2*a)
            return max(root1, root2)

        for idx, (desc, target, current) in enumerate(tasks, 1):
            totalidx += idx
            totalcurrent += current
            table += f"| {idx} | {desc} | {target}% | {current}% |\n"
        totalidx = int(get_larger_root(1, 1, -2 * totalidx))
        table += f"| Total | Duration: {elapsed_time:.2f}/{target_time:.2f} hours | 100% | {totalcurrent}% |\n"
        if elapsed_time > target_time:
            # Remove the goal from goals and progress tables
            self.cursor.execute('DELETE FROM goals WHERE username = ?', (author,))
            self.cursor.execute('DELETE FROM progress WHERE username = ?', (author,))
            
            # Update the stats table
            self.cursor.execute('SELECT challenges_taken FROM stats WHERE username = ?', (author,))
            challenges = self.cursor.fetchone()
            if challenges:
                challenges_taken = challenges[0] + 1
                self.cursor.execute('UPDATE stats SET challenges_taken = ? WHERE username = ?', (challenges_taken, author))
            else:
                self.cursor.execute('INSERT INTO stats (username, challenges_taken) VALUES (?, 1)', (author,))

            # For hours_studied, using ratio of target overall percentage completed out of allotted time
            total_percentage_completed = totalcurrent
            hours_studied = (total_percentage_completed / 100) * target_time / 3600
            
            self.cursor.execute('UPDATE stats SET hours_studied = hours_studied + ? WHERE username = ?', (hours_studied, author))
            self.conn.commit()
            return f"""{table}\n
            You forgot to update the task. This table will be removed from the database now.
            See your current stats using 'u/padhle-bsdkk stats'
            """
        return table

    def add_goal(self, author, command_text):
        # Extracting goal data
        goal_data_match = re.search(r'"(.*?)"', command_text)
        texttemp = ""
        self.cursor.execute('''SELECT task_description, current_percentage FROM progress WHERE username = ?''', (author,))
        current_percentages = dict(self.cursor.fetchall())

        if "%" in command_text:
            texttemp += 'Avoid using %'
        if not goal_data_match or "%" in command_text:
            return f"""*Invalid goal format. {texttemp}*
            **Dummy Example**: 
            ```
            u/padhle-bsdkk addgoal "Modern Physics PYQ from Marks: 0.5 hours"
            ```
            **Syntax**: <task description>: x hours (keep in hours. for 30 minutes: 0.5 hours)
            """
        
        goal_data_str = goal_data_match.group(1)
        task_description, target_time_str = goal_data_str.rsplit(':', 1)
        try:
            additional_time = float(target_time_str.strip().split()[0]) * 3600  # Convert hours to seconds
        except ValueError:
            return """*Invalid time format*. 
            **Dummy Example**: 
            ```
            u/padhle-bsdkk addgoal "Modern Physics PYQ from Marks: 0.5 hours"
            ```
            **Syntax**: <task description>: x hours (keep in hours. for 30 minutes: 0.5 hours)
            """

        # Fetch existing goals and time
        self.cursor.execute('''
            SELECT goal_data, target_time
            FROM goals
            WHERE username = ?
        ''', (author,))
        existing_goals = self.cursor.fetchone()
        if not existing_goals:
            return "No existing goals found for the user."

        existing_goal_data, existing_target_time = existing_goals
        tasks = json.loads(existing_goal_data)
        total_time = existing_target_time + additional_time

        # Check if task already exists
        if any(task_description.strip() in task for task in tasks):
            return f"Task '{task_description.strip()}' already exists for {author}."

        new_percentage = round((additional_time / total_time) * 100, 2)
        tasks.append(f"{task_description.strip()} [{new_percentage}%]")

        # Adjust percentages for existing tasks
        for idx, task in enumerate(tasks[:-1]):
            task_desc, percentage_str = task.rsplit('[', 1)
            old_percentage = float(percentage_str.split('%')[0])
            new_task_percentage = round((round((old_percentage / 100) * existing_target_time, 2) / (total_time)) * 100, 2)
            tasks[idx] = f"{task_desc.strip()} [{new_task_percentage}%]"

        # Update the goals in the database
        self.cursor.execute('''
            UPDATE goals
            SET goal_data = ?, target_time = ?
            WHERE username = ?
        ''', (json.dumps(tasks), total_time, author))

        for task in tasks:
            task_desc, percentage_str = task.rsplit('[', 1)
            target_percentage = float(percentage_str.split('%')[0])
            current_percentage = current_percentages.get(task_desc.strip(), 0)  # Use the stored current percentage if it exists
            self.cursor.execute('''INSERT OR REPLACE INTO progress (username, task_description, target_percentage, current_percentage)
                                    VALUES (?, ?, ?, ?)''', (author, task_desc.strip(), target_percentage, current_percentage))
        
        self.conn.commit()  # Commit changes to the database

        return f"Added new goal for {author}. Total time is now {total_time / 3600} hours!"


    def days_hours_minutes_remaining(self, target_date, event_name):
        current_date = datetime.now()
        difference = target_date - current_date
        total_seconds = difference.total_seconds()
        days = int(total_seconds // (24 * 3600))
        remaining_seconds = total_seconds % (24 * 3600)
        hours = int(remaining_seconds // 3600)
        remaining_seconds %= 3600
        minutes = int(remaining_seconds // 60)
        return f"{event_name}: {days} days, {hours} hours, {minutes} minutes remaining"

    def display_time_remaining(self, comment, author):
        jee_date = datetime(2024, 1, 24)
        neet_date = datetime(2024, 5, 7)
        imagenum = random.choice([1, 2, 3])

        background = Image.open(f'main{imagenum}.png')
        image = Image.new('RGBA', background.size, (255, 255, 255, 0))
        font_arialbd = './arialbd.ttf'
        
        font1 = ImageFont.truetype(font_arialbd, 36)
        font2 = ImageFont.truetype(font_arialbd, 30)
        draw = ImageDraw.Draw(image)
        
        colorcode = {
            1: [255, 255, 255, 0, 0, 0],
            2: [255, 255, 255, 255, 255, 255],
            3: [54, 22, 6, 250, 187, 12]
        }
        
        bg_width, bg_height = background.size

        draw.text((10, 15),
                f'Padhle {author}!',
                font=font1,
                fill=(colorcode[imagenum][0], colorcode[imagenum][1],
                        colorcode[imagenum][2]))
        
        quote = self.give_random_quote()
        print("dimension: ", bg_width, bg_height)
        y1 = 60
        quote_text = textwrap.wrap(quote, width=25)

        draw.rectangle([(8, 58),
                        (bg_width - 12, y1 + len(quote_text) * 30 + 5)],
                        fill=(0, 0, 0, 128))
        for line in quote_text:
            draw.text((10, y1),
                    line,
                    font=font2,
                    fill=(colorcode[imagenum][0], colorcode[imagenum][1],
                            colorcode[imagenum][2]))
            y1 += 30
        
        arg = {1: 330, 2: 330, 3: 190}[imagenum]
        jee_text = self.days_hours_minutes_remaining(jee_date, 'Mains 2024')
        neet_text = self.days_hours_minutes_remaining(neet_date, 'NEET 2024')
        jee_lines = textwrap.wrap(jee_text, width=30)
        neet_lines = textwrap.wrap(neet_text, width=30)
        y = {1: 370, 2: 370, 3: 230}[imagenum]

        draw.rectangle([(9, arg - 5),
                        (bg_width - 12, y +
                        (len(jee_lines) + len(neet_lines)) * 30)],
                    fill=(0, 0, 0, 128))
        draw.text((10, arg),
                'Time left: ',
                font=font1,
                fill=(colorcode[imagenum][3], colorcode[imagenum][4],
                        colorcode[imagenum][5]))

        for line in jee_lines:
            draw.text((10, y),
                    line,
                    font=font2,
                    fill=(255, 0, 0))
            y += 30
        for line in neet_lines:
            draw.text((10, y),
                    line,
                    font=font2,
                    fill=(colorcode[imagenum][3], colorcode[imagenum][4],
                            colorcode[imagenum][5]))
            y += 30

        image = Image.alpha_composite(background.convert('RGBA'), image)
        image.save('time_remaining.png')
        uploaded_image = self.client.upload_from_path('time_remaining.png')
        image_link = uploaded_image['link']
        comment.reply(f"There you go! [time left]({image_link})")
        os.remove("time_remaining.png")
    def remove_goal(self, author, command_text):
        # Extracting task number to be removed
        task_num_match = re.search(r'removegoal (\d+)', command_text)
        if not task_num_match:
            return """*Invalid command format*. 
            **Dummy Example**: 
            ```
            u/padhle-bsdkk removegoal 2
            ```
            **Syntax**: removegoal <task number>
            """

        task_num = int(task_num_match.group(1))

        # Fetch existing goals
        self.cursor.execute('''SELECT goal_data, target_time FROM goals WHERE username = ?''', (author,))
        existing_goals = self.cursor.fetchone()
        if not existing_goals:
            return "No existing goals found for the user."

        existing_goal_data,current_total_time = existing_goals
        tasks = json.loads(existing_goal_data)

        if task_num > len(tasks) or task_num < 1:
            return "Invalid task number. Please provide a valid task number to remove."

        # Remove the task
        print(tasks)
        removed_task = tasks.pop(task_num - 1)
        _, removed_percentage_str = removed_task.rsplit('[', 1)
        removed_percentage = float(removed_percentage_str.split('%')[0])
        time_to_be_removed = (removed_percentage / 100) * current_total_time

        # Adjust the total time
        new_total_time = current_total_time - time_to_be_removed
        # Calculate the total percentage of remaining tasks before adjustment
        total_percentage_before = sum(float(task.rsplit('[', 1)[1].split('%')[0]) for task in tasks)

        # Adjust the percentages of the remaining tasks
        for idx, task in enumerate(tasks):
            task_desc, percentage_str = task.rsplit('[', 1)
            old_percentage = float(percentage_str.split('%')[0])
            # The adjustment is proportional to each task's previous percentage
            adjustment = (old_percentage / total_percentage_before) * removed_percentage
            new_percentage = old_percentage + adjustment
            tasks[idx] = f"{task_desc.strip()} [{new_percentage:.2f}%]"

        # Update the goals in the database
        self.cursor.execute('''
            UPDATE goals
            SET goal_data = ?, target_time = ?
            WHERE username = ?
        ''', (json.dumps(tasks), new_total_time, author))

        for task in tasks:
            task_desc, percentage_str = task.rsplit('[', 1)
            target_percentage = float(percentage_str.split('%')[0])
            self.cursor.execute('''
                INSERT OR REPLACE INTO progress (username, task_description, target_percentage, current_percentage)
                VALUES (?, ?, ?, 0)
            ''', (author, task_desc.strip(), target_percentage))

        # Remove the task from the progress table
        task_desc, _ = removed_task.rsplit('[', 1)
        self.cursor.execute('''
            DELETE FROM progress
            WHERE username = ? AND task_description = ?
        ''', (author, task_desc.strip()))

        self.conn.commit()
        return f"Removed goal {task_num} for {author}!"



    def display_stats(self, author):
        self.cursor.execute('''
            SELECT challenges_taken, streak, hours_studied
            FROM stats
            WHERE username = ?
        ''', (author,))
        stats_data = self.cursor.fetchone()
        
        if not stats_data:
            return f"No stats data found for {author}."

        challenges_taken, streak, hours_studied = stats_data

        return (f"**Stats for {author}**:\n\n"
                f"- Challenges taken: {challenges_taken}\n"
                f"- Current streak: {streak} days\n"
                f"- Total hours studied: {hours_studied:.2f} hours")
    def run(self):
        print("Checking for new messages...")
        while True:
            for comment in self.subreddit.stream.comments(skip_existing=True):
                if comment.id in self.processed_comments:
                    continue
                self.processed_comments.add(comment.id)
                try:
                    author = comment.author.name
                except AttributeError:
                    continue

                print(f"New message from {author}...")
                if "u/padhle-bsdkk time" in comment.body.lower() and author != 'padhle-bsdkk' and self.is_valid_command_url(comment, "time"):
                    self.display_time_remaining(comment, author)
                if "u/padhle-bsdkk setgoal" in comment.body.lower() and author != 'padhle-bsdkk' and self.is_valid_command_url(comment, "setgoal"):
                    response = self.set_goal(author, comment.body)
                    comment.reply(response)
                if "u/padhle-bsdkk updategoal" in comment.body.lower() and author != 'padhle-bsdkk' and self.is_valid_command_url(comment, "updategoal"):
                    response = self.update_goal(author, comment.body)
                    comment.reply(response)
                if "u/padhle-bsdkk viewgoal" in comment.body.lower() and author != 'padhle-bsdkk' and self.is_valid_command_url(comment, "viewgoal"):
                    response = self.view_goal(author)
                    comment.reply(response)
                if "u/padhle-bsdkk addgoal" in comment.body.lower() and author != 'padhle-bsdkk' and self.is_valid_command_url(comment, "addgoal"):
                    response = self.add_goal(author, comment.body)
                    comment.reply(response)
                if "u/padhle-bsdkk removegoal" in comment.body.lower() and author != 'padhle-bsdkk' and self.is_valid_command_url(comment, "removegoal"):
                    response = self.remove_goal(author, comment.body)
                    comment.reply(response)
                if "u/padhle-bsdkk stats" in comment.body.lower() and author!='padhle-bsdkk' and self.is_valid_command_url(comment, 'stats'):
                    response = self.display_stats(author)
                    comment.reply(response)


if __name__ == "__main__":
    bot = RedditBot()
    # mode = input("Enter 'simulate' to run in simulation mode or 'run' to run normally: ")
    mode = 'simulate'
    if mode == "simulate":
        bot.simulate()
    else:
        bot.run()
