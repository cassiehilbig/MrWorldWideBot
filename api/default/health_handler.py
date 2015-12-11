from app import app


@app.route('/health/', methods=['GET'])
def health():
    return '', 200
