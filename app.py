from flask import Flask, render_template, request, redirect, url_for
import matplotlib.pyplot as plt
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scan', methods=['GET', 'POST'])
def scan():
    
    if request.method == 'GET':
        return redirect(url_for('home'))

    url = request.form.get('url')

    if not url:
        return redirect(url_for('home')) 

    if not url.startswith("http"):
        url = "https://" + url

    try:
        response = requests.get(url)
        headers = response.headers
    except Exception as e:
        return f"Error while accessing website: {e}"

    score = 100
    issues = []

    if not url.startswith("https"):
        score -= 20
        issues.append("HTTPS not used")
    if 'X-Frame-Options' not in headers:
        score -= 15
        issues.append("X-Frame-Options missing")
    if 'X-XSS-Protection' not in headers:
        score -= 15
        issues.append("X-XSS-Protection missing")
    if 'Strict-Transport-Security' not in headers:
        score -= 10
        issues.append("Strict-Transport-Security missing")
    if 'Set-Cookie' in headers and "Secure" not in headers['Set-Cookie']:
        score -= 20
        issues.append("Cookies not marked Secure")

    if score >= 90:
        grade = "A"
    elif score >= 70:
        grade = "B"
    elif score >= 50:
        grade = "C"
    else:
        grade = "D"

    secure_part = score
    vulnerable_part = 100 - score

    plt.figure(figsize=(4, 4))
    plt.style.use('dark_background')
    plt.pie([secure_part, vulnerable_part],
            labels=['Secure', 'Vulnerable'],
            autopct='%1.1f%%',
            startangle=90)
    plt.title("Website Security Score")
    plt.tight_layout()
    plt.savefig('static/chart.png') 
    plt.close()

    return render_template('result.html',
                           url=url,
                           score=score,
                           grade=grade,
                           issues=issues,
                           chart='static/chart.png')

if __name__ == "__main__":
    app.run(debug=True)
