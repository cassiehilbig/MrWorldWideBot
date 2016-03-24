# Bot starter kit

Use this repository to start building a bot based on Google App Engine.

## Prerequisites (Mac)

1. Fork this project.

2. In the project's root directory, run:

    ```sh
    ./setup.mac.sh
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

In a different terminal window/tab:

```sh
ngrok http 8080
```
This will create a public tunnel to your local environment. Copy the URL that starts with `https`.

Go to your [Reply Settings](https://engine.kik.com/#/engine) and change the URL to the one that you just copied followed by `/incoming`.
For instance: `https://4ce24529.ngrok.com/incoming`.

Start the server by running:

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

2. Export your project id for the deploy command to use:

    ```sh
    export GOOGLE_PROJECT_ID={{project id}}
    ```

3. Do an initial deploy. You will need to login through your Google account that is linked to the application.

    ```sh
    fab deploy
    ```

    The deploy command will modify some files to prepare them for deployment. Do not check in these changes.

    (For automated deploys)

4. The deploy command should output your refresh token. Add this to the environment to have automated deploys using `fab deploy`.

    ```sh
    export GOOGLE_REFRESH_TOKEN={{refresh token}}
    ```

## Using Mixpanel

The starter kit has a built in metrics tracking framework using Mixpanel.
To use this functionality you need to set your Mixpanel token:

```sh
export MIXPANEL_TOKEN={{your mixpanel token}}
```

The Mixpanel functionality lives in [lib.metrics](lib/metrics.py).
Just import the `track` function, and call it with a distinct ID (probably either a username or a conversation ID, depending on how you want to tract metrics), the name of the event and a dictionary containing any additional data you want to track.

Example
```python
from lib.metrics import track

track(user, 'A Very Important Event', {'Some Property Name': 'somevalue'})
```