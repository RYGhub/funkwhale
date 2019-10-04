from funkwhale_api.users.admin import MyUserCreationForm


def test_clean_username_success(db):
    # Instantiate the form with a new username
    form = MyUserCreationForm(
        {
            "username": "alamode",
            "password1": "thisismypassword",
            "password2": "thisismypassword",
        }
    )
    # Run is_valid() to trigger the validation
    valid = form.is_valid()
    assert valid

    # Run the actual clean_username method
    username = form.clean_username()
    assert "alamode" == username


def test_clean_username_false(factories):
    user = factories["users.User"]()
    # Instantiate the form with the same username as self.user
    form = MyUserCreationForm(
        {
            "username": user.username,
            "password1": "thisismypassword",
            "password2": "thisismypassword",
        }
    )
    # Run is_valid() to trigger the validation, which is going to fail
    # because the username is already taken
    valid = form.is_valid()
    assert not valid

    # The form.errors dict should contain a single error called 'username'
    assert len(form.errors) == 1
    assert "username" in form.errors
