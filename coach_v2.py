import os
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

st.set_page_config(page_title="Coach sportif IA", page_icon="🏋️")


# ============================================================
# LE MODÈLE ET LES CHAÎNES
# ============================================================
llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
    model="gpt-4o-mini",
    temperature=0.5,
   # extra_body={"thinking": {"type": "disabled"}},
)

# Chaîne 1 : le coach crée le programme
prompt_coach = ChatPromptTemplate.from_template(
    """Tu es un coach sportif bienveillant et motivant.
Crée un programme d'entraînement pour une semaine, adapté à cette personne :
- Prénom : {prenom}
- Âge : {age} ans
- Niveau : {niveau}
- Objectif : {objectif}
- Séances par semaine : {jours}
- Durée d'une séance : {duree} minutes
- Matériel disponible : {materiel}
- Blessures ou limitations : {limitations}

Chaque séance commence par un échauffement et se termine par des étirements."""
)
chaine_coach = prompt_coach | llm | StrOutputParser()

# Chaîne 2 : le kinésiologue vérifie le programme (deuxième avis)
prompt_kine = ChatPromptTemplate.from_template(
    """Tu es un kinésiologue expérimenté. Un coach a créé ce programme pour une personne
de {age} ans, de niveau {niveau}, avec ces limitations : {limitations}.

PROGRAMME DU COACH :
{programme}

Donne ton deuxième avis, en 3 parties courtes (3 phrases maximum par partie) :
1. Points forts du programme
2. Risques ou points à surveiller (surcharge, manque de repos, blessures)
3. Ta note de sécurité sur 10, avec une phrase d'explication"""
)
chaine_kine = prompt_kine | llm | StrOutputParser()


# ============================================================
# LES FONCTIONS
# ============================================================
def afficher_entete():
    """Affiche le titre et le message de bienvenue."""
    st.markdown("""
        <div style="text-align: center; margin: 2rem 0;">
            <h1 style="font-size: 3.5rem; font-weight: bold; background: linear-gradient(45deg, #FF6B35, #FFD700); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                <span style="-webkit-text-fill-color: initial;">🏋️</span> Coach sportif IA
            </h1>
            <p style="color: #b0b0b0; font-size: 1.2rem; margin-top: -0.5rem;">
                Un programme fait sur mesure pour toi
            </p>
            <div style="background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); padding: 1rem; border-radius: 15px; margin: 1rem 0; border: 1px solid rgba(255, 255, 255, 0.1);">
                <p style="color: #d0d0d0; margin: 0; font-size: 1.1rem;">
                    👋 <strong style="color: #FF6B35;">Bienvenue !</strong> Je suis ton coach sportif personnel propulsé par l'IA.
                    Remplis le formulaire ci-dessous, et je te prépare un programme d'entraînement sur mesure.
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.caption("⚠️ Programme généré par une IA, à titre indicatif : il ne remplace pas l'avis d'un professionnel de la santé.")


def afficher_formulaire():
    """Affiche le formulaire et renvoie le profil de l'utilisateur (un dictionnaire)."""
    profil = {
        "prenom": st.text_input("Ton prénom :"),
        "age": st.number_input("Ton âge :", min_value=16, max_value=90, value=30),
        "niveau": st.selectbox("Ton niveau :", ["Débutant", "Intermédiaire", "Avancé"]),
        "objectif": st.selectbox("Ton objectif :", ["Perdre du poids", "Prendre du muscle", "Améliorer mon cardio", "Rester en forme"]),
        "jours": st.slider("Nombre de séances par semaine :", min_value=1, max_value=6, value=3),
        "duree": st.select_slider("Durée d'une séance (minutes) :", options=[20, 30, 45, 60, 90], value=45),
        "materiel": ", ".join(st.multiselect("Matériel disponible :", ["Aucun", "Haltères", "Élastiques", "Tapis", "Vélo", "Salle de sport"], default=["Aucun"])),
        "limitations": st.text_input("Blessures ou limitations (facultatif) :", placeholder="ex. douleur au genou droit"),
    }
    if profil["limitations"] == "":
        profil["limitations"] = "aucune"
    return profil


def generer_programme(profil):
    """Chaîne 1 : le coach crée le programme à partir du profil."""
    return chaine_coach.invoke(profil)


def demander_avis(profil, programme):
    """Chaîne 2 : le kinésiologue vérifie le programme du coach."""
    return chaine_kine.invoke({
        "age": profil["age"],
        "niveau": profil["niveau"],
        "limitations": profil["limitations"],
        "programme": programme,   # la sortie de la chaîne 1 devient l'entrée de la chaîne 2
    })


# ============================================================
# L'APPLICATION
# ============================================================
# Les boîtes qui survivent à la relecture du script
if "programme" not in st.session_state:
    st.session_state.programme = ""
if "avis" not in st.session_state:
    st.session_state.avis = ""

afficher_entete()
profil = afficher_formulaire()

# --- Bouton 1 : générer le programme ---
if st.button("💪 Générer mon programme"):
    if profil["prenom"] == "":
        st.warning("Indique ton prénom.")
    else:
        with st.spinner("🏃 Ton coach prépare ton programme..."):
            st.session_state.programme = generer_programme(profil)
        st.session_state.avis = ""   # nouveau programme : on efface l'ancien avis

# --- Le programme, l'avis et le téléchargement (seulement si un programme existe) ---
if st.session_state.programme != "":
    st.subheader(f"🏋️ Ton programme, {profil['prenom']} !")
    with st.expander("Voir le programme", expanded=True):
        st.markdown(st.session_state.programme)

    # --- Bouton 2 : demander un deuxième avis ---
    if st.button("🧑‍⚕️ Demander l'avis du kinésiologue"):
        with st.spinner("🔎 Le kinésiologue analyse le programme..."):
            st.session_state.avis = demander_avis(profil, st.session_state.programme)

    if st.session_state.avis != "":
        st.subheader("🩺 L'avis du kinésiologue")
        st.info(st.session_state.avis, icon="👨‍⚕️")

    st.download_button("📥 Télécharger mon programme", st.session_state.programme, file_name="mon_programme.txt")
