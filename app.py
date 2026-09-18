# app.py

import os
import random
from flask import Flask, render_template
import redis

app = Flask(__name__)

redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = int(os.getenv("REDIS_PORT", 6379))

redis_client = redis.Redis(host=redis_host, port=redis_port)

quotes = [
    "Doubt kills more dreams than failure ever will. – Suzy Kassem",
    "Keep your face always toward the sunshine, and shadows will fall behind you. – Walt Whitman",
    "Whether you think you can or think you can't, you're right. – Henry Ford",
    "Your talent determines what you can do. Your motivation determines how much you're willing to do. Your attitude determines how well you do it. – Lou Holtz",
    "The happiness of your life depends on the quality of your thoughts. – Marcus Aurelius",
    "Nothing is impossible. The word itself says 'I'm possible!' – Audrey Hepburn"
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/count')
def count():
    visits = redis_client.incr('counter')
    quote = random.choice(quotes)
    return render_template('count.html', visit_count=visits, quote=quote)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
