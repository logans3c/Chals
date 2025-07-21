# Name: Traversal
# Level: Medium
# Category: Web
# Subject: SQL Injection, Local File Inclusion
# Port: 5000

## Description

Our new secure note-taking app lets you store your thoughts with style! Choose from our gallery of thumbnails to personalize your entries. We've implemented robust authentication with JWT tokens, so your notes stay private and secure... or do they?

## Clear Objective

Your mission is to exploit multiple vulnerabilities in the application. First, discover a path traversal vulnerability in the thumbnail feature that allows local file inclusion. Then, leverage a second-order SQL injection in the feedback system to escalate your privileges to admin. By chaining these exploits together, you'll be able to access the flag endpoint.

## Flag
flag{s3cond_0rd3r_SQLi_1s_tw1c3_as_d4ng3rous}