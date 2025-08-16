import logging
from flask import Flask, render_template, request, jsonify
import requests
import os
from requests.utils import quote as url_quote
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

app = Flask(__name__)

# === CONFIGURAÇÃO DE LOG ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# === CONFIGURAÇÕES DO WHATSAPP ===
WHATSAPP_NUMERO = os.getenv("WHATSAPP_NUMERO", "551199887766")
WHATSAPP_LINK = f"https://wa.me/{WHATSAPP_NUMERO}?text="

# === PALAVRAS-JURÍDICAS POR ÁREA (abrangente) ===
PALAVRAS_JURIDICAS = {
    "Direito de Família": ["divórcio", "guarda", "alimentos", "casamento", "união estável", "pensão", "pensão alimentícia", "filho", "criança", "separação", "herança familiar"],
    "Direito Trabalhista": ["demitido", "justa causa", "horas extras", "fgts", "reclamação", "trabalho", "emprego", "salário", "verbas rescisórias", "acordo", "empregador"],
    "Direito Previdenciário": ["aposentadoria", "inss", "auxílio-doença", "bpc", "loas", "seguro desemprego", "auxílio reclusão", "auxílio-acidente", "revisão", "benefício"],
    "Direito do Consumidor": ["golpe", "pix", "cobrança", "procon", "juros abusivos", "fraude", "compra", "estorno", "cancelamento", "devolução", "dívida"],
    "Indenização": ["acidente", "danos", "moral", "erro médico", "indenização", "compensação", "responsabilidade civil", "acidente de carro", "dano material"],
    "Direito Penal": ["boletim de ocorrência", "prisão", "flagrante", "advogado criminal", "delito", "crime", "penal", "liberdade", "habeas corpus"],
    "Direito Imobiliário": ["aluguel", "despejo", "fiador", "contrato", "imóvel", "aluguel", "inadimplência", "locatário", "proprietário"],
    "Direito Empresarial": ["empresa", "mei", "faturamento", "abrir empresa", "encerrar", "contrato social", "sócios", "dissolução", "sociedade"],
    "Direito Tributário": ["imposto", "ir", "irpf", "isenção", "declaração", "receita federal", "multa", "taxa"],
    "Direito Digital": ["deepfake", "cyberbullying", "vazamento", "dados", "internet", "rede social", "fake news", "crimes digitais"],
    "Geral": ["lei", "direito", "advogado", "justiça", "direitos", "processo", "ação", "juiz"]
}

# === FUNÇÕES DE DETECÇÃO ===
def eh_tema_juridico(pergunta: str) -> bool:
    p = pergunta.lower()
    return any(palavra in p for area in PALAVRAS_JURIDICAS.values() for palavra in area)

def detectar_area(pergunta: str) -> str:
    p = pergunta.lower()
    melhor_area = "Jurídico Geral"
    max_count = 0
    for area, palavras in PALAVRAS_JURIDICAS.items():
        count = sum(1 for palavra in palavras if palavra in p)
        if count > max_count:
            max_count = count
            melhor_area = area
    return melhor_area

# === BOTÃO WHATSAPP ===
def botao_whatsapp(texto: str, mensagem: str) -> str:
    msg = url_quote(mensagem)
    return f'<a href="{WHATSAPP_LINK}{msg}" style="background:#1a3a6e; color:white; padding:12px 18px; border-radius:8px; text-decoration:none; font-weight:bold; display:inline-block; margin-top:10px;">📞 {texto}</a>'

# === CHAMADA À GROQ (LLAMA 3) – COM PROMPT HUMANIZADO ===
def perguntar(pergunta: str) -> dict | None:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        logger.error("GROQ_API_KEY não configurada")
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Prompt humanizado, empático e direto
    prompt = f"""
Você é o Dr. Legal, um advogado virtual empático e direto.
Responda com no máximo 2 frases, em linguagem simples, como se estivesse falando com alguém em dificuldade.
NUNCA diga "será analisado por um advogado".
Sempre termine com uma chamada para ação que gere urgência e confiança.
Use palavras como: "você tem direito", "não está sozinho", "podemos te ajudar", "é possível reverter".
Pergunta: {pergunta}
Resposta:
    """.strip()

    data = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.8,
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
    data = request.json or {}
    pergunta = data.get("pergunta", "").strip()

    if not pergunta:
        return jsonify({
            "resposta": (
                "Olá! Aqui é o <b>Dr. Legal</b> 🌟<br><br>"
                "Seu direito é importante — e eu estou aqui para te ajudar.<br><br>"
                "Posso te orientar sobre:<br>⚖️ Família | 💼 Trabalho | 🛡️ Consumidor | 🏥 Previdência | ⚖️ Penal | 🏠 Imobiliário<br><br>"
                f"{botao_whatsapp('💬 Falar com um advogado agora', 'Tenho uma dúvida jurídica urgente.')}"
            )
        })

    p = pergunta.lower()

    # Saudações
    if any(w in p for w in ["oi", "olá", "bom dia", "boa tarde"]):
        return jsonify({
            "resposta": (
                "Olá! Aqui é o <b>Dr. Legal</b>, seu assistente jurídico. 😊<br><br>"
                "Estou aqui para te ajudar com:<br>"
                "🔹 Divórcio, guarda, pensão<br>"
                "🔹 Demissão, FGTS, horas extras<br>"
                "🔹 Golpes no PIX, cobranças indevidas<br>"
                "🔹 Aposentadoria, auxílio-doença, BPC<br>"
                "🔹 Acidentes, erros médicos, indenizações<br><br>"
                "Me conta o que você precisa?<br><br>"
                f"{botao_whatsapp('📞 Falar com especialista agora', 'Quero falar com um advogado agora.')}"
            )
        })

    # Despedidas
    if any(w in p for w in ["tchau", "obrigado", "valeu"]):
        return jsonify({"resposta": "Fico feliz em ter ajudado! Conte com o Dr. Legal sempre que precisar. Até breve! 👋"})

    # Temas comuns (respostas rápidas)
    temas = {
        "divórcio": "Temos especialistas em divórcio rápido, consensual ou litigioso.",
        "trabalho": "Podemos te ajudar com direitos trabalhistas e verbas rescisórias.",
        "pix": "Errou no PIX? Temos ações para tentar recuperar seu dinheiro.",
        "acidente": "Se foi vítima de acidente, você pode ter direito a indenização.",
        "inss": "Problema com aposentadoria ou auxílio? Podemos revisar seu caso."
    }
    for tema, desc in temas.items():
        if tema in p:
            esp = detectar_area(pergunta)
            return jsonify({
                "resposta": f"{desc}<br><br>📌 <b>{esp}</b><br>{botao_whatsapp(f'📞 Falar com {esp}', f'Quero falar sobre {tema}.')}"
            })

    # Usar IA se for tema jurídico
    if eh_tema_juridico(pergunta):
        logger.info(f"Processando pergunta jurídica com IA: {pergunta}")
        resultado = perguntar(pergunta)
        if resultado:
            esp = resultado["especialidade"]
            return jsonify({
                "resposta": f"{resultado['resposta']}<br><br>📌 <b>{esp}</b><br>{botao_whatsapp(f'📩 Falar com especialista em {esp}', f'Preciso de ajuda com um caso de {esp}.')}"
            })
        else:
            logger.warning("IA falhou. Usando fallback.")
            esp = detectar_area(pergunta)
            return jsonify({
                "resposta": f"Isso é sério, e você não precisa enfrentar sozinho.<br><br>Vamos te encaminhar para um <b>especialista em {esp}</b>.<br><br>{botao_whatsapp('📩 Falar com um advogado agora', f'Preciso de ajuda com: {pergunta[:100]}...')}"
            })

    # Não jurídico
    return jsonify({
        "resposta": (
            "Isso é importante para a vida, mas meu foco é te ajudar com direitos.<br><br>"
            "Como:<br>⚖️ Família | 💼 Trabalho | 🛡️ Consumidor | 🏥 Previdência | ⚖️ Penal | 🏠 Imobiliário<br><br>"
            f"{botao_whatsapp('✅ Falar sobre meu caso', 'Quero falar sobre um problema jurídico.')}"
        )
    })

# === INICIAR ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)