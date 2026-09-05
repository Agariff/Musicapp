import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.audio import SoundLoader
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

MUSIC_DIR = "/sdcard/Music"

# Spotify-style colors
BG_COLOR = (0.07, 0.07, 0.07, 1)        # #121212
CARD_COLOR = (0.12, 0.12, 0.12, 1)      # #1e1e1e
GREEN = (0.11, 0.72, 0.33, 1)           # #1DB954
WHITE = (1, 1, 1, 1)
GREY = (0.65, 0.65, 0.65, 1)


def get_tags(path):
    """Try to read title/artist tags, fallback to filename."""
    try:
        audio = EasyID3(path)
        title = audio.get("title", [None])[0]
        artist = audio.get("artist", [None])[0]
        return title, artist
    except Exception:
        return None, None


class SongRow(BoxLayout):
    def __init__(self, filename, title, artist, on_play, **kwargs):
        super().__init__(orientation="horizontal", size_hint_y=None, height=64, padding=10, spacing=10, **kwargs)
        with self.canvas.before:
            Color(*CARD_COLOR)
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)

        info = BoxLayout(orientation="vertical")
        info.add_widget(Label(text=title or filename, color=WHITE, bold=True,
                               halign="left", valign="middle", size_hint_y=0.6,
                               text_size=(Window.width - 140, None)))
        info.add_widget(Label(text=artist or "Unknown Artist", color=GREY,
                               halign="left", valign="middle", size_hint_y=0.4,
                               text_size=(Window.width - 140, None)))
        self.add_widget(info)

        play_btn = Button(text="▶", size_hint_x=None, width=50,
                           background_color=GREEN, color=WHITE)
        play_btn.bind(on_press=lambda inst: on_play(filename, title or filename, artist))
        self.add_widget(play_btn)

    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size


class MiniPlayer(BoxLayout):
    def __init__(self, toggle_play, stop_song, **kwargs):
        super().__init__(orientation="horizontal", size_hint_y=None, height=70,
                          padding=10, spacing=10, **kwargs)
        with self.canvas.before:
            Color(0.15, 0.15, 0.15, 1)
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)

        self.now_playing = Label(text="Nothing playing", color=WHITE, bold=True,
                                  halign="left", valign="middle",
                                  text_size=(Window.width - 160, None))
        self.add_widget(self.now_playing)

        play_btn = Button(text="⏯", size_hint_x=None, width=50,
                           background_color=GREEN, color=WHITE)
        play_btn.bind(on_press=toggle_play)
        self.add_widget(play_btn)

        stop_btn = Button(text="⏹", size_hint_x=None, width=50,
                           background_color=(0.3, 0.3, 0.3, 1), color=WHITE)
        stop_btn.bind(on_press=stop_song)
        self.add_widget(stop_btn)

    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def set_song(self, title, artist):
        self.now_playing.text = f"{title} — {artist}" if artist else title


class MusicApp(App):
    def build(self):
        self.sound = None
        self.current_song = None

        root = BoxLayout(orientation="vertical")
        with root.canvas.before:
            Color(*BG_COLOR)
            self.bg_rect = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=self.update_bg, size=self.update_bg)

        # Header
        header = Label(text="Your Library", color=WHITE, bold=True, font_size=24,
                        size_hint_y=None, height=60, halign="left", valign="middle")
        header.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        root.add_widget(header)

        # Scrollable song list
        scroll = ScrollView()
        self.song_list = GridLayout(cols=1, size_hint_y=None, spacing=2, padding=5)
        self.song_list.bind(minimum_height=self.song_list.setter("height"))
        scroll.add_widget(self.song_list)
        root.add_widget(scroll)

        # Mini player bar at bottom
        self.mini_player = MiniPlayer(self.toggle_play, self.stop_song)
        root.add_widget(self.mini_player)

        self.load_songs()
        return root

    def update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def load_songs(self):
        if not os.path.exists(MUSIC_DIR):
            self.song_list.add_widget(Label(text=f"No folder found: {MUSIC_DIR}",
                                             color=GREY, size_hint_y=None, height=50))
            return

        songs = [f for f in os.listdir(MUSIC_DIR) if f.lower().endswith((".mp3", ".wav", ".ogg"))]

        if not songs:
            self.song_list.add_widget(Label(text="No songs found", color=GREY,
                                             size_hint_y=None, height=50))
            return

        for song in songs:
            path = os.path.join(MUSIC_DIR, song)
            title, artist = get_tags(path) if song.lower().endswith(".mp3") else (None, None)
            row = SongRow(song, title, artist, self.play_song)
            self.song_list.add_widget(row)

    def play_song(self, filename, title, artist):
        if self.sound:
            self.sound.stop()

        path = os.path.join(MUSIC_DIR, filename)
        self.sound = SoundLoader.load(path)

        if self.sound:
            self.sound.play()
            self.current_song = filename
            self.mini_player.set_song(title, artist)

    def toggle_play(self, instance):
        if self.sound:
            if self.sound.state == "play":
                self.sound.stop()
            else:
                self.sound.play()

    def stop_song(self, instance):
        if self.sound:
            self.sound.stop()
            self.mini_player.set_song("Nothing playing", "")


if __name__ == "__main__":
    MusicApp().run()
