import aiosqlite
import asyncio

from datetime import date
from exceptions import UserBlacklisted

#async def show_tables() -> None:                                               # // DEBUGGING
#    async with aiosqlite.connect("../discord.db") as db:
#        async with db.execute("SELECT name FROM sqlite_schema") as cursor:
#            result = await cursor.fetchall()
#            print(result)

async def user_exists(user_id: int, server_id: int, relative_route = "./") -> bool:
    """
        Check if a user exists in the database.
        :param user_id: The ID of the user that should be checked
        :return: True if the user exists, else False
    """
    async with aiosqlite.connect(relative_route + "aider/database.db") as db:
        async with db.execute("SELECT 1 FROM user_server WHERE user_id=? AND server_id = ?", (user_id, server_id)) as cursor:
            result = await cursor.fetchone()
            return result is not None

async def server_exists(server_id : int, relative_route = "./") -> bool:
    """
    Check if a server exists in the database.
    :param server_id:
    :return: boolean that represents if the server exists
    """
    async with aiosqlite.connect(relative_route + "aider/database.db") as db:
        async with db.execute("SELECT 1 FROM Server WHERE ID=?", (server_id,)) as cursor:
            result = await cursor.fetchone()
            await cursor.close()
            return result is not None


async def get_blacklisted_users(server_id : int, relative_route = "./") -> list: # To be checked and updated
    """
        This function return all user ids that are blacklisted in the server given by parameter.
        :param server_id: The ID of the server that should be checked.
        :return: list of all blacklisted user id's
    """
    async def get_server_users() -> list:
        async with aiosqlite.connect(relative_route + "aider´/database.db") as db:
            async with db.execute("SELECT user_id FROM user_server WHERE server_id=?", (server_id,)) as cursor:
                results = await cursor.fetchall()
                await cursor.close()
                return results

    async with aiosqlite.connect(relative_route + "aider/database.db") as db:
        result = []
        users = get_server_users()
        for user_id in users:
            async with db.execute("SELECT user_id FROM Blacklist WHERE user_id=?", (user_id,)) as cursor:
                result.append(await cursor.fetchone())
        await cursor.close()
        return result

async def is_blacklisted(user_id: int, server_id: int, relative_route = "./") -> bool:
    """
        This function will check if a user is blacklisted.
        :param user_id: The ID of the user that should be checked.
        :return: True if the user is blacklisted, False if not.
    """
    async with aiosqlite.connect(relative_route + "aider/database.db") as db:
        async with db.execute("SELECT 1 FROM Blacklist WHERE user_id = ? AND server_id = ?", (user_id,server_id)) as cursor:
            result = await cursor.fetchone()
            await cursor.close()
            return result is not None


async def add_user_to_blacklist(user_id: int, server_id: int, reason: str, relative_route = "./") -> int: # To be checked and updated
    """
        This function will add a user based on its ID in the blacklist.
        :param user_id: The ID of the user that should be added into the blacklist.
    """
    today = date.today().strftime("%d/%m/%Y")
    if(await is_blacklisted(user_id, server_id, relative_route)):
        raise UserBlacklisted
    else:
        async with aiosqlite.connect(relative_route + "aider/database.db") as db:
            if(reason):
                await db.execute("INSERT INTO Blacklist VALUES (?, ?, ?, ?)", (server_id, user_id, today, reason))
            else:
                await db.execute("INSERT INTO Blacklist VALUES (?, ?, ?, NULL)", (server_id, user_id, today))
            await db.commit()
            rows = await db.execute("SELECT COUNT(*) FROM Blacklist")
            async with rows as cursor:
                result = await cursor.fetchone()
                await cursor.close()
                return result[0] if result is not None else 0

async def delete_user_from_blacklist(user_id: int, server_id: int, relative_route = "./") -> int: # To be checked and updated
    """
        This function will delete a user based on its ID from the blacklist.
        :param user_id: The ID of the user that should be deleted from the blacklist.
        :return: The number of blacklisted users.
    """
    async with aiosqlite.connect(relative_route + "aider/database.db") as db:
        await db.execute("DELETE FROM Blacklist WHERE user_id = ? AND server_id = ?", (user_id, server_id))
        await db.commit()
        rows = await db.execute("SELECT COUNT(*) FROM Blacklist")
        async with rows as cursor:
            result = await cursor.fetchone()
            await cursor.close()
            return result[0] if result is not None else 0

async def parse_users_from_guild(users: dict, server_id: int, owner_id: int, relative_route = "./") -> int:
    """
        This function will parse all users from a guild and add them to the database.
        :param users: list of users to be added
        :param server_id: integer representing the server id
        :return: epoch time of the last user addition
    """
    async with aiosqlite.connect(relative_route + "aider/database.db") as db:
        users = await purge_existing(users, server_id, db)
        if (users):
            if(await server_exists(server_id, relative_route)):
                await insert_users(users, server_id, db)
            else:
                await db.execute("INSERT INTO server(ID, owner_id) VALUES (?, ?)", (server_id, owner_id))
                await insert_users(users, server_id, db)
            await db.commit()
            rows = await db.execute("SELECT COUNT(*) FROM user_server WHERE server_id = ?", (server_id,))
            async with rows as cursor:
                result = await cursor.fetchone()
                await cursor.close()
                return result[0] if result is not None else 0
        else:
            return 0

async def delete_users_from_guild(users: dict, server_id: int, relative_route = "./") -> int:
    """
    This function will delete all users from a guild and add them to the database
    :param users: dict of users to be added and their role to the database
    :param server_id: integer representing the server id
    :return:
    """
    async with aiosqlite.connect(relative_route + "aider/database.db") as db:
        users = await purge_nonexisting(users, server_id, db)
        if (users):
            if(await server_exists(server_id, relative_route)):
                await delete_users(users, server_id, db, relative_route)
                await db.commit()
                return 1
            else:
                return 0
        else:
            return 0

async def insert_users(users : dict, server_id : int, db):
    """
        This function will insert users into the database.
        :param users: users that are part of the guild
        :param server_id: id of the guild we are parsing
        :param db: Database connection
        :return:
    """
    for user in users:
        try:
            await db.execute("INSERT INTO User(ID, name) VALUES (?, ?)", (user.id, user.name))
        except Exception as e:
            None
#            print(e)
        await db.execute("INSERT INTO user_server(user_id, server_id) VALUES (?, ?)", (user.id, server_id))

async def delete_users(users : list, server_id : int, db, relative_route = "'/") -> int:
    """
        This function will delete users from the database.
        :param users: users that are part of the guild
        :param server_id: id of the guild we are parsing
        :param db: Database connection
        :return:
    """
    for user in users:
        if(await is_blacklisted(user.id, server_id, relative_route)):
            await delete_user_from_blacklist(user.id, server_id, relative_route)
        await db.execute("DELETE FROM User WHERE ID = ?", (user.id,))
        await db.execute("DELETE FROM user_server WHERE user_id = ? AND server_id = ?", (user.id, server_id))
    return 1
async def purge_existing(users : dict, server_id : int, db):
    """
    This function will purge all users that already exist in the database.
    :param users: users that are part of the guild
    :param server_id: server id
    :param db: Database connection
    :return: users that are not in the database
    """
    async with db.execute("SELECT user_id FROM user_server WHERE server_id=?", (server_id,)) as cursor:
        existing = await cursor.fetchall()
        await cursor.close()
        if existing:
            users = [user for user in users if user.id not in {user_id_tuple[0] for user_id_tuple in existing}]
    return users

async def purge_nonexisting(users : dict, server_id : int, db):
    async with db.execute("SELECT user_id FROM user_server WHERE server_id=?", (server_id,)) as cursor:
        existing = await cursor.fetchall()
        await cursor.close()
        if existing:
            users = [user for user in users if user.id in {user_id_tuple[0] for user_id_tuple in existing}]
        else:
            users = {}
    return users