# 📖 WasteWisely Kullanım Kılavuzu (Mala Anlatır Gibi)

WasteWisely'yi kullanmak çok basit, ama "ne işe yarıyor bu?" diyorsan işte adım adım rehber:

## 1. Kurulum
- `WasteWisely_Installer.exe` dosyasını çalıştır. 
- "Kur" de, masaüstüne ikonun gelsin. (Yönetici izni isterse "Evet" de, çünkü Program Files'a kuruluyor).

## 2. Tarama Başlatma
- Uygulamayı açınca devasa bir **"Dizini Tara"** butonu göreceksin.
- Taramak istediğin klasörü seç (Masaüstü, İndirilenler veya komple bir proje klasörü).
- Uygulama o klasörün içindeki tüm gereksizleri (node_modules, dev loglar, .env dosyaları vb.) saniyeler içinde bulacak.

## 3. Analiz Ekranı
- Tarama bitince bir "Dashboard" açılır. 
- Renkli grafiklerle ne kadar "atık" olduğunu görürsün.
- **Kategoriler:**
    - 📦 **Ağır Bağımlılıklar:** Çok yer kaplayan kütüphane klasörleri.
    - 🔑 **Hassas Sızıntılar:** Unuttuğun şifre/config dosyaları.
    - 👻 **Hayalet Dosyalar:** Windows'un arkada bıraktığı çöpler.

## 4. Temizlik Zamanı (Kritik Nokta!)
Her dosyanın yanında iki seçenek göreceksin:

### 🗑️ Sil (Delete)
- Dosyayı kalıcı olarak siler. Geri dönüşü yoktur. "Bundan eminim, kesin çöp" dediğin şeyler için kullan.

### 🛡️ Arşivle (Archive) - **Tavsiye Edilir!**
- "Ya lazım olursa?" dediğin şeyler için.
- Dosyayı sıkıştırıp `.zip` yapar ve taradığın klasörün içindeki gizli `.wastewise_archive` klasörüne atar.
- Orijinalini siler ama yedeği orada durur. İstediğinde geri çıkarabilirsin.

## 5. Güvenlik Notu
- WasteWisely senin için kritik Windows dosyalarını asla silmez, onları görmezden gelir.
- Kendi kendini silmeni engeller.
- Tarama ve silme işlemi tamamen senin bilgisayarında olur, hiçbir yere veri göndermez.

Tertemiz diskler dileriz! ✨
