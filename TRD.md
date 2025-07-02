Tool Name : repo_setup
Description : We have the github token for the user. This tool is used to setup a new repository for a project.

Steps:
1. clone the repository https://github.com/Jeetanshu18/react-vite with the name of the project given by the user.
2. remove the .git folder from the cloned repository.
3. create a new repository on github with the name of the project given by the user.(via github API call using the github token)
4. push the cloned repository to the new repository on github.(via github API call using the github token)
5. deploy the project on amplify and add webhook (optional).



