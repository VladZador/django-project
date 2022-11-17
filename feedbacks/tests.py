from django.urls import reverse


def test_feedbacks_page(client):
    # Open page as unregistered user
    url = reverse("feedbacks")
    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("login") + f"?next={url}" for i in response.redirect_chain)
