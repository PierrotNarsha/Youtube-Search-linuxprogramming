#!/usr/bin/python

from apiclient.__init__.discovery import build
from apiclient.__init__.errors import HttpError
from oauth2client.tools import argparser
import os
from datetime import datetime
import webbrowser

dt = datetime
# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.

# 유튜브 api 개발자 key를 저장합니다.
DEVELOPER_KEY = "AIzaSyB_oulTx-vylJgWxSCrEi1aEnoyCw1K7WE"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# 비디오 타이틀 저장할 배열

keyword = ""

# 유튜브 검색 함수
def youtube_search(options):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

    videos = []

    # Call the search.list method to retrieve results matching the specified
    # query term.
    search_response = youtube.search().list(
        q=options.q,
        part="id,snippet",
        maxResults=options.max_results
    ).execute()

    # Add each result to the appropriate list, and then display the lists of

    # 검색후 읽어 온 값을 배열에 저장하고 영상이름, 비디오 아이디로 구분함
    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            videos.append("%s (%s)" % (search_result["snippet"]["title"],
                                        search_result["id"]["videoId"]))

    print("Videos:\n"+"\n".join(videos))

    fd = os.open("title.txt", os.O_WRONLY | os.O_CREAT)
    file_object = os.fdopen(fd, "a")

    file_object.write("\n" + str(dt.now()) + "\n")
    file_object.write("keyword : " + keyword + "\n")
    file_object.write("Videos:\n")
    file_object.write("\n".join(videos)+"\n\n")

    file_object.close()


def youtube_url(options):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

    #webbrowser를 web객체로 생성
    web = webbrowser

    videos_url = []

    search_response = youtube.search().list(
        q=options.q,
        part="id,snippet",
        maxResults=options.max_results
    ).execute()

    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            videos_url.append("%s id:%s" % (search_result["snippet"]["title"],
                                        search_result["id"]["videoId"]))



    print("어떤 영상으로 가기를 원하십니까\n")

    for i in range(0, 11):
        print(str(i+1)+"\t"+videos_url[i])

    select_video = input("\n번호를 입력해주십시요 : ")
    videos_id = videos_url[int(select_video)-1]

    url = "https://www.youtube.com/watch?v="+videos_id.split('id:')[1]
    print("\n선택한 영상의 url입니다.\n")
    print(url)
    try:
        web.open(url)
    except HttpError as e:
        print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))


if __name__ == "__main__":

    print("환영합니다. \'유튜브 서치\' 입니다.")

    #부모 pid를 출력
    print("부모 pid: " + str(os.getpid()))
    #검색 키워드 입력받기
    keyword = input("\n검색하고자하는 키워드를 입력하시오 : ")
    print("")

    #pid1에게 자식 프로세스할당
    pid1 = os.fork()
    if pid1 == 0:
        print("1번째 자식 pid %d" % (os.getpid()))

        argparser.add_argument("--q", help="Search term", default=keyword)
        # 파싱할 제목 수
        argparser.add_argument("--max-results", help="Max results", default=11)
        args = argparser.parse_args()

        try:
            youtube_search(args)
        except HttpError as e:
            print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))



        exit(0)

    os.waitpid(pid1, 0)

    print("\n\n유튜브 url로 이동하시겠습니까?\n(이동을 원하시면 1, 아니면 0을 입력해주십시요)")
    select = int(input())

    if select == 1:
        pid2 = os.fork()
        if pid2 == 0:

            print("2번째 자식 pid : "+str(os.getpid())+"")

            argparser.add_argument("--q", help="Search term", default=keyword)
            argparser.add_argument("--max-results", help="Max results", default=11)
            args = argparser.parse_args()
            try:
                youtube_url(args)
            except HttpError as e:
                print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))

            exit(2)

        os.waitpid(pid2, 0)

    print("프로그램을 종료합니다.")

