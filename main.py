import datetime
import os
import time

from googletrans import Translator
import configparser
import tkinter as tk
import test_gui

displayed_success_message = False


def load_ini(changeDir=False):
    if not os.path.exists('settings.ini'):
        with open('settings.ini', 'w') as ini:
            pass
    config = configparser.ConfigParser()
    config.read('settings.ini')
    if len(config.sections()) == 0 or changeDir:
        root = tk.Tk()
        if changeDir:
            app = test_gui.Application(master=root, file_error=True)
        else:
            app = test_gui.Application(master=root)
        app.mainloop()
        folderName = test_gui.fd
        config['SETTINGS'] = {'LogPath': folderName, 'lang': 'en'}
        with open('settings.ini', 'w') as configfile:
            config.write(configfile)
    return config['SETTINGS']['logpath'], config['SETTINGS']['lang']


logFileFolderPath, userLanguage = load_ini()


def find_newest_log():
    filenames = os.listdir(logFileFolderPath)
    newest_file_name = filenames[0]

    for filename in filenames:
        current_winner = datetime.datetime.strptime(newest_file_name, '%Y-%m-%d.log')
        new_date = datetime.datetime.strptime(filename, '%Y-%m-%d.log')
        if new_date > current_winner:
            newest_file_name = filename
    return newest_file_name


def parseMessage(line):
    message = line.split("]: ", 1)[1]
    message = message.strip()
    return message


def nation_faction_bug_fix(tag_string):
    base_tags = ["Nation", "Faction"]
    new_tags = ["Faction", "Nation"]
    list_length = len(base_tags)

    for x in range(list_length):
        if tag_string.find(base_tags[x]) != -1:
            tag_string = tag_string.replace(base_tags[x], new_tags[x])
            break
    return tag_string


def getUserTag(line):
    tag = line.split("|", 1)[1]
    tag = tag.split("]: ", 1)[0]
    tag = nation_faction_bug_fix(tag)
    return tag + "]: "


def translateMessage(message):
    translator = Translator()
    lang = translator.detect(message).lang

    if type(lang) != str:
        lang = userLanguage

    print("Language: " + lang)

    if lang == userLanguage:
        print(message)
        return

    print(translator.translate(message, dest=userLanguage, src=lang).text)


def watch_log():
    global logFileFolderPath
    global userLanguage
    global displayed_success_message

    try:
        log_filename = find_newest_log()
        log_filename_path = logFileFolderPath + log_filename
        file = open(log_filename_path, encoding='utf8', mode='r')
    except:
        print("No log file found")
        logFileFolderPath, userLanguage = load_ini(changeDir=True)
        return

    if not displayed_success_message:
        print("Log file found, waiting for new messages...")
        displayed_success_message = True

    st_results = os.stat(log_filename_path)
    st_size = st_results[6]
    file.seek(st_size)

    old_line = ""

    while 1:
        where = file.tell()
        line = file.readline()
        if not line:
            time.sleep(1)
            file.seek(where)
        else:
            if old_line == "":
                translateMessage(getUserTag(line) + parseMessage(line))
                old_line = getUserTag(line) + parseMessage(line)
            if old_line != (getUserTag(line) + parseMessage(line)):
                translateMessage(getUserTag(line) + parseMessage(line))
                old_line = getUserTag(line) + parseMessage(line)

        if log_filename != find_newest_log():
            return


while 1:
    watch_log()