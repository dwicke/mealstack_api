# Auto Meal Planning API

[![<dwicke>](https://circleci.com/gh/dwicke/mealstack_api.svg?style=svg)](https://app.circleci.com/pipelines/github/dwicke/mealstack_api)

This is the python api for the mealstack app.  Currently porting the code from collab project so that I can make a front end for it. The idea is for users to add meals and ingredients and serve these as options for meals to add to a cookbook.  Then the user will be able to generate meal plans based on minizing the overall cost of meals for the week and maintaining a somewhat diverse set of meals.  The meal plan will generate a shopping list that will be able to then be used to go shopping.  The api will also have functionality to scrape meals/recipe info from other websites.  Currently supported is Dinnerly.

Currently this was implemented using google sheets and collab notebook and only for Dinnerly.  The plan here is to move to a python fastapi + firestore (though I think it will be good to be able to move to mongodb and gridfs overlay for filestorage).
