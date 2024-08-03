from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def root():
    return jsonify("Thank you for using bookstore application")

if __name__ == '__main__':
    app.run(debug=True)
