# app.py

from flask import Flask
import redis
import random

app = Flask(__name__)

redis_client = redis.Redis(host='redis', port=6379)

quotes = [
    "Doubt kills more dreams than failure ever will. – Suzy Kassem",
    "Keep your face always toward the sunshine, and shadows will fall behind you. – Walt Whitman",
    "Whether you think you can or think you can't, you're right. – Henry Ford",
    "Your talent determines what you can do. Your motivation determines how much you're willing to do. Your attitude determines how well you do it. – Lou Holtz",
    "The happiness of your life depends on the quality of your thoughts. – Marcus Aurelius",
    "Nothing is impossible. The word itself says 'I'm possible!' – Audrey Hepburn"
]

def render_page(title, subtitle=""):
    return f"""
    <html>
      <head>
        <title>Flask + Redis App</title>
        <style>
          body {{
            font-family: Arial, sans-serif;
            text-align: center;
            margin-top: 100px;
          }}
          h1 {{
            font-size: 36px;
          }}
          p {{
            font-size: 20px;
            color: #555;
          }}
        </style>
      </head>
      <body>
        <h1>{title}</h1>
        <p>{subtitle}</p>
      </body>
    </html>
    """

@app.route('/')
def home():
    return render_page("Welcome to my Flask + Redis app!")

@app.route('/count')
def count():
    visits = redis_client.incr('counter')
    quote = random.choice(quotes)
    return render_page(f"Visit count: {visits}", quote)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
