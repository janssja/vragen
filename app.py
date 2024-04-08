import streamlit as st
import json
import random
import openai
from openai import OpenAI
import os

# Initializeer antwoorden lijst binnen de sessiestatus indien nog niet bestaat
if 'antwoorden' not in st.session_state:
    st.session_state['antwoorden'] = []

api_key = st.secrets["openai_secret_key"]

def genereer_feedback(antwoorden_lijst):
    client = OpenAI(api_key=api_key)
    try:
        prompt = "Genereer een gedetailleerd Nederlandstalig rapport op basis van de volgende vragen en antwoorden:\n"
        
        for antwoord_dict in antwoorden_lijst:
            for vraag, antwoord in antwoord_dict.items():
                prompt += f"Vraag: {vraag}\nAntwoord: {antwoord}\n"

        response = client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "system", 
                        "content": """
                            Je bent een expert in het bekijken van vragen rond False positives en False Negatives en leert managers om dit te beoordelen.
                            De gebruiker heeft vragen beantwoord over False positives en False Negatives en gaat jou de vragen en antwoorden geven.
                            Je geeft enerzijds een globale feedback op de antwoorden van de gebruiker en anderzijds ga je in op individuele vragen als
                            dat relevant is voor de globale feedback. Je motiveert jouw feedback en geeft tips om de antwoorden te verbeteren.
                            Je geeft duidelijk aan of het een binaire keuze was op de vraag of dat het een ethische of organisatorische keuze was die 
                            je kon maken. Je linkt het ook aan machine learning en AI. Je sluit af met een positieve noot en een aanmoediging om verder te leren.
                            Je ondertekent met inspirerende groeten van Jackie Janssen.
                            Daaronder zet je een disclaimer dat dit een AI-generatie is en de feedback fouten kan bevatten.
                        """},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt}
                        ]
                    }
                ],
                max_tokens=2500,
                temperature=0.2,
                # response_format={"type": "json_object"},
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
        return response.choices[0].message.content
    except Exception as e:
        # Foutafhandeling
        return f"Er is een fout opgetreden bij het genereren van de feedback: {str(e)}"

# Laad de vragen van het configuratiebestand
def laad_vragen():
    try:
        with open('vragen.json', 'r', encoding='utf-8') as file:
            vragen = json.load(file)
        return vragen
    except Exception as e:
        st.error(f"Er is een fout opgetreden bij het laden van de vragen: {str(e)}")
        return []

# Selecteer willekeurig vragen
def selecteer_willekeurige_vragen(vragen_lijst, aantal=5):
    try:
        return random.sample(vragen_lijst, aantal)
    except ValueError:
        # Dit gebeurt als het aantal gevraagde items groter is dan de lijst
        st.error("Er zijn niet genoeg vragen om een willekeurige selectie te maken.")
        return []

def vraag_en_antwoord_opslaan(vraag, antwoord):
    # Deze functie zal de vraag en het antwoord in de sessie opslaan
    st.session_state.antwoorden.append({vraag: antwoord})

def toon_vragen_en_verzamel_antwoorden(gecombineerde_vragen):
    if 'huidige_vraag' not in st.session_state:
        st.session_state['huidige_vraag'] = 0
        
    huidige_vraag_nummer = st.session_state['huidige_vraag']
    
    if huidige_vraag_nummer < len(gecombineerde_vragen):
        vraag = gecombineerde_vragen[huidige_vraag_nummer]

        st.write(vraag)

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("False Negative", key=f"fn_{huidige_vraag_nummer}"):
                st.session_state.antwoorden.append({vraag: "False Negative"})
                st.session_state.huidige_vraag += 1

        with col2:
            if st.button("Geen van beide", key=f"gvb_{huidige_vraag_nummer}"):
                st.session_state.antwoorden.append({vraag: "Geen van beide"})
                st.session_state.huidige_vraag += 1

        with col3:
            if st.button("False Positive", key=f"fp_{huidige_vraag_nummer}"):
                st.session_state.antwoorden.append({vraag: "False Positive"})
                st.session_state.huidige_vraag += 1

        # Update de progress bar direct na het tonen van elke vraag
        st.progress((huidige_vraag_nummer + 1) / len(gecombineerde_vragen))


def toon_generatie_scherm():
    st.subheader("Generatie van feedback met generatieve AI")
    st.markdown("""
    Alle vragen zijn beantwoord. Klik op de onderstaande knop om feedback te genereren. 
    Jouw antwoorden zijn anoniem. Wil je meer in detail leren over False Positives en False Negatives?
    
    Vanuit Happy 2 Change voorzien we inspiratie en opleiding. 
    Contacteer ons via [jackie@happy2change.be](mailto:jackie@happy2change.be) 
    of via onze website: [happy2change.be](https://happy2change.be).
    """, unsafe_allow_html=True)
    
    if st.button("Genereer feedback"):
        with st.spinner('Even geduld alstublieft, uw feedback wordt gegenereerd...'):
            feedback = genereer_feedback(st.session_state.antwoorden)
            st.success("De feedback is gegenereerd.")
            st.write(feedback)
        # Reset voor een nieuwe sessie
        st.session_state.huidige_vraag = 0
        st.session_state.antwoorden = []


# Hoofdapp
def main():
    st.title("False Positives en False Negatives")
    
    vragen = laad_vragen()
    gecombineerde_vragen = selecteer_willekeurige_vragen(vragen['duidelijke_voorkeur'] + vragen['organisatorische_keuze'])

    toon_vragen_en_verzamel_antwoorden(gecombineerde_vragen)
    
    if 'huidige_vraag' in st.session_state and st.session_state.huidige_vraag >= len(gecombineerde_vragen):
        toon_generatie_scherm()

if __name__ == "__main__":
    main()