import streamlit as st
import pandas as pd
from healthcare.ui_style import apply_custom_style, render_hero, render_feature_cards
from healthcare.database import initialize_database, create_patient
from healthcare.records import (get_patients, get_patient, get_medical_history,
                                add_medical_record, update_medical_record,
                                generate_history_context)
from healthcare.appointments import (get_doctors, get_available_slots,
                                     book_appointment, get_patient_appointments,
                                     cancel_appointment)
from healthcare.medical_search import retrieve_medical_information
from healthcare.config import generate_ai_response

st.set_page_config(page_title='MediFlow AI',page_icon='🏥',layout='wide')
apply_custom_style()
initialize_database()

PAGES = ['🏠 Dashboard','👤 Patients','📅 Appointments','📋 Medical Records',
         '🩺 History Summary','🔎 Medical Research','🤖 AI Healthcare Assistant',
         '🧠 FAISS Memory','📊 Evaluation & Monitoring']

# Process navigation BEFORE the radio widget is instantiated.
if '_next_page' in st.session_state:
    st.session_state['page'] = st.session_state.pop('_next_page')

def navigate(destination):
    st.session_state['_next_page'] = destination
    st.rerun()

@st.cache_data(ttl=120)
def department_guide():
    return {
        'Kidney disease, urinary kidney concerns': 'Nephrology',
        'Heart, blood pressure, chest-related concerns': 'Cardiology',
        'Headaches, seizures, nerve-related concerns': 'Neurology',
        'Bones, joints, injuries': 'Orthopedics',
        'Skin, acne, rashes': 'Dermatology',
        'Stomach, digestion, liver concerns': 'Gastroenterology',
        'Diabetes, thyroid, hormones': 'Endocrinology',
        'Breathing, lungs, asthma': 'Pulmonology',
        'Ear, nose and throat': 'ENT',
        'Eyes and vision': 'Ophthalmology',
        'Women’s reproductive health': 'Gynecology',
        'Mental health and mood': 'Psychiatry',
        'Children’s health': 'Pediatrics',
        'Not sure / routine consultation': 'General Medicine',
    }

def table(rows,empty='No entries found.'):
    if rows:
        st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True)
    else:
        st.info(empty)

def outcome(result,success='Saved successfully.'):
    if isinstance(result,dict) and result.get('success') is False:
        st.error(result.get('message','Operation failed.'))
        return False
    st.success(result.get('message',success) if isinstance(result,dict) else success)
    return True

with st.sidebar:
    st.title('🏥 MediFlow AI')
    st.caption('INTERACTIVE HEALTHCARE CAPSTONE')
    page=st.radio('Explore modules',PAGES,key='page')
    st.divider()
    st.subheader('👤 Demo Patient')
    patients=get_patients()
    if not patients:
        st.error('No demo patients available.')
        st.stop()
    options={f"{p['name']} • ID {p['id']}":p['id'] for p in patients}
    selected=st.selectbox('Select patient',list(options),key='patient_choice')
    patient_id=options[selected]
    patient=get_patient(patient_id)
    st.write(f"**Name:** {patient['name']}")
    st.write(f"**Age:** {patient['age']} years")
    if st.button('➕ Add a new patient',use_container_width=True):
        navigate('👤 Patients')
    st.caption('Fictional records only. No authentication is implemented.')

st.title('🏥 MediFlow AI')
st.caption('Agentic healthcare automation • Gemini • LangGraph • FAISS • Streamlit')
st.info('Educational demonstration only. No real patient information or clinical decisions. All doctors and appointments are fictional.')

if page=='🏠 Dashboard':
    render_hero()
    appointments=get_patient_appointments(patient_id)
    c1,c2,c3,c4=st.columns(4)
    c1.metric('Patients',len(patients))
    c2.metric('Demo Doctors',len(get_doctors()))
    c3.metric('Patient Records',len(get_medical_history(patient_id)))
    c4.metric('Active Bookings',sum(a.get('status')=='Booked' for a in appointments))
    st.subheader('✨ Explore the Platform')
    render_feature_cards()
    st.subheader('📋 Patient Snapshot')
    table(get_medical_history(patient_id)[:5],'No history yet. Add a fictional record.')
    if st.button('Book an appointment',type='primary'):
        navigate('📅 Appointments')

elif page=='👤 Patients':
    st.header('👤 Register a Fictional Patient')
    st.write('Enter a patient name and age, then select that patient from the sidebar.')
    with st.form('register_patient',clear_on_submit=True):
        name=st.text_input('Patient full name',placeholder='Example: Riya Sharma')
        age=st.number_input('Age',min_value=0,max_value=120,value=30,step=1)
        submitted=st.form_submit_button('➕ Create Patient',type='primary')
    if submitted:
        try:
            new_id=create_patient(name,age)
            st.success(f'Created fictional patient {name.strip()} (ID {new_id}).')
            st.info('Select the new patient in the sidebar to work with their records.')
        except Exception as exc:
            st.error(str(exc))
    st.subheader('All Demo Patients')
    table(get_patients())

elif page=='📅 Appointments':
    st.header('📅 Smart Appointment Booking')
    st.write(f"Booking for **{patient['name']}** (patient ID {patient_id}).")
    st.subheader('1. Which department should the patient visit?')
    concern=st.selectbox('Select the patient concern',list(department_guide()))
    suggestion=department_guide()[concern]
    st.info(f'Suggested department: **{suggestion}**. This is general routing guidance, not a diagnosis.')
    if concern.startswith('Heart'):
        st.warning('New, severe chest pain, breathing difficulty or fainting may require emergency care rather than routine booking.')
    if concern.startswith('Headaches'):
        st.caption('Sudden severe neurological symptoms may require emergency assessment.')
    doctors=get_doctors()
    departments=sorted({d['specialization'] for d in doctors})
    default=departments.index(suggestion) if suggestion in departments else 0
    department=st.selectbox('2. Choose department',departments,index=default,key=f'department_{concern}')
    matches=[d for d in doctors if d['specialization']==department]
    if matches:
        doctor_names={f"{d['name']} — {d['specialization']}":d['id'] for d in matches}
        doctor_label=st.selectbox('3. Choose doctor',list(doctor_names))
        doctor_id=doctor_names[doctor_label]
        slots=get_available_slots(doctor_id,days=7)
        if slots:
            slot=st.selectbox('4. Choose available date and time',slots)
            with st.container(border=True):
                st.markdown('#### Confirm appointment')
                st.write(f'**Patient:** {patient["name"]}')
                st.write(f'**Department:** {department}')
                st.write(f'**Doctor:** {doctor_label}')
                st.write(f'**Time:** {slot}')
                confirmed=st.checkbox('I confirm this simulated booking.',key='confirm_booking')
                if st.button('✅ Book Appointment',type='primary',disabled=not confirmed):
                    try:
                        if outcome(book_appointment(patient_id,doctor_id,slot),'Appointment booked.'):
                            st.rerun()
                    except Exception as exc:
                        st.error(f'Booking failed: {exc}')
        else:
            st.warning('No slots available in the next seven days. Try another doctor.')
    else:
        st.warning('No doctors available in this department.')
    st.divider()
    st.subheader('Patient Appointment History')
    bookings=get_patient_appointments(patient_id)
    table(bookings)
    active=[a for a in bookings if a.get('status')=='Booked']
    if active:
        booking_map={f"#{a['id']} • {a.get('doctor_name','Doctor')} • {a['appointment_time']}":a['id'] for a in active}
        cancel_label=st.selectbox('Select appointment to cancel',list(booking_map))
        if st.button('Cancel selected demo booking'):
            try:
                if outcome(cancel_appointment(booking_map[cancel_label]),'Appointment cancelled.'):
                    st.rerun()
            except Exception as exc:
                st.error(str(exc))

elif page=='📋 Medical Records':
    st.header('📋 Medical Record Management')
    st.write(f"**Selected patient:** {patient['name']}")
    records=get_medical_history(patient_id)
    table(records,'No records yet. Add a fictional diagnosis below.')
    st.subheader('Add Medical Record')
    with st.form('add_medical_record'):
        diagnosis=st.text_input('Diagnosis / condition',placeholder='Example: Chronic kidney disease')
        treatment=st.text_area('Treatment / plan (fictional data)')
        notes=st.text_area('Additional medical notes')
        submitted=st.form_submit_button('💾 Save Record',type='primary')
    if submitted:
        if not diagnosis.strip():
            st.warning('Enter a diagnosis.')
        else:
            try:
                add_medical_record(patient_id,diagnosis.strip(),treatment,notes)
                st.success('Medical record added.')
                st.rerun()
            except Exception as exc:
                st.error(str(exc))
    if records:
        st.subheader('Update Existing Record')
        choices={f"#{r['id']} — {r['diagnosis']}":r for r in records}
        chosen=choices[st.selectbox('Select record',list(choices))]
        with st.form('update_medical_record'):
            new_diagnosis=st.text_input('Diagnosis',value=chosen.get('diagnosis') or '')
            new_treatment=st.text_area('Treatment',value=chosen.get('treatment') or '')
            new_notes=st.text_area('Notes',value=chosen.get('notes') or '')
            update=st.form_submit_button('Update Record')
        if update:
            if not new_diagnosis.strip():
                st.warning('Diagnosis cannot be empty.')
            else:
                try:
                    update_medical_record(chosen['id'],new_diagnosis,new_treatment,new_notes)
                    st.success('Record updated.')
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))

elif page=='🩺 History Summary':
    st.header('🩺 AI Medical History Summary')
    st.write(f"**Patient:** {patient['name']}")
    records=get_medical_history(patient_id)
    table(records,'No history found. Add a fictional medical record first.')
    if st.button('✨ Generate Gemini History Summary',type='primary',disabled=not bool(records)):
        with st.spinner('Summarizing existing records...'):
            try:
                context=generate_history_context(patient_id)
                prompt=('Summarize ONLY the supplied fictional patient history. '
                        'Include known diagnoses, documented treatments, and relevant notes. '
                        'Do not invent missing details, diagnose, or prescribe. '
                        'Clearly say when information is missing.\n\n'+context)
                summary=generate_ai_response(prompt)
                st.session_state['history_summary']=(patient_id,summary)
            except Exception as exc:
                st.error(f'Summary failed: {exc}')
    saved=st.session_state.get('history_summary')
    if saved and saved[0]==patient_id:
        st.markdown('### Generated Summary')
        st.write(saved[1])
        st.caption('AI-generated educational summary; verify against the original records.')

elif page=='🔎 Medical Research':
    st.header('🔎 Trusted Medical Information Search')
    st.caption('Searches MedlinePlus. Results depend on the external service being available.')
    topic=st.text_input('Medical topic',value='chronic kidney disease')
    if st.button('Search trusted medical sources',type='primary'):
        if not topic.strip():
            st.warning('Enter a topic.')
        else:
            with st.spinner('Searching MedlinePlus...'):
                try:
                    result=retrieve_medical_information(topic)
                    st.session_state['research']=(topic,result)
                except Exception as exc:
                    st.error(f'Search failed: {exc}')
    research=st.session_state.get('research')
    if research and research[0]==topic:
        sources=research[1].get('sources',[])
        if not sources:
            st.warning('No verified sources returned. Try a broader medical term.')
        for item in sources:
            with st.container(border=True):
                st.subheader(item.get('title','Medical information'))
                st.write(item.get('content','No preview available.'))
                url=item.get('url','')
                if url.startswith('https://medlineplus.gov/') or url.startswith('https://www.medlineplus.gov/'):
                    st.link_button('Open MedlinePlus Source',url)

elif page=='🤖 AI Healthcare Assistant':
    st.header('🤖 Agentic Healthcare Assistant')
    st.caption('Plans multi-step tasks. Appointment confirmation remains manual.')
    query=st.text_area('Enter a multi-step request',value='Summarize patient history, find nephrology appointments, and research chronic kidney disease.',height=120)
    if st.button('Run LangGraph Agent',type='primary'):
        with st.spinner('Running agent...'):
            try:
                from healthcare.agent import run_healthcare_agent
                result=run_healthcare_agent(query,patient_id)
                st.session_state['agent_result']=(patient_id,result)
            except Exception as exc:
                st.error(f'Agent failed: {exc}')
    saved=st.session_state.get('agent_result')
    if saved and saved[0]==patient_id:
        result=saved[1]
        st.subheader('Agent Response')
        st.write(result.get('response','No response returned.'))
        with st.expander('Planning breakdown'):
            st.write(result.get('plan','No plan returned.'))
        with st.expander('Execution trace'):
            st.write(result.get('execution_trace',[]))
        with st.expander('Medical sources'):
            st.write(result.get('medical_sources',[]))
    if st.button('Proceed to confirmed booking'):
        navigate('📅 Appointments')

elif page=='🧠 FAISS Memory':
    st.header('🧠 FAISS Semantic Memory')
    query=st.text_input('Search fictional patient memory',placeholder='kidney disease treatment')
    if st.button('Search Vector Memory',type='primary'):
        if not query.strip():
            st.warning('Enter a search term.')
        else:
            with st.spinner('Searching FAISS...'):
                try:
                    from healthcare.memory import retrieve_patient_memory
                    results=retrieve_patient_memory(patient_id,query)
                    if results:
                        for item in results:
                            with st.container(border=True):
                                st.write(item.get('content',''))
                                st.caption(f"Similarity: {item.get('similarity',0):.3f}")
                    else:
                        st.info('No matching records.')
                except Exception as exc:
                    st.error(f'FAISS search failed: {exc}')

elif page=='📊 Evaluation & Monitoring':
    st.header('📊 Agent Evaluation & Monitoring')
    try:
        from healthcare.monitoring import get_agent_logs, get_monitoring_metrics
        st.subheader('Monitoring metrics')
        st.json(get_monitoring_metrics())
        st.subheader('Execution logs')
        table(get_agent_logs(limit=100))
    except Exception as exc:
        st.error(f'Monitoring unavailable: {exc}')
    try:
        from healthcare.evaluation import get_evaluation_metrics
        st.subheader('Evaluation metrics')
        st.json(get_evaluation_metrics())
    except Exception as exc:
        st.error(f'Evaluation unavailable: {exc}')

st.markdown('<div class="footer">MediFlow AI • Educational Capstone • Fictional Demo Data Only</div>',unsafe_allow_html=True)
