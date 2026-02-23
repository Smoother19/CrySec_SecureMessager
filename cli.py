import sys

class cli_parser:
    def __init__(self, connection):
        self.connection = connection 
        
        self.commands = {
            '/help': {
                'action': self.cmd_help, 
                'desc': "Display all available commands and their descriptions."
            },
            '/t': {
                'action': self.cmd_send_text, 
                'desc': "Send a normal text message to the server (ex: /t Hello World)."
            },
            '/s': {
                'action': self.cmd_send_caesar, 
                'desc': "Send a Caesar cipher encrypted message (ex: /s Hello World)."
            },
            '/key': {
                'action': self.cmd_key, 
                'desc': "Set and send an encryption key (ex: /key 1234)."
            },
            '/quit': {
                'action': self.cmd_quit, 
                'desc': "Quit the application."
            }
        }

    def cmd_help(self, args):
        print("\n--- Available Commands ---")
        for cmd_name, info in self.commands.items():
            print(f"{cmd_name} : {info['desc']}")
        print("--------------------------\n")

    def cmd_send_text(self, args):
        if args:
            message = " ".join(args)
            self.connection.send_message(message, 't') 
        else:
            print("Error: The message is empty.")

    def cmd_send_caesar(self, args):
        if args:
            message = " ".join(args)
            self.connection.send_message(message, 's') 
        else:
            print("Error: The message is empty.")

    def cmd_key(self, args):
        if args:
            key_value = args[0]
            print(f"Sending key: {key_value}")
            self.connection.send_message(key_value, 'k') 
        else:
            print("Error: Please specify a key (ex: /key 1234).")

    def cmd_quit(self, args):
        print("Disconnecting...")
        self.connection.client.close()
        sys.exit(0) 

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
                print(f"Unknown command: {cmd}. Type /help to see the list.")
                
        else:
            full_message = cmd + " " + " ".join(args) if args else cmd
            self.connection.send_message(full_message, 't')