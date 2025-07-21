# Name: KBs of payloads
# Level: HARD
# Category: Web Security
# Subject: WAF Bypass & SQL Injection
# Port:80

# Description:
So I just launched my super secure note-taking app! 
My friend who's really into cybersecurity kept nagging me about writing secure code (whatever that means 🙄). 
I told him I don't have time for all that complexity - I'm a startup, I move fast! 
But he wouldn't shut up about it, so I finally gave in and added some high-tech security stuff:
- Got this awesome WAF thing that blocks all the hackers 
- Added some nginx magic with regex to restrict the access of the secret stuff

* Clear Objective:
Find a way to bypass the security measures and gain access to the admin panel to capture the flag.

* Story or Scenario:
You're facing a classic case of "security theater" - a developer who added security features without understanding them properly. The application is protected by multiple layers (WAF, nginx, authentication) but each has critical flaws that can be chained together. Your mission is to demonstrate why security shouldn't be an afterthought by breaking through each layer and capturing the flag from the admin panel.

# Flag: flag{N3v3r_Tru5t_4_St4rtup}