import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import mysql.connector
import bcrypt
import os
import shutil
from datetime import datetime

# --- KONFIGURASI DATABASE ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # sesuaikan dengan MySQL Anda
    'database': 'pengarsipan_surat'
}

UPLOAD_FOLDER = "upload_files"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- Fungsi koneksi ---
def get_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Gagal koneksi DB: {e}")
        return None

# --- Fungsi hash password ---
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def check_password(password, hashed):
    if isinstance(hashed, str):
        hashed = hashed.encode()
    return bcrypt.checkpw(password.encode(), hashed)

# --- Login Window ---
class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Login Pengarsipan Surat")
        self.geometry("320x250")  # sedikit lebih tinggi untuk tombol Sign Up

        tk.Label(self, text="Username").pack(pady=5)
        self.entry_user = tk.Entry(self)
        self.entry_user.pack()

        tk.Label(self, text="Password").pack(pady=5)
        self.entry_pass = tk.Entry(self, show='*')
        self.entry_pass.pack()

        tk.Button(self, text="Login", command=self.login).pack(pady=10)
        tk.Button(self, text="Sign Up", command=self.open_signup).pack(pady=5)

    def login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Username dan password harus diisi")
            return

        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password_hash, role FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password(password, user[2]):
            self.destroy()
            user_id, user_name, _, role = user
            if role == 'Admin':
                AdminDashboard(user_id, user_name).mainloop()
            else:
                UserDashboard(user_id, user_name).mainloop()
        else:
            messagebox.showerror("Error", "Username atau password salah")

    def open_signup(self):
        SignupWindow(self)

# --- Sign Up Window ---
class SignupWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Daftar User Baru")
        self.geometry("350x250")
        self.parent = parent

        tk.Label(self, text="Username").pack(pady=5)
        self.entry_username = tk.Entry(self)
        self.entry_username.pack()

        tk.Label(self, text="Password").pack(pady=5)
        self.entry_password = tk.Entry(self, show='*')
        self.entry_password.pack()

        tk.Label(self, text="Role").pack(pady=5)
        self.role_var = tk.StringVar()
        self.role_var.set("User")
        self.role_option = ttk.Combobox(self, values=["User"], textvariable=self.role_var, state="readonly")
        self.role_option.pack()

        tk.Button(self, text="Daftar", command=self.register_user).pack(pady=15)

    def register_user(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get()
        role = self.role_var.get()

        if not username or not password:
            messagebox.showerror("Error", "Username dan password harus diisi")
            return

        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM users WHERE username=%s", (username,))
            if cursor.fetchone():
                messagebox.showerror("Error", "Username sudah digunakan")
                return
            pw_hash = hash_password(password)   
            cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                           (username, pw_hash, role))
            conn.commit()
            messagebox.showinfo("Sukses", f"User {username} berhasil didaftarkan")
            self.destroy()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Gagal daftar user: {e}")
        finally:
            cursor.close()
            conn.close()

# --- Dashboard Admin ---
class AdminDashboard(tk.Tk):
    def __init__(self, user_id, username):
        super().__init__()
        self.title(f"Dashboard Admin - {username}")
        self.geometry("1000x650")
        self.user_id = user_id
        self.username = username

        self.sidebar = tk.Frame(self, width=220, bg="#cccccc")
        self.sidebar.pack(side='left', fill='y')

        tk.Label(self.sidebar, text=f"Admin: {username}", bg="#cccccc", font=("Arial", 12, 'bold')).pack(pady=10)

        btn_user = tk.Button(self.sidebar, text="Manajemen User", command=self.show_manajemen_user)
        btn_user.pack(fill='x', pady=5, padx=10)

        btn_surat = tk.Button(self.sidebar, text="Manajemen Surat", command=self.show_manajemen_surat)
        btn_surat.pack(fill='x', pady=5, padx=10)

        btn_riwayat = tk.Button(self.sidebar, text="Riwayat Pengarsipan", command=self.show_riwayat)
        btn_riwayat.pack(fill='x', pady=5, padx=10)

        btn_logout = tk.Button(self.sidebar, text="Logout", fg="red", command=self.logout)
        btn_logout.pack(fill='x', pady=20, padx=10)

        self.container = tk.Frame(self)
        self.container.pack(side='right', fill='both', expand=True)

        self.current_frame = None
        self.show_welcome()

    def logout(self):
        self.destroy()
        LoginWindow().mainloop()

    def show_welcome(self):
        self.clear_container()
        lbl = tk.Label(self.container, text=f"Selamat datang {self.username}", font=("Arial", 18))
        lbl.pack(expand=True)

    def clear_container(self):
        if self.current_frame:
            self.current_frame.destroy()
            self.current_frame = None

    def show_manajemen_user(self):
        self.clear_container()
        self.current_frame = ManajemenUser(self.container)
        self.current_frame.pack(fill='both', expand=True)

    def show_manajemen_surat(self):
        self.clear_container()
        self.current_frame = ManajemenSurat(self.container, self.user_id, 'Admin')
        self.current_frame.pack(fill='both', expand=True)

    def show_riwayat(self):
        self.clear_container()
        self.current_frame = RiwayatPengarsipan(self.container)
        self.current_frame.pack(fill='both', expand=True)

# --- Dashboard User ---
class UserDashboard(tk.Tk):
    def __init__(self, user_id, username):
        super().__init__()
        self.title(f"Dashboard User - {username}")
        self.geometry("1000x650")
        self.user_id = user_id
        self.username = username

        btn_logout = tk.Button(self, text="Logout", fg="red", command=self.logout)
        btn_logout.pack(pady=10)

        lbl = tk.Label(self, text=f"Selamat datang {username}", font=("Arial", 18))
        lbl.pack(pady=20)

        self.manajemen_surat = ManajemenSurat(self, self.user_id, 'User')
        self.manajemen_surat.pack(fill='both', expand=True)

    def logout(self):
        self.destroy()
        LoginWindow().mainloop()

# --- Manajemen User (Admin) ---
class ManajemenUser(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.selected_user_id = None

        form_frame = tk.Frame(self)
        form_frame.pack(fill='x', padx=20, pady=10)

        tk.Label(form_frame, text="Username").grid(row=0, column=0, sticky='w')
        self.entry_username = tk.Entry(form_frame)
        self.entry_username.grid(row=0, column=1, sticky='w')

        tk.Label(form_frame, text="Password").grid(row=1, column=0, sticky='w')
        self.entry_password = tk.Entry(form_frame, show='*')
        self.entry_password.grid(row=1, column=1, sticky='w')

        tk.Label(form_frame, text="Role").grid(row=2, column=0, sticky='w')
        self.role_var = tk.StringVar()
        self.role_var.set('User')
        self.role_option = ttk.Combobox(form_frame, values=['Admin', 'User'], textvariable=self.role_var, state='readonly')
        self.role_option.grid(row=2, column=1, sticky='w')

        btn_save = tk.Button(form_frame, text="Simpan User", command=self.save_user)
        btn_save.grid(row=3, column=1, sticky='w', pady=10)

        btn_cancel = tk.Button(form_frame, text="Batal", command=self.reset_form)
        btn_cancel.grid(row=3, column=2, sticky='w', pady=10)

        self.tree = ttk.Treeview(self, columns=('id', 'username', 'role'), show='headings')
        self.tree.heading('id', text='ID')
        self.tree.heading('username', text='Username')
        self.tree.heading('role', text='Role')
        self.tree.column('id', width=50, anchor='center')
        self.tree.pack(fill='both', expand=True, padx=20, pady=10)
        self.tree.bind("<Double-1>", self.on_edit)

        btn_delete = tk.Button(self, text="Hapus User Terpilih", command=self.delete_user)
        btn_delete.pack(pady=5)

        self.load_users()

    def load_users(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role FROM users ORDER BY id ASC")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in rows:
            self.tree.insert('', 'end', values=row)

    def save_user(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get()
        role = self.role_var.get()

        if not username or (self.selected_user_id is None and not password):
            messagebox.showerror("Error", "Username dan password wajib diisi")
            return

        conn = get_connection()
        cursor = conn.cursor()
        try:
            if self.selected_user_id is None:
                cursor.execute("SELECT id FROM users WHERE username=%s", (username,))
                if cursor.fetchone():
                    messagebox.showerror("Error", "Username sudah dipakai")
                    return
                pw_hash = hash_password(password)
                cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                               (username, pw_hash, role))
                messagebox.showinfo("Sukses", "User berhasil ditambahkan")
            else:
                if password:
                    pw_hash = hash_password(password)
                    cursor.execute("UPDATE users SET username=%s, password_hash=%s, role=%s WHERE id=%s",
                                   (username, pw_hash, role, self.selected_user_id))
                else:
                    cursor.execute("UPDATE users SET username=%s, role=%s WHERE id=%s",
                                   (username, role, self.selected_user_id))
                messagebox.showinfo("Sukses", "User berhasil diupdate")
            conn.commit()
            self.reset_form()
            self.load_users()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Gagal menyimpan user: {e}")
        finally:
            cursor.close()
            conn.close()

    def reset_form(self):
        self.selected_user_id = None
        self.entry_username.delete(0, tk.END)
        self.entry_password.delete(0, tk.END)
        self.role_var.set('User')

    def on_edit(self, event):
        item = self.tree.selection()
        if not item:
            return
        item = item[0]
        user_id, username, role = self.tree.item(item, 'values')
        self.selected_user_id = user_id
        self.entry_username.delete(0, tk.END)
        self.entry_username.insert(0, username)
        self.entry_password.delete(0, tk.END)
        self.role_var.set(role)

    def delete_user(self):
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Peringatan", "Pilih user untuk dihapus")
            return
        item = item[0]
        user_id, username, _ = self.tree.item(item, 'values')

        if messagebox.askyesno("Konfirmasi", f"Yakin ingin menghapus user '{username}'?"):
            conn = get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
                conn.commit()
                messagebox.showinfo("Sukses", "User berhasil dihapus")
                self.load_users()
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Error", f"Gagal menghapus user: {e}")
            finally:
                cursor.close()
                conn.close()

# --- Manajemen Surat ---
class ManajemenSurat(tk.Frame):
    def __init__(self, parent, user_id, user_role):
        super().__init__(parent)
        self.user_id = int(user_id)
        self.user_role = user_role
        self.selected_surat_id = None
        self.filepath = None

        # Form input surat
        form_frame = tk.Frame(self)
        form_frame.pack(fill='x', padx=20, pady=10)

        labels = ["Nomor Surat", "Pengirim", "Tanggal Surat (YYYY-MM-DD)", "Perihal", "Isi Surat", "File Lampiran", "Kategori"]
        for i, text in enumerate(labels):
            tk.Label(form_frame, text=text).grid(row=i, column=0, sticky='w', pady=2)

        self.entry_nomor = tk.Entry(form_frame, width=50)
        self.entry_nomor.grid(row=0, column=1, sticky='w', pady=2)

        self.entry_pengirim = tk.Entry(form_frame, width=50)
        self.entry_pengirim.grid(row=1, column=1, sticky='w', pady=2)

        self.entry_tanggal = tk.Entry(form_frame, width=20)
        self.entry_tanggal.grid(row=2, column=1, sticky='w', pady=2)

        self.entry_perihal = tk.Entry(form_frame, width=50)
        self.entry_perihal.grid(row=3, column=1, sticky='w', pady=2)

        self.text_isi = tk.Text(form_frame, width=38, height=5)
        self.text_isi.grid(row=4, column=1, sticky='w', pady=2)

        self.label_file = tk.Label(form_frame, text="Belum ada file")
        self.label_file.grid(row=5, column=1, sticky='w', pady=2)

        tk.Button(form_frame, text="Upload File", command=self.upload_file).grid(row=5, column=2, sticky='w', padx=5)

        self.kategori_var = tk.StringVar()
        self.kategori_var.set("Masuk")
        self.option_kategori = ttk.Combobox(form_frame, values=["Masuk", "Keluar"], textvariable=self.kategori_var, state='readonly')
        self.option_kategori.grid(row=6, column=1, sticky='w', pady=2)

        tk.Button(form_frame, text="Simpan Surat", command=self.simpan_surat).grid(row=7, column=1, sticky='w', pady=10)
        tk.Button(form_frame, text="Batal", command=self.reset_form).grid(row=7, column=2, sticky='w', pady=10)

        # Filter & cari
        filter_frame = tk.Frame(self)
        filter_frame.pack(fill='x', padx=20)

        tk.Label(filter_frame, text="Filter Kategori").grid(row=0, column=0, sticky='w')
        self.filter_kategori_var = tk.StringVar()
        self.filter_kategori_var.set("Semua")
        self.filter_kategori = ttk.Combobox(filter_frame, values=["Semua", "Masuk", "Keluar"], textvariable=self.filter_kategori_var, state='readonly')
        self.filter_kategori.grid(row=0, column=1, sticky='w', padx=5)
        self.filter_kategori.bind("<<ComboboxSelected>>", lambda e: self.load_data())

        tk.Label(filter_frame, text="Cari Kata Kunci").grid(row=0, column=2, sticky='w', padx=10)
        self.search_var = tk.StringVar()
        self.entry_search = tk.Entry(filter_frame, textvariable=self.search_var, width=30)
        self.entry_search.grid(row=0, column=3, sticky='w')
        self.entry_search.bind('<KeyRelease>', lambda e: self.load_data())

        # Tabel surat
        self.tree = ttk.Treeview(self, columns=("id", "nomor_surat", "pengirim", "tanggal_surat", "perihal", "kategori", "username", "file_path", "user_id"), show="headings")
        headings = ["ID", "Nomor Surat", "Pengirim", "Tanggal Surat", "Perihal", "Kategori", "Pengarsip", "File", "User ID"]
        for col, hd in zip(self.tree['columns'], headings):
            self.tree.heading(col, text=hd)
        self.tree.column("id", width=40, anchor='center')
        self.tree.column("nomor_surat", width=140)
        self.tree.column("pengirim", width=140)
        self.tree.column("tanggal_surat", width=100, anchor='center')
        self.tree.column("perihal", width=180)
        self.tree.column("kategori", width=80, anchor='center')
        self.tree.column("username", width=100, anchor='center')
        self.tree.column("file_path", width=160)
        self.tree.column("user_id", width=80, anchor='center')

        self.tree.pack(fill='both', expand=True, padx=20, pady=10)
        self.tree.bind("<Double-1>", self.on_edit)

        tk.Button(self, text="Arsipkan Surat Terpilih", command=self.arsipkan_surat).pack(pady=5)

        self.load_data()

    def upload_file(self):
        ftypes = [("PDF files", "*.pdf"), ("DOCX files", "*.docx")]
        file_path = filedialog.askopenfilename(filetypes=ftypes)
        if file_path:
            self.filepath = file_path
            self.label_file.config(text=os.path.basename(file_path))

    def reset_form(self):
        self.selected_surat_id = None
        self.entry_nomor.delete(0, tk.END)
        self.entry_pengirim.delete(0, tk.END)
        self.entry_tanggal.delete(0, tk.END)
        self.entry_perihal.delete(0, tk.END)
        self.text_isi.delete('1.0', tk.END)
        self.label_file.config(text="Belum ada file")
        self.filepath = None
        self.kategori_var.set("Masuk")

    def load_data(self):
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        sql = "SELECT id, nomor_surat, pengirim, tanggal_surat, perihal, kategori, username, file_path, user_id FROM view_surat_aktif WHERE 1=1"
        params = []

        if self.filter_kategori_var.get() != "Semua":
            sql += " AND kategori = %s"
            params.append(self.filter_kategori_var.get())

        keyword = self.search_var.get()
        if keyword:
            like_kw = f"%{keyword}%"
            sql += " AND (nomor_surat LIKE %s OR pengirim LIKE %s OR perihal LIKE %s)"
            params.extend([like_kw]*3)

        if self.user_role != "Admin":
            sql += " AND user_id = %s"
            params.append(self.user_id)

        sql += " ORDER BY tanggal_surat DESC"

        print("DEBUG: Query load_data =", sql)
        print("DEBUG: Params =", params)

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        print(f"DEBUG: jumlah baris yang diterima: {len(rows)}")
        for r in rows:
            print("DEBUG: row:", r)
        cursor.close()
        conn.close()

        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in rows:
            self.tree.insert("", "end", values=row)

    def simpan_surat(self):
        nomor = self.entry_nomor.get().strip()
        pengirim = self.entry_pengirim.get().strip()
        tanggal_surat = self.entry_tanggal.get().strip()
        perihal = self.entry_perihal.get().strip()
        isi = self.text_isi.get('1.0', tk.END).strip()
        kategori = self.kategori_var.get()

        if not nomor or not pengirim or not tanggal_surat or not perihal or not isi:
            messagebox.showerror("Error", "Semua field harus diisi kecuali file lampiran")
            return

        try:
            datetime.strptime(tanggal_surat, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Format tanggal salah (YYYY-MM-DD)")
            return

        file_db_path = None
        if self.filepath:
            fn = os.path.basename(self.filepath)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            fn_new = f"{timestamp}_{fn}"
            dest = os.path.join(UPLOAD_FOLDER, fn_new)
            try:
                shutil.copy2(self.filepath, dest)
                file_db_path = dest
            except Exception as e:
                messagebox.showerror("Error", f"Gagal upload file: {e}")
                return

        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        tanggal_arsip = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            if self.selected_surat_id is None:
                # Stored Procedure dipanggil di sini
                args = [nomor, pengirim, tanggal_surat, perihal, isi, file_db_path, kategori, tanggal_arsip, self.user_id, 0]
                result_args = cursor.callproc('sp_insert_surat', args)
                surat_id = result_args[-1]  # Output param id baru
                messagebox.showinfo("Sukses", "Surat berhasil disimpan")
            else:
                if file_db_path:
                    cursor.execute("""UPDATE surat SET nomor_surat=%s, pengirim=%s, tanggal_surat=%s, perihal=%s,
                                      isi=%s, file_path=%s, kategori=%s WHERE id=%s""",
                                   (nomor, pengirim, tanggal_surat, perihal, isi, file_db_path, kategori, self.selected_surat_id))
                else:
                    cursor.execute("""UPDATE surat SET nomor_surat=%s, pengirim=%s, tanggal_surat=%s, perihal=%s,
                                      isi=%s, kategori=%s WHERE id=%s""",
                                   (nomor, pengirim, tanggal_surat, perihal, isi, kategori, self.selected_surat_id))
                cursor.execute("INSERT INTO riwayat (surat_id, aksi, user_id, waktu) VALUES (%s,%s,%s,%s)",
                               (self.selected_surat_id, 'Update', self.user_id, tanggal_arsip))
                messagebox.showinfo("Sukses", "Surat berhasil diupdate")

            conn.commit()
            self.reset_form()
            self.load_data()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Gagal simpan surat: {e}")
        finally:
            cursor.close()
            conn.close()

    def on_edit(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        item = sel[0]
        values = self.tree.item(item, 'values')
        surat_id = values[0]

        if self.user_role != 'Admin' and int(self.user_id) != int(values[8]):  # user_id ada di kolom 8
            messagebox.showerror("Error", "Anda hanya dapat mengedit surat milik sendiri")
            return

        self.selected_surat_id = surat_id
        self.entry_nomor.delete(0, tk.END)
        self.entry_nomor.insert(0, values[1])
        self.entry_pengirim.delete(0, tk.END)
        self.entry_pengirim.insert(0, values[2])
        self.entry_tanggal.delete(0, tk.END)
        self.entry_tanggal.insert(0, values[3])
        self.entry_perihal.delete(0, tk.END)
        self.entry_perihal.insert(0, values[4])

        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        cursor.execute("SELECT isi, file_path, kategori FROM surat WHERE id=%s", (surat_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if row:
            isi, file_path, kategori = row
            self.text_isi.delete('1.0', tk.END)
            self.text_isi.insert(tk.END, isi)
            self.kategori_var.set(kategori)
            if file_path:
                self.label_file.config(text=os.path.basename(file_path))
                self.filepath = file_path
            else:
                self.label_file.config(text="Belum ada file")
                self.filepath = None

    def arsipkan_surat(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Peringatan", "Pilih surat untuk diarsipkan")
            return
        item = sel[0]
        values = self.tree.item(item, 'values')
        surat_id = values[0]

        if self.user_role != 'Admin' and int(self.user_id) != int(values[8]):
            messagebox.showerror("Error", "Anda hanya dapat mengarsipkan surat milik sendiri")
            return

        if messagebox.askyesno("Konfirmasi", f"Yakin ingin arsipkan surat nomor {values[1]}?"):
            conn = get_connection()
            if not conn:
                return
            cursor = conn.cursor()
            try:
                cursor.execute("UPDATE surat SET status_arsip = 'Arsip' WHERE id = %s", (surat_id,))
                cursor.execute("INSERT INTO riwayat (surat_id, aksi, user_id, waktu) VALUES (%s,%s,%s,%s)",
                               (surat_id, 'Arsip', self.user_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                messagebox.showinfo("Sukses", "Surat berhasil diarsipkan")
                self.load_data()
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Error", f"Gagal arsipkan surat: {e}")
            finally:
                cursor.close()
                conn.close()
# --- Riwayat Pengarsipan ---
class RiwayatPengarsipan(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.tree = ttk.Treeview(self, columns=("id", "surat_id", "aksi", "username", "waktu"), show='headings')
        self.tree.heading("id", text="ID")
        self.tree.heading("surat_id", text="ID Surat")
        self.tree.heading("aksi", text="Aksi")
        self.tree.heading("username", text="User")
        self.tree.heading("waktu", text="Waktu")
        self.tree.column("id", width=40, anchor='center')
        self.tree.pack(fill='both', expand=True, padx=20, pady=20)

        # Tombol hapus
        btn_delete = tk.Button(self, text="Hapus Riwayat Terpilih", command=self.hapus_riwayat)
        btn_delete.pack(pady=5)

        self.load_riwayat()

    def load_riwayat(self):
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        cursor.execute("""SELECT r.id, r.surat_id, r.aksi, u.username, r.waktu
                          FROM riwayat r JOIN users u ON r.user_id = u.id
                          ORDER BY r.waktu DESC""")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in rows:
            self.tree.insert("", "end", values=row)

    def hapus_riwayat(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Peringatan", "Pilih riwayat untuk dihapus")
            return
        item = sel[0]
        riwayat_id = self.tree.item(item, 'values')[0]

        if messagebox.askyesno("Konfirmasi", f"Yakin ingin menghapus riwayat ID {riwayat_id}?"):
            conn = get_connection()
            if not conn:
                return
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM riwayat WHERE id=%s", (riwayat_id,))
                conn.commit()
                messagebox.showinfo("Sukses", "Riwayat berhasil dihapus")
                self.load_riwayat()
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Error", f"Gagal menghapus riwayat: {e}")
            finally:
                cursor.close()
                conn.close()

# --- Jalankan program ---
if __name__ == "__main__":
    # NOTE: Pastikan database dan tabel sudah dibuat.
    # Bisa buat user admin awal di database manual untuk login pertama kali.
    LoginWindow().mainloop()
