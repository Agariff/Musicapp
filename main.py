import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.audio import SoundLoader

MUSIC_DIR = "/sdcard/Music"  # folder on your phone where songs live

class MusicApp(App):
    def build(self):
        self.sound = None
        self.current_song = None

        root = BoxLayout(orientation="vertical")

        # Now playing label
        self.now_playing = Label(text="No song playing", size_hint_y=0.1)
        root.add_widget(self.now_playing)

        # Play/Pause/Stop controls
        controls = BoxLayout(size_hint_y=0.1)
        play_btn = Button(text="Play/Pause")
        play_btn.bind(on_press=self.toggle_play)
        stop_btn = Button(text="Stop")
        stop_btn.bind(on_press=self.stop_song)
        controls.add_widget(play_btn)
        controls.add_widget(stop_btn)
        root.add_widget(controls)

        # Scrollable song list
        scroll = ScrollView(size_hint_y=0.8)
        self.song_list = GridLayout(cols=1, size_hint_y=None)
        self.song_list.bind(minimum_height=self.song_list.setter("height"))
        scroll.add_widget(self.song_list)
        root.add_widget(scroll)

        self.load_songs()
        return root

    def load_songs(self):
        if not os.path.exists(MUSIC_DIR):
            self.song_list.add_widget(Label(text=f"No folder found: {MUSIC_DIR}", size_hint_y=None, height=50))
            return

        songs = [f for f in os.listdir(MUSIC_DIR) if f.lower().endswith((".mp3", ".wav", ".ogg"))]

        if not songs:
            self.song_list.add_widget(Label(text="No songs found", size_hint_y=None, height=50))
            return

        for song in songs:
            btn = Button(text=song, size_hint_y=None, height=60)
            btn.bind(on_press=lambda instance, s=song: self.play_song(s))
            self.song_list.add_widget(btn)

    def play_song(self, song_name):
        if self.sound:
            self.sound.stop()

        path = os.path.join(MUSIC_DIR, song_name)
        self.sound = SoundLoader.load(path)

        if self.sound:
            self.sound.play()
            self.current_song = song_name
            self.now_playing.text = f"Playing: {song_name}"

    def toggle_play(self, instance):
        if self.sound:
            if self.sound.state == "play":
                self.sound.stop()
            else:
                self.sound.play()

    def stop_song(self, instance):
        if self.sound:
            self.sound.stop()
            self.now_playing.text = "Stopped"

if __name__ == "__main__":
    MusicApp().run()
