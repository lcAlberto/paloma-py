# notifications/services.py
from .models import Notification
from users.models import User

class NotificationService:

    @staticmethod
    def send_farm_alert(farm, title, message, category, priority='medium', target_object_type=None, target_object_id=None):
        """
        Dispara um alerta para todos os usuários associados à fazenda
        respeitando as preferências individuais de cada um.
        """
        # Busca todos os usuários vinculados à fazenda
        users = farm.users.all()

        notifications_to_create = []

        for user in users:
            # Verifica se o usuário tem a preferência criada (se não tiver, usa padrão)
            pref, _ = UserPreference.objects.get_or_create(user=user)

            # 1. Cria Notificação In-App na base
            notification = Notification(
                user=user,
                farm=farm,
                category=category,
                priority=priority,
                title=title,
                message=message,
                target_object_type=target_object_type,
                target_object_id=target_object_id
            )
            notifications_to_create.append(notification)

            # 2. Gatilhos para canais externos (assíncrono em segundo plano)
            if pref.notify_by_email:
                # Ex: send_email_async.delay(user.email, title, message)
                pass

            if pref.notify_by_push:
                # Ex: send_push_notification.delay(user.id, title, message)
                pass

        # Cria todas as notificações no banco em um único batch (alta performance)
        Notification.objects.bulk_create(notifications_to_create)