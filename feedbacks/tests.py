from django.urls import reverse

from feedbacks.model_form import FeedbackModelForm
from feedbacks.models import Feedback


def test_feedbacks_page(client, login_user, feedback_factory, faker):
    feedback = feedback_factory()
    url = reverse("feedbacks")

    # Open page as unregistered user
    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("login") + f"?next={url}" for i in response.redirect_chain)

    # Open page as registered user
    client, user = login_user
    response = client.get(url)
    assert response.status_code == 200
    assert isinstance(response.context["form"], FeedbackModelForm)
    assert response.context["feedbacks"].filter(id=feedback.id)

    # Post incorrect data: empty data
    assert Feedback.objects.all().count() == 1
    response = client.post(url, data={})
    assert response.status_code == 200
    assert response.context["form"].errors["text"][0] == 'This field is required.'
    assert response.context["form"].errors["user"][0] == 'This field is required.'
    assert response.context["form"].errors["rating"][0] == 'This field is required.'
    assert Feedback.objects.all().count() == 1

    # Post incorrect data: wrong user id
    data = {
        "text": faker.sentence(),
        "user": faker.uuid4(),
        "rating": 3
    }
    response = client.post(url, data=data)
    assert response.status_code == 200
    assert response.context["form"].errors["user"][0] == \
           'Select a valid choice. That choice is not one of the available choices.'
    assert Feedback.objects.all().count() == 1

    # Post incorrect data: wrong rating type
    data = {
        "text": faker.sentence(),
        "user": str(user.id),
        "rating": faker.word()
    }
    response = client.post(url, data=data)
    assert response.status_code == 200
    assert response.context["form"].errors["rating"][0] == 'Enter a whole number.'
    assert Feedback.objects.all().count() == 1

    # Post incorrect data: wrong rating (>5)
    data = {
        "text": faker.sentence(),
        "user": str(user.id),
        "rating": 10
    }
    response = client.post(url, data=data)
    assert response.status_code == 200
    assert response.context["form"].errors["rating"][0] == 'Ensure this value is less than or equal to 5.'
    assert Feedback.objects.all().count() == 1

    # Post incorrect data: wrong rating (<0)
    data = {
        "text": faker.sentence(),
        "user": str(user.id),
        "rating": -5
    }
    response = client.post(url, data=data)
    assert response.status_code == 200
    assert response.context["form"].errors["rating"][0] == 'Ensure this value is greater than or equal to 0.'
    assert Feedback.objects.all().count() == 1

    # Post incorrect data: wrong rating (=0)
    data = {
        "text": faker.sentence(),
        "user": str(user.id),
        "rating": 0
    }
    response = client.post(url, data=data)
    assert response.status_code == 200
    assert response.context["form"].errors["rating"][0] == 'Ensure this value is greater than or equal to 1.'
    assert Feedback.objects.all().count() == 1

    # Post correct data into form; new object have to be displayed
    text = faker.sentence()
    data = {
        "text": text,
        "user": str(user.id),
        "rating": faker.pyint(min_value=1, max_value=5)
    }
    response = client.post(url, data=data)
    assert response.status_code == 200
    assert Feedback.objects.filter(text=text)
    assert Feedback.objects.all().count() == 2
    assert Feedback.objects.filter(
        text=data["text"],
        user=data["user"],
        rating=data["rating"]
    )
    assert response.context["feedbacks"].filter(
        text=data["text"],
        user=data["user"],
        rating=data["rating"]
    )

    # Post correct data into form; symbols have to be excluded from the text
    symbols = "&%$#@"
    raw_text = faker.sentence()
    text = raw_text + symbols
    data = {
        "text": text,
        "user": str(user.id),
        "rating": faker.pyint(min_value=1, max_value=5)
    }
    response = client.post(url, data=data)
    assert response.status_code == 200
    assert Feedback.objects.filter(text=raw_text)
    feedback = Feedback.objects.get(text=raw_text)
    assert symbols not in feedback.text
