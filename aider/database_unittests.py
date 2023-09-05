import aider.db_parser as db
import asyncio

import discord
import aiounittest

class Test(aiounittest.AsyncTestCase):

    def check_blacklisting(self):
        asyncio.run(db.add_user_to_blacklist(134024815936929792, 123, "test"))
        return self.check_blacklisted()
    
    def check_blacklisted(self):
        check = asyncio.run(db.is_blacklisted(134024815936929792, 123))
        return check

    def check_unique_user_parser(self):
        user = discord.User
        user.id = 123
        user.name = "Alex"
        check = asyncio.run(db.parse_users_from_guild({user : "Tonto"}, 123, 123))
        return check

    def check_multiple_user_parser(self):
        users = []  # Create an empty list to store user objects
        names = ["Alex", "Gabriel", "Murlock"]
        ids = [123, 456, 789]
        roles = ["Tonto", "Tonto", "Tonto"]

        for i in range(len(names)):
            user = discord.User()  # Create a new User object
            user.id = ids[i]
            user.name = names[i]
            users.append(user)  # Add the user to the list

        user_role_mapping = {users[i]: roles[i] for i in range(len(users))}

        check = asyncio.run(db.parse_users_from_guild(user_role_mapping, 123, 123))
        return check
    
    def check_unblacklisting(self):
        asyncio.run(db.delete_user_from_blacklist(134024815936929792, 123))
        return self.check_blacklisted()

    def check_blacklist_and_unblacklist(self):
        print("Blacklisting user ... ", end=' ')
        assert(self.check_blacklisting() == True)
        print("Correct")
        print("Unblacklisting user ... ", end=' ')
        print("Correct")
        assert(self.check_unblacklisting() == False)
        return

    def check_parse_users_from_guild(self):
        print("Checking unique user parser ... ", end=' ')
        assert(self.check_unique_user_parser())
        print("Correct")

test = Test()

test.check_blacklist_and_unblacklist()
