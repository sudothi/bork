import customtkinter as ctk
import threading
import time
import requests
import base64
import os
import urllib3
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class LCU_Handler:
    def __init__(self):
        self.port = None
        self.auth_key = None
        self.lockfile_path = r"C:\Riot Games\League of Legends\lockfile"
        self.champion_map = {}

    def get_auth(self):
        if not os.path.exists(self.lockfile_path):
            return False, "Lockfile não encontrado. O cliente do LoL está aberto?"
        
        with open(self.lockfile_path, 'r') as f:
            content = f.read().split(':')
            self.port = content[2]
            password = content[3]
            self.auth_key = base64.b64encode(f"riot:{password}".encode()).decode()
        return True, "Autenticação bem-sucedida!"

    def make_request(self, method, endpoint, payload=None):
        url = f"https://127.0.0.1:{self.port}{endpoint}"
        headers = {"Authorization": f"Basic {self.auth_key}", "Content-Type": "application/json"}
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, verify=False)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=payload if payload is not None else {}, verify=False)
            elif method.upper() == 'PATCH':
                response = requests.patch(url, headers=headers, json=payload, verify=False)
            return response
        except requests.exceptions.RequestException:
            return None

    def initialize_champion_data(self):
        endpoint = '/lol-champ-select/v1/all-champions'
        response = self.make_request('GET', endpoint)

        if response is None or response.status_code != 200:
            endpoint = '/lol-champions/v1/owned-champions-minimal'
            response = self.make_request('GET', endpoint)

        if response and response.status_code == 200:
            try:
                champions = response.json()
                if isinstance(champions, dict) and 'champions' in champions:
                    champion_list = champions['champions']
                else:
                    champion_list = champions

                self.champion_map = {
                    champ['name'].lower().replace(" ", "").replace("'", "").replace(".", ""): champ['id']
                    for champ in champion_list
                }
                return True
            except (json.JSONDecodeError, KeyError):
                return False
        return False

    def get_champion_id(self, name):
        clean_name_input = name.lower().replace(" ", "").replace("'", "").replace(".", "")
        if not clean_name_input:
            return None
            
        if clean_name_input in self.champion_map:
            return self.champion_map[clean_name_input]
            
        for champ_name, champ_id in self.champion_map.items():
            if clean_name_input in champ_name:
                return champ_id
        
        return None

    def get_gameflow_phase(self):
        response = self.make_request('GET', '/lol-gameflow/v1/gameflow-phase')
        return response.json() if response and response.ok else None

    def accept_queue(self):
        return self.make_request('POST', '/lol-matchmaking/v1/ready-check/accept')

    def get_champ_select_session(self):
        response = self.make_request('GET', '/lol-champ-select/v1/session')
        return response.json() if response and response.ok else None

    def perform_champ_select_action(self, action_id, champion_id):
        endpoint = f'/lol-champ-select/v1/session/actions/{action_id}'
        payload = {"championId": champion_id, "completed": True}
        return self.make_request('PATCH', endpoint, payload)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("bork")
        self.geometry("420x320")
        self.resizable(False, False)

        self.lcu = LCU_Handler()
        self.is_loop_running = False
        self.worker_thread = None

        self.TEXT_COLOR = "#0077be"
        self.BORDER_COLOR = "black"

        self.auto_accept_enabled = ctk.BooleanVar(value=False)
        self.auto_ban_enabled = ctk.BooleanVar(value=False)
        self.auto_pick_enabled = ctk.BooleanVar(value=False)

        self.title_label = ctk.CTkLabel(self, text="bork by @islazed", font=ctk.CTkFont(size=20, weight="bold"), text_color=self.TEXT_COLOR)
        self.title_label.pack(pady=10)
        
        self.accept_frame = ctk.CTkFrame(self, border_width=2, border_color=self.BORDER_COLOR)
        self.accept_frame.pack(pady=5, padx=10, fill="x")
        self.accept_label = ctk.CTkLabel(self.accept_frame, text="queue autoaccept", font=ctk.CTkFont(size=14), text_color=self.TEXT_COLOR)
        self.accept_label.pack(side="left", padx=15, pady=10)
        self.accept_switch = ctk.CTkSwitch(self.accept_frame, text="", variable=self.auto_accept_enabled, command=self.on_toggle)
        self.accept_switch.pack(side="right", padx=15, pady=10)

        self.ban_frame = ctk.CTkFrame(self, border_width=2, border_color=self.BORDER_COLOR)
        self.ban_frame.pack(pady=5, padx=10, fill="x")
        self.ban_frame.grid_columnconfigure(1, weight=1)

        self.ban_label = ctk.CTkLabel(self.ban_frame, text="champion ban:", font=ctk.CTkFont(size=14), text_color=self.TEXT_COLOR)
        self.ban_label.grid(row=0, column=0, padx=(15, 5), pady=10)
        
        self.ban_entry = ctk.CTkEntry(self.ban_frame, placeholder_text="Ex: Yasuo", border_width=2, border_color=self.BORDER_COLOR)
        self.ban_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        self.ban_switch = ctk.CTkSwitch(self.ban_frame, text="", variable=self.auto_ban_enabled, command=self.on_toggle)
        self.ban_switch.grid(row=0, column=2, padx=15, pady=10)

        self.pick_frame = ctk.CTkFrame(self, border_width=2, border_color=self.BORDER_COLOR)
        self.pick_frame.pack(pady=5, padx=10, fill="x")
        self.pick_frame.grid_columnconfigure(1, weight=1)

        self.pick_label = ctk.CTkLabel(self.pick_frame, text="champion pick:", font=ctk.CTkFont(size=14), text_color=self.TEXT_COLOR)
        self.pick_label.grid(row=0, column=0, padx=(15, 5), pady=10)

        self.pick_entry = ctk.CTkEntry(self.pick_frame, placeholder_text="Ex: Lux", border_width=2, border_color=self.BORDER_COLOR)
        self.pick_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        self.pick_switch = ctk.CTkSwitch(self.pick_frame, text="", variable=self.auto_pick_enabled, command=self.on_toggle)
        self.pick_switch.grid(row=0, column=2, padx=15, pady=10)
        
        self.status_label = ctk.CTkLabel(self, text="Desligado. Ligue uma função para começar.", text_color="gray50")
        self.status_label.pack(pady=20, padx=10)

    def on_toggle(self):
        any_switch_on = self.auto_accept_enabled.get() or self.auto_ban_enabled.get() or self.auto_pick_enabled.get()

        if any_switch_on and not self.is_loop_running:
            self.is_loop_running = True
            self.worker_thread = threading.Thread(target=self.main_loop, daemon=True)
            self.worker_thread.start()
        elif not any_switch_on and self.is_loop_running:
            self.is_loop_running = False
            self.status_label.configure(text="Todas as funções desligadas.", text_color="gray50")

    def main_loop(self):
        self.status_label.configure(text="Conectando ao cliente do LoL...", text_color="#E87500") 
        
        success, message = self.lcu.get_auth()
        if not success:
            self.status_label.configure(text=message, text_color="red"); self.stop_all_features(); return
        
        self.status_label.configure(text="Buscando dados de campeões...", text_color="#E87500")
        if not self.lcu.initialize_champion_data():
            self.status_label.configure(text="Falha ao buscar campeões.", text_color="red"); self.stop_all_features(); return
            
        self.status_label.configure(text="Monitorando...", text_color="green")
        
        action_performed_in_session = {'ban': False, 'pick': False}

        while self.is_loop_running:
            phase = self.lcu.get_gameflow_phase()
            
            if phase is None:
                self.status_label.configure(text="Cliente do LoL fechado.", text_color="red"); self.stop_all_features(); break
            
            if phase in ["Lobby", "Matchmaking", "None"]:
                if action_performed_in_session['pick']:
                    self.status_label.configure(text="Monitorando...", text_color="green")
                    action_performed_in_session = {'ban': False, 'pick': False}

            if self.auto_accept_enabled.get() and phase == "ReadyCheck":
                self.status_label.configure(text="Partida encontrada! Aceitando...", text_color=self.TEXT_COLOR)
                self.lcu.accept_queue()
                time.sleep(1)

            if phase == "ChampSelect":
                session = self.lcu.get_champ_select_session()
                if not session: continue
                
                timer_phase = session.get('timer', {}).get('phase')
                if timer_phase == 'BAN_PICK':
                    my_action = next((action for action_group in session.get('actions', []) for action in action_group if action.get('actorCellId') == session.get('localPlayerCellId') and action.get('isInProgress')), None)
                    
                    if my_action:
                        action_type = my_action.get('type')
                        
                        if self.auto_ban_enabled.get() and action_type == 'ban' and not action_performed_in_session['ban']:
                            ban_name = self.ban_entry.get()
                            if ban_name:
                                champion_id = self.lcu.get_champion_id(ban_name)
                                if champion_id:
                                    self.status_label.configure(text=f"Banindo {ban_name.title()}...", text_color=self.TEXT_COLOR)
                                    self.lcu.perform_champ_select_action(my_action['id'], champion_id)
                                    action_performed_in_session['ban'] = True

                        elif self.auto_pick_enabled.get() and action_type == 'pick' and not action_performed_in_session['pick']:
                            pick_name = self.pick_entry.get()
                            if pick_name:
                                champion_id = self.lcu.get_champion_id(pick_name)
                                if champion_id:
                                    self.status_label.configure(text=f"Selecionando {pick_name.title()}...", text_color=self.TEXT_COLOR)
                                    self.lcu.perform_champ_select_action(my_action['id'], champion_id)
                                    action_performed_in_session['pick'] = True
            
            time.sleep(1)
            
    def stop_all_features(self):
        self.is_loop_running = False
        self.accept_switch.deselect()
        self.ban_switch.deselect()
        self.pick_switch.deselect()

if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    app = App()

    app.mainloop()
