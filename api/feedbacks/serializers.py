import re

from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from feedbacks.models import Feedback


class UserDetailSerializer(ModelSerializer):
    """Serializer for displaying user info in the feedbacks API."""
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

    @staticmethod
    def validate_text(value):
        """Validates the text for urls."""
        if re.search(
                r"([\w+]+://)?([\w-]+\.)*[\w-]+[.:]\w+([/?=&#.]?[\w-]+)*/?",
                value
        ):
            raise ValidationError("The text field must not contain urls.")
        return value

    def create(self, validated_data):
        validated_data.update({"user": self.context["request"].user})
        return super().create(validated_data)

# todo: Add serializers for other apps

# todo: reinstall docker

# todo: fill the readme file
