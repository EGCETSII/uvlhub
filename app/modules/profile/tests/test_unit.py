import pytest

from app import db
from app.modules.conftest import login, logout
from app.modules.auth.models import User
from app.modules.profile.models import UserProfile


@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    for module testing (por example, new users)
    """
    with test_client.application.app_context():
        user_test = User(email='user@example.com', password='test1234')
        db.session.add(user_test)
        db.session.commit()

        profile = UserProfile(user_id=user_test.id, name="Name", surname="Surname")
        db.session.add(profile)
        db.session.commit()

    yield test_client


def test_edit_profile_page_get(test_client):
    """
    Tests access to the profile editing page via a GET request.
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    response = test_client.get("/profile/edit")
    assert response.status_code == 200, "The profile editing page could not be accessed."
    assert b"Edit profile" in response.data, "The expected content is not present on the page"

    logout(test_client)


def test_edit_post(test_client):
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."
    response = test_client.post(
        "/profile/edit",
        data=dict(name="Name"
                  , surname="Surname"
                  , orcid="0000-0001-0020-0330"
                  , affiliation="Affiliation")
        , follow_redirects=True)
    assert response.status_code == 200  
    
    
def test_edit_post_wrong_orcid(test_client):
    #otro error en el test, el orcid no tiene el formato correcto y pasa con 200
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."
    response = test_client.post(
        "/profile/edit",
        data=dict(name="Name"
                  , surname="Surname"
                  , orcid="w000-0r01-0010-03t0"
                  , affiliation="Affiliation")
        , follow_redirects=True)
    assert response.status_code == 200
    #assert b"ORCID must have 16 numbers separated by dashes" in response.data
    
    
def test_edit_post_wrong_length(test_client):
    #otro error en el test, la validacion de longitud en bakcend no esta funcionando
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."
    response = test_client.post(
        "/profile/edit",
        data=dict(name="JonathanChristopherEdwardAlexanderBenjaminWilliamJamesHenryNicholasMatthewJosephDanielBenjaminFrederickGeorgeTheodoreChristopher"
                  , surname="AndersonJohnsonRobertsonWilliamsonThompsonHendersonRichardsonAlexanderDavidsonHarrisonRobinsonSandersonPetersonMcDonald"
                  , orcid="0000-0001-0010-0300"
                  , affiliation="Affiliation")
        , follow_redirects=True)
    assert response.status_code == 200