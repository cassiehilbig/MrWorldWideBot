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

#### Install backend dependencies

```sh
fab install_xlib
```

You might get the error 

```sh
DistutilsOptionError: must supply either home or prefix/exec-prefix -- not both

Fatal error: local() encountered an error (return code 2) while executing 'pip install --upgrade --no-deps --requirement requirements_xlib.txt -t xlib'
```

In which case follow this [Stack Overflow post](http://stackoverflow.com/q/24257803/368772) and run

```sh
echo "[install]"\n"prefix="\n > ~/.pydistutils.cfg
fab install_backend_dependencies
```

#### Starting ngrok and your debug server
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

## Running unit tests

In the project's root directory, run:

```sh
fab test
```

## Deploying

1. Setup a project on the [Google Developers Console](https://console.developers.google.com/).

2. Edit the `application` field in `app.yaml` with your application id.

3. Do an initial deploy. You will need to login through your Google account that is linked to the application.

```sh
fab deploy
```

(For automated deploys)

4. The deploy command should output your refresh token. Add this to the environment to have automated deploys using `fab deploy`.

```sh
export GOOGLE_REFRESH_TOKEN={{refresh token}}
```
