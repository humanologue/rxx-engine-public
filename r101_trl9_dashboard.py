# r101_trl9_dashboard_v99.py - V9.9 FIX datetime + 11 COLS
import streamlit as st
from r_engine import TRLEngine
import pandas as pd
from datetime import datetime  # ← FIX CRITIQUE AJOUTÉ

def main():
    st.set_page_config(page_title="TRL9 DASHBOARD V9.9", layout="wide")
    st.title("🌍 TRL9 GLOBAL DASHBOARD V9.9 - 11 COLS REFERENCE")
    
    engine = TRLEngine()
    
    st.sidebar.header("⚙️ CONTROLES")
    if st.sidebar.button("🔍 SCAN MODULES"):
        engine.discover()
        st.session_state.modules = engine.modules
        st.sidebar.success(f"✅ {len(engine.modules)} modules")
    
    if 'modules' in st.session_state:
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("TOTAL", len(engine.modules), f"{len(engine.modules)/201*100:.1f}%")
        with col2: 
            working = st.session_state.get('working_sources', 0) if 'results' in st.session_state else 0
            st.metric("WORKING", working, "-")
        with col3: st.metric("SOURCES>0", "0/0", "-")
        with col4: st.metric("STATUS", "V9.9 REFERENCE", "✅")

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🚀 TEST TOUS"):
                with st.spinner("Exécution TRL9 V9.9..."):
                    results = engine.process_all_nodes()  # ✅ Now properly scoped
                    st.session_state.results = results
                    working = sum(1 for r in results.values() if r['statut'] == '🟢')
                    st.session_state.working_sources = working
                    st.balloons()
                    st.success(f"🎉 {working}/{len(results)} modules 🟢!")

        with col_b:
            if st.button("💾 EXPORT CSV REFERENCE") and 'results' in st.session_state:
                export_csv_ref(st.session_state.results)

    
    # FIX SessionState - TOUT DANS if 'results'
    if 'results' in st.session_state:
        display_results_v99(st.session_state.results, engine.modules)

def display_results_v99(results, modules):
    total = len(results)
    working = sum(1 for r in results.values() if r['statut'] == '🟢')
    
    st.subheader("📊 RÉSUMÉ TRL9 V9.9")
    col1, col2, col3 = st.columns(3)
    col1.metric("TOTAL", total, f"{total/201*100:.1f}%")
    col2.metric("🟢 OK", f"{working}/{total}", f"{working/total*100:.1f}%")
    col3.metric("DOMAINE", len(set(r['domain'] for r in results.values())), "Varié")
    
    # DataFrame 9 COLS (vue synthétique)
    df_data = []
    for r_num, data in results.items():
        df_data.append({
            'ID': data['id'],
            'Métrique': data['metric'][:25],
            'Valeur': data['reel'],
            'Seuil': data['seuil'],
            'Statut': data['statut'],
            'Source': data['source'],
            'Domaine': data['domain'],
            'Freshness': data['freshness']
        })
    
    df = pd.DataFrame(df_data)
    st.dataframe(df, width="stretch", height=600)
    
    # Exports
    col_export1, col_export2 = st.columns(2)
    with col_export1:
        csv_full = pd.DataFrame(list(results.values())).to_csv(index=False).encode('utf-8')
        st.download_button("💾 CSV COMPLET 11 COLS", csv_full, "TRL9_V99_FULL.csv", "text/csv")
    
    with col_export2:
        csv_summary = df.to_csv(index=False).encode('utf-8')
        st.download_button("📊 CSV SYNTHÈSE", csv_summary, "TRL9_V99_SUMMARY.csv", "text/csv")

def export_csv_ref(results):
    """🎯 EXPORT CSV REFERENCE 11 COLS"""
    df = pd.DataFrame(list(results.values()))
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')  # ← MAINTENANT OK
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "💾 CSV REFERENCE OPEX", 
        csv, 
        f"TRL9_V99_{timestamp}.csv",  # ← FIXÉ
        "text/csv"
    )
    st.success(f"✅ TRL9_V99_{timestamp}.csv généré!")

if __name__ == "__main__":
    main()
