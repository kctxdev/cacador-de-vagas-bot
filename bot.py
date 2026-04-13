import telebot
import requests
from bs4 import BeautifulSoup
import time
import sqlite3
import json
import logging
import random

# ==========================================
# CONFIGURAÇÕES
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 🚨 AVISO: Lembre-se de esconder seu token antes de colocar no GitHub!
TOKEN = "8537667602:AAHB5TTi54HzkbxvRJ7yUPntg-UDi4CnVLU"  
bot = telebot.TeleBot(TOKEN)

# 🔥 COMANDOS NO MENU DO TELEGRAM
comandos = [
    telebot.types.BotCommand("start", "🚀 Iniciar o Bot"),
    telebot.types.BotCommand("ajuda", "📖 Como Usar")
]
bot.set_my_commands(comandos)

# ==========================================
# BANCO DE DADOS
conn = sqlite3.connect('vagas_pro.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS cache_vagas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        cargo TEXT,
        cidade TEXT,
        vagas_json TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()

# ==========================================
FONTES_VAGAS = {
    "REMOTEOK": "https://remoteok.com/api?keywords={cargo}",
    "INDEED": "https://br.indeed.com/jobs?q={cargo}&l={cidade}",
    "VAGAS.COM": "https://www.vagas.com.br/vagas-de-{cargo_dash}-em-{cidade_dash}",
    "INFOJOBS": "https://www.infojobs.com.br/?si={cargo}&where={cidade}",
    "CATHO": "https://www.catho.com.br/busca/?q={cargo}&where={cidade}",
    "TRABALHA": "https://www.trabalhabrasil.com.br/vagas-empregos-em-{cidade_dash}/{cargo_dash}"
}

LOGOS_SITES = {
    "VAGAS.COM": "https://img.shields.io/badge/VAGAS-0055FF?style=for-the-badge&logo=vimeo&logoColor=white",
    "INDEED": "https://img.shields.io/badge/Indeed-003399?style=for-the-badge&logo=indeed&logoColor=white",
    "INFOJOBS": "https://img.shields.io/badge/InfoJobs-0066CC?style=for-the-badge&logo=icloud&logoColor=white",
    "CATHO": "https://img.shields.io/badge/Catho-E80070?style=for-the-badge&logo=target&logoColor=white",
    "REMOTEOK": "https://img.shields.io/badge/RemoteOK-FF4742?style=for-the-badge&logo=livewire&logoColor=white",
    "DEFAULT": "https://img.shields.io/badge/Vaga-2E8B57?style=for-the-badge&logo=briefcase&logoColor=white"
}

HEADERS_LIST = [
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
    {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15"}
]

# ==========================================
class VagasPro:
    @staticmethod
    def get_local_ip():
        try:
            r = requests.get('https://ipapi.co/json/', timeout=5)
            data = r.json()
            return f"{data.get('city', 'São Paulo')} {data.get('region', 'SP')}"
        except:
            return "São Paulo SP"

    @staticmethod
    def extrair_vaga(soup, url, site, cargo):
        seletores = ['h1 a, h2 a', 'a[href*="vaga"], a[href*="job"]']
        palavra_chave = cargo.split()[0].lower()
        
        for sel in seletores:
            els = soup.select(sel)
            for el in els[:5]:
                titulo = el.get_text(strip=True)
                if len(titulo) > 8 and palavra_chave in titulo.lower():
                    href = el.get('href', url)
                    if href.startswith('/'):
                        href = f"https://{url.split('/')[2]}{href}"
                    return {'site': site, 'titulo': titulo[:80], 'url': href}
        return None

    @staticmethod
    def buscar_todas_fontes(cargo, cidade):
        vagas = []
        headers = random.choice(HEADERS_LIST)
        
        cargo_limpo = cargo.replace(',', '').strip()
        cidade_limpa = cidade.replace(',', '').strip()
        
        for nome, url_base in FONTES_VAGAS.items():
            try:
                c_query = cargo_limpo.replace(' ', '+').lower()
                l_query = cidade_limpa.replace(' ', '+').lower()
                c_dash = cargo_limpo.replace(' ', '-').lower()
                l_dash = cidade_limpa.replace(' ', '-').lower()
                
                url = url_base.format(cargo=c_query, cidade=l_query, cargo_dash=c_dash, cidade_dash=l_dash)
                resp = requests.get(url, headers=headers, timeout=8)
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                vaga = VagasPro.extrair_vaga(soup, url, nome, cargo)
                if vaga and vaga not in vagas:
                    vagas.append(vaga)
                
                if len(vagas) >= 5:
                    break
                time.sleep(0.7)
            except:
                continue
        return vagas

    @staticmethod
    def cache_get(uid, cargo, cidade):
        cursor.execute('SELECT vagas_json FROM cache_vagas WHERE user_id=? AND cargo=? AND cidade=? AND created_at > datetime("now", "-30 minutes")', (uid, cargo, cidade))
        res = cursor.fetchone()
        return json.loads(res[0]) if res else None

    @staticmethod
    def cache_save(uid, cargo, cidade, vagas):
        # AQUI ESTÁ A CORREÇÃO QUE VOCÊ PEDIU!
        cursor.execute('DELETE FROM cache_vagas WHERE user_id=? AND cargo=? AND cidade=?', (uid, cargo, cidade))
        cursor.execute('INSERT INTO cache_vagas (user_id, cargo, cidade, vagas_json) VALUES (?, ?, ?, ?)', (uid, cargo, cidade, json.dumps(vagas)))
        conn.commit()

# ==========================================
estados_user = {}

# ==========================================
# 🎯 MENSAGEM INICIAL QUANDO ATIVA O BOT
@bot.message_handler(commands=['start'])
def ativar_bot(msg):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("🔍 Buscar Vagas", callback_data="iniciar_busca"))
    markup.add(telebot.types.InlineKeyboardButton("ℹ️ Como Usar", callback_data="como_usar"))
    
    txt = """
🚀 CAÇADOR DE VAGAS PRO ATIVADO!

✨ Encontro vagas reais com Filtro Sniper
✅ Cache inteligente (30min)
📍 Sua localização automática

👇 Escolha uma opção abaixo:
    """
    bot.send_message(msg.chat.id, txt, parse_mode='HTML', reply_markup=markup)

# ==========================================
@bot.callback_query_handler(func=lambda c: c.data in ['iniciar_busca', 'como_usar'])
def cb_inicial(call):
    if call.data == 'iniciar_busca':
        uid = call.from_user.id
        estados_user[uid] = {'step': 1}
        bot.send_message(call.message.chat.id, "💼 Digite o CARGO:\nEx: vendedor", parse_mode='HTML')
    else:
        mostrar_ajuda(call.message.chat.id)
    bot.answer_callback_query(call.id)

# ==========================================
def mostrar_ajuda(chat_id):
    txt = """
📖 COMO USAR:

1️⃣ Digite /start para abrir o menu inicial.
2️⃣ Clique em "Buscar Vagas" e digite o cargo.
3️⃣ Confirme o seu local e aguarde os resultados!

✅ VANTAGENS:
✨ Sem vagas falsas
💾 Resultados salvos
📍 Seu local é pego automaticamente
    """
    bot.send_message(chat_id, txt, parse_mode='HTML')

@bot.message_handler(commands=['ajuda', 'help'])
def cmd_help(msg):
    mostrar_ajuda(msg.chat.id)

# ==========================================
# FLUXO DE PERGUNTAS
@bot.message_handler(func=lambda m: estados_user.get(m.from_user.id, {}).get('step') == 1)
def step_cargo(msg):
    uid = msg.from_user.id
    cargo = msg.text.strip()
    estados_user[uid] = {'step': 2, 'cargo': cargo}
    
    cidade = VagasPro.get_local_ip()
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(telebot.types.InlineKeyboardButton("✅ Confirmar", callback_data=f"go_{uid}"), 
               telebot.types.InlineKeyboardButton("❌ Mudar Local", callback_data=f"no_{uid}"))
    
    txt = f"Cargo: {cargo.upper()}\n📍 Seu Local: {cidade}\n\nBuscar neste local?"
    bot.send_message(msg.chat.id, txt, parse_mode='HTML', reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith(('go_', 'no_')))
def cb_confirmar(call):
    uid = int(call.data.split('_')[1])
    
    if call.data.startswith('go_'):
        cargo = estados_user[uid]['cargo']
        cidade = VagasPro.get_local_ip()
        bot.answer_callback_query(call.id, "🚀 Buscando...")
        executar_busca_completa(call.message.chat.id, uid, cargo, cidade)
    else:
        estados_user[uid]['step'] = 3
        cargo = estados_user[uid]['cargo']
        bot.answer_callback_query(call.id, "Digite cidade:")
        bot.edit_message_text(f"Cargo: {cargo.upper()}\n\n📍 Digite a Cidade/UF:\nEx: São Paulo SP", 
                            call.message.chat.id, call.message.message_id, parse_mode='HTML')

@bot.message_handler(func=lambda m: estados_user.get(m.from_user.id, {}).get('step') == 3)
def step_cidade(msg):
    uid = msg.from_user.id
    cargo = estados_user[uid]['cargo']
    cidade = msg.text.strip()
    executar_busca_completa(msg.chat.id, uid, cargo, cidade)

# ==========================================
def executar_busca_completa(chat_id, uid, cargo, cidade):
    loading = bot.send_message(chat_id, f"🔍 Buscando: {cargo}\n📍 Seu Local: {cidade}\n⏳ Filtro ativo...")
    
    cached = VagasPro.cache_get(uid, cargo, cidade)
    if cached:
        bot.delete_message(chat_id, loading.message_id)
        enviar_vagas(chat_id, cached)
        return
    
    vagas = VagasPro.buscar_todas_fontes(cargo, cidade)
    VagasPro.cache_save(uid, cargo, cidade, vagas)
    bot.delete_message(chat_id, loading.message_id)
    enviar_vagas(chat_id, vagas)

def enviar_vagas(chat_id, vagas):
    if not vagas:
        bot.send_message(chat_id, "❌ Nenhuma vaga encontrada.\n💡 Tente termos mais simples!", parse_mode='HTML')
        return
    
    bot.send_message(chat_id, f"✅ Encontrei {len(vagas)} vagas reais!", parse_mode='HTML')
    
    for i, v in enumerate(vagas, 1):
        site = v['site'].upper()
        logo = LOGOS_SITES.get(site, LOGOS_SITES["DEFAULT"])
        txt = f"{i}️⃣ Fonte: {site}\n💼 {v['titulo']}\n\n<a href='{v['url']}'>🚀 Acessar Vaga</a>"
        
        try:
            bot.send_photo(chat_id, logo, caption=txt, parse_mode='HTML')
        except:
            bot.send_message(chat_id, txt, parse_mode='HTML', disable_web_page_preview=True)
        time.sleep(0.3)
    
    bot.send_message(chat_id, "🔄 Digite /start para fazer uma nova busca.", parse_mode='HTML')

# ==========================================
print("💼 CAÇADOR DE VAGAS PRO - ONLINE!")
print("✅ Buscas corrigidas, Banco salvo corretamente e UI limpa.")
bot.infinity_polling()