import sys, os, math
from MessageHandler import MessageHandler

class cli_parser:
    def __init__(self, connection):
        self.connection = connection
        self.message_handler = connection.message_handler
        self.plain_buffer = ""
        self.encoded_buffer = ""
        self.waiting_for_task = False
        self.auto_task_key = None
        self.auto_task_algo = None

        # Link the CLI to the ConnectionHandler for automated task handling
        self.connection.set_callback(self.handle_server_message)
        
        self.commands = {
            '/help': {
                'action': self._cmd_help, 
                'desc': "Affiche toutes les commandes disponibles."
            },
            '/set': {
                'action': self._cmd_set,
                'desc': "<plain|encoded> <text> : Enregistre le texte dans le buffer spécifié."
            },
            '/show': {
                'action': self._cmd_show,
                'desc': "Affiche le contenu des buffers 'plain' et 'encoded'."
            },
            '/clearbuf': {
                'action': self._cmd_clearbuf,
                'desc': "[plain|encoded] : Vide un buffer spécifique ou tous les buffers."
            },
            '/encode': {
                'action': self._cmd_encode,
                'desc': "<algo> <clé> : Encode 'plain' vers 'encoded'. Algos: shift, vigenere."
            },
            '/decode': {
                'action': self._cmd_decode,
                'desc': "<algo> <clé> : Décode 'encoded' vers 'plain'. Algos: shift, vigenere."
            },
            '/send': {
                'action': self._cmd_send,
                'desc': "<text>|plain|encoded [-s] : Envoie un message (type 't' par défaut, 's' avec flag)."
            },
            '/quit': {
                'action': self._cmd_quit, 
                'desc': "Quitte l'application."
            },
            # '/rsa': {
            #     'action': self._cmd_rsa,
            #     'desc': "<key_size> : Génère une paire de clés RSA avec la taille spécifiée."
            # }
        }

    def handle_server_message(self, message):
        # Astuce pour nettoyer la console et éviter les ">>"
        efface = "\r" + " " * 70 + "\r"
        
        # --- 1. CAS OÙ ON ATTEND LE MOT À CHIFFRER ---
        if getattr(self, 'waiting_for_task', False):
            self.plain_buffer = message
            self.waiting_for_task = False
            print(f"{efface}[+] Le mot a été récupéré dans le buffer 'Plain' : {message}")
            print(f"[+] CMD pour envoyer le message : /encode {self.auto_task_algo} {self.auto_task_key}")
            print("> ", end="", flush=True)
            return

        # --- 2. CAS OÙ ON DÉTECTE UNE INSTRUCTION DE TÂCHE ---
        msg_lower = message.lower()
        if "encode the text" in msg_lower:
            mots = message.split() # On découpe la phrase
            
            if "shift-key" in msg_lower:
                self.auto_task_algo = "shift"
                self.auto_task_key = mots[-1] # Le dernier mot est la clé
                self.waiting_for_task = True
                print(f"{efface}[!] Tâche Shift détectée (Clé: {self.auto_task_key})")
                print("> ", end="", flush=True)
                return
                
            elif "vigenere key" in msg_lower:
                self.auto_task_algo = "vigenere"
                self.auto_task_key = mots[-1] # Le dernier mot est la clé
                self.waiting_for_task = True
                print(f"{efface}[!] Tâche Vigenère détectée (Clé: {self.auto_task_key})")
                print("> ", end="", flush=True)
                return

        # --- 3. CAS NORMAL (Message classique du serveur) ---
        print(f"{efface}[Serveur] : {message}")
        # print("> ", end="", flush=True)

    def _cmd_help(self, args):
        print("\n--- Commandes disponibles ---")
        for cmd_name, info in self.commands.items():
            print(f"{cmd_name} {info.get('params', '')} : {info['desc']}")
        print("---------------------------\n")

    def _cmd_set(self, args):
        if len(args) < 2:
            print("Usage: /set <plain|encoded> <text>")
            return
        
        buffer_type = args[0].lower()
        text_to_set = " ".join(args[1:])

        if buffer_type == 'plain':
            self.plain_buffer = text_to_set
            print(f"Buffer 'plain' mis à jour.")
        elif buffer_type == 'encoded':
            self.encoded_buffer = text_to_set
            print(f"Buffer 'encoded' mis à jour.")
        else:
            print(f"Erreur: Buffer inconnu '{buffer_type}'. Utilisez 'plain' ou 'encoded'.")

    def _cmd_show(self, args):
        print("\n--- Contenu des Buffers ---")
        print(f"Plain   : {self.plain_buffer}")
        print(f"Encoded : {self.encoded_buffer}")
        print("---------------------------\n")

    def _cmd_clearbuf(self, args):
        if not args:
            self.plain_buffer = ""
            self.encoded_buffer = ""
            print("Buffers 'plain' et 'encoded' vidés.")
        elif args[0].lower() == 'plain':
            self.plain_buffer = ""
            print("Buffer 'plain' vidé.")
        elif args[0].lower() == 'encoded':
            self.encoded_buffer = ""
            print("Buffer 'encoded' vidé.")
        else:
            print("Usage: /clearbuf [plain|encoded]")

    def _cmd_encode(self, args):
        """
        Encode le contenu de plain_buffer vers encoded_buffer en utilisant l'algorithme spécifié.
        """
        if len(args) < 2:
            print("Usage: /encode <algorithme> <clé>")
            print("Algorithmes supportés: shift, vigenere")
            return

        if not self.plain_buffer:
            print("Erreur: Le buffer 'plain' est vide. Utilisez /set plain <texte> pour le définir.")
            return

        algo = args[0].lower()
        key = " ".join(args[1:])

        try:
            if algo == 'shift':
                shift_key = int(key)
                self.encoded_buffer = self.message_handler.encode_shift(self.plain_buffer, shift_key)
                print(f"Buffer 'plain' encodé dans 'encoded' avec l'algorithme a décalage (shift) et la clé '{shift_key}'.")

            elif algo == 'vigenere':
                self.encoded_buffer = self.message_handler.encode_vigenere(self.plain_buffer, key)
                print(f"Buffer 'plain' encodé dans 'encoded' avec l'algorithme de Vigenère et la clé '{key}'.")

            else:
                print(f"Erreur: Algorithme d'encodage '{algo}' non reconnu.")
                return
                
            self._cmd_show(None)

        except ValueError:
            print(f"Erreur: La clé pour l'algorithme 'shift' doit être un entier (ex: 24).")
        except AttributeError as e:
            if 'encode_vigenere' in str(e):
                print(f"Erreur: La méthode 'encode_vigenere' n'est pas encore implémentée dans MessageHandler.py.")
            else:
                print(f"Une erreur est survenue: {e}")
        except Exception as e:
            print(f"Une erreur est survenue lors de l'encodage: {e}")

    def _cmd_decode(self, args):
        """
        Décode le contenu de encoded_buffer vers plain_buffer en utilisant l'algorithme spécifié.
        """
        if len(args) < 2:
            print("Usage: /decode <algorithme> <clé>")
            print("Algorithmes supportés: shift, vigenere")
            return

        if not self.encoded_buffer:
            print("Erreur: Le buffer 'encoded' est vide. Encodez un message ou utilisez /set encoded <texte>.")
            return

        algo = args[0].lower()
        key = " ".join(args[1:])

        try:
            if algo == 'shift':
                shift_key = int(key)
                self.plain_buffer = self.message_handler.decode_shift(self.encoded_buffer, shift_key)
                print(f"Buffer 'encoded' décodé dans 'plain' avec l'algorithme a décalage (shift) et la clé '{shift_key}'.")

            elif algo == 'vigenere':
                self.plain_buffer = self.message_handler.decode_vigenere(self.encoded_buffer, key)
                print(f"Buffer 'encoded' décodé dans 'plain' avec l'algorithme de Vigenère et la clé '{key}'.")

            else:
                print(f"Erreur: Algorithme de décodage '{algo}' non reconnu.")
                return
                
            self._cmd_show(None)

        except ValueError:
            print(f"Erreur: La clé pour l'algorithme 'shift' doit être un entier (ex: 24).")
        except AttributeError as e:
            if 'decode_vigenere' in str(e):
                 print(f"Erreur: La méthode 'decode_vigenere' n'est pas encore implémentée dans MessageHandler.py.")
            else:
                print(f"Une erreur est survenue: {e}")
        except Exception as e:
            print(f"Une erreur est survenue lors du décodage: {e}")

    def _cmd_send(self, args):
        if not args:
            print("Usage: /send <text>|plain|encoded [-s]")
            return

        msg_type = 't'
        if '-s' in args:
            msg_type = 's'
            args.remove('-s')

        if not args:
            print("Erreur: Le message ne peut pas être vide.")
            print("Usage: /send <text>|plain|encoded [-s]")
            return

        message_to_send = ""
        source = args[0].lower()

        if source == 'plain':
            if not self.plain_buffer:
                print("Erreur: Le buffer 'plain' est vide.")
                return
            message_to_send = self.plain_buffer
        elif source == 'encoded':
            if not self.encoded_buffer:
                print("Erreur: Le buffer 'encoded' est vide.")
                return
            message_to_send = self.encoded_buffer
        else:
            message_to_send = " ".join(args)

        try:
            self.connection.send_message(message_to_send, msg_type)
            print(f"Message envoyé (type: {msg_type}): '{message_to_send}'")
        except Exception as e:
            print(f"Erreur lors de l'envoi du message: {e}")       

    def _cmd_quit(self, args):
        print("Déconnexion...")
        self.connection.client.close()
        os._exit(0) 

    def parse_args(self, user_input):
        if not user_input.strip():
            return None, None

        args = user_input.split(' ')
        cmd = args[0]
        
        if user_input.startswith('/'):
            return (cmd, args[1:])
            
        return (cmd, args)
    
    def execute_command(self, cmd, args):
        if cmd is None:
            return

        if cmd.startswith('/'):
            if cmd in self.commands:
                action_to_call = self.commands[cmd]['action']
                action_to_call(args)
            else:
                print(f"Commande inconnue: {cmd}. Tapez /help pour voir la liste.")
                
        else:
            full_message = cmd + " " + " ".join(args) if args else cmd
            self.connection.send_message(full_message, 't')
