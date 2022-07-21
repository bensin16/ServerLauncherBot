import discord
from random import choice
from subprocess import Popen, PIPE
from time import sleep
from pywinauto import Desktop

import Secrets


class TerrariaServerManager:
    def __init__(self):
        self.__dlg = None
        self.is_running = False

    def start_server_subprocess(self):

        if self.is_running:
            return

        Popen(
            Secrets.SERVER_BAT_LOCATION,
            shell=False,
            bufsize=0,
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
        )

        sleep(3)

        # dont ask me why it opens a nameless dialog window
        self.__dlg = Desktop(backend="uia")["dialog0"]

        sleep(3)
        self.__dlg.type_keys("n~")  # no to using steam

        self.is_running = True

    def stop_server_subprocess(self):
        self.__dlg.type_keys("exit~")
        sleep(5)
        self.__dlg = None
        self.is_running = False


class ServerClient(discord.Client):
    def __init__(self):
        self.__server_manager = TerrariaServerManager()
        super().__init__()

    async def on_ready(self):
        print("Logged in as {0.user}".format(self))

    async def on_message(self, message):
        if message.author == self.user:
            return

        tokens = self.tokenize_message(message)
        print("Tokens: {0}".format(tokens))  # debug

        # i think this also covers the len(tokens) != 0 since it returns None if it would be empty
        if tokens:
            new_message_content = self.handle_command(tokens)

        if new_message_content:
            await message.channel.send(new_message_content)

    def tokenize_message(self, message):
        tokens = []

        content_str = message.content

        if content_str[0] != "!":
            return

        # trim ! before splitting
        tokens = content_str[1:].split()

        return tokens

    def handle_command(self, tokens):
        current_token = tokens.pop(0)

        if current_token == "server":
            current_token = tokens.pop(0)
            if current_token == "start":
                if self.__server_manager.is_running:
                    return "Server already running"
                else:
                    self.__server_manager.start_server_subprocess()
                    return "Starting Server"

            elif current_token == "stop":
                if self.__server_manager.is_running:
                    self.__server_manager.stop_server_subprocess()
                    return "Stopping Server"
                else:
                    return "Server not running"

        elif current_token == "help":
            return """ 
Available commands: 
!gaiss
!server [start/stop]
"""


client = ServerClient()
client.run(Secrets.APP_API_KEY)  # hiding key in another untracked python file
