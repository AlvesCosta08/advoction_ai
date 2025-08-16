import logging
from flask import Flask, render_template, request, jsonify
import requests
import os
from requests.utils import quote as url_quote
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# === LOG ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# === WHATSAPP ===
WHATSAPP_NUMERO = os.getenv("WHATSAPP_NUMERO", "551199887766")
WHATSAPP_LINK = f"https://wa.me/{WHATSAPP_NUMERO}?text="

# === PALAVRAS JURÍDICAS ===
PALAVRAS_JURIDICAS = {
    "Direito de Família": ["divórcio", "guarda", "alimentos", "casamento", "adoção"],
    "Direito Trabalhista": ["demitido", "justa causa", "horas extras", "fgts", "reclamação"],
    "Direito Previdenciário": ["aposentadoria", "inss", "auxílio-doença", "bpc", "loas"],
    "Direito do Consumidor": ["golpe", "pix", "cobrança", "procon", "juros abusivos"],
    "Indenização": ["acidente", "danos", "moral", "erro médico"],
    "Geral": ["lei", "direito", "advogado", "justiça"]
}

def eh_tema_juridico(pergunta):
    p = pergunta.lower()
    return any(palavra in p for area in PALAVRAS_JURIDICAS.values() for palavra in area)

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

def botao_whatsapp(texto, mensagem):
    msg = url_quote(mensagem)
    return f'<a href="{WHATSAPP_LINK}{msg}" style="background:#1a3a6e; color:white; padding:12px 18px; border-radius:8px; text-decoration:none; font-weight:bold; display:inline-block; margin-top:10px;">📞 {texto}</a>'

def perguntar(pergunta):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": f"""
Você é o Dr. Legal, um advogado virtual empático.
Responda com até 2 frases, em linguagem simples.
NUNCA diga 'será analisado'.
Termine com uma chamada para ação.
Pergunta: {pergunta}
Resposta:
        """.strip()}],
        "temperature": 0.7,
        "max_tokens": 200
    }

    try:
        resp = requests.post("https://api.groq.com/openai/v1/chat/completions", json=data, headers=headers, timeout=30)
        resp.raise_for_status()
        resposta = resp.json()["choices"][0]["message"]["content"].strip()
        especialidade = detectar_area(pergunta)
        return {"resposta": resposta, "especialidade": especialidade}
    except Exception as e:
        logger.error(f"Erro na API Groq: {e}")
        return None

# === ROTAS ===
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    pergunta = (request.json or {}).get("pergunta", "").strip()
    if not pergunta:
        return jsonify({"resposta": f"Olá! Sou o <b>Dr. Legal</b> 🌟<br><br>Posso te ajudar com:<br>⚖️ Família | 💼 Trabalho | 🛡️ Consumidor<br><br>{botao_whatsapp('💬 Falar com advogado', 'Tenho uma dúvida jurídica.')}"})

    p = pergunta.lower()

    if any(w in p for w in ["oi", "olá", "bom dia"]):
        return jsonify({"resposta": f"Olá! Como posso te ajudar? 😊<br><br>{botao_whatsapp('📞 Falar agora', 'Quero falar com um advogado.')}"})

    if any(w in p for w in ["tchau", "obrigado"]):
        return jsonify({"resposta": "Até logo! Conte com o Dr. Legal!"})

    temas = {
        "divórcio": "Temos especialistas em divórcio rápido.",
        "trabalho": "Podemos te ajudar com direitos trabalhistas.",
        "pix": "Errou no PIX? Temos ações para recuperar."
    }
    for tema, desc in temas.items():
        if tema in p:
            esp = detectar_area(pergunta)
            return jsonify({"resposta": f"{desc}<br><br>📌 <b>{esp}</b><br>{botao_whatsapp(f'📞 Falar com {esp}', f'Quero falar sobre {tema}.')}"})

    if eh_tema_juridico(pergunta):
        resultado = perguntar(pergunta)
        if resultado:
            esp = resultado["especialidade"]
            return jsonify({"resposta": f"{resultado['resposta']}<br><br>📌 <b>{esp}</b><br>{botao_whatsapp(f'📞 Falar com {esp}', f'Preciso de ajuda com {esp}.')}"})
        else:
            esp = detectar_area(pergunta)
            return jsonify({"resposta": f"Vamos te encaminhar para um especialista em {esp}.<br>{botao_whatsapp('✅ Enviar caso', pergunta[:100])}"})

    return jsonify({"resposta": f"Isso é importante, mas meu foco é direito.<br><br>{botao_whatsapp('✅ Falar sobre direitos', 'Quero falar sobre um problema jurídico.')}"})

# === INICIAR ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)