from flask import Flask, render_template, request, send_file
import hashlib
import base64
import os
import string
import random
from datetime import datetime

app = Flask(__name__)
REPORT_FOLDER = "reports"
os.makedirs(REPORT_FOLDER, exist_ok=True)

ALPHABET = string.ascii_uppercase

def caesar_encrypt(text, shift):
    result = ""
    for ch in text:
        if ch.isalpha():
            base = ord('A') if ch.isupper() else ord('a')
            result += chr((ord(ch) - base + shift) % 26 + base)
        else:
            result += ch
    return result

def caesar_decrypt(text, shift):
    return caesar_encrypt(text, -shift)

def vigenere_encrypt(text, key):
    result = ""
    key = ''.join([c.upper() for c in key if c.isalpha()])
    if not key:
        return "Invalid key. Please enter alphabetic key."
    ki = 0
    for ch in text:
        if ch.isalpha():
            shift = ord(key[ki % len(key)]) - ord('A')
            base = ord('A') if ch.isupper() else ord('a')
            result += chr((ord(ch) - base + shift) % 26 + base)
            ki += 1
        else:
            result += ch
    return result

def vigenere_decrypt(text, key):
    result = ""
    key = ''.join([c.upper() for c in key if c.isalpha()])
    if not key:
        return "Invalid key. Please enter alphabetic key."
    ki = 0
    for ch in text:
        if ch.isalpha():
            shift = ord(key[ki % len(key)]) - ord('A')
            base = ord('A') if ch.isupper() else ord('a')
            result += chr((ord(ch) - base - shift) % 26 + base)
            ki += 1
        else:
            result += ch
    return result

def xor_encrypt_decrypt(text, key):
    if not key:
        return "Invalid key. Please enter a key."
    output = ''.join(chr(ord(ch) ^ ord(key[i % len(key)])) for i, ch in enumerate(text))
    return base64.b64encode(output.encode(errors="ignore")).decode()

def xor_decrypt(encoded_text, key):
    if not key:
        return "Invalid key. Please enter a key."
    try:
        decoded = base64.b64decode(encoded_text.encode()).decode(errors="ignore")
        return ''.join(chr(ord(ch) ^ ord(key[i % len(key)])) for i, ch in enumerate(decoded))
    except Exception:
        return "Invalid Base64 encrypted text."

def base64_encode(text):
    return base64.b64encode(text.encode()).decode()

def base64_decode(text):
    try:
        return base64.b64decode(text.encode()).decode()
    except Exception:
        return "Invalid Base64 input."

def hash_text(text, algorithm):
    data = text.encode()
    if algorithm == "md5":
        return hashlib.md5(data).hexdigest()
    elif algorithm == "sha1":
        return hashlib.sha1(data).hexdigest()
    elif algorithm == "sha256":
        return hashlib.sha256(data).hexdigest()
    elif algorithm == "sha512":
        return hashlib.sha512(data).hexdigest()
    return "Invalid hash algorithm."

def password_strength(password):
    score = 0
    remarks = []

    if len(password) >= 8:
        score += 1
    else:
        remarks.append("Use at least 8 characters")

    if any(c.islower() for c in password):
        score += 1
    else:
        remarks.append("Add lowercase letters")

    if any(c.isupper() for c in password):
        score += 1
    else:
        remarks.append("Add uppercase letters")

    if any(c.isdigit() for c in password):
        score += 1
    else:
        remarks.append("Add numbers")

    if any(c in string.punctuation for c in password):
        score += 1
    else:
        remarks.append("Add special symbols")

    if score <= 2:
        level = "Weak"
    elif score <= 4:
        level = "Medium"
    else:
        level = "Strong"

    return level, score * 20, remarks

def generate_password(length=14):
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(chars) for _ in range(length))

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    operation = ""
    strength = None
    recommendations = []

    if request.method == "POST":
        operation = request.form.get("operation", "")
        text = request.form.get("text", "")
        key = request.form.get("key", "")
        shift = int(request.form.get("shift", "3") or 3)
        hash_algorithm = request.form.get("hash_algorithm", "sha256")

        if operation == "caesar_encrypt":
            result = caesar_encrypt(text, shift)
        elif operation == "caesar_decrypt":
            result = caesar_decrypt(text, shift)
        elif operation == "vigenere_encrypt":
            result = vigenere_encrypt(text, key)
        elif operation == "vigenere_decrypt":
            result = vigenere_decrypt(text, key)
        elif operation == "xor_encrypt":
            result = xor_encrypt_decrypt(text, key)
        elif operation == "xor_decrypt":
            result = xor_decrypt(text, key)
        elif operation == "base64_encode":
            result = base64_encode(text)
        elif operation == "base64_decode":
            result = base64_decode(text)
        elif operation == "hash":
            result = hash_text(text, hash_algorithm)
        elif operation == "password_strength":
            level, score, remarks = password_strength(text)
            strength = {"level": level, "score": score}
            recommendations = remarks
            result = f"Password Strength: {level} ({score}/100)"
        elif operation == "generate_password":
            result = generate_password()

    return render_template("index.html", result=result, operation=operation, strength=strength, recommendations=recommendations)

@app.route("/file-hash", methods=["POST"])
def file_hash():
    uploaded_file = request.files.get("file")
    algorithm = request.form.get("file_hash_algorithm", "sha256")

    if not uploaded_file:
        return render_template("index.html", result="No file uploaded.", operation="file_hash")

    file_data = uploaded_file.read()
    if algorithm == "md5":
        result = hashlib.md5(file_data).hexdigest()
    elif algorithm == "sha1":
        result = hashlib.sha1(file_data).hexdigest()
    elif algorithm == "sha256":
        result = hashlib.sha256(file_data).hexdigest()
    else:
        result = hashlib.sha512(file_data).hexdigest()

    result = f"{algorithm.upper()} hash of {uploaded_file.filename}: {result}"
    return render_template("index.html", result=result, operation="file_hash")

@app.route("/download-report")
def download_report():
    path = os.path.join(REPORT_FOLDER, "cryptography_project_report.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write("CRYPTOGRAPHY IMPLEMENTATION PROJECT REPORT\n")
        f.write("=" * 50 + "\n")
        f.write(f"Generated on: {datetime.now()}\n\n")
        f.write("Project Title: Cryptography Algorithms Implementation\n\n")
        f.write("Objective:\n")
        f.write("To implement encryption, decryption, hashing, password strength checking, and file hash verification using Python and Flask.\n\n")
        f.write("Algorithms Implemented:\n")
        f.write("1. Caesar Cipher\n2. Vigenere Cipher\n3. XOR Encryption\n4. Base64 Encoding/Decoding\n5. MD5, SHA1, SHA256, SHA512 Hashing\n6. Password Strength Analyzer\n7. File Hash Generator\n\n")
        f.write("Applications:\n")
        f.write("- Secure communication\n- Data integrity verification\n- Password security awareness\n- Cybersecurity learning\n\n")
        f.write("Conclusion:\n")
        f.write("This project demonstrates core cryptography concepts in a practical and user-friendly web application.\n")
    return send_file(path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
