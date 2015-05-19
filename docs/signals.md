Signals
=======

user\_signed\_up
----------------

Triggered when a user signs up successfully. Providing arguments `user`
(User instance) and `form` (form instance) as arguments.

user\_sign\_up\_attempt
-----------------------

Triggered when a user tried but failed to sign up. Providing arguments
`username` (string), `email` (string) and `result` (boolean, False if
the form did not validate).

user\_logged\_in
----------------

Triggered when a user logs in successfully. Providing arguments `user`
(User instance) and `form` (form instance).

user\_login\_attempt
--------------------

Triggered when a user tries and fails to log in. Providing arguments
`username` (string) and `result` (boolean, False if the form did not
validate).

signup\_code\_sent
------------------

Triggered when a signup code was sent. Providing argument `signup_code`
(SignupCode instance).

signup\_code\_used
------------------

Triggered when a user used a signup code. Providing argument
`signup_code_result` (SignupCodeResult instance).

email\_confirmed
----------------

Triggered when a user confirmed an email. Providing argument
`email_address`(EmailAddress instance).

email\_confirmation\_sent
-------------------------

Triggered when an email confirmation was sent. Providing argument
`confirmation` (EmailConfirmation instance).

password\_changed
-----------------

Triggered when a user changes his password. Providing argument `user`
(User instance).
