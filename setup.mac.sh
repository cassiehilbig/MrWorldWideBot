#!/usr/bin/env bash

if ! type "brew" > /dev/null; then
    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
fi

dependencies=(
    git 
    python 
    app-engine-python
)

brew tap caskroom/cask

# Make sure we're using the latest brew, then upgrade all existing items.
brew update
brew upgrade ${dependencies[@]} 2> /dev/null

brew install ${dependencies[@]}
brew cask install ngrok

pip install --upgrade --quiet --requirement requirements.txt
