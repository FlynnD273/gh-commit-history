# Github Commit History Writer

This is just a little script that writes commits to an empty repo to draw images in your Github profile's commit history. To work properly, you must have Github CLI installed as well as git.

Github CLi needs to have permission to delete repos for you, call `gh auth refresh -h github.com -s delete_repo` from command line to enable this. DO NOT RUN THIS PROGRAM ON REPOS THAT YOU WANT TO KEEP. The way it works is that it will delete the repo if it exists already and add commits to a fresh repo with the same name.

Inspired by https://youtu.be/_aDvNg9F6w8 
