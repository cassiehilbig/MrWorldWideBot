# Bot starter kit

Use this repository to start building a bot based on Google App Engine.

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
fab test
```

## Setting up your bot

1. Go to the [Bot Dashboard](https://engine.kik.com) and scan the Kik Code to create a new bot.
2. Once you've created your bot, set the `BOT_USERNAME` and `BOT_API_KEY` environment variables.

`BOT_USERNAME` is the username of your bot,
and `BOT_API_KEY` can be found in your [Reply Settings](https://engine.kik.com/#/engine).

```sh
export BOT_USERNAME={{username}}
export BOT_API_KEY={{api key}}
```

## Running the debug server

Install backend dependencies by running:

```sh
fab install_backend_dependencies
```

You might get the error 

```sh
DistutilsOptionError: must supply either home or prefix/exec-prefix -- not both

Fatal error: local() encountered an error (return code 2) while executing 'pip install --upgrade --no-deps --requirement requirements_xlib.txt -t xlib'
```

In which case follow this [stack overflow post](http://stackoverflow.com/questions/24257803/distutilsoptionerror-must-supply-either-home-or-prefix-exec-prefix-not-both) and run `echo "[install]"\n"prefix="\n > ~/.pydistutils.cfg` and then run `fab install_backend_dependencies`

Start ngrok by running:
```sh
ngrok 8080
```
This will create a public tunnel to your local environment. Copy the URL that starts with `https`.

Go to your [Reply Settings](https://engine.kik.com/#/engine) and change the URL to the one that you just copied followed by `/receive`.
For instance: `https://4ce24529.ngrok.com/receive`.

Start the sever by running:

```sh
fab debug
```

Start texting your bot. Enjoy!

## Deploying

Coming soon
