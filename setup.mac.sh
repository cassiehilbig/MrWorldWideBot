#!/usr/bin/env bash

if ! type "brew" > /dev/null; then
    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
else
    brew update
fi

brew install git python app-engine-python ngrok

# In case something was already installed, updgrade new version.
brew upgrade

pip install --upgrade --quiet --requirement requirements.txt
