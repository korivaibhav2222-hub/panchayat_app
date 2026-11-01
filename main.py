# main.py - Clean - Created by Vaibhav
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
import json, os

DATA_FILE = "panchayat_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"users": [], "friends": {}, "requests": {}, "chats": {}}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

data = load_data()

class SplashScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'login'), 5)

class LoginScreen(Screen):
    def login(self):
        u = self.ids.user_input.text.strip()
        p = self.ids.pass_input.text.strip()
        user = next((x for x in data["users"] if x["username"].lower()==u.lower() or x["mobile"]==u), None)
        if not user or user["password"]!=p:
            self.ids.err.text = "Invalid username/mobile or password"
            return
        self.manager.get_screen('main').current_user = user
        self.manager.current = 'main'

class SignupScreen(Screen):
    def next_step(self):
        u = self.ids.username.text.strip()
        m = self.ids.mobile.text.strip()
        if not u or not m:
            self.ids.err.text = "Required"
            return
        if any(x["username"].lower()==u.lower() for x in data["users"]):
            self.ids.err.text = "This username is already exist, please choose another username"
            return
        self.manager.get_screen('setpass').temp_data = {"username":u, "mobile":m}
        self.manager.current = 'setpass'

class SetPassScreen(Screen):
    temp_data = {}
    def create_id(self):
        p = self.ids.pass1.text.strip()
        cp = self.ids.pass2.text.strip()
        if p != cp:
            self.ids.err.text = "Password match nahi"
            return
        nid = str(len(data["users"])+1000)
        user = {"id":nid, "username":self.temp_data["username"], "mobile":self.temp_data["mobile"], "password":p}
        data["users"].append(user)
        data["friends"][nid]=[]
        data["requests"][nid]=[]
        save_data(data)
        self.manager.get_screen('main').current_user = user
        self.manager.current = 'main'

class MainScreen(Screen):
    current_user = None
    def on_enter(self):
        self.ids.welcome.text = f"{self.current_user['username']}"
        self.refresh()
    def refresh(self):
        self.ids.friends_box.clear_widgets()
        for fid in data["friends"].get(self.current_user["id"], []):
            u = next((x for x in data["users"] if x["id"]==fid), None)
            if not u: continue
            btn = Button(text=f"{u['username']} - {u['mobile']}", size_hint_y=None, height=50)
            btn.bind(on_press=lambda x, f=fid: self.open_chat(f))
            self.ids.friends_box.add_widget(btn)
    def search(self, text):
        self.ids.search_box.clear_widgets()
        q = text.lower().strip()
        if len(q)<2: return
        for u in data["users"]:
            if u["id"]==self.current_user["id"]: continue
            if q in u["username"].lower() or q in u["mobile"]:
                box = BoxLayout(size_hint_y=None, height=50)
                box.add_widget(Label(text=f"{u['username']} - {u['mobile']}", font_size=12))
                b = Button(text="Follow Request", size_hint_x=0.4, background_color=(0,0.66,0.51,1))
                b.bind(on_press=lambda x, uid=u["id"]: self.send_req(uid))
                box.add_widget(b)
                self.ids.search_box.add_widget(box)
    def send_req(self, to_id):
        if to_id not in data["requests"]:
            data["requests"][to_id]=[]
        data["requests"][to_id].append(self.current_user["id"])
        save_data(data)
    def open_chat(self, fid):
        self.manager.get_screen('chat').friend_id = fid
        self.manager.get_screen('chat').current_user = self.current_user
        self.manager.current = 'chat'

class ChatScreen(Screen):
    friend_id = None
    current_user = None
    def on_enter(self):
        u = next((x for x in data["users"] if x["id"]==self.friend_id), None)
        self.ids.header.text = f"{u['username']} - Private Chat"
    def send(self):
        txt = self.ids.msg_input.text.strip()
        if not txt: return
        cid = "_".join(sorted([self.current_user["id"], self.friend_id]))
        if cid not in data["chats"]:
            data["chats"][cid]=[]
        data["chats"][cid].append({"from":self.current_user["id"], "to":self.friend_id, "text":txt})
        save_data(data)
        self.ids.msg_input.text=""

class PanchayatApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(SplashScreen(name='splash'))
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(SignupScreen(name='signup'))
        sm.add_widget(SetPassScreen(name='setpass'))
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(ChatScreen(name='chat'))
        return sm

PanchayatApp().run()
