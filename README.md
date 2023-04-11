# [Krypto](https://discordapp.com/oauth2/authorize?client_id=555820515965534208&permissions=8&scope=bot)
![Discord Bots](https://top.gg/api/widget/servers/555820515965534208.svg)
###### All-in-One Discord Bot with Auto-Moderation, Bump Advertising, Economy System, Moderation Commands, Mod Mail, Music Player, Vouch System, and Many More Commands & Features

### Requirements
- [Python 3.8+](https://www.python.org/downloads/)
- [Discord Developer Portal](https://discord.com/developers/applications) Application Information
- [MongoDB Cloud Account](https://cloud.mongodb.com/) *(Free)*
- [TopGG](https://top.gg), [Discord Bot List](https://discordbotlist.com/bots/mine), & [Discord Bots](https://discord.bots.gg/profile) API Tokens *(Optional)*
- [Reddit Account](https://www.reddit.com/prefs/apps/) *(Optional)*
- [Clash of Clans API Account](https://developer.clashofclans.com/#/new-key) *(Optional)*

### Configuration
- Clone the Repository `git clone https://github.com/Jerry12798/Krypto.git`
- Move into Repository's Main Directory `cd Krypto`
- Install Dependencies `pip3 install -r Requirements.txt`
- Create Config.json `cp Config.json.example Config.json`
- Enter Information into `Config.json` *(Create All Necessary Channels & Roles)*
- Place Bot's Logo in `public/images` *(Must be Named `Logo.png`)*
- [Create Favicons](https://realfavicongenerator.net/) *(Be Sure to Set PATH to `/public/images/favicons`)*
- Place Extracted Favicon Images into `public/images/favicons`

### MongoDB Setup
- Create [MongoDB Cloud Account](https://cloud.mongodb.com/)
- [Create MongoDB Organization](https://cloud.mongodb.com/v2#/preferences/organizations/create)
- Create MongoDB Database
- Create MongoDB Connection String *(Connect -> Connect Your Application -> Python 3.4 or Later)*
- Enter MongoDB Client/Connection String into `Config.json`
- Whitelist Host IP on MongoDB Cloud *(Located in Network Access on Database Page)*

### Bot Listing Setup
#### TopGG
- Submit Required Information to List the Bot
- The Dashboard/Website URL is `http://HOST_EXTERNAL_IP:5000`
- The Webhook URL is `http://HOST_EXTERNAL_IP:7777/ggwebhook`
- The Webhook Authorization is Created by You and Entered into `Config.json`
- Generate API Token for Bot and Enter into `Config.json`
##### *Remove this Feature by Removing Line `25` in `Cogs/Server.py`, `201-308` in `Cogs/Information.py`, and `173-277` in `Cogs/Slash/Info.py`*
#### Discord Bot List
- Submit Required Information to List the Bot
- The Dashboard/Website URL is `http://HOST_EXTERNAL_IP:5000`
- The Webhook URL is `http://HOST_EXTERNAL_IP:7777/dblwebhook`
- The Webhook Secret is Created by You and Entered into `Config.json`
- Generate API Token for Bot and Enter into `Config.json`
##### *Remove this Feature by Removing Line `239-249` in `Cogs/Server.py`*
#### Discord Bots
- Submit Required Information to List the Bot
- The Dashboard/Website URL is `http://HOST_EXTERNAL_IP:5000`
- [Generate API Token](https://discord.bots.gg/docs) and Enter into `Config.json`
##### *Remove this Feature by Removing Line `250-260` in `Cogs/Server.py`*

### Reddit Setup
- Create Reddit Account
- Navigate to [Reddit's Developer Portal](https://www.reddit.com/prefs/apps/)
- Create Personal Use Script *(Redirect URI is the Bot's Invite)*
- Enter Client ID *(Below Name & App Type)* into `Config.json`
- Enter Client Secret into `Config.json`
- Enter Reddit Username into `Config.json`
- Enter Reddit Password into `Config.json`
- Enter User Agent *(Name of App)* into `Config.json`
##### *Remove this Feature by Removing Line `77` & `747-761` in `Cogs/General.py` and `72` & `652-665` in `Cogs/Slash/Everyone.py`*

### Clash of Clans API Setup
- [Create Clash of Clans API Account](https://developer.clashofclans.com/#/register)
- [Create New Key](https://developer.clashofclans.com/#/new-key)
- Enter Clash of Clans API Account Email into `Config.json`
- Enter Clash of Clans API Account Password into `Config.json`
- Enter Clash of Clans API Key Name into `Config.json`
##### *Remove this Feature by Removing the Entire `Cogs/COC.py` & `Cogs/Slash/CoC.py` Files*

### Running
- Move into Repository's Main Directory `cd Krypto`
- Create Bot's Tmux Instance `tmux new -s krypto`
- Move into Bot's Tmux Instance `tmux a -t krypto`
- Start the Bot `python3 Krypto.py`
- Create Site's Tmux Instance `tmux new -s dash`
- Move into Site's Tmux Instance `tmux a -t dash`
- Start the Dashboard `python3 Dash.py`
- Stop the Bot `CTRL + C`, `CTRL + Z`, or `&logout`
- Stop the Dashboard `CTRL + C` or `CTRL + Z`

### Updating
- Move into Repository's Main Directory `cd Krypto`
- Run Git Fetch `git fetch`

### Contributing
- Report Bugs, Issues, or Errors on [Github](https://github.com/Jerry12798/Krypto/issues) or Our [Discord Support Server](https://discord.gg/SM35Sfs)
- Contribute to Code by Posting [Pull Requests](https://github.com/Jerry12798/Krypto/pulls) or DMing [Anonymous Jerry#4513](https://discordapp.com/users/414227652178870282/)

### Links
- [Support Server](https://discord.gg/SM35Sfs)
- [Krypto's Invite](https://discordapp.com/oauth2/authorize?client_id=555820515965534208&permissions=8&scope=bot)
- [Krypto's Dashboard](https://krypto.codes)
- [Krypto's TopGG Page](https://top.gg/bot/555820515965534208)
- [Krypto's Discord Bot List Page](https://discordbotlist.com/bots/krypto-6851)
- [Krypto's Discord Bots Page](https://discord.bots.gg/bots/555820515965534208)
- [Anonymous Jerry#4513](https://discordapp.com/users/414227652178870282/)
- [Donate](https://paypal.me/Lou1295)