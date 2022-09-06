
#import inbuilt modules
from ast import main
import os, shutil, time, re, logging, requests


#import downloaders
import yt_dlp
import instaloader

#import Methods
from instaloader import Post

#Import Telegram Features
from telegram import *
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

ig_session_USER = os.environ.get('ig_session')

API_HASH = os.environ.get('BOT_TOKEN')

ig_USER = ''
ig_PASS = ''
SHORTCODE = ''
def ig_num_id(link):
    userid=(link.split('/'))[4]
    resp = (requests.get('https://www.instagram.com/'+userid)).text
    ig_act = resp.find('profilePage_')
    ig_num_id = int((resp[ig_act+12:ig_act+12+15]).split("\"")[0])
    return ig_num_id

def convert_html(string):
    string= string.replace('&', '&amp')
    string= string.replace('"', '&quot')
    string= string.replace("'", "&#039")
    string= string.replace('<', '&lt')
    string= string.replace('>', '&gt')
    return string

def clean_clutter():
    print("Removing If any Previously unused files.")
    for files in os.listdir():    
        if files.endswith(('py','json','Procfile','txt','text','pip','git','pycache','cache','session','vendor','profile.d','heroku'))==False:
            if os.path.isdir(files) == True: #and (files =='Stories' or files == SHORTCODE):
                print("Removing Dir : {}".format(files))
                shutil.rmtree(files)
            #elif os.path.isdir(files) == True:
                #print("Skipping Dir : {}".format(files))
            else:
                os.remove(files)
                print("Removed File : {}".format(files))

def check_ig_login():
    global ig_USER
    if ig_USER != '' and ig_PASS != '':
        return True
    for files in os.listdir():
        if files.endswith('session') and files =="{}.session".format(ig_session_USER):
            return True
    return False

def instagram_dl_selector(url):
    if check_ig_login() == True:
        a = url.split('/')
        if str(a[3])=='stories':
            return 'instaloader_login_story'
        else:
            return 'instaloader_login_postsreels'
    elif check_ig_login() == False:
        return 'instaloader_nologin'


#instaloader Instance
def ins_instance_login():
    L = instaloader.Instaloader(download_video_thumbnails=False, save_metadata=False)
    if ig_USER != '' and ig_PASS != '':
        try:
            L.login(ig_USER, ig_PASS)
            print("Logged in using credentials of : "+ig_USER)
        except BaseException:
            print("Base Exception on Login By password")
            L.load_session_from_file(username = ig_session_USER,filename = '{}.session'.format(ig_session_USER))
    else:
        print("Loading session as normal file")
        L.load_session_from_file(username = ig_session_USER,filename = '{}.session'.format(ig_session_USER))
    return L


def igdl_story(link): #Story downloader
    username = (link.split('/'))[4]
    CAPTION = '<a href="{}"> Some STORIES from : @{}</a>'.format('https://www.instagram.com/'+username,username)
    SHORTCODE = 'Stories'
    L = ins_instance_login()
    id =[ig_num_id(link)]
    for story in L.get_stories(userids=id):
    # story is a Story object
        for item in story.get_items():
            # item is a StoryItem object
            L.download_storyitem(item, SHORTCODE)
    try:
        downloaded_files = os.listdir("./{}/".format(SHORTCODE))
    except FileNotFoundError:
        print("Stories were Never downloaded.")
        return FileNotFoundError
    downloads = []
    for lists in downloaded_files:
        files = os.path.join("./{}/".format(SHORTCODE),lists)
        downloads.append(files)
    return CAPTION, downloads, SHORTCODE

def igdl_posts_pri(link):
    URLS = link
    L = ins_instance_login()
    CAPTION = '<a href="{}">✨</a>'.format(link)
    SHORTCODE = (link.split('/'))[4]
    post = Post.from_shortcode(L.context, SHORTCODE)      
    L.download_post(post, target=SHORTCODE)

    downloaded_files = os.listdir("./{}/".format(SHORTCODE))
    downloads = []
    for lists in downloaded_files:
        files = os.path.join("./{}/".format(SHORTCODE),lists)
        downloads.append(files)

    for posts in downloads: #Caption Part
        if posts.endswith(".txt"):
            #Opening Text file
            a= open(posts,'r',encoding="utf8")
            sentence = a.read()
            a.close()
            sentence = str(convert_html(sentence))
            CAPTION = '<a href="{}">{}</a>'.format(URLS,sentence)
            os.remove(posts)
            downloads.remove(posts)
    
    return CAPTION, downloads,SHORTCODE

def simple_ig_dl(links):
    URLS = links
    L = instaloader.Instaloader(download_video_thumbnails=False, save_metadata=False)
    a= links.split('/')
    SHORTCODE = a[4]
    post = Post.from_shortcode(L.context, SHORTCODE)
    L.download_post(post, target=SHORTCODE)
    CAPTION = '<a href="{}">✨</a>'.format(links)

    downloaded_files = os.listdir("./{}/".format(SHORTCODE))
    downloads = []
    for lists in downloaded_files:
        files = os.path.join("./{}/".format(SHORTCODE),lists)
        downloads.append(files)

    for posts in downloads: #Caption Part
        if posts.endswith(".txt"):
            #Opening Text file
            a= open(posts,'r',encoding="utf8")
            sentence = a.read()
            a.close()
            sentence = str(convert_html(sentence))
            CAPTION = '<a href="{}">{}</a>'.format(URLS,sentence)
            os.remove(posts)
            downloads.remove(posts)
    return CAPTION, downloads, SHORTCODE

async def ig_tg_sender(update,context,CAPTION, downloads, SHORTCODE):
    if len(downloads)>1:
        media_group=[]
        media_group_counter = 0
        totalfiles= len(downloads)
        for posts in downloads:
            if totalfiles > 1: # If multiple files are remaining
                if posts.endswith(".mp4"): #appends mp4
                #print(posts)
                    media_group.append(InputMediaVideo(open(posts,'rb'),caption = CAPTION if len(media_group) == 0 else '',parse_mode='HTML'))
                    media_group_counter += 1
                elif posts.endswith(".jpg"): #appends jpg
                #print(posts)
                    media_group.append(InputMediaPhoto(open(posts,'rb'), caption = CAPTION if len(media_group) == 0 else '',parse_mode='HTML'))
                    media_group_counter +=1
                if len(media_group)==10: #sends 10 first files
                    await context.bot.send_media_group(chat_id = update.message.chat.id, media = media_group, write_timeout=60)
                    media_group = []
                    media_group_counter = 0
                    totalfiles= len(downloads) - 10
                    continue
            elif totalfiles == 1: #If only file is remaining
                if posts.endswith(".mp4"):
                    await context.bot.send_video(chat_id = update.message.chat.id, video=open(posts, 'rb'), caption=CAPTION, parse_mode='HTML')
                elif posts.endswith(".jpg"):
                    await context.bot.send_photo(chat_id = update.message.chat.id, photo=open(posts, 'rb'), caption=CAPTION, parse_mode='HTML')
        if media_group_counter>1:
            await context.bot.send_media_group(chat_id = update.message.chat.id, media = media_group, write_timeout=60)
            print("Sending Media Group")
        try: #message Deletion
            await context.bot.delete_message(chat_id=update.message.chat.id, message_id=update.message.message_id)
        except BaseException:
                print("Message was already deleted.")
        try:
            for remaints in downloads:
                os.remove(remaints)
            os.rmdir(SHORTCODE) if SHORTCODE != '' else print('In root directory, so no need of removing any folder.')
        except:
            print("Some error while removing instagram files")
        print("Clean Success!")
        time.sleep(2)
    elif len(downloads)==1:
        for post in downloads:
            if post.endswith(".mp4"):
                await context.bot.send_video(chat_id = update.message.chat.id, video=open(post, 'rb'), caption=CAPTION, parse_mode='HTML')
                time.sleep(3)
                os.remove(post)
                try:
                    await context.bot.delete_message(chat_id=update.message.chat.id, message_id=update.message.message_id)
                except BaseException:
                    print("Message was already deleted.")
                os.rmdir(SHORTCODE) if SHORTCODE != '' else print('In root directory, so no need of removing any folder.')	
            elif post.endswith(".jpg"):
                await context.bot.send_photo(chat_id = update.message.chat.id, photo=open(post, 'rb'), caption=CAPTION, parse_mode='HTML')
                time.sleep(1)
                os.remove(post)
                try:
                    await context.bot.delete_message(chat_id=update.message.chat.id, message_id=update.message.message_id)
                except BaseException:
                    print("Message was already deleted.")
                os.rmdir(SHORTCODE) if SHORTCODE != '' else print('In root directory, so no need of removing any folder.')	
        else:
            print('Instagram Task Done')

def yt_dlp_tiktok_dl(URLS):
    r = requests.head(URLS, allow_redirects=False)
    URLS = r.headers['Location']
    ydl_opts = {'ignoreerrors': True, 'trim_file_name' : 25}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(URLS)
        video_title = info['title']
    video_title = "✨" if video_title == '' else video_title
    video_title = convert_html(video_title)
    CAPTION = '<a href="{}">{}</a>'.format(URLS,video_title)
    return CAPTION

def yt_dlp_ig_failsafe_dl(URLS):
    ydl_opts = {'ignoreerrors': True, 'trim_file_name' : 25}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(URLS)
        video_title = info['description']
    video_title = "✨" if video_title == '' else video_title
    video_title = convert_html(video_title)
    CAPTION = '<a href="{}">{}</a>'.format(URLS,video_title)
    downloaded_files = os.listdir("./")
    downloads = []
    for files in downloaded_files:
        if files.endswith(('avi', 'flv', 'mkv', 'mov', 'mp4', 'webm', '3g2', '3gp', 'f4v', 'mk3d', 'divx', 'mpg', 'ogv', 'm4v', 'wmv')):
            downloads.append(files)
    SHORTCODE = ''
    return CAPTION, downloads, SHORTCODE

def yt_dlp_youtube_dl(URLS):
    ydl_opts = {'trim_file_name' : 20,'max_filesize':50*1024*1024, 'format_sort': ['res:1080','ext:mp4:m4a']}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(URLS)
        video_title = info['title']
    video_title = "✨" if video_title == '' else video_title
    video_title = convert_html(video_title)
    CAPTION = '<a href="{}">{}</a>'.format(URLS,video_title)
    return CAPTION

def yt_dlp_youtube_audio_dl(URLS):
    ydl_opts = {'format': 'm4a/bestaudio/best',
    # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
    'postprocessors': [{  # Extract audio using ffmpeg
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',}]}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(URLS)
        audio_title = info['title']
    audio_title = "✨" if audio_title == '' else audio_title
    CAPTION = '<a href="{}">{}</a>'.format(URLS,audio_title)
    return CAPTION

def yt_dlp_Others_dl(URLS):
    ydl_opts = {'trim_file_name' : 20, 'max_filesize':50*1024*1024}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(URLS)
        video_title = info['title']
    video_title = "✨" if video_title == '' else video_title
    video_title = convert_html(video_title)
    CAPTION = '<a href="{}">{}</a>'.format(URLS,video_title)
    return CAPTION

async def yt_dlp_sender(update,context,CAPTION):
    downloaded_files = os.listdir('./')
    for files in downloaded_files:
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

            elif files.endswith(('py','json','Procfile','txt','text','pip', 'md','git','pycache','cache','session','vendor','profile.d'))==False:
                os.remove(files)
        else:
            print(files + "is "+str(size)+" MB."+"\n"+"Which is greater than 50 MB, So removing it !!")
            os.remove(files)



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    print(update.message['text']+" - Bot is already running!")
    await update.message.reply_html(
        rf"Dear {user.mention_html()}, Bot is active, Send URLs of supported sites to get video.", reply_markup=ReplyKeyboardRemove(selective=True))

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    user = update.effective_user
    print(update.message['text']+" - Help Command Issued")
    await context.bot.delete_message(chat_id=update.message.chat.id, message_id=update.message.message_id)
    await context.bot.send_message(chat_id=update.message.chat.id, text='''<b><u> A lot of help commands available.</u></b>\n \n    <code>/start</code> - <i>Check whether bot is working or not.</i>\n    <code>/help</code> - <i>This menu is displayed.</i>\n    <code>/clean</code> - <i>Resets the bot server to the deployment time.</i>\n\n<b><u> Some Instagram module commands:</u></b>\n     <code>/iglogin</code> - <i>Displays instagram related commands.</i>\n    <code>/igusername</code> - <i>Sets instagram username.</i>\n    <code>/igpassword</code> - <i>Sets instagram password.</i>\n    <code>/iglogout</code> - <i>Log out of instagram account and cleans your data on server.</i>\n    <code>/igcheck</code> - <i>Shows if any username or password are on server.</i>\n    <code>/igstories username</code> - <i>Sends stories of the user mentioned using pre-installed credentials.</i> \n\n<i>Note : </i><u>Two Step Verification must be turned off! and this feature always don't work as Instagram limits on account access from new IP.</u>\n\n    \n \n    <b>Any Sort of Public Video Links </b> - <i>Sends you video upto 50MB using that link.</i>\n\n    <code>/ytaudio </code><u>your_youtube_link</u> - <i>Sends audio from link.</i> \n\n\n<b>Isn't this help enough ???</b>''',parse_mode='HTML')

#''''''

async def clean(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /clean is issued."""
    global ig_PASS, ig_USER, L
    clean_clutter()
    print("Server clean was success.")
    ig_USER = ''
    ig_PASS = ''
    L = None
    await context.bot.delete_message(chat_id=update.message.chat.id, message_id=update.message.message_id)
    await context.bot.send_message(chat_id=update.message.chat.id, text='Server is <b>virgin</b> again.',parse_mode='HTML')

async def iglogin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    '''await update.message.reply_html(
        rf"Dear {user.mention_html()}, Bot is active bro upto this moment, solve next step!.",
        reply_markup=ForceReply(selective=True),)'''
    await update.message.reply_html(
        rf"Dear {update.effective_user.mention_html()}, Enter your username and password in given formats!", reply_markup=ForceReply(selective=True))
    await context.bot.send_message(chat_id=update.message.chat.id, text='<code>/igusername </code><u>username</u> \n <code>/igpassword </code><u>password</u> \n \n <b>To Logout :</b>\n Simply send /iglogout command.\n\n <b>To Check :</b>\n Simply send /igcheck command.',parse_mode='HTML')    

async def igusername(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /igusername is issued."""
    global ig_USER
    ig_USER =((update.message['text']).split(" "))[1]
    igusername = ig_USER
    print("Received username  : "+ igusername)
    await context.bot.send_message(chat_id=update.message.chat.id, text='Your username for instagram is : <b>{}</b> \n \n If it is incorrect, send again using same format. \n \n Send <code>/igpassword </code> <b>yourpassword</b> to enter password \n \n<i>Note : </i><u>Two Step Verification must be turned off!</u>'.format(igusername),parse_mode='HTML')

async def igpassword(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /igpassword is issued."""
    global ig_PASS
    ig_PASS = (((update.message['text']).split(" "))[1])
    print("Password too received!")
    astpass = ''
    for char in ig_PASS:
        astpass += "*"
    await context.bot.delete_message(chat_id=update.message.chat.id, message_id=update.message.message_id)
    await context.bot.send_message(chat_id=update.message.chat.id, text='Your password : {}  was received. \n \n Send links of posts or stories to download using that password. Server will use it until you logout manually by issuing /iglogout command.\n\n<i>Note : </i><u>Two Step Verification must be turned off for actually making the Bot work!</u>'.format(astpass),parse_mode='HTML')

async def igstories(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    storyof = (((update.message['text']).split(" "))[1])
    print( "User Id is : "+ ig_USER)
    astpass =''
    for char in ig_PASS:
        astpass += "*"
    print( "User pass is : "+ astpass)
    #await context.bot.send_message(chat_id=update.message.chat.id, text='<b><u>The credentials in server are :</u></b> \n     <b>Username : </b><code>{}</code>\n     <b>Password: </b><code>{}</code> \n \n Server will use it until you logout manually by issuing /iglogout command. \n\n For now downloading stories from {}. \n\n<i>Note : </i><u>Two Step Verification must be turned off for actually making the Bot work!</u>'.format(ig_USER, astpass,storyof),parse_mode='HTML')
    URLS = 'https://www.instagram.com/stories/{}/'.format(storyof)
    try:
        CAPTION, downloads, SHORTCODE = igdl_story(URLS)
        await ig_tg_sender(update, context, CAPTION, downloads, SHORTCODE)
    except FileNotFoundError:
        print("Stories were not downloaded.")
        await context.bot.send_message(chat_id=update.message.chat.id, text="Sorry, Couldn't download stories of user {} . \n Some Error Occurred (╥_╥)".format(storyof),parse_mode='HTML')

async def yt_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    link = (((update.message['text']).split(" "))[1])
    print("Through Yt-audio downloader")
    try :
        CAPTION = yt_dlp_youtube_audio_dl(link)
        await yt_dlp_sender(update,context,CAPTION)
    except BaseException:
        print("Audio Download Error")
        await context.bot.send_message(chat_id=update.message.chat.id, text="Sorry, Couldn't download audio of from given link : <code>{}</code> . \n Check link again and make sure if it works.".format(link),parse_mode='HTML')


async def iglogout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    clean_clutter()
    global ig_USER, ig_PASS, L
    ig_USER = ''
    ig_PASS = ''
    L = None
    print("Server clean was success.")
    await context.bot.send_message(chat_id=update.message.chat.id, text='Removed credentials Successfully. \n \n Send /igcheck to look if your credentials are removed or not.',parse_mode='HTML')

async def igcheck(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print( "User Id is : "+ ig_USER)
    astpass =''
    for char in ig_PASS:
        astpass += "*"
    print( "User pass is : "+ astpass)
    await context.bot.send_message(chat_id=update.message.chat.id, text='<b><u>The data in server is :</u></b> \n     <b>Username : </b><code>{}</code>\n     <b>Password : </b><code>{}</code> \n \n Server will use it until you logout manually by issuing /iglogout command.\n\n<i>Note : </i><u>Two Step Verification must be turned off for actually making the Bot work!</u>'.format(ig_USER, astpass),parse_mode='HTML')

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    clean_clutter()
    string = update.message.text
    print(string)
    pattern = '([^\s\.]+\.[^\s]{2,}|www\.[^\s]+\.[^\s]{2,})'
    entries = re.findall(pattern, string)
    for URLS in entries:
        if re.match(r"(?:https:\/\/)?([vt]+|[www]+)\.?([tiktok]+)\.([com]+)\/([\/\w@?=&\.-]+)", URLS):
            CAPTION = yt_dlp_tiktok_dl(URLS)
            await yt_dlp_sender(update,context,CAPTION)
        
        elif re.match(r"((?:http|https):\/\/)(?:www.)?(?:instagram.com|instagr.am|instagr.com)\/(\w+)\/([\w\-/?=&]+)",URLS):
            try:
                downloadmode = instagram_dl_selector(URLS)
                if downloadmode == 'instaloader_login_story':
                    try:
                        CAPTION, downloads, SHORTCODE = igdl_story(URLS)
                        await ig_tg_sender(update, context, CAPTION, downloads, SHORTCODE)
                    except FileNotFoundError:
                        print("Stories were not downloaded.")
                if downloadmode == 'instaloader_login_postsreels':
                    try:
                        CAPTION, downloads, SHORTCODE = igdl_posts_pri(URLS)
                        await ig_tg_sender(update, context, CAPTION, downloads, SHORTCODE)
                    except BaseException:
                        await context.bot.send_message(chat_id=update.message.chat.id, text='Maybe Login is required for this post.\n\n Send /iglogin to login using your credentials and try again.',parse_mode='HTML')
                if downloadmode == 'instaloader_nologin':
                    print("Instaloader Session without Login is trying ....")
                    if re.match(r"((?:http|https):\/\/)(?:www.)?(?:instagram.com|instagr.am|instagr.com)\/(p|tv|reel)\/([\w\-/?=&]+)",URLS):
                        CAPTION, downloads, SHORTCODE = simple_ig_dl(URLS)
                        await ig_tg_sender(update, context, CAPTION, downloads, SHORTCODE)
                    else:
                        print("Unsupported Link Type or Story or Private/Deleted Post.")
            except BaseException:
                print("Instaloader Module Failed, retrying with yt-dlp")
                try:
                    CAPTION, downloads, SHORTCODE = yt_dlp_ig_failsafe_dl(URLS)
                    await ig_tg_sender(update, context, CAPTION, downloads, SHORTCODE)
                except BaseException:
                    print("yt-dlp module too failed downloading this video. \n Maybe not a video or private one.")
        
        elif re.match(r"(?:https?:\/\/)?(?:www\.|m\.)?youtu\.?be(?:\.com)?\/?.*(?:watch|embed)?(?:.*v=|v\/|\/)([\w\-_\&=]+)?", URLS):
            CAPTION = yt_dlp_youtube_dl(URLS)
            await yt_dlp_sender(update,context,CAPTION)
        
        else:
            try:
                CAPTION = yt_dlp_Others_dl(URLS)
                await yt_dlp_sender(update,context,CAPTION)
            except BaseException:
                print("Unsupported URL : {}".format(URLS))



def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(API_HASH).read_timeout(10).write_timeout(50).get_updates_read_timeout(42).connect_timeout(30).build()
    print("Application is running!")
    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("clean", clean))
    #Instagram Logins
    application.add_handler(CommandHandler("iglogin", iglogin))
    application.add_handler(CommandHandler("igusername", igusername))
    application.add_handler(CommandHandler("igpassword", igpassword))
    application.add_handler(CommandHandler("iglogout", iglogout))
    application.add_handler(CommandHandler("igcheck", igcheck))
    application.add_handler(CommandHandler("igstories", igstories))

    #youtube music
    application.add_handler(CommandHandler("ytaudio", yt_audio))

    #For other links
    application.add_handler(MessageHandler(filters.Regex('([^\s\.]+\.[^\s]{2,}|www\.[^\s]+\.[^\s]{2,})') & ~filters.COMMAND, download))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == "__main__":
    main()