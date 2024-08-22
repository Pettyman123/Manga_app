import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import AsyncImage
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from functools import partial

class MangaReader(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Add title
        self.add_widget(Label(text='Manga Reader App', size_hint=(1, 0.1), font_size='20sp'))

        # Scrollable area for manga list
        self.scrollview = ScrollView(size_hint=(1, 0.9))
        self.manga_list = BoxLayout(orientation='vertical', size_hint_y=None)
        self.manga_list.bind(minimum_height=self.manga_list.setter('height'))
        self.scrollview.add_widget(self.manga_list)
        self.add_widget(self.scrollview)

        # Fetch and display manga data
        self.get_manga_data()

    def get_manga_data(self):
        try:
            response = requests.get('https://api.mangadex.org/manga?includes[]=cover_art')
            if response.status_code == 200:
                mangas = response.json().get('data', [])
                for manga in mangas:
                    title = manga['attributes']['title'].get('en', 'No Title')
                    manga_id = manga['id']
                    
                    # Retrieve cover art
                    cover_art = next((rel['attributes']['fileName'] for rel in manga['relationships'] if rel['type'] == 'cover_art'), None)
                    cover_url = f'https://uploads.mangadex.org/covers/{manga_id}/{cover_art}' if cover_art else ''

                    # Create button with image and title
                    button_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=200)
                    img = AsyncImage(source=cover_url, size_hint=(1, 0.8))
                    btn = Button(text=title, size_hint=(1, 0.2))
                    btn.bind(on_press=partial(self.show_manga_details, manga_id))
                    
                    button_layout.add_widget(img)
                    button_layout.add_widget(btn)
                    self.manga_list.add_widget(button_layout)
            else:
                self.manga_list.add_widget(Label(text='Error fetching data', size_hint_y=None, height=40))
        except Exception as e:
            self.manga_list.add_widget(Label(text=f'Error: {str(e)}', size_hint_y=None, height=40))

    def show_manga_details(self, manga_id, instance):
        try:
            chapters_response = requests.get(f'https://api.mangadex.org/manga/{manga_id}/feed?translatedLanguage[]=en&order[chapter]=asc')
            if chapters_response.status_code == 200:
                chapters_data = chapters_response.json().get('data', [])
                
                # Popup content .
                content = BoxLayout(orientation='vertical', size_hint=(1, 0.9))
                scroll = ScrollView(size_hint=(1, 0.8))
                chapter_list = BoxLayout(orientation='vertical', size_hint_y=None)
                chapter_list.bind(minimum_height=chapter_list.setter('height'))
                
                scroll.add_widget(chapter_list)
                content.add_widget(scroll)

                for chap in chapters_data:
                    chapter_title = chap['attributes'].get('title', f"Chapter {chap['attributes'].get('chapter', '')}")
                    chapter_id = chap['id']
                    btn = Button(text=chapter_title, size_hint_y=None, height=40)
                    btn.bind(on_press=partial(self.show_chapter, chapter_id))
                    chapter_list.add_widget(btn)
                
                close_button = Button(text='Close', size_hint=(1, 0.1))
                content.add_widget(close_button)
                
                popup = Popup(title='Chapters', content=content, size_hint=(0.8, 0.8))
                close_button.bind(on_press=popup.dismiss)
                popup.open()
            else:
                print('Error fetching chapters')
        except Exception as e:
            print(f'Error: {str(e)}')

    def show_chapter(self, chapter_id, instance):
        try:
            pages_response = requests.get(f'https://api.mangadex.org/at-home/server/{chapter_id}')
            if pages_response.status_code == 200:
                base_url = pages_response.json()['baseUrl']
                chapter_hash = pages_response.json()['chapter']['hash']
                pages = pages_response.json()['chapter']['data']

                content = BoxLayout(orientation='vertical')
                scroll = ScrollView()
                chapter_view = BoxLayout(orientation='vertical', size_hint_y=None)
                chapter_view.bind(minimum_height=chapter_view.setter('height'))
                
                for page in pages:
                    img = AsyncImage(source=f"{base_url}/data/{chapter_hash}/{page}", size_hint_y=None, height=500)
                    chapter_view.add_widget(img)

                scroll.add_widget(chapter_view)
                content.add_widget(scroll)

                close_button = Button(text='Close', size_hint=(1, 0.1))
                content.add_widget(close_button)

                popup = Popup(title='Chapter View', content=content, size_hint=(0.9, 0.9))
                close_button.bind(on_press=popup.dismiss)
                popup.open()
            else:
                print('Error fetching chapter pages')
        except Exception as e:
            print(f'Error: {str(e)}')

class MangaReaderApp(App):
    def build(self):
        return MangaReader()

if __name__ == '__main__':
    MangaReaderApp().run()
