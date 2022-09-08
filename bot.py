
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

API_HASH = os.environ.get('BOT_TOKEN')
ig_session_USER = ''
ig_session_file = ''

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
    for files in os.listdir():
        if files.endswith('session') and files ==ig_session_file:
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
    try:
        print("Loading session as normal file")
        L.load_session_from_file(username = ig_session_USER,filename = ig_session_file)
    except BaseException:
        print("Login Using Sessionfile Failed.")
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
    if re.match(r"(?:https:\/\/)?([vt]+)\.([tiktok]+)\.([com]+)\/([\/\w@?=&\.-]+)", URLS):
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
    try:
        await context.bot.delete_message(chat_id=update.message.chat.id, message_id=update.message.message_id)
    except BaseException:
        print("Yt-DLP Sender, Message was already deleted.")


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
    await context.bot.send_message(chat_id=update.message.chat.id, text='''<b><u> A lot of help commands available.</u></b>\n \n    <code>/start</code> - <i>Check whether bot is working or not.</i>\n    <code>/help</code> - <i>This menu is displayed.</i>\n    <code>/clean</code> - <i>Resets the bot server to the deployment time (doesn't delete session files).</i>\n\n<b><u> Some Instagram module commands:</u></b>\n     <code>/iglogin</code> - <i>Guides you throughly Instagram Login process.</i>\n    <code>/iglogout</code> - <i>Log out of instagram account (doesn't delete session files).</i>\n    <code>/igcheck</code> - <i>Shows which account is being used.</i>\n    <code>/igstories username</code> - <i>Sends stories of the user mentioned using your session file.</i>\n /igsession - <i>Sends session generator code written in Python.</i>\n     <code>/rmigsession username</code> - <i>Deletes your session file from server.</i>\n \n    <b>Any Sort of Public Video Links </b> - <i>Sends you video upto 50MB using that link.</i>\n\n    <code>/ytaudio </code><u>your_youtube_link</u> - <i>Sends audio from link.</i> \n\n\n<b>Isn't this help enough ???</b>''',parse_mode='HTML')

#''''''

async def clean(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /clean is issued."""
    clean_clutter()
    print("Server clean was success.")
    ig_session_USER = ''
    L = None
    await context.bot.delete_message(chat_id=update.message.chat.id, message_id=update.message.message_id)
    await context.bot.send_message(chat_id=update.message.chat.id, text='Server is <b>virgin</b> again.',parse_mode='HTML')

async def sessiondownload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("Received Session File : " + update.message.document.file_name)
    messeger = str((update._effective_user['id']))
    if int(update.message.document.file_size) <= 1000:
        file_name=update.message.document.file_name
        file_id = update.message.document.file_id
        newFile = await context.bot.get_file(file_id)
        await newFile.download(messeger+"#"+file_name)
        await context.bot.send_message(chat_id=update.message.chat.id, text="<b>Session File <code>{}</code> Received!</b> \n \n If you want to use your session for downloading posts/stories, just send <code>/iglogin username</code> command. \n\n Other commands: \n <b>To Logout :</b>\n Simply send /iglogout command.\n <b>To Check :</b>\n Simply send /igcheck command.".format(file_name),parse_mode='HTML')

def check_old_session(ig_session_file):
    old_session= False
    for files in os.listdir("./"):
        if files.endswith(('session')):
            if files ==ig_session_file:
                old_session = True
                return old_session


async def iglogin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global ig_session_USER,  ig_session_file
    ig_session_USER = (((update.message['text']).split(" "))[1]).lower()
    messeger = str((update._effective_user['id']))
    ig_session_file = messeger+"#"+ig_session_USER+".session"
    if check_old_session(ig_session_file)==True:
        await context.bot.send_message(chat_id=update.message.chat.id, text="<b>Session File Already Exists!</b> \n \n If you want to use your old session for user <code>{}</code>, just ignore this message. \n\n If you want to replace with new session file, Simply send a new session file in format <u>username.session</u> \n If you need session generator file again send /igsession".format(ig_session_USER),parse_mode='HTML')
    else:
        await sessiongenerator(update,context)

async def sessiongenerator(update,context):
    await update.message.reply_html(
                    rf"Dear {update.effective_user.mention_html()}, Send a session file generated by running the session generator file sent below.", reply_markup=ForceReply(selective=True))
    await context.bot.send_document(chat_id=update.message.chat.id, document = open('session_generator.py','rb'),caption = '<b>After sending session files, you can use these command to do different tasks</b>\n \n <b>To Log In :</b>\n Simply send <code>/iglogin username</code> command.\n <b>To Logout :</b>\n Simply send <code>/iglogout username</code>command.\n <b>To Check :</b>\n Simply send /igcheck command.\n <b>To Remove Session File :</b>\n Simply send <code>/rmigsession username</code> command. \n\n <b>For full list of commands :</b>\n Simply send /help command.',parse_mode='HTML')

async def sessiongen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await sessiongenerator(update,context)

async def rmsessionfile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global ig_session_USER,  ig_session_file
    ig_session_USER = (((update.message['text']).split(" "))[1])
    messeger = str((update._effective_user['id']))
    ig_session_file = messeger+"#"+ig_session_USER+".session"
    for files in os.listdir("./"):
        if files.endswith(('session')):
            if files ==ig_session_file:
                os.remove(ig_session_file)
                await context.bot.send_message(chat_id=update.message.chat.id, text="<b>Session File of user : {} Removed Successfully!</b> \n \n If you want to use your session again just start from <code>/iglogin username</code>. \n\n\n If you need session generator file again send /sessiongenerator".format(ig_session_USER),parse_mode='HTML')
    ig_session_USER = ''
    ig_session_file = ''

async def igstories(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    messeger = str((update._effective_user['id']))
    global ig_session_file, ig_session_USER
    ig_session_file = messeger+"#"+ig_session_USER+".session"
    if await ig_session_check(update, context) == False:
        try:
            ig_session_USER,ig_session_file = login_from_saved_sessions(update, context)
        except BaseException:
            ig_session_USER,ig_session_file = '',''
            print("User not registered for posts downloads.")
    ig_session_file = messeger+"#"+ig_session_USER+".session"
    storyof = (((update.message['text']).split(" "))[1])
    print( "Account used for stories is : "+ ig_session_USER)
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
    """Send a message when the command /iglogout is issued."""
    clean_clutter()
    global ig_session_USER,  ig_session_file
    ig_session_USER1 = (((update.message['text']).split(" "))[1]).lower()
    messeger = str((update._effective_user['id']))
    ig_session_file1 = messeger+"#"+ig_session_USER+".session"
    if ig_session_file1 == ig_session_file:
        ig_session_USER = ''
        ig_session_file = ''
        L = None
        print("Server clean was success.")
        await context.bot.send_message(chat_id=update.message.chat.id, text='Removed credentials Successfully. \n \n Send /igcheck to look if your credentials are removed or not.',parse_mode='HTML')
    else:
        await context.bot.send_message(chat_id=update.message.chat.id, text='You are not logged in to log out.',parse_mode='HTML')

async def igcheck(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    messeger = str((update._effective_user['id']))
    #ig_session_file = messeger+"#"+ig_session_USER+".session"
    #print(ig_session_file)
    igusername = []
    igactivestatus = False
    for files in os.listdir():
        if files.endswith('session'):
            igusernames = files.split("#")
            if igusernames[0]==messeger:
                igusername.append((igusernames[1])[:-8])
    if len(igusername) >= 1:
        a = 0
        igusrformat = ''
        
        for listedigusername in igusername:
            igusrformat = igusrformat + "    • " +listedigusername+"\n"
            #print ("Ig sesssion : "+ ig_session_USER)
            # ("listed one : "+ listedigusername)
            if ig_session_USER == listedigusername:
                igactivestatus = True
        if igactivestatus == True:
            await context.bot.send_message(chat_id=update.message.chat.id, text="""<b><u>Currently used account for sending posts is :</u></b> \n\n     <b>Username : </b><code>{}</code>\n\n Server won't use until you login by yourself.\n\n All of your available accounts are listed below : \n {} \n\nFor all available options, simply send /help command.""".format(ig_session_USER,igusrformat),parse_mode='HTML')
        elif igactivestatus == False:
            await context.bot.send_message(chat_id=update.message.chat.id, text="""<b>None</b> of your accounts are currently in use for downloading posts and stories.\n\nServer won't use until you login by yourself.\n\n All of your available accounts are listed below : \n {} \n\nFor all available options, simply send /help command.""".format(igusrformat),parse_mode='HTML')
    else:
        await context.bot.send_message(chat_id=update.message.chat.id, text="""You don't have any accounts saved here! \n \n To add, just send <code>/iglogin username</code> command and follow further steps. \n\n Send /help command to list all available commands.""",parse_mode='HTML')

async def ig_session_check(update, context):
    global ig_session_file, ig_session_USER
    messeger = str((update._effective_user['id']))
    #ig_session_file = messeger+"#"+ig_session_USER+".session"
    igusername = []
    igactivestatus = False
    for files in os.listdir():
        if files.endswith('session'):
            igusernames = files.split("#")
            if igusernames[0]==messeger:
                igusername.append((igusernames[1])[:-8])
    if len(igusername) >= 1:
        a = 0
        igusrformat = ''
        for listedigusername in igusername:
            igusrformat = igusrformat + "    • " +listedigusername+"\n"
            print ("Ig sesssion : "+ ig_session_USER)
            print ("listed one : "+ listedigusername)
            if ig_session_USER == listedigusername:
                igactivestatus = True
    return igactivestatus

async def login_from_saved_sessions(update, context):
    global ig_session_file, ig_session_USER
    messeger = str((update._effective_user['id']))
    #ig_session_file = messeger+"#"+ig_session_USER+".session"
    igusername = []
    igactivestatus = False
    for files in os.listdir():
        if files.endswith('session'):
            igusernames = files.split("#")
            if igusernames[0]==messeger:
                igusername.append((igusernames[1])[:-8])
    if len(igusername)>= 1:
        ig_session_USER = igusername[0]
        ig_session_file = messeger + "#"+ig_session_USER+".session"
        return ig_session_USER,ig_session_file
    else:
        return False

async def main_url_dl(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    messeger = str((update._effective_user['id']))
    global ig_session_file, ig_session_USER
    ig_session_file = messeger+"#"+ig_session_USER+".session"
    if await ig_session_check(update, context) == False:
        try:
            ig_session_USER,ig_session_file = login_from_saved_sessions(update, context)
        except BaseException:
            ig_session_USER,ig_session_file = '',''
            print("User not registered for posts downloads.")
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
    application.add_handler(CommandHandler("iglogout", iglogout))
    application.add_handler(CommandHandler("igcheck", igcheck))
    application.add_handler(CommandHandler("igstories", igstories))
    application.add_handler(CommandHandler("igsession", sessiongen))
    application.add_handler(CommandHandler("rmigsession", rmsessionfile))
    #youtube music
    application.add_handler(CommandHandler("ytaudio", yt_audio))

    #For other links
    application.add_handler(MessageHandler(filters.Regex('([^\s\.]+\.[^\s]{2,}|www\.[^\s]+\.[^\s]{2,})') & ~filters.COMMAND, main_url_dl))

    #sessionfile watcher
    application.add_handler(MessageHandler(filters.Document.FileExtension("session"), sessiondownload))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == "__main__":
    main()