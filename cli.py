import sys, os, math, re
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

        self.rsa_pub = None
        self.rsa_priv = None
        
        self.dh_p = None
        self.dh_a = None
        
        self.rsa_pub = None
        self.rsa_priv = None

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
                'desc': "<algo> <clé> : Encode 'plain' vers 'encoded'. Algos: shift, vigenere, rsa [n e]."
            },
            '/decode': {
                'action': self._cmd_decode,
                'desc': "<algo> <clé> : Décode 'encoded' vers 'plain'. Algos: shift, vigenere, rsa [n d]."
            },
            '/send': {
                'action': self._cmd_send,
                'desc': "<text>|plain|encoded [-s] : Envoie un message (type 't' par défaut, 's' avec flag)."
            },
            '/quit': {
                'action': self._cmd_quit, 
                'desc': "Quitte l'application."
            },
            '/rsa': {
                'action': self._cmd_rsa,
                'desc': "<key_size> : Génère une paire de clés RSA avec la taille spécifiée."
            },
            '/dh_gen': {
                'action': self._cmd_dh_gen,
                'desc': "Génère les paramètres Diffie-Hellman (p, g, a, A)."
            },
            '/dh_sec': {
                'action': self._cmd_dh_sec,
                'desc': "<B> : Calcule le secret partagé avec la clé publique (B) du serveur."
            },
            '/hash': {
                'action': self._cmd_hash,
                'desc': "[texte] : Hache le texte (ou le buffer 'plain') avec SHA-256 vers 'encoded'."
            }
        }

    def handle_server_message(self, message):
        efface = "\r" + " " * 70 + "\r"
        
        if getattr(self, 'waiting_for_task', False):
            self.plain_buffer = message
            self.waiting_for_task = False
            print(f"{efface}[+] Le mot a été récupéré dans le buffer 'Plain' : '{message}'")
            
            if self.auto_task_algo == "rsa":
                print(f"[+] CMD pour envoyer le message : /encode rsa")
            elif self.auto_task_algo == "hash":
                print(f"[+] CMD pour envoyer le message : /hash")
            else:
                print(f"[+] CMD pour envoyer le message : /encode {self.auto_task_algo} {self.auto_task_key}")
                
            print("> ", end="", flush=True)
            return

        msg_lower = message.lower()
        
        if "encode the text" in msg_lower or "hash" in msg_lower:
            mots = message.split()
            
            if "shift-key" in msg_lower:
                self.auto_task_algo = "shift"
                self.auto_task_key = mots[-1]
                self.waiting_for_task = True
                print(f"{efface}[!] Tâche Shift détectée (Clé: {self.auto_task_key})")
                print("> ", end="", flush=True)
                return
                
            elif "vigenere key" in msg_lower:
                self.auto_task_algo = "vigenere"
                self.auto_task_key = mots[-1]
                self.waiting_for_task = True
                print(f"{efface}[!] Tâche Vigenère détectée (Clé: {self.auto_task_key})")
                print("> ", end="", flush=True)
                return

            elif "hash" in msg_lower and not any(mot in msg_lower for mot in ["correspond", "correct", "invalid", "unknown", "running"]):
                self.auto_task_algo = "hash"
                self.waiting_for_task = True
                print(f"{efface}[!] Tâche Hash SHA-256 détectée")
                print("> ", end="", flush=True)
                return
                
            else:
                import re
                match_n = re.search(r'n\s*[=:]?\s*(\d+)', message, re.IGNORECASE)
                match_e = re.search(r'e\s*[=:]?\s*(\d+)', message, re.IGNORECASE)
                
                if match_n and match_e:
                    self.auto_task_algo = "rsa"
                    n = int(match_n.group(1))
                    e = int(match_e.group(1))
                    
                    self.rsa_pub = (n, e)
                    self.auto_task_key = f"n={n}, e={e}"
                    self.waiting_for_task = True
                    
                    print(f"{efface}[!] Tâche RSA détectée (Clé publique stockée: {self.auto_task_key})")
                    print("> ", end="", flush=True)
                    return

        print(f"{efface}[Serveur] : {message}")

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
        
        if isinstance(self.encoded_buffer, bytes):
            print(f"Encoded : {self.encoded_buffer}")
        else:
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

    def _cmd_rsa(self, args):
        if not args:
            print("Usage: /rsa <key_size_en_bits>")
            return
        
        try:
            key_size = int(args[0])
            n, e, d = self.message_handler.rsa_keygen(key_size)
            self.rsa_pub = (n, e)
            self.rsa_priv = (n, d)
            
            print(f"\n--- Clés RSA générées ({key_size} bits) ---")
            print(f"Clé Publique (n, e) : {n}, {e}")
            print(f"Clé Privée (n, d)   : {n}, {d}")
            print("---------------------------------------")
            
        except ValueError as e:
            print(f"Erreur lors de la génération RSA : {e}")

    def _cmd_encode(self, args):
        if len(args) < 1:
            print("Usage: /encode <algorithme> [clé]")
            print("Algorithmes supportés: shift, vigenere, rsa")
            return

        if not self.plain_buffer:
            print("Erreur: Le buffer 'plain' est vide. Utilisez /set plain <texte> pour le définir.")
            return

        algo = args[0].lower()

        try:
            if algo == 'shift':
                if len(args) < 2: return print("Erreur: Clé manquante. Usage: /encode shift <clé>")
                shift_key = int(args[1])
                self.encoded_buffer = self.message_handler.encode_shift(self.plain_buffer, shift_key)
                print(f"Buffer 'plain' encodé dans 'encoded' avec l'algorithme a décalage (shift) et la clé '{shift_key}'.")

            elif algo == 'vigenere':
                if len(args) < 2: return print("Erreur: Clé manquante. Usage: /encode vigenere <clé>")
                key = " ".join(args[1:])
                self.encoded_buffer = self.message_handler.encode_vigenere(self.plain_buffer, key)
                print(f"Buffer 'plain' encodé dans 'encoded' avec l'algorithme de Vigenère et la clé '{key}'.")

            elif algo == 'rsa':
                n, e = None, None
                if len(args) >= 3:
                    n, e = int(args[1]), int(args[2])
                elif self.rsa_pub: 
                    n, e = self.rsa_pub
                else:
                    print("Erreur: Aucune clé RSA disponible. Précisez <n> <e> ou attendez une tâche du serveur.")
                    return

                self.encoded_buffer = self.message_handler.rsa_encrypt(self.plain_buffer, n, e)
                print(f"Buffer 'plain' encodé avec RSA (clé publique: n={n}, e={e}).")

            else:
                print(f"Erreur: Algorithme d'encodage '{algo}' non reconnu.")
                return
                
            self._cmd_show(None)

        except ValueError:
            print(f"Erreur de typage (La clé doit généralement être un nombre entier selon l'algorithme).")
        except Exception as e:
            print(f"Une erreur est survenue lors de l'encodage: {e}")

    def _cmd_decode(self, args):
        if len(args) < 1:
            print("Usage: /decode <algorithme> [clé]")
            print("Algorithmes supportés: shift, vigenere, rsa")
            return

        if not self.encoded_buffer:
            print("Erreur: Le buffer 'encoded' est vide. Encodez un message ou utilisez /set encoded <texte>.")
            return

        algo = args[0].lower()

        try:
            if algo == 'shift':
                if len(args) < 2: return print("Erreur: Clé manquante.")
                shift_key = int(args[1])
                self.plain_buffer = self.message_handler.decode_shift(self.encoded_buffer, shift_key)
                print(f"Buffer 'encoded' décodé dans 'plain' avec l'algorithme a décalage (shift).")

            elif algo == 'vigenere':
                if len(args) < 2: return print("Erreur: Clé manquante.")
                key = " ".join(args[1:])
                self.plain_buffer = self.message_handler.decode_vigenere(self.encoded_buffer, key)
                print(f"Buffer 'encoded' décodé dans 'plain' avec Vigenère.")

            elif algo == 'rsa':
                n, d = None, None
                if len(args) >= 3:
                    n, d = int(args[1]), int(args[2])
                elif self.rsa_priv:
                    n, d = self.rsa_priv
                else:
                    print("Erreur: Aucune clé RSA privée disponible. Précisez <n> <d> ou générez avec /rsa.")
                    return

                buffer_bytes = self.encoded_buffer
                if isinstance(buffer_bytes, str):
                    try:
                        buffer_bytes = bytes.fromhex(buffer_bytes)
                    except ValueError:
                        print("Erreur: Pour décoder RSA depuis une chaîne, le buffer 'encoded' doit être en hexadécimal.")
                        return

                self.plain_buffer = self.message_handler.rsa_decrypt(buffer_bytes, n, d)
                print(f"Buffer 'encoded' décodé avec RSA (clé privée: n={n}, d={d}).")

            else:
                print(f"Erreur: Algorithme de décodage '{algo}' non reconnu.")
                return
                
            self._cmd_show(None)

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
            print(f"Message envoyé (type: {msg_type}).")
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

    def _cmd_dh_gen(self, args):
        try:
            p, g, a, A = self.message_handler.diffie_hellman_keygen()
            self.dh_p = p
            self.dh_a = a
            
            print(f"\n--- Paramètres Diffie-Hellman générés ---")
            print(f"Modulus (p)     : {p}")
            print(f"Générateur (g)  : {g}")
            print(f"Clé privée (a)  : {a}")
            print(f"Clé publique (A): {A}")
            print("-----------------------------------------")
            print(f"[!] ÉTAPE 1 : Envoyez p et g au serveur avec la commande :")
            print(f"> /send -s {p},{g}")
            print(f"[!] ÉTAPE 2 : Plus tard, envoyez votre clé publique avec :")
            print(f"> /send -s {A}")
        except Exception as e:
            print(f"Erreur lors de la génération : {e}")

    def _cmd_dh_sec(self, args):
        if not args:
            print("Usage: /dh_sec <clé_publique_du_serveur_B>")
            return
            
        if not self.dh_p or not self.dh_a:
            print("Erreur: Vous devez d'abord générer les paramètres avec /dh_gen.")
            return

        try:
            B = int(args[0])
            secret = self.message_handler.diffie_hellman_shared_key(B, self.dh_a, self.dh_p)
            
            print(f"\n--- Secret Diffie-Hellman ---")
            print(f"Secret partagé calculé : {secret}")
            print("-----------------------------")
            print(f"[!] ÉTAPE 3 : Envoyez ce secret au serveur avec la commande :")
            print(f"> /send -s {secret}")
            
        except ValueError:
            print("Erreur: La clé publique du serveur doit être un nombre entier.")
        except Exception as e:
            print(f"Erreur lors du calcul du secret : {e}")

    def _cmd_hash(self, args):
        if args:
            text_to_hash = " ".join(args)
        elif getattr(self, 'waiting_for_task', False) or self.plain_buffer:
            text_to_hash = self.plain_buffer
            self.waiting_for_task = False
        else:
            print("Erreur: Spécifiez un texte (/hash <texte>) ou remplissez le buffer 'plain'.")
            return

        try:
            hashed_result = self.message_handler.sha256_hash(text_to_hash)
            
            self.encoded_buffer = hashed_result
            
            print(f"\n--- Hachage SHA-256 ---")
            print(f"Texte original : {text_to_hash}")
            print(f"Hash (Hex)     : {hashed_result}")
            print("-----------------------")
            print(f"[+] Le hash a été sauvegardé dans le buffer 'Encoded'.")
            print(f"> Tapez '/send -s encoded' pour l'envoyer au serveur.")
            
        except Exception as e:
            print(f"Erreur lors du hachage : {e}")