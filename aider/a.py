import aider.db_parser as db
import asyncio

import discord
import aiounittest

class Test(aiounittest.AsyncTestCase):
    def check_blacklisting(self):
        check = asyncio.run(db.add_user_to_blacklist(134024815936929792, 123, "test"))
        return check
    def check_blacklisted(self):
        check = asyncio.run(db.is_blacklisted(134024815936929792, 123))
        return check

    def check_unique_user_parser(self):
        user = discord.User
        user.id = 123
        user.name = "Alex"
        check = asyncio.run(db.parse_users_from_guild({user : "Tonto"}, 123, 123))
        return check

test = Test()

#print(test.check_blacklisted())

#print(test.check_blacklisting())

print(test.check_unique_user_parser())
