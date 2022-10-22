from flask import Flask
from threading import Thread
from itertools import cycle

app = Flask('')
status = cycle(['from Python', 'JetHub'])
@app.route('/')
def home():
  return "Bot still running."

def run():
  app.run(host = '0.0.0.0', port = 8080)

def keep_alive():
  t = Thread(target = run)
  t.start()