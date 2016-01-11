#!/usr/bin/env bash

if ! type "brew" > /dev/null; then
    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
fi

# Make sure we're using the latest brew, then upgrade all existing items.
brew update
brew upgrade

brew tap caskroom/cask

brew install git python app-engine-python
brew cask install ngrok

pip install --upgrade --quiet --requirement requirements.txt
