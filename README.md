📄 Dr. Legal & Advogados – Assistente Jurídico Virtual
Chatbot jurídico com IA local, triagem inteligente e conversão via WhatsApp.
Desenvolvido com Flask, Ollama e Docker para privacidade, desempenho e conversão. 

🚀 Visão Geral
Sistema de atendimento jurídico automatizado que:

Entende dúvidas em linguagem natural.
Detecta áreas como Família, Trabalhista, Previdenciário, etc.
Responde com empatia e clareza.
Direciona o usuário para um advogado real via WhatsApp com CTAs personalizados.
✅ Toda a IA roda localmente com Ollama
✅ Sem coleta de dados – ideal para LGPD
✅ Chatbot integrado ao site institucional


🔧 Arquitetura
Dois serviços em Docker:

ollama
IA local com modelo
tinyllama:1.1b
web
Backend Flask + Frontend responsivo


´´
projeto/
├── ollama-container/
│   ├── Dockerfile
│   └── start.sh
├── web-container/
│   ├── Dockerfile
│   ├── app.py
│   ├── requirements.txt
│   └── templates/index.html
├── docker-compose.yml
└── README.md

⚙️ Como Funciona
1. IA Local (Ollama)
Modelo: tinyllama:1.1b
Inicia com ollama serve
Expõe API em http://localhost:11434
Persiste modelos com volume Docker
2. Backend (Flask)
Detecta temas jurídicos por palavras-chave.
Classifica área do direito.
Consulta IA local e gera respostas humanizadas.
Sempre termina com botão do WhatsApp.
3. Frontend (index.html)
Design moderno com Bootstrap 5.
Chatbot fixo no canto inferior direito.
Interface limpa, responsiva e com animação de pulsação.
🐳 Como Executar
Clone o repositório
Execute:

docker-compose up --build

Acesse:
Site: http://localhost:5000
API da IA: http://localhost:11434

💡 Conversão Garantida
O sistema nunca falha:

Se a IA não responder, o usuário é redirecionado ao WhatsApp.
CTAs personalizados por área aumentam conversão.
Primeira consulta gratuita como gatilho.
🛡️ Privacidade
Nenhum dado do usuário é armazenado.
IA roda
100% local.
Sem cookies ou rastreamento.
Dr. Legal & Advogados – Justiça Acessível, com Tecnologia. ⚖️💙 # advoction_ai
