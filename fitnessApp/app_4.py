import sqlite3
import streamlit as st
from datetime import date
from datetime import datetime
from streamlit_lottie import st_lottie
import json
import requests
import pandas as pd
import webbrowser

# ---------------
# calculating BMI
# ---------------
activity_factors = {
        "Sitzend (keine oder wenig Bewegung)": 1.2,
        "Leicht aktiv (leichte Übung/Sport 1-3 Tage/Woche)": 1.375,
        "Mäßig aktiv (mäßige Übung/Sport 3-5 Tage/Woche)": 1.55,
        "Sehr aktiv (harte Übung/Sport 6-7 Tage/Woche)": 1.725,
        "Extrem aktiv (sehr harte Übung/Sport, körperliche Arbeit)": 1.9
    }
#---lottiefile_ Animation---------
def get(path:str):
    with open(path,"r") as p:
        return json.load(p)
path= get("app_animation/a1.json")
path_1= get("app_animation/a2.json")
path_2= get("app_animation/a3.json")
path_3= get("app_animation/a4.json")
#---------------------------#
def calculate_bmi(weight: int, height: float):
    bmi = (weight / (height * height))
    return round(bmi, 1)
def calculate_calories(gender, weight, height, age:int, activity_level):
    if gender == "Mann":
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
#-----------------------------------#

#---------Übungen_methode------------------
# Hier könntest du realistischere Berechnungen basierend auf Übungstyp und Intensität einfügen.
def calculate_calories_burned(exercise, repetitions):
    
    # Hier könntest du realistischere Berechnungen basierend auf Übungstyp und Intensität einfügen.
    calories_per_rep = {
        "Push-up": 0.2,
        "Sit-up": 0.3,
        "Squat": 0.4,
        "Jumping Jacks": 0.5,
        "Kniebeuge":0.3,
        "Kreuzheben":0.4,
        "Klimmzüge":0.4,
        "Überkopfdrücken":0.30

       
    }
    
    if exercise in calories_per_rep:
        return calories_per_rep[exercise] * repetitions
    else:
        return 0
 

# --------------------------------------------------------------
# user registered and data  in users/history in user_db is saved
# --------------------------------------------------------------

def save_to_db(switch, check, create_table_query, insert_query, data):

    counter = 0

    try:
        connection = sqlite3.connect('user_db.sqlite')
        cursor = connection.cursor()

        check_table_query = "SELECT name FROM sqlite_master Where type = 'table' AND name = 'users'"
        cursor.execute(check_table_query)

        table_exists = cursor.fetchone()
        if table_exists:
            query = "SELECT COUNT(*) FROM users WHERE first_name = ? AND last_name = ?"
            cursor.execute(query, (str(check[0]), str(check[1])))

            result = cursor.fetchone()

            if result[0] > 0 and switch == 'register':
                print('User already exists')
                st.write('Ein Konto unter diesem Namen existiert bereits')

            elif (result[0] == 0 and switch == 'register') or (result[0] > 0 and switch == 'history'):
                cursor.execute(create_table_query)
                cursor.execute(insert_query, data)
                connection.commit()
                print('data was saved')

                counter += 1
                return counter

        else:
            cursor.execute(create_table_query)
            cursor.execute(insert_query, data)
            connection.commit()
            print('data was saved')

            counter += 1
            return counter

    except sqlite3.Error as err:
        print('Error:', err)

    finally:
        if connection:
            connection.close()

# -------------------------------------
# getting the user_id for the next user
# -------------------------------------

def get_user_id():

    try:
        connection = sqlite3.connect('user_db.sqlite')
        cursor = connection.cursor()

        check_table_query = "SELECT name FROM sqlite_master Where type = 'table' AND name = 'users'"
        cursor.execute(check_table_query)

        table_exists = cursor.fetchone()
        if table_exists:
            query = "SELECT * FROM users ORDER BY user_id DESC"
            cursor.execute(query)
            result = cursor.fetchone()
            return (result[0] + 1)

        else:
            return 1 

    except sqlite3.Error as err:
        print('Error:', err)

    finally:
        if connection:
            connection.close()

# ---------------------
# get stuff from the db
# ---------------------

def get_from_db(query, data):

    try:
        connection = sqlite3.connect('user_db.sqlite')
        connection.row_factory = sqlite3.Row

        cursor = connection.cursor()
        cursor.execute(query, data)

        row_dict = dict(cursor.fetchone())
        return row_dict
        
    except sqlite3.Error as err:
        print('Error:', err)

    finally:
        if connection:
            connection.close()

# ----------
# st.sidebar
# ----------

selected_section = st.sidebar.radio('Bereich auswählen', ('Home', 'Konto', 'Macro Calculator','Diät','Contact','Übungen von youtube'))

# ----
# Home
# ----

if selected_section == 'Home':
   st.header("wellcom to your FitnessApp💪")
   st.markdown(
       """
        <style>
        .pulse {
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
        </style>
        """,
       unsafe_allow_html=True,
   )

   st.write("Deine Fitnessreise beginnt hier.")
  


   with st.container():
       st.markdown('<p class="pulse">🏋️‍♂️</p>', unsafe_allow_html=True)
       st.write("Starte dein Training!")
       st_lottie(path,
                 speed=1,
                 reverse=False,
                 quality='high',
             width=None,
             height=None)   
    
              

# -----
# Konto
# -----

elif selected_section == 'Konto':
    st.header('Konto Optionen')
    account_choice = st.radio('Bitte auswählen',('Anmeldung', 'Registrierung'))

    # ----------------------
    # radio button Anmeldung
    # ----------------------

    if account_choice == 'Anmeldung':

        st.header("Anmeldung")
        with st.form('login'):
            first_name = st.text_input('Vorname')
            last_name  = st.text_input('Nachname')
            submitted  = st.form_submit_button('Bestätigen')
            if submitted:
                query = 'SELECT * FROM users WHERE first_name = ? AND last_name = ?'
                data  = (first_name, last_name)
                users_dict = get_from_db(query, data)
                if 'user_data' not in st.session_state:
                    st.session_state['user_data'] = users_dict

                query = 'SELECT * FROM history WHERE user_id = ? ORDER BY id DESC LIMIT 1'
                data  = str(users_dict['user_id'])
                history_dict = get_from_db(query, data)
                if 'user_history' not in st.session_state:
                    st.session_state['user_history'] = history_dict

                st.write('Willkommen zurück '+ users_dict['first_name'] + ' !!')
        st_lottie(path_1,
                 speed=1,
                 reverse=False,
                 quality='high',
             width=None,
             height=None)   
    # --------------------------
    # radio button Registrierung
    # --------------------------

    elif account_choice == 'Registrierung':
        st.header("Registrierung")
        st.write("Hier können Sie sich registrieren um alle Funktionen nutzen zu können.")

        with st.form('registry'):
            gender      = st.selectbox('Bitte auswählen:', ('Mann', 'Frau'))
            first_name  = st.text_input('Vorname')
            last_name   = st.text_input('Nachname')
            age         = st.slider('Bitte Alter angeben', min_value = 18, max_value = 99)
            height      = st.slider('Bitte Größe angeben', min_value = 1.60, max_value = 2.50)
            weight      = st.slider('Bitte Gewicht angeben', min_value = 50, max_value = 250)
            activity_level = st.selectbox("Aktivitätslevel:",set(activity_factors.keys()))
            submitted   = st.form_submit_button('Bestätigen')
            if submitted:
                user_id = get_user_id()
                bmi     = calculate_bmi(height, weight)
                Kalorien= calculate_calories(gender, weight, height, age, activity_level)
                
                total_counter = 0

                # ------------------------------------
                # saving stuff to 'history' in user_db
                # ------------------------------------

                switch = 'register'
                create_table_query = '''
                    CREATE TABLE IF NOT EXISTS history (
                    id INTEGER Primary KEY,
                    user_id INTEGER,
                    height REAL,
                    weight INTEGER,
                    weight_date DATE,
                    bmi REAL,
                    FOREIGN KEY (user_id) REFERENCES user(user_id)
                    )
                    '''
                insert_query = '''
                    INSERT INTO history (user_id, height, weight, weight_date, bmi)
                    VALUES (?, ?, ?, ?, ?)
                    '''
                check = (first_name, last_name)
                data  = (user_id, height, weight, datetime.now().date(), bmi)
                counter = save_to_db(switch, check, create_table_query, insert_query, data)
                total_counter += counter

                # ----------------------------------
                # saving stuff to 'users' in user_db
                # ----------------------------------

                switch = 'register'
                create_table_query = '''
                    CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    first_name TEXT,
                    last_name TEXT,
                    age INTEGER,
                    gender TEXT
                    )
                    '''
                insert_query = '''
                    INSERT INTO users (user_id, first_name, last_name, age, gender)
                    VALUES (?, ?, ?, ?, ?)
                    '''
                check = (first_name, last_name)
                data  = (user_id, first_name, last_name, age, gender)
                counter = save_to_db(switch, check, create_table_query, insert_query, data)
                total_counter += counter

                # -------------------
                # both saves complete
                # -------------------

                if total_counter == 2:
                    query = 'SELECT * FROM users WHERE first_name = ? AND last_name = ?'

                    data  = (first_name, last_name)
                    users_dict = get_from_db(query, data)
                    if 'user_data' not in st.session_state:
                        st.session_state['user_data'] = users_dict

                    query = 'SELECT * FROM history WHERE user_id = ? ORDER BY id DESC LIMIT 1'
                    data  = str(users_dict['user_id'])
                    history_dict = get_from_db(query, data)
                    if 'user_history' not in st.session_state:
                        st.session_state['user_history'] = history_dict

# ----------
# Auswertung
# ----------

elif selected_section == 'Macro Calculator':
    st.header('Auswertungen')
    evaluate_choice = st.radio('Bitte auswählen',('Gewicht', 'BMI'))

    # --------------------
    # radio button Gewicht
    # --------------------

    if evaluate_choice == 'Gewicht':
        if 'user_history' in st.session_state and 'user_data' in st.session_state:
            st.header("Gewicht")
            st.write('Hier können sie ihr Gewicht einsehen und aktualisieren.')
            st.write('Ihr letztes Gewicht betrug: ')
         
                    # st.success(f"Dein geschätzter täglicher Kalorienbedarf beträgt etwa {bmr:.2f} Kalorien.")
           

            # ---------------------
            # update the new weight
            # ---------------------

            with st.form('update_weight'):
                weight = st.slider('Bitte aktuelles Gewicht eingeben', 
                        min_value = 50, max_value = 250, value = st.session_state['user_history'].get('weight'))
                submitted  = st.form_submit_button('Bestätigen')
                
                if submitted:
                    st.session_state['user_history'].update({'weight': weight})
                    
                    
                    

                    st.write('Das aktuelle Gewicht wurde auf ' + str(weight) + ' gesetzt')
                    #st.experimental_rerun()

            # ------------------------------------
            # saving stuff to 'history' in user_db
            # ------------------------------------

            with st.form('save_update'):
                st.write('Möchten sie es speichern?')
                submitted = st.form_submit_button('Bestätigen')
                if submitted:
                    switch = 'history'
                    create_table_query = '''
                        CREATE TABLE IF NOT EXISTS history (
                        id INTEGER Primary KEY,
                        user_id INTEGER,
                        weight_date DATE,
                        weight INTEGER,
                        bmi REAL,
                        FOREIGN KEY (user_id) REFERENCES user(user_id)
                        )
                        '''
                    insert_query = '''
                        INSERT INTO history (user_id, height, weight, weight_date, bmi)
                        VALUES (?, ?, ?, ?, ?)
                        '''
                    user_id = st.session_state['user_history'].get('user_id')
                    height  = st.session_state['user_history'].get('height')
                    weight  = st.session_state['user_history'].get('weight')
                    bmi     = st.session_state['user_history'].get('bmi')
                    check   = (0, 0)

                    data = (user_id, height, weight, datetime.now().date(), bmi)
                    save_to_db(switch, check, create_table_query, insert_query, data)
                    st.success('Anmeldedaten erfolgreich gespeichert')
                    #st.experimental_rerun()
        st_lottie(path_2,
                 speed=1,
                 reverse=False,
                 quality='high',
             width=None,
             height=None) 
    # ----------------
    # radio button BMI
    # ----------------

    elif evaluate_choice == 'BMI':
        if 'user_history' in st.session_state and 'user_data' in st.session_state:
            st.header('BMI')
            st.write('Hier können sie ihren aktuellen BMI sehen')
            st.write('Ihr letzter BMI betrug: ')
            st.write(st.session_state['user_history'].get('bmi'))

        else:
            pass
elif selected_section== "Diät":       
 # Verbindung zur SQLite-Datenbank herstellen
    conn = sqlite3.connect('my_tracker.db')
    c = conn.cursor()

# Tabelle erstellen, falls sie noch nicht existiert
    c.execute('''
    CREATE TABLE IF NOT EXISTS daily_activities (
        id INTEGER PRIMARY KEY,
        date DATE,
        eaten TEXT,
        trained TEXT
    )
    ''')
    conn.commit()

# Streamlit-App starten



    st.title("Mein Aktivitäts-Tracker")

    # Eingabefelder für Essen und Training
    eaten = st.text_input("Heute gegessen:", "")
    trained = st.text_input("Heute trainiert:", "")
    
   

    if st.button("Speichern"):
        today = date.today()

        # Daten in die Datenbank einfügen
        c.execute("INSERT INTO daily_activities (date, eaten, trained) VALUES (?, ?, ?)",
                  (today, eaten, trained))
        conn.commit()

        st.success("Daten erfolgreich gespeichert!")

    # Daten aus der Datenbank abrufen und in Streamlit anzeigen
    st.subheader("Heute gegessen:") 
    today = date.today()
    c.execute("SELECT eaten FROM daily_activities WHERE date=?", (today,))
    eaten_data = c.fetchone()
    if eaten_data:
        st.write(eaten_data[0])
    else:
        st.write("Keine Daten gefunden.")

    st.subheader("Heute trainiert:")
    c.execute("SELECT trained FROM daily_activities WHERE date=?", (today,))
    trained_data = c.fetchone()
    if trained_data:
        st.write(trained_data[0])
    else:
        st.write("Keine Daten gefunden.")
    tab_Übung,  tab_Kalorienrechner,lebensmittel = st.tabs(["Übungen ", "tab_Kalorienrechner","lebensmittel"] )
    with tab_Übung:
        #übungen
        exercise_options = ["Push-up", "Sit-up", "Squat", "Jumping Jacks","Kniebeuge","Kreuzheben","Klimmzüge","Überkopfdrücken"]
        selected_exercise = st.selectbox("Wähle eine Übung aus:", exercise_options)
    
        repetitions = st.number_input("Anzahl der Wiederholungen:", value=10, step=1)
    
        if st.button("Berechne verbrannte Kalorien"):
            calories_burned = calculate_calories_burned(selected_exercise, repetitions)
            st.success(f"Du könntest etwa {calories_burned} Kalorien verbrennen.")
    
    #die kal für Diät rechnen  
    
    with tab_Kalorienrechner:
        gender      = st.selectbox('Bitte auswählen:', ('Mann', 'Frau'))
        age         = st.slider('Bitte Alter angeben', min_value = 18, max_value = 99)
        height      = st.slider('Bitte Größe angeben', min_value = 1.60, max_value = 2.50)
        weight      = st.slider('Bitte Gewicht angeben', min_value = 50, max_value = 250)
        activity_level = st.selectbox("Aktivitätslevel:",set(activity_factors.keys()))

        
    
        if st.button("Berechne Kalorienbedarf"):
           if gender == "Mann":
                bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
           else:
                bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
           st.success(f"Dein geschätzter täglicher Kalorienbedarf beträgt etwa {bmr:.2f} Kalorien.")
     
    with lebensmittel : 
        with open("essen.json",encoding="UTF-8") as file:
                    
                    data=json.load(file)
                    df=pd.DataFrame(data)
                    st.title("Lebensmittelkalorien")
                    st.write("Hier ist eine Tabelle mit Lebensmitteln und ihren Kalorienwerten:")
                    

# Anzeigen der Tabelle
                    st.dataframe(df)        
    st_lottie(path_3,
                 speed=1,
                 reverse=False,
                 quality='high',
             width=None,
             height=None)  
#-----contact------#
#     
elif selected_section == "Contact":
    st.header(":mailbox: Get In Touch With Us!")
    contact_form= """
  
<form action="https://formsubmit.co/m2mondx333@gmail.com" method="POST">
    <input type="hidden" name="_captcha" value="false">
    <input type="text" name="name" placeholder="Your Name" required>
    <input type="email" name="email" placeholder="Your Email" required>
    <textarea name="message" placeholder="Details of your problem"></textarea>
    <button type="submit">Send</button>
</form>
"""
    st.markdown(contact_form,unsafe_allow_html=True)
#-----css reder------#
def local_css(filename):
    with open(filename) as f:
        st.markdown(f"<style>{f.read()}</style>",unsafe_allow_html=True)
local_css("app_animation/style.css")        
  
#Hilfs vedios-------#
if selected_section  == "Übungen von youtube ":
 url = 'https://https://musclewiki.com/'

if st.button('Open browser'):
        webbrowser.open_new_tab(url)
