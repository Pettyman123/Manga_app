from flask import Flask, render_template, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def get_manga_updates():
    mangadex_url = 'https://mangadex.org/updates'
    response = requests.get(mangadex_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    updates = soup.find_all('div', class_='update-class')  # Adjust based on actual HTML structure
    
    manga_list = []
    for update in updates:
        title = update.find('a').text
        link = update.find('a')['href']
        image = update.find('img')['src']
        manga_list.append({'title': title, 'link': link, 'image': image})
    
    return manga_list

@app.route('/api/manga')
def manga_api():
    manga_list = get_manga_updates()
    return jsonify(manga_list)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
