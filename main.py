import random
import string
import json
from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)
shortened_urls = {}

def generate_short_url(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        short_url = generate_short_url()
        while short_url in shortened_urls:
            short_url = generate_short_url()
        shortened_urls[short_url] = url
        with open("urls.json", "w") as file:
            json.dump(shortened_urls, file)
        return f"Shortened URL: <a href='{url_for('redirect_to_url', short_url=short_url, _external=True)}'>{url_for('redirect_to_url', short_url=short_url, _external=True)}</a>"
    return render_template('index.html')

@app.route('/<short_url>')
def redirect_to_url(short_url):
    url = shortened_urls.get(short_url)
    if url is None:
        return "URL not found", 404 # Not Found)
    return redirect(url)

if __name__ == '__main__':
    app.run(debug=True)