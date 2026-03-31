"""
AutoCare Pro — Streamlit Frontend
===================================
Deploy: streamlit run streamlit_app.py
Cloud:  Push to GitHub → connect at share.streamlit.io
"""

import streamlit as st
from datetime import datetime, timedelta
from langchain_community.chat_models import ChatOpenAI
import sys
import os

# -------------------------------
# Setup OpenAI API Key
# -------------------------------
os.environ["OPENAI_API_KEY"] = st.secrets['OPENAI_API_KEY']

llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.2,
    api_key=os.environ["OPENAI_API_KEY"]
)

# ── Allow import of main.py from same directory ──────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))
from main import AutomotiveServiceOrchestrator, ServiceType, AppointmentStatus

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AutoCare Pro AI Agent",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: white;
    }
    .agent-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 2px;
    }
    .badge-crew   { background:#7c3aed; color:white; }
    .badge-autogen{ background:#0891b2; color:white; }
    .badge-sk     { background:#059669; color:white; }
    .badge-voice  { background:#d97706; color:white; }
    .chat-user {
        background: #e0f2fe;
        border-radius: 12px 12px 4px 12px;
        padding: 0.6rem 1rem;
        margin: 4px 0;
        text-align: right;
    }
    .chat-bot {
        background: #f0fdf4;
        border-radius: 12px 12px 12px 4px;
        padding: 0.6rem 1rem;
        margin: 4px 0;
    }
    .metric-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 1px 4px rgba(0,0,0,.06);
    }
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ─── Session State Initialisation ────────────────────────────────────────────
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = AutomotiveServiceOrchestrator()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []   # list of (role, text, agent)
if "chat_phone" not in st.session_state:
    st.session_state.chat_phone = ""
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "💬 Chat"

orchestrator: AutomotiveServiceOrchestrator = st.session_state.orchestrator

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/car-service.png", width=72)
    st.title("AutoCare Pro")
    st.caption("Multi-Framework AI Agent System")

    st.divider()
    st.markdown("**Active Agents**")
    st.markdown("""
    <span class="agent-badge badge-crew">🤖 ARIA — CrewAI</span><br>
    <span class="agent-badge badge-autogen">📅 APEX — AutoGen</span><br>
    <span class="agent-badge badge-sk">🧠 NEXUS — Semantic Kernel</span><br>
    <span class="agent-badge badge-voice">📞 VOICE Handler</span>
    """, unsafe_allow_html=True)

    st.divider()
    page = st.radio(
        "Navigate",
        ["💬 Chat", "📅 Book Appointment", "👤 CRM Lookup",
         "📞 Phone Simulation", "📊 Dashboard", "➕ Add Customer"],
        label_visibility="collapsed"
    )

    st.divider()
    st.caption("v1.0 · Built with Streamlit + FastAPI")

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h2 style="margin:0">🚗 AutoCare Pro — AI Service Agent</h2>
    <p style="margin:4px 0 0 0; opacity:.8; font-size:.9rem">
        CrewAI &nbsp;·&nbsp; AutoGen &nbsp;·&nbsp; Semantic Kernel &nbsp;·&nbsp; Voice Handler
    </p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: CHAT
# ══════════════════════════════════════════════════════════════════════════════
if page == "💬 Chat":
    st.subheader("💬 Chat with ARIA (CrewAI Receptionist)")

    phone_input = st.text_input(
        "Your phone number (optional — helps us recognise you)",
        placeholder="+91-9876543210",
        key="phone_input_chat"
    )

    # Display history
    for role, text, agent in st.session_state.chat_history:
        if role == "user":
            st.markdown(f'<div class="chat-user">👤 <b>You</b><br>{text}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bot">🤖 <b>{agent}</b><br>{text}</div>', unsafe_allow_html=True)

    # Input row
    col_msg, col_send, col_clear = st.columns([6, 1, 1])
    with col_msg:
        user_msg = st.text_input("Message", placeholder="e.g. Hi, I need an oil change", label_visibility="collapsed", key="chat_input")
    with col_send:
        send = st.button("Send ➤", use_container_width=True)
    with col_clear:
        if st.button("🗑️", use_container_width=True, help="Clear chat"):
            st.session_state.chat_history = []
            st.session_state.orchestrator = AutomotiveServiceOrchestrator()
            orchestrator = st.session_state.orchestrator
            st.rerun()

    if send and user_msg.strip():
        phone = phone_input.strip() or None
        st.session_state.chat_history.append(("user", user_msg, "You"))

        with st.spinner("ARIA is thinking…"):
            result = orchestrator.handle_chat_interaction(user_msg, phone)

        primary = result.get("primary_response", {})
        msg = primary.get("message", "I'm here to help!")
        agent_label = primary.get("agent", "ARIA (CrewAI)")
        st.session_state.chat_history.append(("bot", msg, agent_label))

        # Show booking confirmation if triggered
        if "booking" in result and result["booking"].get("success"):
            booking = result["booking"]
            bk_msg = booking.get("message", "Appointment booked!")
            st.session_state.chat_history.append(("bot", bk_msg, "APEX (AutoGen Booking)"))

        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: BOOK APPOINTMENT
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📅 Book Appointment":
    st.subheader("📅 Book an Appointment — APEX (AutoGen)")

    customers = orchestrator.crm.customers
    if not customers:
        st.warning("No customers found. Please add a customer first.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            customer_options = {f"{c.name} ({cid})": cid for cid, c in customers.items()}
            selected_label = st.selectbox("Select Customer", list(customer_options.keys()))
            customer_id = customer_options[selected_label]
            customer = customers[customer_id]
            st.info(f"🚗 {customer.vehicle_year} {customer.vehicle_make} {customer.vehicle_model}  \n"
                    f"📞 {customer.phone}  \n⭐ {customer.loyalty_points} loyalty pts")

        with col2:
            service_options = [s.value for s in ServiceType]
            service_choice = st.selectbox("Service Type", service_options)
            preferred_date = st.date_input(
                "Preferred Date",
                value=datetime.now().date() + timedelta(days=1),
                min_value=datetime.now().date()
            )
            date_str = preferred_date.strftime("%Y-%m-%d")

        # Available slots
        available_slots = orchestrator.crm.get_available_slots(date_str)
        if available_slots:
            preferred_time = st.selectbox("Available Time Slots", available_slots)
        else:
            st.error("No slots available on this date. Please choose another date.")
            preferred_time = None

        if st.button("✅ Confirm Booking", type="primary") and preferred_time:
            with st.spinner("APEX is processing your booking…"):
                service_enum = ServiceType(service_choice)
                result = orchestrator.booking_agent.orchestrate_booking(
                    customer_id, service_enum, date_str, preferred_time
                )

            if result.get("success"):
                apt = result.get("appointment")
                st.success(f"**Booking Confirmed!** Appointment ID: `{apt['id']}`")
                cols = st.columns(4)
                cols[0].metric("Service", apt["service"])
                cols[1].metric("Date & Time", f"{apt['date']} {apt['time']}")
                cols[2].metric("Advisor", apt["advisor"])
                cols[3].metric("Estimated Cost", f"₹{apt['estimated_cost']:,.0f}")
                st.balloons()
            else:
                st.error(f"Booking failed: {result.get('error', 'Unknown error')}")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: CRM LOOKUP
# ══════════════════════════════════════════════════════════════════════════════
elif page == "👤 CRM Lookup":
    st.subheader("🧠 CRM Intelligence — NEXUS (Semantic Kernel)")

    customers = orchestrator.crm.customers
    customer_options = {f"{c.name} ({cid})": cid for cid, c in customers.items()}
    selected = st.selectbox("Select Customer", list(customer_options.keys()))
    customer_id = customer_options[selected]

    if st.button("🔍 Run CRM Intelligence Pipeline", type="primary"):
        with st.spinner("NEXUS is analysing the customer profile…"):
            result = orchestrator.crm_agent.run_customer_pipeline(customer_id)

        if result.get("success"):
            profile = result["customer_profile"]
            intel = result["intelligence"]
            recs = result.get("recommendations", [])

            col1, col2, col3 = st.columns(3)
            col1.metric("Customer", profile["name"])
            col2.metric("Vehicle", profile["vehicle"])
            col3.metric("Total Spent", f"₹{intel['total_spent']}")

            col4, col5, col6 = st.columns(3)
            col4.metric("Loyalty Tier", intel["loyalty_tier"])
            col5.metric("Loyalty Points", intel["loyalty_points"])
            col6.metric("VIP Status", "⭐ Yes" if intel["is_vip"] else "No")

            # Service history
            with st.expander("📋 Service History"):
                history = profile.get("service_history", [])
                if history:
                    for h in history:
                        st.write(f"• {h}")
                else:
                    st.write("No service history yet.")

            # Recommendations
            st.markdown("### 💡 Service Recommendations")
            for rec in recs:
                priority_color = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(rec["priority"], "⚪")
                st.markdown(
                    f"{priority_color} **{rec['service']}** — {rec['reason']}  \n"
                    f"Estimated cost: **{rec['estimated_cost']}** · Priority: `{rec['priority']}`"
                )
        else:
            st.error(result.get("error", "CRM lookup failed."))

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: PHONE SIMULATION
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📞 Phone Simulation":
    st.subheader("📞 Phone Call Simulation — VOICE Handler")
    st.caption("Simulate an incoming phone call through the AI voice agent.")

    caller_phone = st.text_input("Caller Phone Number", value="+91-9988776655")

    st.markdown("**Conversation Script** — one line per customer utterance")
    default_script = (
        "Hello, I need to book a service appointment\n"
        "I need an oil change for my Honda City\n"
        "Tomorrow morning would be great"
    )
    script_text = st.text_area("Customer utterances (one per line)", value=default_script, height=140)

    if st.button("📞 Simulate Call", type="primary"):
        conversation = [line.strip() for line in script_text.splitlines() if line.strip()]
        sim_orchestrator = AutomotiveServiceOrchestrator()   # fresh instance per call

        with st.spinner("Simulating call…"):
            call_result = sim_orchestrator.handle_phone_call(caller_phone, conversation)

        st.success(f"Call ID: `{call_result['call_id']}` · Caller: {call_result['caller']}")
        st.markdown("**Agents used:** " + " → ".join(call_result.get("agents_used", [])))

        st.markdown("### 📝 Call Transcript")
        for item in call_result.get("flow", []):
            if "greeting" in item:
                st.markdown(f"🤖 **ARIA:** {item['greeting']}")
            elif "customer_input" in item:
                st.markdown(f"👤 **Caller:** {item['customer_input']}")
            elif "spoken_response" in item:
                st.markdown(f"🤖 **ARIA:** {item['spoken_response']}")
            elif "booking_triggered" in item and item.get("result", {}).get("success"):
                booking = item["result"].get("appointment", {})
                st.success(
                    f"✅ **Booking confirmed!** ID: `{booking.get('id')}` — "
                    f"{booking.get('service')} on {booking.get('date')} at {booking.get('time')}"
                )
            elif "transcript" in item:
                st.info(f"📵 Call ended · Duration: {item.get('duration_turns', '?')} turns")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Dashboard":
    st.subheader("📊 CRM Dashboard")

    dashboard = orchestrator.get_crm_dashboard()

    # KPI row
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("👥 Total Customers",     dashboard["total_customers"])
    k2.metric("📅 Total Appointments",  dashboard["total_appointments"])
    k3.metric("✅ Confirmed",           dashboard["confirmed_appointments"])
    k4.metric("💰 Revenue Pipeline",    f"₹{dashboard['total_revenue_pipeline']:,.0f}")

    st.divider()
    tab_cust, tab_apt = st.tabs(["👥 Customers", "📅 Appointments"])

    with tab_cust:
        customers_data = dashboard["customers"]
        if customers_data:
            import pandas as pd
            df_c = pd.DataFrame(customers_data)
            df_c.columns = [c.replace("_", " ").title() for c in df_c.columns]
            st.dataframe(df_c, use_container_width=True, hide_index=True)
        else:
            st.info("No customers yet.")

    with tab_apt:
        appointments_data = dashboard["appointments"]
        if appointments_data:
            import pandas as pd
            df_a = pd.DataFrame(appointments_data)
            # Colour-code status
            def colour_status(val):
                colours = {
                    "confirmed": "background-color:#dcfce7",
                    "pending":   "background-color:#fef9c3",
                    "cancelled": "background-color:#fee2e2",
                    "completed": "background-color:#e0f2fe",
                }
                return colours.get(val, "")
            df_a.columns = [c.replace("_", " ").title() for c in df_a.columns]
            st.dataframe(df_a.style.applymap(colour_status, subset=["Status"]),
                         use_container_width=True, hide_index=True)
        else:
            st.info("No appointments yet.")

    if st.button("🔄 Refresh Dashboard"):
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ADD CUSTOMER
# ══════════════════════════════════════════════════════════════════════════════
elif page == "➕ Add Customer":
    st.subheader("➕ Add New Customer")

    with st.form("new_customer_form"):
        col1, col2 = st.columns(2)
        with col1:
            name  = st.text_input("Full Name *", placeholder="Arjun Mehta")
            phone = st.text_input("Phone *", placeholder="+91-9876543210")
            email = st.text_input("Email *", placeholder="arjun@email.com")
        with col2:
            make  = st.text_input("Vehicle Make *", placeholder="Toyota")
            model = st.text_input("Vehicle Model *", placeholder="Innova")
            year  = st.number_input("Vehicle Year *", min_value=1990,
                                    max_value=datetime.now().year + 1,
                                    value=2021, step=1)

        submitted = st.form_submit_button("➕ Add Customer", type="primary")

    if submitted:
        if not all([name, phone, email, make, model]):
            st.error("Please fill in all required fields.")
        else:
            customer = orchestrator.crm.create_customer(
                name, phone, email, make, model, int(year)
            )
            st.success(f"✅ Customer created! ID: **{customer.id}**")
            st.json({
                "id": customer.id, "name": customer.name,
                "phone": customer.phone, "email": customer.email,
                "vehicle": f"{customer.vehicle_year} {customer.vehicle_make} {customer.vehicle_model}"
            })
