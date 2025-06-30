import streamlit as st
from fpdf import FPDF
import io
import pandas as pd
from datetime import datetime

# Titel
st.title("Klimaklar SMB")
st.write("Velkommen til din CO2-rapport generator! Udfyld felterne nedenfor for at beregne dit CO2-aftryk.")

# Emissionsfaktorer
FAKTOR_EL = 0.233
FAKTOR_GAS = 2.2
FAKTOR_VAREBIL = 0.180
FAKTOR_LASTBIL = 0.500
FAKTOR_STAAL = 1.9
FAKTOR_TRAE = 0.2
FAKTOR_PLAST = 3.0
FAKTOR_BETON = 0.1
FAKTOR_ALU = 8.0
FAKTOR_PAPIR = 1.0

# Virksomhedsoplysninger
st.sidebar.header("Virksomhedsoplysninger")
firma_navn = st.sidebar.text_input("Virksomhedsnavn", value="Eksempel ApS")
branche = st.sidebar.text_input("Branche", value="Produktion")
rapport_aar = st.sidebar.text_input("Rapportår", value="2025")

# Inputfelter med hjælpetekster
with st.expander("🔌 Energiforbrug"):
    el = st.number_input("Elforbrug (kWh pr. år)", min_value=0.0, step=100.0,
                         help="Du finder dette på din årlige elregning eller ved at samle månedsforbrug. Angives i kilowatt-timer (kWh).")
    gas = st.number_input("Gasforbrug (m³ pr. år)", min_value=0.0, step=10.0,
                          help="Du finder dette på din årlige gasregning eller leverandørens årsopgørelse. Angives i kubikmeter (m³).")

with st.expander("🚚 Transport"):
    km_varebil = st.number_input("Kilometer kørt i varebil (pr. år)", min_value=0.0, step=100.0,
                                 help="Samlet antal kilometer kørt af virksomhedens varebiler pr. år. Kan findes i kørebog eller regnskab for firmabiler.")
    km_lastbil = st.number_input("Kilometer kørt i lastbil (pr. år)", min_value=0.0, step=100.0,
                                 help="Samlet antal kilometer kørt af virksomhedens lastbiler pr. år.")

with st.expander("🏗 Materialer"):
    kg_staal = st.number_input("Stålforbrug (kg pr. år)", min_value=0.0, step=10.0,
                               help="Vægt af stål anvendt i produktion, byggeri eller projekter pr. år.")
    kg_trae = st.number_input("Træforbrug (kg pr. år)", min_value=0.0, step=10.0,
                              help="Vægt af træ anvendt i produktion, emballage eller byggeri pr. år.")
    kg_plast = st.number_input("Plastforbrug (kg pr. år)", min_value=0.0, step=10.0,
                               help="Vægt af plast anvendt i emballage, komponenter mv. pr. år.")
    kg_beton = st.number_input("Betonforbrug (kg pr. år)", min_value=0.0, step=10.0,
                               help="Vægt af beton anvendt i byggeri eller projekter pr. år.")
    kg_alu = st.number_input("Aluminiumforbrug (kg pr. år)", min_value=0.0, step=10.0,
                             help="Vægt af aluminium anvendt i produktion, byggeri mv. pr. år.")
    kg_papir = st.number_input("Papir/papforbrug (kg pr. år)", min_value=0.0, step=10.0,
                               help="Vægt af papir og pap anvendt i kontor, emballage mv. pr. år.")

# Beregning
if st.button("Beregn CO2-aftryk"):
    co2_el = el * FAKTOR_EL
    co2_gas = gas * FAKTOR_GAS
    co2_varebil = km_varebil * FAKTOR_VAREBIL
    co2_lastbil = km_lastbil * FAKTOR_LASTBIL
    co2_staal = kg_staal * FAKTOR_STAAL
    co2_trae = kg_trae * FAKTOR_TRAE
    co2_plast = kg_plast * FAKTOR_PLAST
    co2_beton = kg_beton * FAKTOR_BETON
    co2_alu = kg_alu * FAKTOR_ALU
    co2_papir = kg_papir * FAKTOR_PAPIR

    co2_total = (co2_el + co2_gas + co2_varebil + co2_lastbil +
                 co2_staal + co2_trae + co2_plast + co2_beton +
                 co2_alu + co2_papir)

    st.session_state['co2_values'] = {
        'co2_el': co2_el,
        'co2_gas': co2_gas,
        'co2_varebil': co2_varebil,
        'co2_lastbil': co2_lastbil,
        'co2_staal': co2_staal,
        'co2_trae': co2_trae,
        'co2_plast': co2_plast,
        'co2_beton': co2_beton,
        'co2_alu': co2_alu,
        'co2_papir': co2_papir,
        'co2_total': co2_total
    }

    st.success(f"Samlet CO2-aftryk: {co2_total:.2f} kg CO2e pr. år")
    st.bar_chart({
        "CO2e (kg)": {
            "Energi": co2_el + co2_gas,
            "Transport": co2_varebil + co2_lastbil,
            "Materialer": co2_staal + co2_trae + co2_plast + co2_beton + co2_alu + co2_papir
        }
    })

# Download
vals = st.session_state.get('co2_values')
if vals:
    df = pd.DataFrame({
        'Kategori': [
            'El', 'Gas', 'Varebil', 'Lastbil',
            'Stål', 'Træ', 'Plast', 'Beton', 'Aluminium', 'Papir/pap'
        ],
        'CO2e (kg)': [
            vals['co2_el'], vals['co2_gas'], vals['co2_varebil'], vals['co2_lastbil'],
            vals['co2_staal'], vals['co2_trae'], vals['co2_plast'], vals['co2_beton'],
            vals['co2_alu'], vals['co2_papir']
        ]
    })
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("⬇ Download data som CSV", data=csv, file_name="klimadata.csv", mime="text/csv")

    # PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 20)
    pdf.cell(0, 15, "Klimarapport", ln=True, align='C')
    pdf.set_draw_color(34, 139, 34)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Virksomhed: {firma_navn}", ln=True)
    pdf.cell(0, 8, f"Branche: {branche}", ln=True)
    pdf.cell(0, 8, f"Rapportår: {rapport_aar}", ln=True)
    pdf.cell(0, 8, f"Genereret: {datetime.now().strftime('%d-%m-%Y')}", ln=True)
    pdf.ln(3)

    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(34, 139, 34)
    pdf.cell(0, 10, f"Samlet CO2-aftryk: {vals['co2_total']:.2f} kg CO2e pr. år", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(2)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(2)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Fordeling:", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, f"Energi: {vals['co2_el'] + vals['co2_gas']:.2f} kg CO2e", ln=True)
    pdf.cell(0, 6, f"Transport: {vals['co2_varebil'] + vals['co2_lastbil']:.2f} kg CO2e", ln=True)
    material_total = sum([vals['co2_staal'], vals['co2_trae'], vals['co2_plast'],
                          vals['co2_beton'], vals['co2_alu'], vals['co2_papir']])
    pdf.cell(0, 6, f"Materialer: {material_total:.2f} kg CO2e", ln=True)
    pdf.ln(2)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Materialefordeling:", ln=True)
    pdf.set_font("Arial", "", 10)
    max_val = max([vals['co2_staal'], vals['co2_trae'], vals['co2_plast'],
                   vals['co2_beton'], vals['co2_alu'], vals['co2_papir']])
    bar_max_width = 120

    for name, value in [
        ("Stål", vals['co2_staal']),
        ("Træ", vals['co2_trae']),
        ("Plast", vals['co2_plast']),
        ("Beton", vals['co2_beton']),
        ("Aluminium", vals['co2_alu']),
        ("Papir/pap", vals['co2_papir'])
    ]:
        pct = (value / material_total * 100) if material_total > 0 else 0
        pdf.cell(0, 6, f"{name}: {value:.2f} kg CO2e ({pct:.1f}%)", ln=True)
        bar_width = (value / max_val) * bar_max_width if max_val > 0 else 0
        y = pdf.get_y()
        pdf.set_fill_color(34, 139, 34)
        pdf.rect(20, y, bar_width, 4, style='F')
        pdf.ln(5)

    pdf.ln(2)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(2)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Metode og tillid:", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(80, 80, 80)
    pdf.multi_cell(0, 6,
                   "Baseret på brugerindtastede tal og standard emissionsfaktorer.\n"
                   "Scope 1 og 2 er dækket, scope 3 ikke inkluderet.\n"
                   "Denne rapport er vejledende og ikke verificeret af tredjepart.")
    pdf.set_text_color(0, 0, 0)

    pdf.set_y(-15)
    pdf.set_font("Arial", "I", 8)
    pdf.cell(0, 10, "Genereret af Klimaklar SMB", 0, 0, 'C')

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    buffer = io.BytesIO(pdf_bytes)

    st.download_button(
        label="💾 Download rapport som PDF",
        data=buffer,
        file_name="klimarapport.pdf",
        mime="application/pdf"
    )
else:
    st.download_button(
        label="💾 Download rapport som PDF",
        data=b"",
        file_name="klimarapport.pdf",
        disabled=True
    )
    st.download_button(
        label="⬇ Download data som CSV",
        data=b"",
        file_name="klimadata.csv",
        disabled=True
    )
