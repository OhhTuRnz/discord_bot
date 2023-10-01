import asyncio

import discord
from discord.ext import commands

import asyncpraw as praw
import configparser
import urllib.request

from prawcore.exceptions import Redirect
from prawcore.exceptions import ResponseException
from urllib.error import HTTPError

class RedditClient():
    def __init__(self, _id, _secret):
        self.id = _id,
        self.secret = _secret,
        self.user_agent = "discord-collector"
        self.urls = []

    def save_list(self,img_url_list):
        for img_url in img_url_list:
            self.urls.append(img_url)

    def delete_img_list(self):
        f = open('img_links.txt', 'r+')
        f.truncate()

    def is_img_link(self, img_link):
        ext = img_link[-4:]
        if ext == '.jpg' or ext == '.png':
            return True
        else:
            return False

    async def get_img_urls(self, sub, li):
        try:
            reddit = praw.Reddit(client_id=self.id, client_secret=self.secret, user_agent=self.user_agent)
            subreddit = await reddit.subreddit(sub)
            async for submission in subreddit.hot(limit=li):
                self.urls.append(submission.url)
            return self.urls

        except Redirect:
            print("Invalid Subreddit!")
            return 0

        except HTTPError:
            print("Too many Requests. Try again later!")
            return 0

        except ResponseException:
            print("Client info is wrong. Check again.")
            return 0

    def download_img(self, img_url, img_title, filename):
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        try:
            print('Downloading ' + img_title + '....')
            urllib.request.urlretrieve(img_url, filename)
            return 1

        except HTTPError:
            print("Too many Requests. Try again later!")
            return 0

    def read_img_links(self):
        with open('img_links.txt') as f:
            links = f.readlines()

        links = [x.strip() for x in links]
        download_count = 0

        for link in links:
            if not self.is_img_link(link):
                continue

            file_name = link.split('/')[-1]
            file_loc = 'result/{}'.format(file_name)

            if not file_name:
                continue

            download_status = self.download_img(link, file_name, file_loc)
            download_count += 1

            if download_status == 0:
                return download_count, 0

        return download_count, 1
class Reddit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.redditClient = RedditClient(_secret=bot.reddit['secret'], _id=bot.reddit['id'])
        print(bot.reddit)
    @commands.hybrid_command(name="get_reddit_memes", description="Get memes from a subreddit")
    async def get_reddit_images(self, context: commands.Context, subreddit = "r/DankMemes", limit = 3):
        img_url_list = await self.redditClient.get_img_urls(subreddit, limit)
        if img_url_list == 0:
            await context.send("There was an error with the subreddit")
            return
        await context.send("Here you go\n {}".format(img_url_list[0]))



client = RedditClient(_id="n1SUZsxjiYpvxd3TovaFgA", _secret="uB8FyHX2aUd951uElQXNSToSYjF0FQ")
asyncio.run(client.get_img_urls("r/DankMemes", 3))
async def setup(bot):
    await bot.add_cog(Reddit(bot))