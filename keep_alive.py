from flask import Flask
from threading import Thread
import os
app = Flask('')

port = int(os.environ.get("PORT", 5000))
@app.route("/")
def home():
  return "hello, I'm alive!"


def run():
  app.run(host="0.0.0.0", port=port)


def keep_alive():
  t = Thread(target=run)
  t.start()
