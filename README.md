# Bot starter kit

Use this repository to start building a bot.

## Prerequisites (Mac)

1. Get [Homebrew](http://brew.sh/):

```sh
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

2. Clone this repository and run the setup script:

```sh
git clone https://github.com/kikinteractive/bot-starter-kit.git
cd bot-starter-kit
./setup.mac.sh
```


## Running unit tests

In the project's root directory, run:

```sh
fab install_test_dependencies
```

## Setting up your bot

1. Go to the [Bot Dashboard](https://engine.kik.com) and scan the Kik Code to create a new bot.
2. Once you've created your bot, open `config.py` and set `BOT_USERNAME` to the username you chose.
3. Open `secrets.py` and set `BOT_API_KEY` to your bot's API key. You can find it in your [Reply Settings](https://engine.kik.com/#/engine).
   **Make sure you never submit your API key to git.**

## Running the debug server

Install backend dependencies by running:

```sh
fab install_backend_dependencies
```

Start ngrok by running:
```sh
ngrok 8080
```
This will create a public tunnel to your local environment. Copy the URL that starts with `https`.

Go to your [Reply Settings](https://engine.kik.com/#/engine) and change the URL to the one that you just copied followed by `/receive`.
For instance: `https://4ce24529.ngrok.com/receive`.

```sh
fab debug
```

Start texting your bot. Enjoy!

## Deploying

Coming soon
