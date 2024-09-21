import streamlit as st
from utab.app.main_page import main_page
from utab.app.request_page import request_page
from utab.app.chart_page import show_charts
from admin import admin_page 
from utab.app.teacher_page import teacher_page

# Sayfa takibi için session state'i başlat
if 'selected_page' not in st.session_state:
    st.session_state['selected_page'] = 'Ana Sayfa'

def render_navigation():
    st.sidebar.title("Haliç Üniversitesi")  # Yan menü başlığı
    
    # Bölüm: Hesap
    st.sidebar.markdown("### Hesap")
    if st.sidebar.button("🔗 Çıkış Yap"):  # Çıkış yap butonu
        st.session_state['teacher_info'] = None
        st.rerun()
    
    # Bölüm: Raporlar
    st.sidebar.markdown("### Raporlar")

    # Buton görünürlüğünü koru ve session state'de seçilen sayfayı güncelle
    if st.sidebar.button("📊 Ana Sayfa"):
        st.session_state['selected_page'] = "Ana Sayfa"
    if st.sidebar.button("📄 Talep"):
        st.session_state['selected_page'] = "Talep"
    if st.sidebar.button("📈 Grafikler"):
        st.session_state['selected_page'] = "Grafikler"
    if st.sidebar.button("📈 Sınav Portalı"):
        st.session_state['selected_page'] = "Portal"

    # Kullanıcı 'admin' ise Admin Sayfası butonunu göster
    if st.session_state['teacher_info'] and st.session_state['teacher_info'][1] == 'admin':  # Giriş yapan kullanıcının 'admin' olup olmadığını kontrol et
        st.sidebar.markdown("### Admin")
        if st.sidebar.button("🔧 Sınav Portalı "):
            st.session_state['selected_page'] = "Admin"

def handle_navigation():
    # Navigasyon menüsünü oluştur
    render_navigation()

    # Session state'e göre seçilen sayfayı göster
    if st.session_state['selected_page'] == "Ana Sayfa":
        main_page()
    elif st.session_state['selected_page'] == "Talep":
        request_page()
    elif st.session_state['selected_page'] == "Grafikler":
        show_charts()
    elif st.session_state['selected_page'] == "Portal":
        teacher_page()  # Admin sayfasını çağır
    elif st.session_state['selected_page'] == "Admin":
        admin_page()  # Admin sayfasını çağır

if __name__ == "__main__":
    handle_navigation()
