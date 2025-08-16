import logging
from flask import Flask, request, make_response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator
import requests
import os
import secrets

app = Flask(__name__)

# === LOG ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# === CONFIGURAÇÕES ===
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
WHATSAPP_NUMERO = os.getenv("WHATSAPP_NUMERO", "551199887766")

# Validador Twilio
validator = RequestValidator(TWILIO_AUTH_TOKEN)

# === PALAVRAS JURÍDICAS ===
PALAVRAS_JURIDICAS = {
    "Família": ["divórcio", "guarda", "alimentos", "casamento", "união estável", "pensão"],
    "Trabalhista": ["demitido", "justa causa", "horas extras", "fgts", "reclamação", "verbas rescisórias"],
    "Previdenciário": ["aposentadoria", "inss", "auxílio-doença", "bpc", "loas", "invalidez"],
    "Consumidor": ["golpe", "pix", "cobrança", "procon", "juros abusivos", "produto com defeito"],
    "Geral": ["lei", "direito", "advogado", "justiça", "tribunal"]
}

def detectar_area(pergunta):
    p = pergunta.lower()
    melhor = "Jurídico Geral"
    max_count = 0
    for area, palavras in PALAVRAS_JURIDICAS.items():
        count = sum(1 for palavra in palavras if palavra in p)
        if count > max_count:
            max_count = count
            melhor = area
    return melhor

# === CHAMADA À GROQ ===
def perguntar(pergunta):
    if not GROQ_API_KEY:
        return "Estou com problemas técnicos. Um advogado entrará em contato."

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": f"""
Você é o Dr. Legal, um advogado virtual empático.
Responda com até 2 frases, em linguagem simples.
NUNCA diga 'será analisado por um advogado'.
Seja direto, humano e termine com uma chamada para ação.
Pergunta: {pergunta}
Resposta:
        """.strip()}],
        "temperature": 0.7,
        "max_tokens": 200
    }

    try:
        resp = requests.post("https://api.groq.com/openai/v1/chat/completions", json=data, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.error(f"Erro Groq: {e}")
        return "Sua situação é importante. Vamos te encaminhar para um especialista."

# === WEBHOOK TWILIO ===
@app.route("/twilio", methods=["POST"])
def twilio_webhook():
    signature = request.headers.get("X-Twilio-Signature", "")
    url = request.url
    params = request.form.to_dict()

    # Valida autenticidade
    if not validator.validate(url, params, signature):
        return "Não autorizado", 403

    incoming_msg = request.form.get("Body", "").strip()
    sender = request.form.get("From")  # whatsapp:+5511999999999

    # Respostas rápidas
    if incoming_msg.lower() in ["oi", "olá", "ola"]:
        resposta = (
            "Olá! Sou o *Dr. Legal*, seu assistente jurídico virtual. 😊\n\n"
            "Posso te ajudar com:\n"
            "• Divórcio, guarda, pensão\n"
            "• Demissão, FGTS, horas extras\n"
            "• Golpes no PIX, cobranças indevidas\n"
            "• Aposentadoria, auxílio-doença\n\n"
            "Me conta o que você precisa?"
        )
    elif incoming_msg.lower() in ["tchau", "obrigado"]:
        resposta = "Fico feliz em ter ajudado! Até breve! 👋"
    else:
        area = detectar_area(incoming_msg)
        ia_response = perguntar(incoming_msg)
        resposta = f"{ia_response}\n\n📌 *Área sugerida:* {area}"

    # Responde no WhatsApp
    resp = MessagingResponse()
    resp.message(resposta)
    return make_response(str(resp)), 200

# === ROTA WEB (opcional) ===
@app.route("/")
def home():
    return """
    <h1>💬 Dr. Legal - Assistente Jurídico</h1>
    <p>Webhook do WhatsApp ativo em <code>/twilio</code>.</p>
    <p>Envie <strong>join [palavra]</strong> para o número do Twilio.</p>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)