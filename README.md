# Auto Meal Planning API

[![<dwicke>](https://circleci.com/gh/dwicke/automealplanning.svg?style=svg)](https://app.circleci.com/pipelines/github/dwicke/automealplanning)

This is the auto meal planning api.  Currently porting the code from collab project so that I can make a front end for it. The idea is to check meal kit websites for meals and ingredients and serve these as options for meals to add to a cookbook.  Then the user will be able to generate meal plans based on minizing the overall cost of meals for the week and maintaining a somewhat diverse set of meals.  The meal plan will generate a shopping list that will be able to then be used to go shopping.

Currently this was implemented using google sheets and collab notebook and only for Dinnerly.  The plan here is to move to a python fastapi + mongodb (and gridfs overlay for filestorage) + firebase for user management.

I'm using circleci to build the dockerfile based on:

https://github.com/JCMais/docker-building-on-ci