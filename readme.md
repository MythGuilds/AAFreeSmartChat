# AAFree Smart Chat
An application that takes any language in the AAFree chat logs and translates it 
To your native language. Uses Google Translate, so don't expect to have an indepth conversation!

# How to compile
Must Be In PyCharm for venv to work

`python -m PyInstaller main.pyw`

# Why not auto translate
I’m extremely tired of people asking this question and arguing with me when I tell them the answer. So I decided to explain it all here. Why does the program make you manually copy and paste text into the Web View pointed to https://translate.google.com/?

1. Google's official translation API costs $20 per million characters. One very active player could rack that much up in one day. Times that by, lets say, 60 users and you can start to see the issue.


2. An unofficial and free Google Translate API exists at https://pypi.org/project/googletrans/. However, after 15 hours of troubleshooting I have figured out that the amount of messages being sent to the API is too much. After 10 minutes of use, this API seems to soft block your IP address. This means that no errors are being thrown, but the API will refuse to translate any text fed to it. Only after changing your IP address via a VPN did the API start working again. Of course this fix only works until that VPN’s address is blocked and you have to connect to a different server.


3. People have suggested bulk / batch calls to the API. This still does not help the IP block. 


4. I refuse to release a product that breaks the more it’s used, even if you put the translation API as a side feature. If you would like to fork my code and make your own buggy version of this program, feel free to.

#### Note: There is a small group of people that, for whatever reason, are not effected by the API block. At least that is their claim. Please remember, you are 1 of like 3 people. I don't have the time to cater to this group at the moment.