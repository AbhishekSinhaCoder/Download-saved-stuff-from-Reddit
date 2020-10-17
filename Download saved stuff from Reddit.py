#Python Reddit API Wrapper PRAW
import praw, json, time, datetime, os, requests, shutil, ffmpeg 
#install ffmpeg via pip install --user ffmpeg-python #also state the path via environment variables
#from pytube import YouTube

#instance
reddit = praw.Reddit(client_id = '',
    client_secret = '',
    username = 'jeunpeun99',
    password = 'password',
    redirect_uri = 'http://localhost:8080/',
    user_agent = 'testscript by /u/jeunpeun99')

"""making a directory with the subreddits as keys, and the data as values"""
#safe each comment in a text document called subreddit_month.txt and give the title of each comment, and the body of the comment
#safe for each submission the whole page with the first 1000 comments via pushshift and save it in the specific subreddit folder
#if the submission only contains a youtube link, download the video and place it in the specific subreddit folder
#if the submission only contains an image, download the image, and give it the title and the name of the user
#if the submission only contains a video, download the video, and give it the title and name of the user
#make a document with links

class objectview(object):
    """to access dictionary items as object attributes"""
    def __init__(self, d):
        self.__dict__ = d

def collecting_saved_data(after):
    for data in reddit.user.me().saved(limit=25, params={"after" : after}):
        # ~ print(dir(data))
        fullnames.append(data.fullname)
        print(data.fullname)
        print(data.subreddit, data.author)
        
        if data.author:
            author = data.author.name
        else:
            author = "unknown"
        
        if getattr(data, 'crosspost_parent_list', None):
            data = objectview(data.crosspost_parent_list[0]) #put the crosspost_parent_list dict within the data dict
            data.fullname = data.name #it is called differently between the two dicts
            subreddit = data.subreddit
        else:
            subreddit = data.subreddit.display_name
            
        if data.fullname[:3] == "t1_": #Reddit comments
            if saved_by_user.get(subreddit):
                saved_by_user[subreddit].append(["comment", data.fullname, data.permalink, author, data.created, data.score, data.link_title, data.body])
            else:
                saved_by_user[subreddit] = []
                saved_by_user[subreddit].append(["comment", data.fullname, data.permalink, author, data.created, data.score, data.link_title, data.body]) #data.replies ])
        if data.fullname[:3] == "t3_":
            if "reddit.com/r/" in data.url: #normal Reddit post
                if saved_by_user.get(subreddit):
                    saved_by_user[subreddit].append(["post", data.fullname, data.permalink, author, data.created, data.score, data.title, data.selftext])
                else:
                    saved_by_user[subreddit] = [] 
                    saved_by_user[subreddit].append(["post", data.fullname, data.permalink, author, data.created, data.score, data.title, data.selftext])
            elif "youtu.be/" in data.url: #youtube, download later
                if saved_by_user.get(subreddit):
                    saved_by_user[subreddit].append(["youtube", data.fullname, data.permalink, author, data.created, data.score, data.title, data.url])
                else:
                    saved_by_user[subreddit] = []
                    saved_by_user[subreddit].append(["youtube", data.fullname, data.permalink, author, data.created, data.score, data.title, data.url])
            elif "v.redd" in data.url:
                if saved_by_user.get(subreddit):
                    saved_by_user[subreddit].append(["video", data.fullname, data.permalink, author, data.created, data.score, data.title, data.media["reddit_video"]["fallback_url"]])
                else:
                    saved_by_user[subreddit] = []
                    saved_by_user[subreddit].append(["video", data.fullname, data.permalink, author, data.created, data.score, data.title, data.media["reddit_video"]["fallback_url"]])
            elif "i.redd" in data.url:
                if saved_by_user.get(subreddit):
                    saved_by_user[subreddit].append(["image", data.fullname, data.permalink, author, data.created, data.score, data.title, data.url])
                else:
                    saved_by_user[subreddit] = []
                    saved_by_user[subreddit].append(["image", data.fullname, data.permalink, author, data.created, data.score, data.title, data.url])
            else:
                if saved_by_user.get(subreddit):
                    saved_by_user[subreddit].append(["link", data.fullname, data.permalink, author, data.created, data.score, data.title, data.url])
                else:
                    saved_by_user[subreddit] = []
                    saved_by_user[subreddit].append(["link", data.fullname, data.permalink, author, data.created, data.score, data.title, data.url])
            
    return fullnames, saved_by_user

saved_by_user = {}
fullnames = []

fullnames, saved_by_user = collecting_saved_data(None)
collected = []


while fullnames[-1] not in collected:
    collected.append(fullnames[-1])
    fullnames, saved_by_user = collecting_saved_data(fullnames[-1])
    time.sleep(1)

print(len(fullnames))
# ~ print(saved_by_user)

date_file = datetime.datetime.utcfromtimestamp(time.time()).strftime('%Y-%m')
with open(f'saved/saved_by_user-{date_file}.json', 'w') as datafile: 
    json.dump(saved_by_user, datafile)


date_file = datetime.datetime.utcfromtimestamp(time.time()).strftime('%Y-%m')
with open(f'saved/saved_by_user-{date_file}.json', 'r') as datafile: 
    saved_by_user = json.load(datafile)
    
def download_file(url, directory, title):
    # ~ local_filename = url.split('/')[-1]
    with requests.get(url, stream=True) as r:
        with open(f'{directory}/{title}', 'wb') as f:
            shutil.copyfileobj(r.raw, f)
    return title
    #does the data stay in memory?

for subreddit, value in saved_by_user.items():
    if not os.path.exists(f'saved/{subreddit}/'): #since each subreddit is being finished subsequently, if subreddit exist it is not needed to download the content again
        print(subreddit)
        os.makedirs(f'saved/{subreddit}/') #create directory if it doesn't exist yet
    for data in value:
        date_file = datetime.datetime.utcfromtimestamp(data[4]).strftime('%Y-%m')
        created = datetime.datetime.utcfromtimestamp(data[4]).strftime('%Y-%m-%d')
        title = data[6].replace('\\', "").replace('/', "").replace(':', "").replace('*', "").replace('?', "").replace('"', "").replace('<', "").replace('>', "").replace('|', "")[:45]
        if "comment" in data[0]:
            with open(f'saved/{subreddit}/comments_{date_file}.txt', 'a', encoding='utf-8') as textfile:
                textfile.write(f'{data[6]}\n')
                textfile.write(f'Author: {data[3]}, Created: {created}, Score: {data[5]}\n')
                textfile.write(f'{data[7]}\n\n')
            
        if "post" in data[0]:
            with open(f'saved/{subreddit}/{title}.txt', 'w', encoding='utf-8') as textfile:
                textfile.write(f'{data[6]}\n')
                textfile.write(f'Author: {data[3]}, Created: {created}, Score: {data[5]}\n')
                textfile.write(f'{data[7]}\n\n')
                
            #extract replies of post
            headers = {
                'Host': 'api.pushshift.io',
                }
            with requests.Session() as s:
                response = s.get(f'https://api.pushshift.io/reddit/search/comment?sort=asc&link_id={data[1]}&limit=10000', headers=headers)
                print(response.status_code)
                extracted = response.json()
                with open(f'saved/{subreddit}/{title}.json', 'w') as datafile: 
                    json.dump(extracted, datafile)
                time.sleep(1) #to be sure not to make to many requests towards Pushshift.io
                
        if "youtube" in data[0]:
            with open(f'saved/youtube_to_download.txt', 'a', encoding='utf-8') as textfile:
                textfile.write(f'{data[7]}\n\n')
            #YouTube(data[7]).streams.first().download(f'saved/{subreddit}/')
            
        if "video" in data[0]:
            audio_url = data[7].split('DASH')[0] + 'audio'
            # ~ print(audio_url)
            video_url = data[7]
            download_file(video_url, f'saved/{subreddit}', title + '-video')
            download_file(audio_url, f'saved/{subreddit}', title + '-audio')
            
            video_stream = ffmpeg.input(f'saved/{subreddit}/{title}-video')
            audio_stream = ffmpeg.input(f'saved/{subreddit}/{title}-audio')
            #combine video and audio
            try:
                concatinated_stream = ffmpeg.concat( video_stream , audio_stream, v=1, a=1)
                concatinated_stream.output(f'saved/{subreddit}/{title}.mp4').run()
            except Exception as e:
                print("cannot mux video and audio: ", e)
        if "image" in data[0]:
            download_file(data[7], f'saved/{subreddit}', title + ".jpg")
            # ~ response = requests.get(data[7], stream=True)
            # ~ with open(f'saved/{subreddit}/{data[6]}_{data[3]}.jpg', 'wb') as out_file:
                # ~ shutil.copyfileobj(response.raw, out_file)
            # ~ del response
            
        if "link" in data[0]:
            with open(f'saved/{subreddit}/links_{date_file}.txt', 'a', encoding='utf-8') as textfile:
                textfile.write(f'{data[6]}\n')
                textfile.write(f'{data[7]}\n\n')