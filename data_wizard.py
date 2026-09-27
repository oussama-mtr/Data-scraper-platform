import streamlit as st

DATA_SOURCES = [
    'Bourse de Casablanca',
    'Bank Al-Maghrib',
    'HCP (High Commission for Planning)',
    'AMMC',
    'Other',
]

DATA_TYPES = [
    'Stock prices',
    'Financial statements',
    'Macroeconomic indicators',
    'Exchange rates',
    'Sector reports',
    'Other',
]

TIME_PERIODS = [
    'Last month',
    'Last quarter',
    'Last year',
    'Last 5 years',
    'Custom',
]

OUTPUT_FORMATS = [
    'Excel table',
    'Raw data (JSON)',
    'Summary text',
]

STEP_LABELS = [
    'Data Source',
    'Data Type',
    'Time Period',
    'Output Format',
    'Confirmation',
]


def _init_wizard_state():
    defaults = {
        'data_wizard_step': 1,
        'data_wizard_source': None,
        'data_wizard_type': None,
        'data_wizard_period': None,
        'data_wizard_format': None,
        'data_wizard_other_mode': None,
        'data_wizard_other_draft': '',
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _reset_wizard():
    st.session_state.data_wizard_step = 1
    st.session_state.data_wizard_source = None
    st.session_state.data_wizard_type = None
    st.session_state.data_wizard_period = None
    st.session_state.data_wizard_format = None
    st.session_state.data_wizard_other_mode = None
    st.session_state.data_wizard_other_draft = ''


def build_prompt(source, data_type, period, output_format):
    return (
        f'Get {data_type} data from {source} for {period} '
        f'and return as {output_format}.'
    )


def _render_progress(step):
    st.progress(step / len(STEP_LABELS), text=f'Step {step} of {len(STEP_LABELS)} — {STEP_LABELS[step - 1]}')


def _render_back_button():
    if st.session_state.data_wizard_step > 1:
        if st.button('← Back', use_container_width=False):
            if st.session_state.data_wizard_other_mode:
                st.session_state.data_wizard_other_mode = None
                st.session_state.data_wizard_other_draft = ''
            else:
                st.session_state.data_wizard_step -= 1
            st.rerun()


def _render_option_buttons(options, session_key, other_mode_key, next_step):
    cols = st.columns(2)
    for index, option in enumerate(options):
        if cols[index % 2].button(option, key=f'wizard_opt_{session_key}_{option}', use_container_width=True):
            if option == 'Other' or option == 'Custom':
                st.session_state.data_wizard_other_mode = other_mode_key
                st.session_state.data_wizard_other_draft = ''
            else:
                st.session_state[session_key] = option
                st.session_state.data_wizard_step = next_step
            st.rerun()


def _render_other_input(label, session_key, next_step):
    st.markdown(f'**{label}**')
    draft = st.text_input(
        'Enter your answer',
        value=st.session_state.data_wizard_other_draft,
        key=f'wizard_other_input_{session_key}',
        placeholder='Type here...',
    )
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button('Continue', type='primary', use_container_width=True):
            if draft.strip():
                st.session_state[session_key] = draft.strip()
                st.session_state.data_wizard_other_mode = None
                st.session_state.data_wizard_other_draft = ''
                st.session_state.data_wizard_step = next_step
                st.rerun()
            else:
                st.warning('Please enter a value before continuing.')


def render_data_wizard():
    """Render the step-by-step data query wizard. Returns a prompt string when Run is clicked."""
    _init_wizard_state()
    step = st.session_state.data_wizard_step

    _render_progress(step)
    _render_back_button()
    st.divider()

    if step == 1:
        st.subheader('Step 1 — Data Source')
        st.markdown('**Which source do you want data from?**')
        if st.session_state.data_wizard_other_mode == 'source':
            _render_other_input(
                'Specify your data source',
                'data_wizard_source',
                2,
            )
        else:
            _render_option_buttons(DATA_SOURCES, 'data_wizard_source', 'source', 2)

    elif step == 2:
        st.subheader('Step 2 — Data Type')
        st.markdown('**What type of data are you looking for?**')
        if st.session_state.data_wizard_other_mode == 'type':
            _render_other_input(
                'Specify the data type',
                'data_wizard_type',
                3,
            )
        else:
            _render_option_buttons(DATA_TYPES, 'data_wizard_type', 'type', 3)

    elif step == 3:
        st.subheader('Step 3 — Time Period')
        st.markdown('**Which time period?**')
        if st.session_state.data_wizard_other_mode == 'period':
            _render_other_input(
                'Enter your custom date range',
                'data_wizard_period',
                4,
            )
        else:
            _render_option_buttons(TIME_PERIODS, 'data_wizard_period', 'period', 4)

    elif step == 4:
        st.subheader('Step 4 — Output Format')
        st.markdown('**In what format do you want the output?**')
        _render_option_buttons(OUTPUT_FORMATS, 'data_wizard_format', None, 5)

    elif step == 5:
        st.subheader('Step 5 — Confirmation')
        st.markdown('Review your selections and run the query.')

        source = st.session_state.data_wizard_source
        data_type = st.session_state.data_wizard_type
        period = st.session_state.data_wizard_period
        output_format = st.session_state.data_wizard_format
        prompt = build_prompt(source, data_type, period, output_format)

        with st.container(border=True):
            st.markdown('#### Request Summary')
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f'**Data Source:** {source}')
                st.markdown(f'**Data Type:** {data_type}')
            with col2:
                st.markdown(f'**Time Period:** {period}')
                st.markdown(f'**Output Format:** {output_format}')
            st.divider()
            st.markdown('**Generated prompt:**')
            st.code(prompt, language=None)

        col_run, col_reset = st.columns([2, 1])
        with col_run:
            run_clicked = st.button('Run', type='primary', use_container_width=True)
        with col_reset:
            if st.button('Start Over', use_container_width=True):
                _reset_wizard()
                st.rerun()

        if run_clicked:
            return prompt

    return None
