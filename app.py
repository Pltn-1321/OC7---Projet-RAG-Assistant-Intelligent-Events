"""Chatbot Streamlit - Assistant Événements RAG."""

import streamlit as st
from pathlib import Path

from src.rag.engine import RAGEngine
from src.config.constants import PROCESSED_DATA_DIR

MAX_HISTORY = 5  # Nombre d'échanges en mémoire


# Configuration moderne de la page
st.set_page_config(
    page_title="Assistant Événements",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Thème personnalisé
st.markdown(
    """
    <style>
    /* Couleurs et thèmes */
    :root {
        --primary: #6366f1;
        --primary-light: #818cf8;
        --secondary: #8b5cf6;
        --accent: #f472b6;
        --bg-dark: #0f172a;
        --bg-card: #1e293b;
        --bg-lighter: #334155;
        --text-primary: #f8fafc;
        --text-secondary: #94a3b8;
        --gradient-1: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
        --gradient-2: linear-gradient(135deg, #f472b6 0%, #ec4899 50%, #db2777 100%);
    }
    
    /* Style global */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        min-height: 100vh;
    }
    
    /* Titre principal avec gradient */
    h1 {
        background: var(--gradient-1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3.5rem !important;
        font-weight: 800 !important;
        text-align: center;
        margin-bottom: 0.5rem !important;
        animation: fadeInDown 1s ease;
    }
    
    /* Sous-titre */
    .subtitle {
        text-align: center;
        color: var(--text-secondary);
        font-size: 1.2rem;
        margin-bottom: 2rem;
        animation: fadeInUp 1s ease;
    }
    
    /* Sidebar moderne */
    .css-1d391kg {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        padding: 2rem;
    }
    
    /* Cartes et conteneurs */
    .card {
        background: var(--bg-card);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 
                    0 2px 4px -2px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    
    /* Messages de chat */
    .stChatMessage {
        padding: 1.5rem 2rem;
        border-radius: 20px;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(10px);
        animation: slideIn 0.3s ease;
    }
    
    .stChatMessage[data-testid="user-message"] {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
    }
    
    .stChatMessage[data-testid="assistant-message"] {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(51, 65, 85, 0.9) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Boutons */
    .stButton > button {
        background: var(--gradient-1) !important;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        color: white !important;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6);
    }
    
    /* Slider personnalisé */
    .stSlider > label {
        color: var(--text-primary) !important;
        font-weight: 600;
    }
    
    /* Input de chat */
    .stChatInputContainer {
        padding: 1.5rem;
        background: var(--bg-card);
        border-radius: 20px;
        box-shadow: 0 -4px 6px -1px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .stChatInput > div > div > input {
        background: var(--bg-lighter);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: var(--text-primary);
        font-size: 1rem;
    }
    
    /* Expander sources */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(244, 114, 182, 0.1) 0%, rgba(236, 72, 153, 0.1) 100%);
        border-radius: 12px;
        border: 1px solid rgba(244, 114, 182, 0.3);
    }
    
    /* Animations */
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.5;
        }
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: var(--text-secondary);
        font-size: 0.9rem;
    }
    
    /* Badge statistiques */
    .stats-badge {
        display: inline-block;
        background: var(--gradient-2);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        box-shadow: 0 4px 15px rgba(244, 114, 182, 0.4);
    }
    
    /* Masquer les éléments par défaut de Streamlit */
    #MainMenu, footer {
        visibility: hidden;
    }
    
    header {
        visibility: visible;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Header avec gradient
st.markdown(
    """
    <div style="text-align: center; margin: 2rem 0;">
        <h1>🎭 Assistant Événements</h1>
        <p class="subtitle">Découvrez les meilleurs événements culturels près de chez vous</p>
    </div>
""",
    unsafe_allow_html=True,
)


@st.cache_resource
def load_rag():
    return RAGEngine()


# Vérifier que l'index existe
if not Path(PROCESSED_DATA_DIR / "faiss_index/events.index").exists():
    st.error("❌ Index FAISS manquant. Exécutez d'abord les notebooks.")
    st.stop()

# Charger le RAG
try:
    rag = load_rag()
except Exception as e:
    st.error(f"❌ Erreur: {e}")
    st.stop()

# Initialiser l'historique de session
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Message de bienvenue stylisé
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": """
### 👋 Bienvenue !

Je suis ton assistant événements culturels ! Je peux t'aider à trouver :
- 🎵 Concerts et festivals
- 🎭 Expositions et théâtre
- 📚 Conférences et ateliers
- 🎪 Événements familiaux

**Pose-moi n'importe quelle question** sur les événements culturels et je te donnerai les meilleures recommandations basées sur tes intérêts !

*Exemple :* *"Quels concerts de jazz sont prévus à Marseille ce week-end ?"*
""",
        }
    )

# Sidebar moderne
with st.sidebar:
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 2rem;">
            <h2 style="color: #f8fafc; font-size: 1.8rem; margin-bottom: 0.5rem;">⚙️ Options</h2>
        </div>
    """,
        unsafe_allow_html=True,
    )

    with st.container():
        st.markdown(
            """
            <div class="card">
                <h3 style="color: #f8fafc; margin-bottom: 1rem;">📊 Paramètres</h3>
            """,
            unsafe_allow_html=True,
        )

        top_k = st.slider(
            "Nombre de résultats",
            min_value=1,
            max_value=10,
            value=5,
            help="Nombre d'événements à afficher",
        )

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Bouton Nouvelle conversation stylisé
    if st.button("🗑️ Nouvelle conversation", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": """
### 🎉 Conversation réinitialisée !

C'est reparti à zéro ! Qu'est-ce qui te ferait plaisir aujourd'hui ?

*N'hésite pas à me poser des questions sur :*
- 📍 Les événements dans ta ville
- 📅 Ce qui se passe ce week-end
- 🎭 Un type d'événement spécifique
""",
            }
        ]
        st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Statistiques stylisées
    st.markdown(
        """
        <div class="card" style="text-align: center;">
            <h3 style="color: #f8fafc; margin-bottom: 1rem;">📈 Statistiques</h3>
            <div class="stats-badge" style="margin: 0.5rem;">
                📚 <strong>{:,}</strong> événements indexés
            </div>
            <br><br>
            <p style="color: #94a3b8; font-size: 0.9rem;">
                🚀 Propulsé par RAG & IA
            </p>
        </div>
    """.format(rag.num_documents),
        unsafe_allow_html=True,
    )

# Container principal pour les messages
st.markdown(
    """
    <div class="card" style="margin-bottom: 2rem;">
        <h3 style="color: #f8fafc; margin-bottom: 1rem;">💬 Conversation</h3>
    """,
    unsafe_allow_html=True,
)

# Afficher l'historique des messages
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🎭"):
        st.markdown(message["content"])

st.markdown("</div>", unsafe_allow_html=True)

# Zone de saisie
if prompt := st.chat_input("💬 Posez votre question sur les événements..."):
    # Ajouter le message user
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Préparer l'historique pour le RAG (sans le message de bienvenue)
    history = []
    for msg in st.session_state.messages[1:-1]:  # Exclure bienvenue et dernier message
        history.append({"role": msg["role"], "content": msg["content"]})

    # Limiter l'historique
    if len(history) > MAX_HISTORY * 2:
        history = history[-(MAX_HISTORY * 2) :]

    # Générer la réponse
    with st.chat_message("assistant", avatar="🎭"):
        with st.spinner("💭 Réflexion..."):
            result = rag.chat(prompt, top_k=top_k, history=history)

        st.markdown(result["response"])

        # Afficher les sources si RAG utilisé
        if result.get("used_rag") and result["sources"]:
            with st.expander(f"📍 Sources ({len(result['sources'])} événements trouvés)"):
                for i, src in enumerate(result["sources"][:3], 1):
                    doc = src["document"]
                    meta = doc["metadata"]

                    url = meta.get("url")
                    if url:
                        link_html = f'<p style="margin: 0.5rem 0;"><a href="{url}" target="_blank" style="color: #6366f1; text-decoration: none; font-weight: 600;">🔗 Voir l\'événement →</a></p>'
                    else:
                        link_html = ""

                    st.markdown(
                        f"""
                        <div style="background: rgba(30, 41, 59, 0.8); 
                                    padding: 1rem; 
                                    border-radius: 12px; 
                                    margin: 1rem 0;
                                    border: 1px solid rgba(255, 255, 255, 0.1);">
                            <h4 style="color: #818cf8; margin: 0 0 0.5rem 0;">
                                {i}. {doc["title"]}
                            </h4>
                            <p style="color: #f472b6; font-size: 0.9rem; margin: 0.5rem 0;">
                                Score de pertinence: <strong>{src["similarity"]:.1%}</strong>
                            </p>
                            <p style="color: #94a3b8; font-size: 0.85rem; margin: 0.25rem 0;">
                                📍 {meta.get("city", "?")} | 📅 {meta.get("start_date", "?")[:10]}
                            </p>
                            {link_html}
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )

    # Sauvegarder la réponse
    st.session_state.messages.append({"role": "assistant", "content": result["response"]})

# Footer moderne
st.markdown(
    """
    <div class="footer">
        <p>💜 Créé avec ❤️ | RAG Assistant Événements Culturels</p>
        <p style="font-size: 0.8rem; margin-top: 0.5rem;">
            Technologies : Streamlit • FAISS • Mistral AI
        </p>
    </div>
""",
    unsafe_allow_html=True,
)
