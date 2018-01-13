def send_message_to_user(userID, adminID, text):
    global MainAdmin
    global bot
    try:
        bot.send_message(userID, text)
    except:
        bot.send_message(adminID,
                         "К сожалению, пользователь запретил отправлять ему сообщения. Рекомендуется удалить его из базы.")
        return False
    bot.send_message(adminID, "Сообщение успешно доставлено.")
    if (adminID != MainAdmin and MainAdmin != userID):
        bot.send_message(MainAdmin, "Администратор " + str(adminID) + " отправил пользователю " +
                         str(userID) + " сообщение следующего содержания:\n\n" + '"' + text + '"')
    return True


def send_advert(adminID, text):
    global users
    global MainAdmin
    global bot
    success_send = 0
    failed_send = 0
    for User in users:
        if (User.spam == 0 and User.ID != MainAdmin and User.ID != adminID):
            try:
                bot.send_message(User.ID,
                                 text + "\n\nВы получили это письмо, так как подписаны на рекламную рассылку от KomusBot. Чтобы отписаться от нее, нажмите сюда -> \\block")
            except:
                bot.send_message(adminID,
                                 "К сожалению, пользователь " + str(
                                     User.ID) + " запретил отправлять ему сообщения. Рекомендуется удалить его из базы.")
                failed_send += 1
            else:
                success_send += 1
    bot.send_message(adminID,
                     "Успешно досталенных сообщений: " + str(success_send) + " из " + str(failed_send + success_send))
    if (adminID != MainAdmin):
        bot.send_message(MainAdmin, "Администратор " + str(
            adminID) + " отправил пользователям рекламное сообщение следующего содержания:\n\n" + '"' + text + '"\n\nУспешно: ' + str(
            success_send) + " из " + str(failed_send + success_send))


def send_message_to_all(adminID, text):
    global users
    global MainAdmin
    global bot
    success_send = 0
    failed_send = 0
    for User in users:
        if (User.ID != MainAdmin and User.ID != adminID):
            try:
                bot.send_message(User.ID, text)
            except:
                bot.send_message(adminID,
                                 "К сожалению, пользователь " + str(
                                     User.ID) + " запретил отправлять ему сообщения. Рекомендуется удалить его из базы.")
                failed_send += 1
            else:
                success_send += 1
    bot.send_message(adminID,
                     "Успешно досталенных сообщений: " + str(success_send) + " из " + str(failed_send + success_send))
    if (adminID != MainAdmin):
        bot.send_message(MainAdmin, "Администратор " +
                         str(
                             adminID) + " отправил пользователям сообщение следующего содержания:\n\n" + '"' + text + '"\n\nУспешно: ' +
                         str(success_send) + " из " + str(failed_send + success_send))


def send_message_to_active_orders(adminID, text):
    global users
    global MainAdmin
    global bot
    success_send = 0
    failed_send = 0
    for User in users:
        answer = "\n\nВы получили это письмо, так как у вас есть следующие активные заказы: "
        count = 0
        for Order in User.Orders:
            if (Order.Type != 0 and Order.Type != 4):
                if (count != 0):
                    answer += ', '
                answer += str(Order.orderID)
                count += 1
        if (User.ID != MainAdmin and User.ID != adminID and count != 0):
            try:
                bot.send_message(User.ID, text + answer)
            except:
                bot.send_message(adminID,
                                 "К сожалению, пользователь " + str(
                                     User.ID) + " запретил отправлять ему сообщения. Рекомендуется удалить его из базы.")
                failed_send += 1
            else:
                success_send += 1
    bot.send_message(adminID,
                     "Успешно досталенных сообщений: " + str(success_send) + " из " + str(failed_send + success_send))
    if (adminID != MainAdmin):
        bot.send_message(MainAdmin, "Администратор " +
                         str(
                             adminID) + " отправил пользователям с активными заказами сообщение следующего содержания:\n\n" + '"' + text + '"\n\nУспешно: ' +
                         str(success_send) + " из " + str(failed_send + success_send))