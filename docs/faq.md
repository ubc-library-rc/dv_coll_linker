# Frequently asked questions

1. **Why don't you just fix the Dataverse code?**
	* Writing a Python utility is much easier than examining 10 years of someone else's Java and datebase schema and testing and debugging. This method uses an easily reversible method to perform the same thing with significantly less effort
	* For operational reasons, not everyone can update to the most current version of Dataverse immediately. This conveniently sidesteps the issue.

2. **How do I reverse the changes made by dv_coll_linker?**
	* The `links` table in the sqlite database shows all the links created by the software. You can feed that table to `dv_coll_linker.linker.unlink` or use [requests](https://pypi.org/project/requests/) or **urllib** to remove the links.

3. **I am not a superuser, nor do I have access to our server. What can I do?**
	* You can add your voice to Dataverse's Github issues page and ask for a fix.



