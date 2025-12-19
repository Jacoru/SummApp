import os
import sys
import streamlit as st
import io
from config import download_to_s3, upload_to_s3
import pandas as pd
import ast


st.markdown("""
<style>
/* Bottoni generici */
   div.stButton > button {
        background-color: #1DB954;
        color: white;
        border: 2px solid #1DB954;
        border-radius: 6px;
        padding: 0.5em 1em;
        font-weight: bold;
        transition: 0.3s ease;
}

/* Hover effect */
div.stButton > button:hover {
        background-color: #1ed760;
        border-color: #1ed760;
        color: black;
        outline: none !important;
        box-shadow: none !important;
}

/* Bottoni spenti (non selezionati) simulati come disabilitati */
div.stButton > button:disabled {
        background-color: #282828;
        color: #888;
        border: 2px solid #444;
        outline: none !important;
        box-shadow: none !important;
}

/* Dropdown e checkbox */
.stSelectbox, .stCheckbox {
        background-color: #282828 !important;
        color: white !important;
}

/* Testo generale */
html, body, [class*="css"] {
color: white;
background-color: #121212;
}


</style>
""", unsafe_allow_html=True)

# Setup path per importare moduli locali
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

content = download_to_s3()
df = pd.read_csv(io.StringIO(content))

 # Interfaccia Streamlit
st.image("arxiv.png")

st.title("Paper Search and Summarization📄", width="stretch")

with st.expander("📘 User Guide", expanded=True):
    st.markdown("""
    - This interface allows users to enter their data and select search parameters, similar to the Arxiv interface.
    - A daily email is sent at **7:00 PM** containing summaries and key data from the day's publications.
    - If no papers are published on a given day, **no email will be sent**.
    - If a preference has already been registered, it can be modified using the same email.
    - To ensure successful submission, wait for the **double confirmation message** after clicking **SAVE**.
    """)

# Input utente
nome = st.text_input("Insert your name *")
cognome = st.text_input("Insert your surname *")
email = st.text_input("Insert your email *")
st.write("Fields with * are obligatory")
st.divider()


if email in df["Email"].values:
        on = st.toggle("Mail already registered. If you want to modify your data, activate this feature.")
        if on:
                st.write("Start modifying your data.")
                dati_utente = df[df["Email"] == email].iloc[0]

                                        # Precompila i campi
                saved_keywords = ast.literal_eval(dati_utente["Keywords"])
                saved_ops = ast.literal_eval(dati_utente["Operator"])
                saved_subjects = ast.literal_eval(dati_utente["Subject"])
                saved_classification = dati_utente["Classification"]


                result = "Your saved keyword(s) are: "

                if len(saved_keywords) == 1:
                        result += f" {saved_keywords[0]}.\n"
                else:
                        for words in saved_keywords:
                                if words == saved_keywords[0]:
                                        result += f" {words},\n"
                                elif words == saved_keywords[-1]:
                                        result += f" {words}.\n"
                                else:
                                        result += f" {words},\n"
                st.divider()

                st.write(f"Your saved search is: {result}")

                if "num_fields" not in st.session_state:
                        st.session_state.num_fields = 1
                terms=[]
                and_or=[]


                for i in range(st.session_state.num_fields):
                        if i == 0:
                                
                                keywords = st.text_input(f"Insert Keyword(s) n°{i+1}", value="", placeholder="Insert",key=f"keyword_{i}")
                                terms.append(keywords)
                        else:
                                col_and, col_k= st.columns([1,1])
                                with col_and:
                                        option = st.selectbox("",("AND", "OR", "NOT"),key=f"op_{i}")
                                        and_or.append(option)
                                with col_k:
                                        keywords = st.text_input(f"Insert Keyword(s) n°{i+1}", value="", placeholder="Insert",key=f"keyword_{i}")
                                        terms.append(keywords)

                col_add, col_rem, col_res = st.columns([1, 1, 1])
                with col_add:
                        if st.button("Add term(s)"):        
                                agree = st.checkbox("Click if you want to add a term")
                                st.session_state.num_fields += 1

                with col_rem:
                        if st.button("Delete term(s)") and st.session_state.num_fields > 1:
                                agree = st.checkbox("Click if you want to remove a term")
                                st.session_state.num_fields -= 1
                                del terms[i]
                with col_res:
                        if st.button("Reset Search term(s)"):
                                agree = st.checkbox("Click if you want to reset the searching")
                                st.session_state.num_fields = 1
                                del terms[0:i]
                if terms == []:
                        terms = saved_keywords
                        and_or = saved_ops

                st.divider()
                for sub in saved_subjects:
                        result = "Your saved subject(s) are: "
                        if len(saved_subjects) == 1:
                                result += f" {sub}.\n"
                        else:
                                for sub in saved_subjects:
                                        if sub == saved_subjects[0]:
                                                result += f" {sub},\n"
                                        elif sub == saved_subjects[-1]:
                                                result += f" {sub}.\n"
                                        else:
                                                result += f" {sub},\n"
                st.write(result)

                diz_sub={"Computer Science (cs)": "computer_science", "Economics (ec)":"economics", "Electrical Engineering and Systems Science (eess)":"electrical_engineering_and_systems_science", "Mathematics (math)":"mathematics", "Physics":"physics", "Quantitative Biology (q-bio)":"quantitative_biology", "Quantitative Finance (q-fin)": "quantitative_finance", "Statistics (stat)":"statistics"}
                options = ["Computer Science (cs)", "Economics (econ)", "Electrical Engineering and Systems Science (eess)", "Mathematics (math)", "Physics (ph)", "Quantitative Biology (q-bio)", "Quantitative Finance (q-fin)", "Statistics (stat)"]
                subject = st.pills("Subject", options, selection_mode="multi")
                if subject == []:
                        subject = saved_subjects
                else:
                        subj=[]
                        for sub in subject:
                                subj.append(diz_sub[sub])
                        subject = subj

                        #sottocategoria Physics
                        if "Physics" in subject:
                                clas = f"Your saved classification(s) are: {saved_classification}\n"
                                st.write(clas)
                                agree = st.checkbox("Click if you want to select a subcategory of Physics")
                                if agree:
                                        classification = st.selectbox(
                                                "Elenco sottocategorie:",
                                                ["all", "astro-ph", "cond-mat", "gr-qc", "hep-ex", "hep-lat",
                                                "hep-ph", "hep-th", "math-ph", "nlin", "nucl-ex", "nucl-th", "physics", "quant-ph"], index=0
                                                )
                                else:
                                        classification = saved_classification
                        else:
                                classification = "all"
                st.divider()
                #bottone per salvataggio dati
                if st.button("🔍 Save"):
                        if not nome or not cognome or not email:
                                st.error("Plese, insert values in all fields with *") #obbligo di compilazione
                        else:
                                st.success(f"Wait for data's updating for: {email}")
                                new_row = {
                                "Email": email,
                                "Name": nome,
                                "Surname": cognome,
                                "Keywords": terms, 
                                "Operator": and_or,
                                "Subject": subject,
                                "Classification": classification
                                }

                                AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
                                AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")      #scarica file direttamente da S3

                                content = download_to_s3()
                                df = pd.read_csv(io.StringIO(content))
                                
                                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)    #Aggiungo la nuova riga
                                index = df[df["Email"] == email].index

                                #aggiorna solo i campi specificati
                                for col, val in new_row.items():
                                                df.loc[index, col] = str(val)

                                upload_to_s3(df) # Scrivo tutto in memoria e sovrascrivo su S3

                                st.success("File successfully updated on S3")

                        
else:
        st.write("**Insert your data.**")
        # Inizializza la session state
        if "num_fields" not in st.session_state:
                st.session_state.num_fields = 1
        terms=[]
        and_or=[]


        for i in range(st.session_state.num_fields):
                if i == 0:
                        keywords = st.text_input(f"Insert Keyword(s) n°{i+1}", value="", placeholder="Insert",key=f"keyword_{i}")
                        terms.append(keywords)
                else:
                        col_and, col_k= st.columns([1,1])
                        with col_and:
                                option = st.selectbox("",("AND", "OR", "NOT"),key=f"op_{i}")
                                and_or.append(option)
                        with col_k:
                                keywords = st.text_input(f"Insert Keyword(s) n°{i+1}", value="", placeholder="Insert",key=f"keyword_{i}")
                                terms.append(keywords)

        col_add, col_rem, col_res = st.columns([1, 1, 1])
        with col_add:
                if st.button("Add term(s)"):        
                        agree = st.checkbox("Click if you want to add a term")
                        st.session_state.num_fields += 1

        with col_rem:
                if st.button("Delete term(s)") and st.session_state.num_fields > 1:
                        agree = st.checkbox("Click if you want to remove a term")
                        st.session_state.num_fields -= 1
                        del terms[i]
        with col_res:
                if st.button("Reset Search term(s)"):
                        agree = st.checkbox("Click if you want to reset the searching")
                        st.session_state.num_fields = 1
                        del terms[0:i]

        st.divider()
        options = ["Computer Science (cs)", "Economics", "Electrical Engineering and Systems Science (eess)", "Mathematics (math)", "Physics", "Quantitative Biology (q-bio)", "Quantitative Finance (q-fin)", "Statistics (stat)"]
        subject = st.pills("Subject", options, selection_mode="multi")

        #sottocategoria Physics
        if "Physics" in subject:
                agree = st.checkbox("Click if you want to select a subcategory of Physics")
                if agree:
                        classification = st.selectbox(
                                "Elenco sottocategorie:",
                                ["all", "astro-ph", "cond-mat", "gr-qc", "hep-ex", "hep-lat",
                                "hep-ph", "hep-th", "math-ph", "nlin", "nucl-ex", "nucl-th", "physics", "quant-ph"], index=0
                                )
        else:
                classification = "all"
        with stylable_container(
             "red",
             css_styles="""
             button {
                 background-color: #FF0000;
             }""",
            ):
             buttonr_clicked = st.button("Delete Email", key="buttonr")
        with stylable_container(
             "red",
             css_styles="""
             write {
                 background-color: #FF0000;
             }""",
            ):
             email = st.text_input("Insert your email *")
        
        if buttonr_clicked:
           st.write("Success")
           em = email
           df = df[df['Email'] == em].reset_index(drop=True)

           
        #bottone per salvataggio dati
        if st.button("🔍 Save"):
                if not nome or not cognome or not email:
                        st.error("Plese, insert values in all fields with *.") #obbligo di compilazione
                else:
                        st.success(f"Wait for data's updating for: {email}")
                        new_row = {
                        "Email": email,
                        "Name": nome,
                        "Surname": cognome,
                        "Keywords": terms, 
                        "Operator": and_or,
                        "Subject": subject,
                        "Classification": classification
                        }

                        AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
                        AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")       #scarica file direttamente da S3
                        content = download_to_s3()
                        df = pd.read_csv(io.StringIO(content))
                        
                        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)    #Aggiungo la nuova riga

                        upload_to_s3(df) # Scrivo tutto in memoria e sovrascrivo su S3

                        st.success("File successfully updated on S3.")







