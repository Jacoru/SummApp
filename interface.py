import os
import sys
import streamlit as st
import io
from config import download_to_s3, upload_to_s3
from dotenv import load_dotenv
import pandas as pd
import ast

# Setup path per importare moduli locali
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

content = download_to_s3()
df = pd.read_csv(io.StringIO(content))

 # Interfaccia Streamlit
st.title("Paper Search and Text Summarization")


# Input utente
nome = st.text_input("Insert your name *")
cognome = st.text_input("Insert your surname *")
email = st.text_input("Insert your email *")
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


                frasi = []
                for i in range(len(saved_keywords)):
                        frasi.append(saved_keywords[i])
                        if i < len(saved_ops):
                                frasi.append(saved_ops[i])

                # Unisci tutto in una frase leggibile
                output = " ".join(frasi)

                st.divider()

                st.write(f"Your saved search is: {output}")
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
                        for sub in saved_subjects:
                                result += f", {sub}\n"
                st.write(result)

                options = ["Computer Science (cs)", "Economics", "Electrical Engineering and Systems Science (eess)", "Mathematics (math)", "Physics", "Quantitative Biology (q-bio)", "Quantitative Finance (q-fin)", "Statistics (stat)"]
                subject = st.pills("Subject", options, selection_mode="multi")
                if subject == []:
                        subject = saved_subjects

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
                if st.button("Save"):
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

                                load_dotenv()       #scarica file direttamente da S3
                                content = download_to_s3()
                                df = pd.read_csv(io.StringIO(content))
                                
                                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)    #Aggiungo la nuova riga
                                index = df[df["Email"] == email].index

                                #aggiorna solo i campi specificati
                                for col, val in new_row.items():
                                                df.loc[index, col] = str(val)

                                upload_to_s3(df) # Scrivo tutto in memoria e sovrascrivo su S3

                                st.success("File successfully updated on S3")

                        
elif email == "":
        st.info("Insert your data.")
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


        #bottone per salvataggio dati
        if st.button("Salva"):
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

                        load_dotenv()       #scarica file direttamente da S3
                        content = download_to_s3()
                        df = pd.read_csv(io.StringIO(content))
                        
                        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)    #Aggiungo la nuova riga

                        upload_to_s3(df) # Scrivo tutto in memoria e sovrascrivo su S3

                        st.success("File successfully updated on S3.")




