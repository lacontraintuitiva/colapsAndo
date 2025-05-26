from flask import Flask, render_template_string
import os

app = Flask(__name__)

@app.route('/test')
def test():
    site_key = os.environ.get('RECAPTCHA_SITE_KEY', 'NO_CONFIGURADO')
    secret_key = os.environ.get('RECAPTCHA_SECRET_KEY', 'NO_CONFIGURADO')
    
    return f"""
    <h1>Test de reCAPTCHA</h1>
    <p><strong>Site Key:</strong> {site_key[:20]}... (primeros 20 caracteres)</p>
    <p><strong>Secret Key:</strong> {secret_key[:20]}... (primeros 20 caracteres)</p>
    <p><strong>Site Key completa:</strong> {site_key}</p>
    """

if __name__ == '__main__':
    app.run(debug=True)