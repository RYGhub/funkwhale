from django.contrib.auth import backends, get_user_model


class ModelBackend(backends.ModelBackend):
    def get_user(self, user_id):
        """
        Select related to avoid two additional queries
        """
        try:
            user = (
                get_user_model()
                ._default_manager.select_related("actor__domain")
                .get(pk=user_id)
            )
        except get_user_model().DoesNotExist:
            return None
        return user if self.user_can_authenticate(user) else None
