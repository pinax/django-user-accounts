.. _signals:

=======
Signals
=======

user_signed_up
--------------

Triggered when a user signs up successfully. Providing arguments ``user``
(User instance) and ``form`` (form instance) as arguments.


user_sign_up_attempt
--------------------

Triggered when a user tried but failed to sign up. Providing arguments
``username`` (string), ``email`` (string) and ``result`` (boolean, False if
the form did not validate).


user_logged_in
--------------

Triggered when a user logs in successfully. Providing arguments ``user``
(User instance) and ``form`` (form instance).


user_login_attempt
------------------

Triggered when a user tries and fails to log in. Providing arguments
``username`` (string) and ``result`` (boolean, False if the form did not
validate).


signup_code_sent
----------------

Triggered when a signup code was sent. Providing argument ``signup_code``
(SignupCode instance).


signup_code_used
----------------

Triggered when a user used a signup code. Providing argument
``signup_code_result`` (SignupCodeResult instance).


email_confirmed
---------------

Triggered when a user confirmed an email. Providing argument
``email_address``(EmailAddress instance).


email_confirmation_sent
-----------------------

Triggered when an email confirmation was sent. Providing argument
``confirmation`` (EmailConfirmation instance).


password_changed
----------------

Triggered when a user changes his password. Providing argument ``user``
(User instance).