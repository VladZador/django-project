import re

from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from feedbacks.models import Feedback


class UserDetailSerializer(ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("first_name", "last_name", "email")


class FeedbackSerializer(ModelSerializer):
    user = UserDetailSerializer(required=False, allow_null=False)

    class Meta:
        model = Feedback
        fields = (
            "text", "user", "rating", "created_at",
        )

    # todo: check this regex
    @staticmethod
    def validate_text(value):
        if re.search(
                "(http(s)?://.)?(www.)?[-a-zA-Z0-9@:%._+~#=]{2,256}.[a-z]{2,6}"
                "\b([-a-zA-Z0-9@:%_+.~#?&/=]*)",
                value
        ):
            raise ValidationError("The text field must not contain urls")
        return value

    def create(self, validated_data):
        validated_data.update({"user": self.context["request"].user})
        return super().create(validated_data)
