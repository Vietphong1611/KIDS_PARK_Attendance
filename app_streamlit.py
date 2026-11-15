import streamlit as st
import cv2
import numpy as np
import pandas as pd
import os
import urllib.request
import datetime
import importlib
import database

# Nạp lại module database tự động
importlib.reload(database)

from database import (
    check_login, add_employee, get_all_faces, record_attendance, 
    get_attendance_history, get_employee_attendance, 
    get_weekly_schedule_matrix, save_weekly_schedule_matrix,
    get_employee_face_status, update_employee_face, get_monthly_attendance_report
)

st.set_page_config(page_title="KIDS PARK Attendance", layout="wide")

# --- QUẢN LÝ TRẠNG THÁI ĐĂNG NHẬP ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['user'] = None

# -------------------------------------------------------------
# MÀN HÌNH ĐĂNG NHẬP
# -------------------------------------------------------------
if not st.session_state['logged_in']:
    st.title("🎡 HỆ THỐNG ĐIỂM DANH NHÂN SỰ - KIDS PARK")
    st.subheader("🔐 Đăng nhập hệ thống")

    col1, col2 = st.columns([1, 1])
    with col1:
        ma_nv = st.text_input("Mã Nhân Viên / Quản Lý (VD: QL01 hoặc NV01)")
        mat_khau = st.text_input("Mật khẩu", type="password")
        
        if st.button("🚀 Đăng nhập", use_container_width=True):
            if ma_nv and mat_khau:
                user = check_login(ma_nv, mat_khau)
                if user:
                    st.session_state['logged_in'] = True
                    st.session_state['user'] = user
                    st.success(f"🎉 Đăng nhập thành công! Xin chào {user['ho_ten']}")
                    st.rerun()
                else:
                    st.error("❌ Mã nhân viên hoặc Mật khẩu không chính xác!")
            else:
                st.warning("⚠️ Vui lòng nhập đầy đủ Mã NV và Mật khẩu.")

    with col2:
        st.info("""
        💡 **Tài khoản mặc định để thử nghiệm:**
        * **Quản lý (Manager):** Mã: `QL01` | Mật khẩu: `123456`
        * **Nhân viên (Staff):** Mã NV đã thêm mới | Mật khẩu mặc định: `123456`
        """)

# -------------------------------------------------------------
# GIAO DIỆN CHÍNH
# -------------------------------------------------------------
else:
    user = st.session_state['user']
    st.sidebar.title("🎡 KIDS PARK")
    st.sidebar.write(f"👤 **{user['ho_ten']}**")
    role_label = "🔴 Quản lý" if user['vai_tro'] == 'Quan_ly' else "🟢 Nhân viên"
    st.sidebar.write(f"Chức vụ: **{user['chuc_vu']}** ({role_label})")
    
    if st.sidebar.button("🚪 Đăng xuất", use_container_width=True):
        st.session_state['logged_in'] = False
        st.session_state['user'] = None
        st.rerun()

    st.sidebar.divider()

    CASCADE_FILE = "haarcascade_frontalface_default.xml"
    if not os.path.exists(CASCADE_FILE):
        url = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"
        with st.spinner("Đang tải tệp mô hình nhận diện khuôn mặt..."):
            urllib.request.urlretrieve(url, CASCADE_FILE)

    #face_cascade = cv2.CascadeClassifier(CASCADE_FILE)

    # Menu Phân quyền
    if user['vai_tro'] == 'Quan_ly':
        menu = [
            "👤 Thêm Nhân Viên Mới", 
            "📅 Quản lý lịch phân ca", 
            "📊 Trích xuất Bảng công Tháng", 
            "📋 Lịch sử chấm công toàn bộ"
        ]
    else:
        menu = [
            "📸 Điểm danh Webcam", 
            "📅 Lịch làm việc cá nhân", 
            "📋 Lịch sử điểm danh cá nhân"
        ]

    choice = st.sidebar.selectbox("Chức năng hệ thống", menu)

    # =========================================================
    # CHỨC NĂNG 1: THÊM NHÂN VIÊN MỚI (Quản lý)
    # =========================================================
    if choice == "👤 Thêm Nhân Viên Mới":
        st.header("👤 Đăng ký Nhân viên Mới")
        st.info("ℹ️ Quản lý chỉ cần nhập thông tin. Nhân viên sẽ tự chụp ảnh khuôn mặt khi đăng nhập và điểm danh lần đầu.")
        
        col1, col2 = st.columns(2)
        with col1:
            ma_nv = st.text_input("Mã Nhân Viên (VD: NV01)")
            ho_ten = st.text_input("Họ và Tên")
            mat_khau_nv = st.text_input("Mật khẩu tài khoản", value="123456")
        with col2:
            chuc_vu = st.selectbox("Chức vụ", ["Soát vé", "Giám sát trò chơi", "Thu ngân", "Kỹ thuật", "Vệ sinh"])
            khu_vuc = st.text_input("Khu vực phụ trách", "Khu nhà bạt")
            vai_tro_nv = st.selectbox("Vai trò hệ thống", ["Nhan_vien", "Quan_ly"])

        if st.button("💾 Lưu Thông Tin Nhân Viên", use_container_width=True):
            if ma_nv and ho_ten:
                try:
                    add_employee(ma_nv, ho_ten, chuc_vu, khu_vuc, face_encoding=None, mat_khau=mat_khau_nv, vai_tro=vai_tro_nv)
                    st.success(f"✅ Đã tạo thành công tài khoản nhân viên: **{ho_ten}** (Mã: {ma_nv})!")
                except Exception as e:
                    st.error(f"❌ Lỗi thêm nhân viên (Có thể Mã NV đã tồn tại): {e}")
            else:
                st.warning("⚠️ Vui lòng nhập đầy đủ Mã NV và Họ tên.")

    # =========================================================
    # CHỨC NĂNG 2: BẢNG PHÂN CA MA TRẬN TUẦN (Quản lý)
    # =========================================================
    elif choice == "📅 Quản lý lịch phân ca":
        st.header("📅 Bảng Phân Công Ca Làm Việc Theo Tuần")
        
        today = datetime.date.today()
        start_of_week = today - datetime.timedelta(days=today.weekday())
        selected_start_date = st.date_input("🗓️ Chọn ngày Thứ 2 đầu tuần:", start_of_week, key="ql_week_picker")
        
        st.info("""
        💡 **Quy ước mã ca:**
        * **A**: Ca Sáng (8h - 12h) | **C**: Ca Chiều (13h - 17h) | **T**: Ca Tối (17h30 - 21h30)
        * **AC**: Cả ngày (Sáng + Chiều) | **AT**: Sáng + Tối | **OFF**: Nghỉ ca
        """)
        
        matrix_data = get_weekly_schedule_matrix(selected_start_date)
        
        if not matrix_data:
            st.warning("⚠️ Chưa có nhân viên nào trong hệ thống!")
        else:
            df = pd.DataFrame(matrix_data)
            shift_codes = ['OFF', 'A', 'C', 'T', 'AC', 'AT']
            column_config = {
                'id': None,
                'Mã NV': st.column_config.TextColumn("Mã NV", disabled=True),
                'Họ và Tên': st.column_config.TextColumn("Họ và Tên", disabled=True),
                'T2': st.column_config.SelectboxColumn("Thứ 2", options=shift_codes, required=True),
                'T3': st.column_config.SelectboxColumn("Thứ 3", options=shift_codes, required=True),
                'T4': st.column_config.SelectboxColumn("Thứ 4", options=shift_codes, required=True),
                'T5': st.column_config.SelectboxColumn("Thứ 5", options=shift_codes, required=True),
                'T6': st.column_config.SelectboxColumn("Thứ 6", options=shift_codes, required=True),
                'T7': st.column_config.SelectboxColumn("Thứ 7", options=shift_codes, required=True),
                'CN': st.column_config.SelectboxColumn("Chủ Nhật", options=shift_codes, required=True),
            }
            
            st.subheader("📝 Bảng điều chỉnh phân ca trực tiếp:")
            edited_df = st.data_editor(
                df, 
                column_config=column_config, 
                hide_index=True, 
                use_container_width=True
            )
            
            if st.button("💾 Lưu Bảng Phân Ca Tuần", use_container_width=True):
                updated_matrix = edited_df.to_dict('records')
                save_weekly_schedule_matrix(updated_matrix, selected_start_date)
                st.success("✅ Đã cập nhật bảng phân ca tuần thành công vào CSDL MySQL!")

 # =========================================================
    # CHỨC NĂNG 3: TRÍCH XUẤT BẢNG CÔNG THÁNG (Quản lý)
    # =========================================================
    elif choice == "📊 Trích xuất Bảng công Tháng":
        st.header("📊 Bảng Tổng Hợp Chấm Công Theo Tháng")
        
        col_m, col_y = st.columns(2)
        current_now = datetime.datetime.now()
        
        with col_m:
            selected_month = st.selectbox("Chọn Tháng", list(range(1, 13)), index=current_now.month - 1)
        with col_y:
            selected_year = st.selectbox("Chọn Năm", list(range(2024, 2030)), index=current_now.year - 2024)
            
        report_data = get_monthly_attendance_report(selected_month, selected_year)
        
        if report_data:
            df_report = pd.DataFrame(report_data)
            st.subheader(f"📋 Bảng công Nhân viên Tháng {selected_month}/{selected_year}")
            st.dataframe(df_report, use_container_width=True)
            
            # Xuất định dạng file Excel (.xlsx) trực tiếp
            import io
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_report.to_excel(writer, index=False, sheet_name=f"BangCong_T{selected_month}")
            buffer.seek(0)
            
            st.download_button(
                label=f"📥 Tải Bảng Công Tháng {selected_month}_{selected_year} (File Excel .xlsx)",
                data=buffer,
                file_name=f"Bang_Cong_KidsPark_T{selected_month}_{selected_year}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        else:
            st.info(f"ℹ️ Chưa có dữ liệu chấm công nào trong tháng {selected_month}/{selected_year}.")
    # =========================================================
    # CHỨC NĂNG 4: LỊCH SỬ CHẤM CÔNG TOÀN BỘ (Quản lý)
    # =========================================================
    elif choice == "📋 Lịch sử chấm công toàn bộ":
        st.header("📋 Bảng Lịch Sử Điểm Danh Nhân Viên")
        history_data = get_attendance_history()

        if history_data:
            df = pd.DataFrame(history_data)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Tổng số lượt điểm danh", len(df))
            with col2:
                st.metric("Số nhân viên đã check-in", df['Mã NV'].nunique())
            with col3:
                st.metric("Lần check-in mới nhất", str(df['Thời gian Check-in'].iloc[0]))

            st.divider()
            st.dataframe(df, use_container_width=True)
        else:
            st.info("ℹ️ Chưa có dữ liệu điểm danh nào.")

    # =========================================================
    # CHỨC NĂNG 5: ĐIỂM DANH WEBCAM (Nhân viên)
    # =========================================================
    elif choice == "📸 Điểm danh Webcam":
        st.header("📸 Màn hình Điểm Danh Real-time")
        
        has_face = get_employee_face_status(user['id'])
        
        if not has_face:
            st.info("ℹ️ **Đăng ký lần đầu:** Bạn chưa có ảnh khuôn mặt mẫu trên hệ thống. Ảnh chụp lần này sẽ được **tự động đăng ký** và **điểm danh lượt đầu tiên** cho bạn!")
            img_label = "📸 Chụp ảnh mặt để ĐĂNG KÝ & ĐIỂM DANH LẦN ĐẦU"
        else:
            img_label = "📸 Chụp ảnh mặt để điểm danh"

        img_file_buffer = st.camera_input(img_label)

        if img_file_buffer is not None:
            bytes_data = img_file_buffer.getvalue()
            cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
            gray = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2GRAY)

            class face_cascade:
                ...

            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            if len(faces) > 0:
                (x, y, w, h) = faces[0]
                face_crop = cv2.resize(gray[y:y+h, x:x+w], (100, 100)).flatten()

                if not has_face:
                    update_employee_face(user['id'], face_crop)
                    record_attendance(user['id'], trang_thai='Dung_gio')
                    st.balloons()
                    st.success(f"🎉 **Đăng ký khuôn mặt thành công!** Đã lưu ảnh mẫu và ghi nhận điểm danh cho: **{user['ho_ten']}** (Mã: {user['ma_nv']})")
                else:
                    record_attendance(user['id'], trang_thai='Dung_gio')
                    st.balloons()
                    st.success(f"🎉 **Điểm danh thành công!** Xin chào: **{user['ho_ten']}** (Mã NV: {user['ma_nv']})")
            else:
                st.error("❌ Không tìm thấy khuôn mặt trong khung hình!")

    # =========================================================
    # CHỨC NĂNG 6: LỊCH LÀM VIỆC CÁ NHÂN (Nhân viên)
    # =========================================================
    elif choice == "📅 Lịch làm việc cá nhân":
        st.header(f"📅 Lịch Trực Theo Tuần Của Nhân Viên: {user['ho_ten']}")
        
        today = datetime.date.today()
        start_of_week = today - datetime.timedelta(days=today.weekday())
        selected_start_date = st.date_input("🗓️ Chọn ngày Thứ 2 đầu tuần:", start_of_week, key="nv_week_picker")
        
        st.info("""
        💡 **Quy ước mã ca:**
        * **A**: Ca Sáng (8h - 12h) | **C**: Ca Chiều (13h - 17h) | **T**: Ca Tối (17h30 - 21h30)
        * **AC**: Cả ngày (Sáng + Chiều) | **AT**: Sáng + Tối | **OFF**: Nghỉ ca
        """)
        
        my_matrix = get_weekly_schedule_matrix(selected_start_date, nhan_vien_id=user['id'])
        
        if my_matrix:
            df_my = pd.DataFrame(my_matrix)
            if 'id' in df_my.columns:
                df_my = df_my.drop(columns=['id'])
            st.dataframe(df_my, use_container_width=True, hide_index=True)
        else:
            st.info("ℹ️ Bạn chưa có lịch phân ca nào trong tuần này.")

    # =========================================================
    # CHỨC NĂNG 7: LỊCH SỬ ĐIỂM DANH CÁ NHÂN (Nhân viên)
    # =========================================================
    elif choice == "📋 Lịch sử điểm danh cá nhân":
        st.header(f"📋 Lịch Sử Check-in Của: {user['ho_ten']}")
        my_history = get_employee_attendance(user['id'])
        if my_history:
            st.dataframe(pd.DataFrame(my_history), use_container_width=True)
        else:
            st.info("ℹ️ Bạn chưa thực hiện lượt điểm danh nào.")