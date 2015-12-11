# Bot starter kit

Use this repository to start building a bot.

## Prerequisites (Mac)

1. Get [Homebrew](http://brew.sh/)
2. Install dependencies:

    ```sh
    brew install git python app-engine-python ngrok
    ```

3. Install Fabric:

    ```sh
    pip install fabric
    ```

4. Clone this repository

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
