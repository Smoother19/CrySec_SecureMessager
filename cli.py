import sys, os
from MessageHandler import MessageHandler

class cli_parser:
    def __init__(self, connection):
        self.connection = connection 
        self.message_handler = MessageHandler()
        self.plain_buffer = ""
        self.encoded_buffer = ""
        
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
                'desc': "shift <k> : Encode le buffer 'plain' avec un décalage de <k> vers le buffer 'encoded'."
            },
            '/decode': {
                'action': self._cmd_decode,
                'desc': "shift <k> : Décode le buffer 'encoded' avec un décalage de <k> vers le buffer 'plain'."
            },
            '/send': {
                'action': self._cmd_send,
                'desc': "<text>|plain|encoded [-s] : Envoie un message (type 't' par défaut, 's' avec flag)."
            },
            '/quit': {
                'action': self._cmd_quit, 
                'desc': "Quitte l'application."
            }
        }

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
        if len(args) != 2 or args[0].lower() != 'shift':
            print("Usage: /encode shift <k>")
            return
        
        try:
            shift = int(args[1])
            self.encoded_buffer = self.message_handler.encode_shift(self.plain_buffer, shift)
            print(f"Buffer 'plain' encodé avec un décalage de {shift} vers le buffer 'encoded'.")
            self._cmd_show(None)
        except ValueError:
            print(f"Erreur: Le décalage '{args[1]}' doit être un entier.")
        except Exception as e:
            print(f"Une erreur d'encodage est survenue: {e}")

    def _cmd_decode(self, args):
        if len(args) != 2 or args[0].lower() != 'shift':
            print("Usage: /decode shift <k>")
            return
            
        try:
            shift = int(args[1])
            self.plain_buffer = self.message_handler.decode_shift(self.encoded_buffer, shift)
            print(f"Buffer 'encoded' décode avec un décalage de {shift} vers le buffer 'plain'.")
            self._cmd_show(None)
        except ValueError:
            print(f"Erreur: Le décalage '{args[1]}' doit être un entier.")
        except Exception as e:
            print(f"Une erreur de décodage est survenue: {e}")

    def _cmd_send(self, args):
        if not args:
            print("Usage: /send <text>|plain|encoded [-s]")
            return

        # Règle 1: Gestion du flag -s
        msg_type = 't'
        if '-s' in args:
            msg_type = 's'
            args.remove('-s')

        # S'il ne reste plus d'arguments après avoir retiré -s, c'est une erreur.
        if not args:
            print("Erreur: Le message ne peut pas être vide.")
            print("Usage: /send <text>|plain|encoded [-s]")
            return

        message_to_send = ""
        source = args[0].lower()

        # Règle 2: Gestion de la source du message
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
            # Si ce n'est ni 'plain' ni 'encoded', c'est un message texte
            message_to_send = " ".join(args)

        # Règle 3: Envoi au serveur
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
            # Par défaut, envoyer un message texte si ce n'est pas une commande
            full_message = cmd + " " + " ".join(args) if args else cmd
            self.connection.send_message(full_message, 't')
