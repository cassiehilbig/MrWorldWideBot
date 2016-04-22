import subprocess

def translate(english):
    translater = subprocess.Popen('pirate', stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    translater.stdin.write(english.encode("utf8")+"\n")
    piratese, _ = translater.communicate()

    # chop off the trailing new line
    piratese = piratese[:-1]
    return piratese

print translate("Hello")