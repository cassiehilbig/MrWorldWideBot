#!/bin/bash

ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
brew tap caskroom/cask
brew update
brew install git python app-engine-python
brew cask install ngrok
pip install --upgrade --quiet --requirement requirements.txt
