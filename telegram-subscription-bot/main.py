from bot.getcourse_api import create_deal_and_get_payment_link

if __name__ == "__main__":
    email = "client@example.com"
    name = "Имя"
    phone = "+79998887766"
    pay_link = create_deal_and_get_payment_link(email, name, phone)
    print("Ссылка на оплату:", pay_link)