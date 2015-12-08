from app import app

@app.route('/_ah/warmup')
def warmup():
    return ''
