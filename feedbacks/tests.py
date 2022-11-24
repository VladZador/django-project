from django.urls import reverse

from feedbacks.model_form import FeedbackModelForm
from feedbacks.models import Feedback


# todo: Removes extra "count()" calls
def test_feedbacks_page(client, login_user, feedback, faker):
    # Open page as unregistered user
    url = reverse("feedbacks")
    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("login") + f"?next={url}" for i in response.redirect_chain)

    # Open page as registered user
    client, user = login_user
    response = client.get(url)
    assert response.status_code == 200
    assert isinstance(response.context["form"], FeedbackModelForm)
    assert feedback.text.encode("utf-8") in response.content
    # assert Feedback.objects.filter(text=feedback.text) in response.context["feedbacks"]
    # todo: Need to find a way to check if existing feedback is shown on the page

    # Post incorrect data: empty data
    assert Feedback.objects.all().count() == 1
    response = client.post(url, data={})
    assert response.status_code == 200
    assert response.context["form"].errors["text"][0] == 'This field is required.'
    assert response.context["form"].errors["user"][0] == 'This field is required.'
    assert response.context["form"].errors["rating"][0] == 'This field is required.'
    assert Feedback.objects.all().count() == 1

    # Post incorrect data: wrong user id
    assert Feedback.objects.all().count() == 1
    data = {
        "text": faker.sentence(),
        "user": faker.random_number(),
        "rating": 3
    }
    response = client.post(url, data=data)
    assert response.status_code == 200
    assert response.context["form"].errors["user"][0] == \
           'Select a valid choice. That choice is not one of the available choices.'
    assert Feedback.objects.all().count() == 1

    # Post incorrect data: wrong rating type
    assert Feedback.objects.all().count() == 1
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
    assert Feedback.objects.all().count() == 1
    data = {
        "text": faker.sentence(),
        "user": str(user.id),
        "rating": 10
    }
    response = client.post(url, data=data)
    assert response.status_code == 200
    assert response.context["form"].errors["rating"][0] == 'Ensure this value is less than or equal to 5.'
    assert Feedback.objects.all().count() == 1

    # Post incorrect data: wrong rating (<1)
    assert Feedback.objects.all().count() == 1
    data = {
        "text": faker.sentence(),
        "user": str(user.id),
        "rating": -5
    }
    response = client.post(url, data=data)
    assert response.status_code == 200
    assert response.context["form"].errors["rating"][0] == 'Ensure this value is greater than or equal to 1.'
    assert Feedback.objects.all().count() == 1

    # Post correct data into form; new object have to be displayed
    assert Feedback.objects.all().count() == 1
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
    # todo: Need to find a way to check if existing feedbacks are shown on the page

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
