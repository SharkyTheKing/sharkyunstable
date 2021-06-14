import re

import discord
from redbot.core import checks, commands

BASECOG = getattr(commands, "Cog", object)


class MorseShark(BASECOG):
    """
    In progress
    """

    def __init__(self, bot):
        self.bot = bot
        # self.regex_string = re.compile(r"(i)[a-z0-9\b]")
        self.regex_string = re.compile(r"(?i)[a-z0-9]\s?")
        self.morse_code = {
            ".-": "a",
            "-...": "b",
            "-.-.": "c",
            "-..": "d",
            ".": "e",
            "..-.": "f",
            "--.": "g",
            "....": "h",
            "..": "i",
            ".---": "j",
            "-.-": "k",
            ".-..": "l",
            "--": "m",
            "-.": "n",
            "---": "o",
            ".--.": "p",
            "--.-": "q",
            ".-.": "r",
            "...": "s",
            "-": "t",
            "..-": "u",
            "...-": "v",
            ".--": "w",
            "-..-": "x",
            "-.--": "y",
            "--..": "z",
            ".----": "1",
            "..---": "2",
            "...--": "3",
            "....-": "4",
            ".....": "5",
            "-....": "6",
            "--...": "7",
            "---..": "8",
            "----.": "9",
            "-----": "0",
        }

    @staticmethod
    def split(message):
        return [char for char in message]

    def decode_morse(self, message: str):
        word_list = []
        string = message.strip("!@#$%^&*()_+<>?,").split()
        for s in string:
            if s in self.morse_code:
                word_list.append(self.morse_code[s])
            if s == "/":
                word_list.append(" ")
        word_string = "".join(word_list)
        return word_string

    def encode_morse(self, message: str):
        alpha_code = {}
        alpha_code = {v: k for k, v in self.morse_code.items()}
        word_list = ""
        string = self.split(message.lower().strip("!@#$%^&*()_+<>?/,"))
        for s in string:
            if s in alpha_code:
                word_list += "{} ".format(alpha_code[s])
            if s == " ":
                word_list += "/ "
        return word_list

    def letter_check_test(self, message):
        confirm = self.regex_string.match(message)
        if not confirm:
            return False
        return True

    def letter_check(self, message):
        confirm = False
        new_string = self.split(message)
        for s in new_string:
            if s in self.character_check:  # cause I don't feel like using regex
                confirm = True
        return confirm

    @commands.group()
    async def morse(self, ctx):
        """
        Decode or Encode messages into/from Morse Code.
        """
        ...

    @morse.command()
    async def decode(self, ctx, *, message: str):
        """
        Decode Morse Code into a Message.

        Having `/` will dictate a space in the message.
        """
        decoded = self.decode_morse(message)
        if not decoded:
            return await ctx.send("Something happened. Please try again.")
        await ctx.send(decoded)

    @morse.command()
    async def encode(self, ctx, *, message: str):
        """
        Encode a Message into Morse Code.

        The encoded message will return `/` for when there's a space.
        """
        confirm_letters = self.letter_check_test(message)
        if not confirm_letters:
            return await ctx.send("You must provide letters.")

        encoded = self.encode_morse(message)
        if not encoded:
            return await ctx.send("Something happened. Please try again.")
        await ctx.send(encoded)
