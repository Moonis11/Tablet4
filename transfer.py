import time

def taqsimla(
    drug_price,
    delivery_fee,
    logistics_fee,
    smart_service,
    apteka_card,
    admin_card,
    kuryer_card
):
    # Hisoblash
    foyda = logistics_fee + smart_service

    print("💸 Pul taqsimoti boshlanmoqda...")
    print(f"💊 Aptekaga: {drug_price:,} → {apteka_card}")
    print(f"🚚 Kuryerga: {delivery_fee:,} → {kuryer_card}")
    print(f"👤 Admin foydasi: {foyda:,} → {admin_card}")

    time.sleep(1)

    return {
        "apteka": {"to": apteka_card, "amount": drug_price},
        "kuryer": {"to": kuryer_card, "amount": delivery_fee},
        "admin": {"to": admin_card, "amount": foyda}
    }

def taqsimla_cart(cart, admin_card):
    transferlar = []
    for item in cart:
        dori_narxi = int(str(item["narx"]).replace(" ", ""))
        logistics_fee = item.get("logistics_fee", 0)
        smart_service = item.get("smart_service", 0)
        apteka_card = item.get("apteka_card")
        kuryer_card = item.get("kuryer_card")

        if apteka_card:
            transferlar.append({
                "recipient": apteka_card,
                "amount": dori_narxi,
                "reason": f"{item['dori_nomi']} uchun dorixona ulushi"
            })

        if logistics_fee > 0:
            transferlar.append({
                "recipient": admin_card,
                "amount": logistics_fee,
                "reason": f"{item['dori_nomi']} uchun logistika"
            })

        if smart_service > 0:
            transferlar.append({
                "recipient": admin_card,
                "amount": smart_service,
                "reason": f"{item['dori_nomi']} uchun AI xizmat"
            })

        if kuryer_card:
            transferlar.append({
                "recipient": kuryer_card,
                "amount": item.get("delivery_fee", 0),
                "reason": f"{item['dori_nomi']} uchun kuryer haqi"
            })

    return transferlar
