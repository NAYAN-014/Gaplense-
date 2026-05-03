"""
run.py — GapLens Server Runner
================================
Server start karne ke liye yeh file run karo:

    python run.py

NOTE: Is file ko project root se run karo, andar se nahi.
"""

from main.app import app

if __name__ == '__main__':
    app.run(debug=True, port=5000)
