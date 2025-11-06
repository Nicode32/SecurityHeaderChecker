from flask import Flask, render_template, request, redirect, url_for
import matplotlib
matplotlib.use('Agg')  # For Render (no GUI backend)
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

    # ---------------- SECURITY HEADER CHECKING ----------------
    security_headers = {
        "HTTPS": url.startswith("https"),
        "Content-Security-Policy": "Content-Security-Policy" in headers,
        "X-Frame-Options": "X-Frame-Options" in headers,
        "X-XSS-Protection": "X-XSS-Protection" in headers,
        "Strict-Transport-Security": "Strict-Transport-Security" in headers,
        "Secure Cookies": 'Set-Cookie' in headers and "Secure" in headers.get('Set-Cookie', '')
    }

    score = 100
    for header, present in security_headers.items():
        if not present:
            if header == "HTTPS":
                score -= 20
            elif header == "Content-Security-Policy":
                score -= 20
            elif header == "X-Frame-Options":
                score -= 15
            elif header == "X-XSS-Protection":
                score -= 15
            elif header == "Strict-Transport-Security":
                score -= 10
            elif header == "Secure Cookies":
                score -= 20

    if score >= 90:
        grade = "A"
    elif score >= 70:
        grade = "B"
    elif score >= 50:
        grade = "C"
    else:
        grade = "D"

    # Generate header status for HTML
    header_status = [(name, "Present" if present else "Missing") for name, present in security_headers.items()]

    # ---------------- MATPLOTLIB PIE CHART ----------------
    secure_part = score
    vulnerable_part = 100 - score

    plt.figure(figsize=(4, 4))
    plt.style.use('dark_background')
    plt.pie(
        [secure_part, vulnerable_part],
        labels=['Secure', 'Vulnerable'],
        autopct='%1.1f%%',
        startangle=90
    )
    plt.title("Website Security Score")
    plt.tight_layout()
    plt.savefig('static/chart.png', dpi=100)
    plt.close()

    return render_template('result.html',
                           score=score,
                           grade=grade,
                           header_status=header_status)

if __name__ == "__main__":
    app.run(debug=True)
