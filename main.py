from tkinter import *
import tkinter as tk
import sqlite3         
import time             
from tkinter import messagebox 
from tkinter import ttk 
import tweepy 
from datetime import date
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


conn = sqlite3.connect('user_database')
c= conn.cursor()

def create_database():
    conn = sqlite3.connect('user_database')
    c= conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    ID integer PRIMARY KEY, 
                    user_name text NOT NULL, 
                    time integer DEFAULT 0)
              ''')
    conn.commit()
    conn.close()
create_database()

def create_time_database():
    conn = sqlite3.connect('user_database')
    c= conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS time ( 
                    user_name text NOT NULL, 
                    saved_time int NOT NULL, 
                    date timestamp NOT NULL )
              ''')
    conn.commit()
    conn.close()
create_time_database()


def runTimer():

    holdvalue = int(minuteString.get())

    global clockTime
    global running

    try:
        clockTime = int(minuteString.get())*60 + int(secondString.get())
    except:
        messagebox.showinfo('wrong input',"this format is not supported.")
    
    running = True

    def insert_time():
        if clockTime == 0:
            curdate = date.today()
            time_var = c.execute("SELECT time FROM users WHERE user_name=?", [username_login])
            time_fetch= time_var.fetchone()
            if time_fetch:
                dateTime = sum(time_fetch)
                dateTime+= holdvalue
                c.execute("INSERT INTO time (user_name, saved_time, date) VALUES (?,?,?)" , (username_login, holdvalue, curdate,))  
                c.execute("UPDATE users SET time=? WHERE user_name=?" , (dateTime, username_login,))
                conn.commit()

    while(clockTime > -1):
        totalMinutes, totalSeconds = divmod(clockTime, 60)
             
        minuteString.set("{0:2d}".format(totalMinutes))
        secondString.set("{0:2d}".format(totalSeconds))

        root.update()
        time.sleep(1)

        clockTime -= 1
        insert_time()

    messagebox.showinfo('time is up',"your time is up and your coin status is changed, check that in the label in the main window.")


def stopTime():
    question = messagebox.askyesno("warning", 
    " if you cancel your study session prematurely, you will not get any coins and the time will not be saved.")
    if question == True:
        global clockTime
        minuteString.set("0")
        secondString.set("0")
        clockTime = -1
    else:
        pass


def records():
    records = Toplevel()
    records.title("records")
    records.geometry("700x750")

    records_tree= ttk.Treeview(records, selectmode="extended")
    records_tree['columns'] = ("Username", "Time", "Date")
    records_tree.column("#0", width=0, minwidth=0)
    records_tree.column("Username", anchor=W, width=120)
    records_tree.column("Time", anchor=CENTER, width=120)
    records_tree.column("Date", anchor=W, width=120)

    records_tree.heading("#0", text = "Label", anchor=W)
    records_tree.heading("Username", text = "Username", anchor=W)
    records_tree.heading("Time", text = "Time", anchor=CENTER)
    records_tree.heading("Date", text = "Date", anchor=W)
    
    data = c.execute("SELECT * FROM time WHERE user_name=?", (username_login,))
    fetched_records= data.fetchall()
    
    count=0
    for record in fetched_records:
            records_tree.insert(parent='', index='end', iid = count, text = '', values=(record[0], record[1], record[2]))  
            count+=1

    records_tree.pack()
    #createLineChart()
    data = c.execute("SELECT saved_time, date FROM time WHERE user_name=?", (username_login,))
    fetched_records = data.fetchall()
    timeStamps = [record[1] for record in fetched_records]
    timeMinutes =  [record[0] for record in fetched_records]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(timeStamps, timeMinutes, marker='o')
    ax.set_xlabel('Timestamp')
    ax.set_ylabel('Time (minutes)')
    ax.set_title('Time Records')
    plt.xticks(rotation=45, ha='right')

    canvas = FigureCanvasTkAgg(fig, master=records)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    c.execute("SELECT time FROM users WHERE user_name=?", (username_login,))
    sum_time = c.fetchone()
    sum_time = sum(sum_time)

    c.execute("SELECT saved_time FROM time WHERE user_name=?", (username_login,))
    count_time = c.fetchall()
    len_all_data = int(len(count_time))
    if len_all_data > 0:
        average= sum_time // len_all_data
        average_sum = Label(records, text='your average time is: '+str(average))
        average_sum.pack()

        records_date = date.today()
        c.execute("SELECT saved_time FROM time WHERE user_name=? AND date=?", (username_login, records_date,)) 
        day_sum = c.fetchall()
        sum_char = sum(day_sum, 0)
        for char in day_sum:
            char = sum(char)
            sum_char += char
    
    daily_sum = Label(records, text='your daily summary of time is: '+str(sum_char) + " minutes",  font=("Calibri", 15))
    daily_sum.pack()
    conn.close()


def share():
    API_KEY= ""
    API_KEY_SECRET = ""

    ACCESS_TOKEN=""
    ACCESS_TOKEN_SECRET = ""

    auth = tweepy.OAuthHandler(API_KEY, API_KEY_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    api = tweepy.API(auth)

    last_record = c.execute("SELECT saved_time FROM time WHERE user_name=?",(username_login,))
    tweet_time = last_record.fetchall()
    lastTweet = tweet_time[-1]
    tweet_time = sum(lastTweet)
    status=('sharing with #studyTimer, today I studied for %s' %(lastTweet)+' minutes')

    try:
        api.verify_credentials()
        api.update_status(status)
        messagebox.showinfo('success',"tweet was successfully posted on Twitter.")       
    except:
        messagebox.showinfo('eror',"tweet could not be posted, try again later please")

def get_tweets():

    tweets = Toplevel()
    tweets.geometry("500x500")
    tweets.title("studyTimer tweets")

    API_KEY= ""
    API_KEY_SECRET = ""

    ACCESS_TOKEN=""
    ACCESS_TOKEN_SECRET = ""
    
    auth = tweepy.OAuthHandler(API_KEY, API_KEY_SECRET)
    auth.set_access_token(ACCESS_TOKEN,ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    keyword= "#studyTimer"
    limit = 30

    fetch_tweets = api.search_tweets(keyword, count= limit)

    k=0
    row=0
    tweet_label=[]
    for tweet in fetch_tweets:
        tweet_label.append(Label(tweets, text = tweet.text, textvariable = tweet.text))
        tweet_label[k].grid(row = row, column = 2 )
        k+=1
        row+=1


def start_app():

    global root
    root = Toplevel()
    root.geometry("700x500")
    root.title("studyTimer!")
    root.configure(bg='#D3D3D3')

    label1 = Label(root, text="Hello, " + username_login + ", how long do you want to study?", bg='#D3D3D3', font=("Calibri", 15))
    label1.place(relx=0.5, rely=0.1, anchor="center")

    global minuteString
    global secondString
    minuteString = StringVar()
    secondString = StringVar()

    minuteString.set("00")
    secondString.set("00")

    minuteTextbox = Entry(root, width=3, font=("Calibri", 24, ""), textvariable=minuteString)
    secondTextbox = Entry(root, width=3, font=("Calibri", 24, ""), textvariable=secondString)
    minuteTextbox.place(relx=0.4, rely=0.4, anchor="center")
    secondTextbox.place(relx=0.6, rely=0.4, anchor="center")

    button1 = Button(root, text="Start", command=runTimer, bg='#808080', fg='white', padx=20, pady=10, borderwidth=0, font=('Calibri', 12))
    button1.place(relx=0.4, rely=0.6, anchor="center")
    button3 = Button(root, text="Stop", command=stopTime, bg='#808080', fg='white', padx=20, pady=10, borderwidth=0, font=('Calibri', 12))
    button3.place(relx=0.6, rely=0.6, anchor="center")


    button7 = Button(root, text="Records", command=records, bg='#808080', fg='white', padx=20, pady=10, borderwidth=0, font=('Calibri', 12))
    button7.place(relx=0.3, rely=0.8, anchor="center")
    button8 = Button(root, text="Share", command=share, bg='#808080', fg='white', padx=20, pady=10, borderwidth=0, font=('Calibri', 12))
    button8.place(relx=0.5, rely=0.8, anchor="center")
    button9 = Button(root, text="Twitter", command=get_tweets, bg='#808080', fg='white', padx=20, pady=10, borderwidth=0, font=('Calibri', 12))
    button9.place(relx=0.7, rely=0.8, anchor="center")
    

def login():

    global login_screen
    global username_login

    username_login = username.get()
    #username_login = StringVar()
    conn = sqlite3.connect('user_database')
    c = conn.cursor()

    try:
        c.execute("SELECT * FROM users WHERE user_name=?", (username_login,))
        existing_user = c.fetchone()

        if existing_user:
            start_app()
        else:
            c.execute("INSERT INTO users (user_name) VALUES (?)", (username_login,))
            conn.commit()
            start_app()
    finally:
        conn.close()

def login_screen():
    screen = Tk()
    screen.geometry("300x250")
    screen.title("First you need to log in")

    top_space = Label(screen, height=3)
    top_space.pack()

    global username
    username = StringVar()

    login_name_entry = Entry(screen, width=35, borderwidth=5, text="your username", textvariable=username)
    login_name_entry.pack()
    login_button = Button(screen, width=35, borderwidth=5, text="login", command=login)
    login_button.pack()
    close_button = Button(screen, text="close", width=35, borderwidth=5, command=screen.destroy)
    close_button.pack()

    screen.mainloop()

login_screen()