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
