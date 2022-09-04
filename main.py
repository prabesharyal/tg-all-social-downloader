import logging
import os
from telegram import __version__ as TG_VER
import yt_dlp
import re 
import requests
import instaloader
from instaloader import Post
import time

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import ForceReply, Update,InputMediaVideo,InputMediaPhoto
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

API_Hash = os.environ.get('BOT_TOKEN')
USER = os.environ.get('username')

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

def html_format(string):
    string= string.replace('&', '&amp')
    string= string.replace('"', '&quot')
    string= string.replace("'", "&#039")
    string= string.replace('<', '&lt')
    string= string.replace('>', '&gt')
    return string

# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Dear {user.mention_html()}, Bot is active and will download videos now onwards.",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("There's No help available here. Call 911.")


async def developer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """About the Bot Developer!"""
    await update.message.reply_text("Bot is developed by @PrabeshAryalNP on Telegram.")


async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Deletes the Tiktok/Yt URL."""
    await context.bot.delete_message(chat_id=update.message.chat.id, message_id=update.message.message_id)

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Downloader."""
    string = update.message.text
    pattern = '([^\s\.]+\.[^\s]{2,}|www\.[^\s]+\.[^\s]{2,})'
    entries = re.findall(pattern, string)
    for URLS in entries:
        try:
            if re.match(r"((?:http|https):\/\/)(?:www.)?(?:instagram.com|instagr.am|instagr.com)\/(\w+)\/([\w\-/?=&]+)",URLS):
                try:
                    #Instance
                    L = instaloader.Instaloader(download_video_thumbnails=False, save_metadata=False)
                    # (login using session file)
                    L.load_session_from_file(username = USER,filename = '{}.session'.format(USER))
                    a= URLS.split('/')
                    if str(a[3])=='stories':
                        userid=a[4]
                        CAPTION = '<a href="{}"> Some STORIES from : @{}</a>'.format('https://www.instagram.com/'+userid,userid)
                        print("Trying to dowload stories of {}".format(userid))
                        SHORTCODE = 'Stories'
                        foruid = requests.get('https://www.instagram.com/'+userid)
                        strres= foruid.text
                        a =strres.find('profilePage_')
                        maybeuid = strres[a+12:a+12+15]
                        id = [int(maybeuid.split("\"")[0])]
                        for story in L.get_stories(userids=id):
                            # story is a Story object
                            for item in story.get_items():
                                # item is a StoryItem object
                                L.download_storyitem(item, SHORTCODE)
                    else:
                        CAPTION = ''
                        SHORTCODE = a[4]
                        #Download Post
                        post = Post.from_shortcode(L.context, SHORTCODE)      
                        L.download_post(post, target=SHORTCODE)
                        print("Sending downloaded Instagram files. \n")
                except instaloader.exceptions.LoginRequiredException:
                    raise TypeError("Prolly Private Post - Instaloader. \n")
                except BaseException:
                    raise TypeError("Some Unknown Error in Instaloader. \n")
                download_dir = "./{}/".format(SHORTCODE)
                downloaded_files = os.listdir(download_dir)
                downloads = []
                for lists in downloaded_files:
                    files = os.path.join(download_dir,lists)
                    downloads.append(files)
                #print(downloads)
                media_group = []
                temp_list = list()
                postcount = 0
                for posts in downloads:
                    if posts.endswith(".txt"):
                        #Opening Text file
                        a= open(posts,'r',encoding="utf8")
                        sentence = a.read()
                        a.close()
                        sentence = str(html_format(sentence))
                        CAPTION = '<a href="{}">{}</a>'.format(URLS,sentence)
                        os.remove(posts)
                        downloads.remove(posts)
                if len(downloads)>1:
                    for posts in downloads:
                        if posts.endswith(".mp4"):
                        #print(posts)
                            media_group.append(InputMediaVideo(open(posts,'rb'),caption ="▶ " + CAPTION if len(media_group) == 0 else '',parse_mode='HTML'))
                            postcount += 1
                            temp_list.append(posts)
                            time.sleep(1)
                        elif posts.endswith(".jpg"):
                        #print(posts)
                            media_group.append(InputMediaPhoto(open(posts,'rb'), caption ="▶ " + CAPTION if len(media_group) == 0 else '',parse_mode='HTML'))
                            postcount += 1
                            temp_list.append(posts)
                            time.sleep(1)
                        if len(media_group)==10:
                            await context.bot.send_media_group(chat_id = update.message.chat.id, media = media_group)
                            media_group = []
                    await context.bot.send_media_group(chat_id = update.message.chat.id, media = media_group)
                    try:
                        await context.bot.delete_message(chat_id=update.message.chat.id, message_id=update.message.message_id)
                    except BaseException:
                            print("Message was already deleted.")
                    time.sleep(2)
                    for posts in downloads:
                        print("removing sent Files")
                        os.remove(posts)
                    os.rmdir(SHORTCODE)
                    postcount = 0
                    time.sleep(2)
                elif len(downloads)==1:
                    for post in downloads:
                        if post.endswith(".mp4"):
                            await context.bot.send_video(chat_id = update.message.chat.id, video=open(post, 'rb'), caption="▶ " + CAPTION, parse_mode='HTML')
                            time.sleep(3)
                            os.remove(post)
                            try:
                                await context.bot.delete_message(chat_id=update.message.chat.id, message_id=update.message.message_id)
                            except BaseException:
                                print("Message was already deleted.")
                            os.rmdir(SHORTCODE)	
                        elif post.endswith(".jpg"):
                            await context.bot.send_photo(chat_id = update.message.chat.id, photo=open(post, 'rb'), caption="▶ " + CAPTION, parse_mode='HTML')
                            time.sleep(1)
                            os.remove(post)
                            try:
                                await context.bot.delete_message(chat_id=update.message.chat.id, message_id=update.message.message_id)
                            except BaseException:
                                print("Message was already deleted.")
                            os.rmdir(SHORTCODE)	
                    else:
                        print('Instagram Task Done')
            else:
                raise TypeError("Maybe not Instagram Link, So following different method.")             
        except TypeError:
                if re.match(r"(https:\/\/)([vt]+)\.([tiktok]+)\.([com]{2,6})([\/\w@?=&\.-]*)", URLS):
                    r = requests.head(URLS, allow_redirects=False)
                    URLS = r.headers['Location']
                    with yt_dlp.YoutubeDL({'ignoreerrors': True}) as ydl:
                        error_code = ydl.download(URLS)
                else:
                    URLS=URLS
                    with yt_dlp.YoutubeDL({'max_filesize':50*1024*1024, 'format_sort': ['res:1080', 'ext:mp4:m4a']}) as ydl:
                        error_code = ydl.download(URLS)

                downloaded_files = os.listdir('./')
                for files in downloaded_files:
                    text = str(files.rsplit(' ', 1)[0])
                    CAPTION = str('<a href="{}">{}</a>'.format(URLS,text))
                    size =int((os.path.getsize(files))/(1024*1024))
                    if os.path.isdir(files):
                        continue
                    elif size < 50:
                        if files.endswith(('avi', 'flv', 'mkv', 'mov', 'mp4', 'webm', '3g2', '3gp', 'f4v', 'mk3d', 'divx', 'mpg', 'ogv', 'm4v', 'wmv')):
                            print("Found Short Video and Sending!!!")
                            await context.bot.send_video(chat_id=update.message.chat_id, video=open(files, 'rb'), supports_streaming=True,caption = CAPTION, parse_mode='HTML')
                            print("Video {} was Sent Successfully!".format(files))
                            os.remove(files)
                            try:
                                await context.bot.delete_message(chat_id=update.message.chat.id, message_id=update.message.message_id)
                            except BaseException:
                                print("Message was already deleted.")

                        elif files.endswith(('aiff', 'alac', 'flac', 'm4a', 'mka', 'mp3', 'ogg', 'opus', 'wav','aac', 'ape', 'asf', 'f4a', 'f4b', 'm4b', 'm4p', 'm4r', 'oga', 'ogx', 'spx', 'vorbis', 'wma')):
                            print("Found Short Audio")
                            await context.bot.send_audio(chat_id=update.message.chat_id, audio=open(files, 'rb'), caption = CAPTION, parse_mode='HTML')
                            print("Audio {} was Sent Successfully!".format(files))
                            os.remove(files)
                            try:
                                await context.bot.delete_message(chat_id=update.message.chat.id, message_id=update.message.message_id)
                            except BaseException:
                                print("Message was already deleted. \n \n")    

                        elif files.endswith(('py','json','Procfile','txt','text','pip', 'md','git','pycache','cache','session'))==False:
                            os.remove(files)
                    else:
                        print(files + "is "+str(size)+" MB."+"\n"+"Which is greater than 50 MB, So removing it !!")
                        os.remove(files)

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(API_Hash).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("developerinfoPA", developer))

    #For other links
    application.add_handler(MessageHandler(filters.Regex('([^\s\.]+\.[^\s]{2,}|www\.[^\s]+\.[^\s]{2,})') & ~filters.COMMAND, download))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == "__main__":
    main()
