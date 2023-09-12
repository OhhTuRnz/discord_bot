import asyncio
import discord
import aiounittest
from unittest.mock import Mock
from aider.db_parser import add_user_to_blacklist, is_blacklisted, delete_user_from_blacklist, parse_users_from_guild, \
    delete_users_from_guild


class Test(aiounittest.AsyncTestCase):
    relative_route = "../"
    async def create_fake_users(self):
        users = []  # Create an empty list to store user objects
        names = ["Alex", "Gabriel", "Murlock"]
        ids = [123, 456, 789]
        roles = ["Tonto", "Tonto", "Tonto"]

        for i in range(len(names)):
            # Create a fake User object using Mock
            user = Mock(spec=discord.User)
            user.id = ids[i]
            user.name = names[i]
            users.append(user)  # Add the user to the list
        return users

    async def test_blacklist_and_unblacklist(self):
        await add_user_to_blacklist(134024815936929792, 123, "test", self.relative_route)
        print("Checking if user is blacklisted ...", end=" ")
        self.assertTrue(await self.check_blacklisted())
        print("Correct")

        await delete_user_from_blacklist(134024815936929792, 123, self.relative_route)
        print("Checking if user is unblacklisted ...", end=" ")
        self.assertFalse(await self.check_blacklisted())
        print("Correct")

    async def test_parse_users_from_guild(self):
        print("Checking one user parse ...", end=" ")
        await self.check_unique_user_parser()
        print("Correct")
        print("Deleting the user ...", end=" ")
        await self.check_unique_delete_user()
        print("Correct")
        print("Checking multiple user parse ...", end=" ")
        await self.check_multiple_user_parser()
        print("Correct")
        print("Deleting the users ...", end=" ")
        await self.check_multiple_delete_user()
        print("Correct")

    async def check_blacklisted(self):
        return await is_blacklisted(134024815936929792, 123, self.relative_route)

    async def check_unique_user_parser(self):
        user = Mock(spec=discord.User)
        user.id = 123
        user.name = "Alex"
        await parse_users_from_guild([user], 123, 123, self.relative_route)

    async def check_unique_delete_user(self):
        user = Mock(spec=discord.User)
        user.id = 123
        user.name = "Alex"
        await delete_users_from_guild([user], 123, self.relative_route)

    async def check_multiple_user_parser(self):
        user_role_mapping = await self.create_fake_users()
        await parse_users_from_guild(user_role_mapping, 123, 123, self.relative_route)

    async def check_multiple_delete_user(self):
        user_role_mapping = await self.create_fake_users()
        await delete_users_from_guild(user_role_mapping, 123, self.relative_route)

    async def create_fake_users(self):
        users = []  # Create an empty list to store user objects
        names = ["Alex", "Gabriel", "Murlock"]
        ids = [123, 456, 789]
        roles = ["Tonto", "Tonto", "Tonto"]

        for i in range(len(names)):
            # Create a fake User object using Mock
            user = Mock(spec=discord.User)
            user.id = ids[i]
            user.name = names[i]
            users.append(user)  # Add the user to the list

        user_role_mapping = {users[i]: roles[i] for i in range(len(users))}
        return user_role_mapping


if __name__ == '__main__':
    aiounittest.main()