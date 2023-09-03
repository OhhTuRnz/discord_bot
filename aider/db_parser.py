import aiosqlite
import asyncio

from datetime import date


#async def show_tables() -> None:                                               # // DEBUGGING
#    async with aiosqlite.connect("../discord.db") as db:
#        async with db.execute("SELECT name FROM sqlite_schema") as cursor:
#            result = await cursor.fetchall()
#            print(result)

async def user_exists(user_id: int, server_id: int) -> bool:
    """
        Check if a user exists in the database.
        :param user_id: The ID of the user that should be checked
        :return: True if the user exists, else False
    """
    async with aiosqlite.connect("../aider/database.db") as db:
        async with db.execute("SELECT 1 FROM user_server WHERE user_id=? AND server_id = ?", (user_id, server_id)) as cursor:
            result = await cursor.fetchone()
            return result is not None

async def server_exists(server_id : int) -> bool:
    async with aiosqlite.connect("../aider/database.db") as db:
        async with db.execute("SELECT 1 FROM Server WHERE ID=?", (server_id,)) as cursor:
            result = await cursor.fetchone()
            return result is not None


async def get_blacklisted_users(server_id : int) -> list: # To be checked and updated
    """
        This function return all user ids that are blacklisted in the server given by parameter.
        :param server_id: The ID of the server that should be checked.
        :return: list of all blacklisted user id's
    """
    async def get_server_users() -> list:
        async with aiosqlite.connect("../aider´/database.db") as db:
            async with db.execute("SELECT user_id FROM user_server WHERE server_id=?", (server_id,)) as cursor:
                results = await cursor.fetchall()
                return results

    async with aiosqlite.connect("../aider/database.db") as db:
        result = []
        users = get_server_users()
        for user_id in users:
            async with db.execute("SELECT user_id FROM Blacklist WHERE user_id=?", (user_id,)) as cursor:
                result.append(await cursor.fetchone())
        return result

async def is_blacklisted(user_id: int, server_id: int) -> bool:
    """
        This function will check if a user is blacklisted.
        :param user_id: The ID of the user that should be checked.
        :return: True if the user is blacklisted, False if not.
    """
    async with aiosqlite.connect("../aider/database.db") as db:
        async with db.execute("SELECT 1 FROM Blacklist WHERE user_id = ? AND server_id = ?", (user_id,server_id)) as cursor:
            result = await cursor.fetchone()
            return result is not None


async def add_user_to_blacklist(user_id: int, server_id: int, reason: str) -> int: # To be checked and updated
    """
        This function will add a user based on its ID in the blacklist.
        :param user_id: The ID of the user that should be added into the blacklist.
    """
    today = date.today().strftime("%d/%m/%Y")
    async with aiosqlite.connect("../aider/database.db") as db:
        if(reason):
            await db.execute("INSERT INTO Blacklist VALUES (NULL, ?, ?, ?, ?)", (server_id, user_id, today, reason))
        else:
            await db.execute("INSERT INTO Blacklist VALUES (NULL, ?, ?, ?, NULL)", (server_id, user_id, today))
        await db.commit()
        rows = await db.execute("SELECT COUNT(*) FROM Blacklist")
        async with rows as cursor:
            result = await cursor.fetchone()
            return result[0] if result is not None else 0

async def parse_users_from_guild(users: dict, server_id: int, owner_id: int) -> int:
    """
        :param users: dict of users to be added and their role to the database
        :param server_id: integer representing the server id
        :return: epoch time of the last user addition
    """
    async with aiosqlite.connect("../aider/database.db") as db:
        users = await purge_existing(users, server_id, db)
        if (users):
            if(server_exists(server_id)):
                await insert_users(users, server_id, db)
            else:
                await db.execute("INSERT INTO server(ID, owner_id) VALUES (?, ?)", (server_id, owner_id))
                await insert_users(users, server_id, db)
            await db.commit()
            rows = await db.execute("SELECT COUNT(*) FROM user_server WHERE server_id = ?", (server_id,))
            async with rows as cursor:
                result = await cursor.fetchone()
                return result[0] if result is not None else 0
        else:
            return 0

async def insert_users(users : dict, server_id : int, db):
    for user, role in users.items():
            await db.execute("INSERT INTO User(ID, name) VALUES (?, ?)", (user.id, user.name))
            await db.execute("INSERT INTO user_server(user_id, server_id, role) VALUES (?, ?, ?)", (user.id, server_id, role))

async def purge_existing(users : dict, server_id : int, db):
    async with db.execute("SELECT user_id FROM user_server WHERE server_id=?", (server_id,)) as cursor:
        existing = await cursor.fetchall()
        users = {key: value for key, value in users.items() if key.id not in existing[0]}
    return users
