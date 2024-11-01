import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
import io
import webbrowser
import webview
import threading
import time

class ElectronicsStoreApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Electronics Store")
        self.root.geometry("1000x800")
        self.root.configure(bg="#f5f5f5")

        # شريط التنقل
        nav_bar = tk.Frame(self.root, bg="#2196F3")
        nav_bar.pack(fill="x")
        nav_label = tk.Label(nav_bar, text="Electronics Store", font=("Helvetica", 20, "bold"), bg="#2196F3", fg="white")
        nav_label.pack(pady=15)

        # عنوان التطبيق
        title = tk.Label(self.root, text="Welcome to Electronics Store", font=("Helvetica", 26, "bold"), bg="#f5f5f5", fg="#333")
        title.pack(pady=10)

        # زر لتحديث المنتجات
        refresh_btn = tk.Button(self.root, text="Refresh Products", command=self.load_products, bg="#4CAF50", fg="white", font=("Helvetica", 16, "bold"), relief="raised")
        refresh_btn.pack(pady=10)

        # إنشاء إطار قابل للتمرير
        self.canvas = tk.Canvas(self.root, bg="#f5f5f5")
        self.vertical_scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#f5f5f5")

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # حزم العناصر
        self.canvas.pack(side="left", fill="both", expand=True)
        self.vertical_scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=self.vertical_scrollbar.set)

        # تحميل المنتجات عند بدء التطبيق
        self.load_products()

    def load_products(self):
        # حذف أي عناصر موجودة مسبقًا
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        try:
            # طلب البيانات من الخادم
            response = requests.get("http://127.0.0.1:5000/products")
            response.raise_for_status()
            self.products = response.json()  # تخزين المنتجات في خاصية للصف
            if not self.products:
                tk.Label(self.scrollable_frame, text="No products available.", font=("Helvetica", 14), bg="#f5f5f5", fg="#555").pack(pady=20)
            else:
                # استخدام Grid لعرض المنتجات بشكل منظم في عمودين
                for index, product in enumerate(self.products):
                    self.create_product_card(product, index)

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Failed to load products: {e}")

    def create_product_card(self, product, index):
        # إطار لكل منتج
        frame = tk.Frame(self.scrollable_frame, bd=3, relief="flat", bg="white", highlightbackground="#E0E0E0", highlightcolor="#E0E0E0")
        frame.grid(row=index // 2, column=index % 2, padx=15, pady=15, sticky="nsew")  # عمودين

        img_label = tk.Label(frame, bg="white")
        img_label.grid(row=0, column=0, rowspan=3, padx=10, pady=10, sticky="nsew")
        self.load_image(product[4], img_label)

        name_label = tk.Label(frame, text=product[1], font=("Helvetica", 18, "bold"), bg="white", anchor="center")
        name_label.grid(row=0, column=1, sticky="ew")
        frame.grid_columnconfigure(1, weight=1)

        desc_label = tk.Label(frame, text=product[2], wraplength=250, bg="white", anchor="center", font=("Helvetica", 12))
        desc_label.grid(row=1, column=1, sticky="ew")

        price_label = tk.Label(frame, text=f"${product[3]:.2f}", font=("Helvetica", 16, "bold"), bg="white", anchor="center")
        price_label.grid(row=2, column=1, sticky="ew")

        # عداد مشاهدة الفيديوهات لكل منتج
        frame.product_video_watch_count = 0  # عداد الفيديوهات المشاهدة

        # أزرار الدفع ومشاهدة الإعلانات
        button_frame = tk.Frame(frame, bg="white")
        button_frame.grid(row=3, column=1, sticky="ew", pady=(10, 0))

        buy_button = tk.Button(button_frame, text="Buy with PayPal", command=lambda: self.buy_with_paypal(product),
                               bg="#FFC107", font=("Helvetica", 12), relief="raised")
        buy_button.grid(row=0, column=0, padx=(0, 5))

        ad_watch_button = tk.Button(button_frame, text="Watch Ads", command=lambda: self.start_ad_video(frame),
                                    bg="#2196F3", fg="white", font=("Helvetica", 12), relief="raised")
        ad_watch_button.grid(row=0, column=1)

        # Label لعرض عدد الفيديوهات المشاهدة
        watch_count_label = tk.Label(frame, text=f"Videos watched: {frame.product_video_watch_count}/7", bg="white")
        watch_count_label.grid(row=4, column=1, sticky="ew")

        # حفظ label في الإطار
        frame.watch_count_label = watch_count_label

        # ضبط الوزن للعمودين لجعلهم يتوسطون
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

    def load_image(self, image_url, label):
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            img_data = io.BytesIO(response.content)

            image = Image.open(img_data)
            image = image.resize((180, 180), Image.LANCZOS)  # جعل الصور أصغر قليلًا
            photo = ImageTk.PhotoImage(image)
            label.config(image=photo)
            label.image = photo
        except:
            label.config(text="Image not available", font=("Helvetica", 10), bg="white")

    def buy_with_paypal(self, product):
        paypal_url = "https://www.paypal.com/cgi-bin/webscr"
        params = {
            "cmd": "_xclick",
            "business": "abdelazizelfanidi@hotmail.com",  # استبدل هذا بعنوان البريد الإلكتروني لحساب PayPal الخاص بك
            "item_name": product[1],
            "amount": f"{product[3]:.2f}",
            "currency_code": "USD",
            "return": "http://yourwebsite.com/success",  # رابط العودة بعد الدفع الناجح
            "cancel_return": "http://yourwebsite.com/cancel",  # رابط العودة بعد إلغاء الدفع
        }
        query_string = "&".join([f"{key}={value}" for key, value in params.items()])
        webbrowser.open(f"{paypal_url}?{query_string}")

    def start_ad_video(self, frame):
        if frame.product_video_watch_count < 7:
            self.show_ad_confirmation(frame)
        else:
            messagebox.showinfo("Already Watched", "You have already watched enough videos for this product.")

    def show_ad_confirmation(self, frame):
        confirmation = messagebox.askyesno("Watch Ad", "Do you want to watch the ad video for 1 minute?")
        if confirmation:
            webview.create_window('Ad Video', 'https://blog.khamsat.com/advertising-types-guide/', width=800, height=600)
            webview.start()
            threading.Thread(target=self.wait_and_update_count, args=(frame,)).start()

    def wait_and_update_count(self, frame):
        time.sleep(60)  # الانتظار لمدة دقيقة
        frame.product_video_watch_count += 1
        frame.watch_count_label.config(text=f"Videos watched: {frame.product_video_watch_count}/7")

        if frame.product_video_watch_count == 7:
            messagebox.showinfo("Congratulations!", "You have watched all 7 videos! You can now purchase the product.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ElectronicsStoreApp(root)
    root.mainloop()

