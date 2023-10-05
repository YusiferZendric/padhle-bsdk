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
            totalPercentage.append(target_percentage)
        if sum(totalPercentage) != 100:
            return """*Total percentage of all Tasks should be 100. Eg: 30 50 20*. 
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
        return f"Goal set for {author}. I'll remind you in {target_time_str} hours!"

    def give_random_quote(self):
        with open("quotes.txt", 'r') as file:
            return random.choice(file.readlines()).strip()
    def update_goal(self, author, command_text):
        # Extracting task updates
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
        
            # Fetch the task description based on the task number
            self.cursor.execute('''
                SELECT task_description FROM progress
                WHERE username = ?
                ORDER BY task_description ASC
                LIMIT 1 OFFSET ?
            ''', (author, task_num - 1))
            result = self.cursor.fetchone()
            if not result:
                continue
            task_description = result[0]

            # Update the current percentage for the task
            self.cursor.execute('''
                UPDATE progress
                SET current_percentage = ?
                WHERE username = ? AND task_description = ?
            ''', (percentage, author, task_description))

        self.conn.commit()

        self.cursor.execute('''
            SELECT current_percentage, target_percentage
            FROM progress
            WHERE username = ?
        ''', (author,))
        results = self.cursor.fetchall()
        if not results:
            return "No goals found for the user."

        progress_messages = []
        total_progress = 0
        total_target = 0
        for current, target in results:
            progress_percentage = (current / 100) * target
            total_progress += progress_percentage
            total_target += target
            progress_messages.append(f"{progress_percentage:.2f}/{target}")

        overall_percentage = (total_progress / total_target) * 100
        progress_summary = ", ".join(progress_messages)
        for task_num, percentage in updates:
            self.cursor.execute('''
                SELECT target_percentage
                FROM progress
                WHERE username = ? AND task_description = ?
            ''', (author, task_description))
            target_percentage = self.cursor.fetchone()[0]
            remaining_percentage = int(target_percentage) - (int(percentage) / 100) * int(target_percentage)
            self.cursor.execute('''
                UPDATE progress
                SET current_percentage = ?, task_description = REPLACE(task_description, ? || '%]', ? || '%]')
                WHERE username = ? AND task_description LIKE ?
            ''', (percentage, target_percentage, remaining_percentage, author, task_description.split('[')[0] + '%'))
        return f"Updated your goals, {author}. Your progress: {progress_summary}. Overall: {overall_percentage:.2f}% of your total goals!"
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
        elapsed_time = (current_time - goal_datetime).seconds / 3600

        print("Most Recent Goal Timestamp:", goal_timestamp)
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
        return table

    def add_goal(self, author, command_text):
        # Extracting goal data
        goal_data_match = re.search(r'"(.*?)"', command_text)
        texttemp = ""
        if "%" in command_text:
            texttemp+='Avoid using %'
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
        new_percentage = round((additional_time/total_time)*100,2)
        tasks.append(f"{task_description.strip()} [{new_percentage}%]")

        # Adjust percentages for existing tasks
        for idx, task in enumerate(tasks[:-1]):
            task_desc, percentage_str = task.rsplit('[', 1)
            old_percentage = float(percentage_str.split('%')[0])
            new_task_percentage = round((round((old_percentage/100)* existing_target_time,2)/(total_time))*100,2)
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
            self.cursor.execute('''
                INSERT OR REPLACE INTO progress (username, task_description, target_percentage, current_percentage)
                VALUES (?, ?, ?, 0)
            ''', (author, task_desc.strip(), target_percentage))
        self.conn.commit()
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
        if task_num > len(tasks) or task_num < 1:
            return "Invalid task number. Please provide a valid task number to remove."

        # Extract the percentage of the task to be removed
        removed_task = tasks.pop(task_num - 1)
        _, removed_percentage_str = removed_task.rsplit('[', 1)
        removed_percentage = float(removed_percentage_str.split('%')[0])

        # Calculate time to be reduced
        time_per_percentage = existing_target_time / 100
        reduced_time = removed_percentage * time_per_percentage
        total_time = existing_target_time - reduced_time

        # Adjust percentages for remaining tasks
        for idx, task in enumerate(tasks):
            task_desc, percentage_str = task.rsplit('[', 1)
            old_percentage = float(percentage_str.split('%')[0])
            new_task_percentage = round((time_per_percentage * old_percentage) / total_time, 2)*100
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
        return f"Removed goal {task_num} for {author}. Total time is now {total_time / 3600} hours!"

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
                if "u/padhle-bsdkk time" in comment.body.lower() and author != 'padhle-bsdkk':
                    self.display_time_remaining(comment, author)
                if "u/padhle-bsdkk setgoal" in comment.body.lower() and author != 'padhle-bsdkk':
                    response = self.set_goal(author, comment.body)
                    comment.reply(response)
                if "u/padhle-bsdkk updategoal" in comment.body.lower() and author != 'padhle-bsdkk':
                    response = self.update_goal(author, comment.body)
                    comment.reply(response)
                if "u/padhle-bsdkk viewgoal" in comment.body.lower() and author != 'padhle-bsdkk':
                    response = self.view_goal(author)
                    comment.reply(response)
                if "u/padhle-bsdkk addgoal" in comment.body.lower() and author != 'padhle-bsdkk':
                    response = self.add_goal(author, comment.body)
                    comment.reply(response)
                if "u/padhle-bsdkk removegoal" in comment.body.lower() and author != 'padhle-bsdkk':
                    response = self.remove_goal(author, comment.body)
                    comment.reply(response)

if __name__ == "__main__":
    bot = RedditBot()
    bot.run()
