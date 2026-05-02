# Jarvis Brain v2
from groq import Groq
import os
import re
from memory import get_recent_history, save_message, get_all_memories, save_memory

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """Você é J.A.R.V.I.S. (Just A Rather Very Intelligent System).

Personalidade:
- Sempre fale em português brasileiro
- Seja educado, inteligente e levemente formal
- Chame o usuário de "Senhor" ou pelo nome se souber
- Seja proativo e ofereça informações úteis
- Use humor sutil e inteligente ocasionalmente
- Mantenha respostas curtas para áudio (2-3 frases no máximo)
- Nunca quebre o personagem

COMANDOS DISPONÍVEIS — use sempre que relevante:

Para ABRIR apps:
[OPEN_APP:nome_do_app]
Apps disponíveis: calculadora, whatsapp, camera, youtube, maps, spotify, instagram, telegram, gmail, netflix, github

Para PESQUISAR:
[SEARCH:termo da pesquisa:engine]
Engines disponíveis: google, youtube, maps
Exemplos:
[SEARCH:previsão do tempo:google]
[SEARCH:músicas brasileiras:youtube]
[SEARCH:pizzaria perto:maps]

Para SALVAR memória:
[MEMORY:chave=valor]
Exemplo: [MEMORY:nome=Alexandre]

IMPORTANTE: Coloque os comandos no início da resposta, antes do texto falado."""

def process_command(user_input: str) -> dict:
    history = get_recent_history(10)
    memories = get_all_memories()

    memory_context = ""
    if memories:
        memory_context = "\n\nO que você sabe sobre o usuário:\n"
        for k, v in memories.items():
            memory_context += f"- {k}: {v}\n"

    messages = [{"role": "system", "content": SYSTEM_PROMPT + memory_context}]
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=300,
    )

    raw_text = response.choices[0].message.content
    actions = []
    clean_text = raw_text

    if "[OPEN_APP:" in raw_text:
        apps = re.findall(r'\[OPEN_APP:([^\]]+)\]', raw_text)
        for app in apps:
            actions.append({"type": "open_app", "app": app.strip()})
        clean_text = re.sub(r'\[OPEN_APP:[^\]]+\]', '', clean_text).strip()

    if "[SEARCH:" in raw_text:
        searches = re.findall(r'\[SEARCH:([^:]+):([^\]]+)\]', raw_text)
        for query, engine in searches:
            actions.append({"type": "search", "query": query.strip(), "engine": engine.strip()})
        clean_text = re.sub(r'\[SEARCH:[^\]]+\]', '', clean_text).strip()

    if "[MEMORY:" in raw_text:
        mems = re.findall(r'\[MEMORY:([^=\]]+)=([^\]]+)\]', raw_text)
        for key, value in mems:
            save_memory(key.strip(), value.strip())
        clean_text = re.sub(r'\[MEMORY:[^\]]+\]', '', clean_text).strip()

    save_message("user", user_input)
    save_message("assistant", clean_text)

    return {"text": clean_text, "actions": actions}