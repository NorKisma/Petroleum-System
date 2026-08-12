# 📘 Advanced POS & Accounting System Walkthrough

Nidaamkan waxaa loogu talagalay inuu ganacsigaaga ka dhigo mid casri ah (Automated). Hagahani wuxuu kuu sharraxayaa sida loo bilaabo iyo sida loo isticmaalo qaybaha kala duwan.

---

## 🚀 Tillaabada 1-aad: Bilowga (System Setup)
Si aad nidaamka u dhex gasho markii ugu horreysay:
1.  **Dhubi Requirements-ka:** Hubi inaad ku rakibtay maktabadaha loo baahanyahay (`pip install -r requirements.txt`).
2.  **Abuuro Demo Data:** Terminal-ka ku qor `python seed.py`. Tani waxay kuu abuuraysaa:
    *   **Email:** `admin@example.com`
    *   **Password:** `admin123`
3.  **Kici System-ka:** Ku qor `python run.py`, ka dibna barowsarka ka fur `http://127.0.0.1:5000`.

---

## 📦 Tillaabada 2-aad: Inventory (Maareynta Alaabta)
Kahor iibka, waa inaad alaab ku dartaa:
1.  Tag menu-ga **Inventory**.
2.  Guji badhanka **Add New Product**.
3.  Geli magaca alaabta, **Qiimaha aad ku soo iisatay (Buy Price)**, iyo **Qiimaha aad iibinayso (Sell Price)**.
    > [!IMPORTANT]
    > Qiimaha "Buy Price" waa muhiim si nidaamku kuu xisaabiyo faa'iidada dhabta ah.

---

## 🛒 Tillaabada 3-aad: POS (Sidee goobta iibku u shaqaysaa?)
Qaybtani waa meesha cashier-ku fariisto:
1.  Guji menu-ga **POS (Sales)**.
2.  Raadi alaabta (Search) ama ka dooro liiska ka muuqda.
3.  Markaad alaabta gujiso, waxay si toos ah u gelaysaa **Cart-ka** (midigta).
4.  Dooro qaabka lacagta loo bixiyay (Cash, EVC Plus, iwm).
5.  Guji **Confirm Sale**.
6.  Nidaamku wuxuu kuu kaxaynayaa bogga **Invoice-ka** si aad rasiidka u daabacdo.

---

## 📊 Tillaabada 4-aad: Accounting (Xisaabaadka & Warbixinnada)
Maamulaha dukaanka wuxuu halkan ka ogaanayaa xaalka dhabta ah:
1.  Tag menu-ga **Accounting**.
2.  **Net Profit:** Halkan waxaad ka arki kartaa faa'iidada saafiga ah (Iibka - Kharashka).
3.  **Manage Expenses:** Guji badhankan haddii aad bixisay Kire, Mushaar, ama Koronto si nidaamku xisaabta uga gooyo.

---

## 👥 Tillaabada 5-aad: Staff (Maareynta Shaqaalaha)
Haddii aad tahay Admin, waxaad abuuri kartaa xisaabaadyo kale:
1.  Tag menu-ga **Staff Management**.
2.  Ku dar cashiers-ka cusub.
3.  Sii role-ka ku habboon (Staff, Manager, ama Admin).

---

## 🛠 Talooyin dheeraad ah (Pro Tips)
- **Responsive:** Nidaamkan waxaad ka furan kartaa Tablet ama Mobile, si fududna waa looga iibin karaa.
- **Thermal Printer:** Rasiidka waxaa loogu talagalay inuu si toos ah ugu soo xirmo makiinadaha yaryar ee rasiidka (80mm).
- **Security:** Had iyo jeer beddel password-ka Admin-ka marka aad nidaamka Live u raddo.

---
**Enjoy your professional POS system! 🚀**
