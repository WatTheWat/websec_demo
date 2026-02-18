Vulnerabilities:

1. Conn_test.php sending connection info in plaintext
2. Login.php $query is not sanitized, just sending query as it appears - SQL injection
3. Login.php ?
4. Dashboard.php just prints username
5. register.php password is not hashed
6. register.php username is not sanitzied - XSS scripting

Fixes:
