"""The 20 starter recipes, as plain data.

Backend-authored content per instructions/build/06-backend.md's "Undefined
seed / sample content" guidance: concept.md and docs/architecture.md specify
the *shape and quantity* (20 recipes across Breakfast, Main, Side, Dessert,
each with a title, category, ingredient list, and step-by-step instructions)
but not the actual recipe content, so this module supplies plausible
content. Pure data, no behavior — read once by database.py on first run
when the `recipes` table is empty.

Unit-spelling convention (per docs/architecture.md §5's "known, intentional
limitation" and the carried-forward flag in summaries/05-architecture.md):
for volume units that recur across multiple recipes on the same ingredient
(e.g. flour, sugar, milk, butter measured by volume), this file consistently
spells the unit as "cups" (never "cup"), and "tbsp"/"tsp" are used as
invariant abbreviations. Countable ingredients that repeat across recipes
(eggs, garlic cloves, onion) are given as a bare number with no unit word.
This keeps the Shopping List's exact-string unit matching from being
*accidentally* defeated by spelling variance when the same ingredient
appears in more than one currently-planned recipe. Genuinely different
units/magnitudes for the same ingredient across recipes (e.g. "2 tbsp milk"
in a scramble vs. "1 cups milk" in pancakes) are left as-is — that is a real
difference in the recipe, not a spelling inconsistency, and correctly
exercises the aggregation algorithm's join-not-sum fallback.
"""

RECIPES = [
    # ---- Breakfast ------------------------------------------------------
    {
        "title": "Blueberry Pancakes",
        "category": "Breakfast",
        "ingredients": [
            {"quantity": "1.5 cups", "name": "all-purpose flour"},
            {"quantity": "2 tbsp", "name": "granulated sugar"},
            {"quantity": "2 tsp", "name": "baking powder"},
            {"quantity": "0.5 tsp", "name": "salt"},
            {"quantity": "1 cups", "name": "milk"},
            {"quantity": "1", "name": "eggs"},
            {"quantity": "2 tbsp", "name": "unsalted butter"},
            {"quantity": "1 cups", "name": "blueberries"},
        ],
        "steps": [
            "Whisk the flour, sugar, baking powder, and salt together in a large bowl.",
            "In a separate bowl, whisk the milk, eggs, and melted butter together.",
            "Pour the wet ingredients into the dry ingredients and stir until just combined.",
            "Gently fold in the blueberries.",
            "Ladle 1/4-cup portions onto a hot, greased griddle and cook until bubbles form on the surface.",
            "Flip and cook the second side until golden brown, then serve warm.",
        ],
    },
    {
        "title": "Veggie Scrambled Eggs",
        "category": "Breakfast",
        "ingredients": [
            {"quantity": "4", "name": "eggs"},
            {"quantity": "2 tbsp", "name": "milk"},
            {"quantity": "1 tbsp", "name": "unsalted butter"},
            {"quantity": "0.5 cups", "name": "diced bell pepper"},
            {"quantity": "0.25 cups", "name": "diced onion"},
            {"quantity": "to taste", "name": "salt"},
            {"quantity": "to taste", "name": "black pepper"},
        ],
        "steps": [
            "Whisk the eggs and milk together in a bowl until well blended.",
            "Melt the butter in a nonstick skillet over medium heat.",
            "Add the bell pepper and onion and saute until softened, about 3 minutes.",
            "Pour in the egg mixture and let it sit for a few seconds before gently stirring.",
            "Continue cooking, stirring gently, until the eggs are just set.",
            "Season with salt and black pepper and serve immediately.",
        ],
    },
    {
        "title": "Avocado Toast",
        "category": "Breakfast",
        "ingredients": [
            {"quantity": "2", "name": "slices whole-grain bread"},
            {"quantity": "1", "name": "avocado"},
            {"quantity": "1 tbsp", "name": "lemon juice"},
            {"quantity": "to taste", "name": "salt"},
            {"quantity": "to taste", "name": "black pepper"},
            {"quantity": "0.25 tsp", "name": "red pepper flakes"},
        ],
        "steps": [
            "Toast the bread slices until golden and crisp.",
            "Mash the avocado in a bowl with the lemon juice, salt, and black pepper.",
            "Spread the mashed avocado evenly over the toast.",
            "Sprinkle with red pepper flakes and serve immediately.",
        ],
    },
    {
        "title": "Overnight Oats",
        "category": "Breakfast",
        "ingredients": [
            {"quantity": "1 cups", "name": "rolled oats"},
            {"quantity": "1 cups", "name": "milk"},
            {"quantity": "0.5 cups", "name": "plain yogurt"},
            {"quantity": "1 tbsp", "name": "honey"},
            {"quantity": "1 tsp", "name": "vanilla extract"},
            {"quantity": "0.5 cups", "name": "sliced strawberries"},
        ],
        "steps": [
            "Combine the oats, milk, yogurt, honey, and vanilla extract in a jar or container.",
            "Stir well until fully combined.",
            "Cover and refrigerate overnight, or at least 4 hours.",
            "Top with sliced strawberries before serving.",
        ],
    },
    {
        "title": "Cheesy Omelette",
        "category": "Breakfast",
        "ingredients": [
            {"quantity": "3", "name": "eggs"},
            {"quantity": "2 tbsp", "name": "milk"},
            {"quantity": "1 tbsp", "name": "unsalted butter"},
            {"quantity": "0.5 cups", "name": "shredded cheddar cheese"},
            {"quantity": "to taste", "name": "salt"},
            {"quantity": "to taste", "name": "black pepper"},
        ],
        "steps": [
            "Whisk the eggs, milk, salt, and black pepper together in a bowl.",
            "Melt the butter in a nonstick skillet over medium heat.",
            "Pour in the egg mixture and let it cook undisturbed until the edges set.",
            "Sprinkle the cheese over half of the omelette.",
            "Fold the omelette in half and cook until the cheese melts, then serve.",
        ],
    },
    # ---- Main -------------------------------------------------------------
    {
        "title": "Spaghetti Bolognese",
        "category": "Main",
        "ingredients": [
            {"quantity": "12 oz", "name": "spaghetti"},
            {"quantity": "1 lb", "name": "ground beef"},
            {"quantity": "1", "name": "onion"},
            {"quantity": "3", "name": "garlic cloves"},
            {"quantity": "2 tbsp", "name": "olive oil"},
            {"quantity": "28 oz", "name": "crushed tomatoes"},
            {"quantity": "2 tbsp", "name": "tomato paste"},
            {"quantity": "1 tsp", "name": "dried oregano"},
            {"quantity": "to taste", "name": "salt"},
            {"quantity": "to taste", "name": "black pepper"},
        ],
        "steps": [
            "Cook the spaghetti in salted boiling water according to package directions; drain.",
            "Heat the olive oil in a large pan and saute the onion and garlic until fragrant.",
            "Add the ground beef and cook, breaking it up, until browned.",
            "Stir in the crushed tomatoes, tomato paste, and oregano; simmer for 20 minutes.",
            "Season with salt and black pepper.",
            "Serve the sauce over the cooked spaghetti.",
        ],
    },
    {
        "title": "Grilled Chicken Breast",
        "category": "Main",
        "ingredients": [
            {"quantity": "4", "name": "chicken breasts"},
            {"quantity": "3 tbsp", "name": "olive oil"},
            {"quantity": "2", "name": "garlic cloves"},
            {"quantity": "1 tbsp", "name": "lemon juice"},
            {"quantity": "1 tsp", "name": "dried thyme"},
            {"quantity": "to taste", "name": "salt"},
            {"quantity": "to taste", "name": "black pepper"},
        ],
        "steps": [
            "In a bowl, whisk together the olive oil, minced garlic, lemon juice, and thyme.",
            "Season the chicken breasts with salt and black pepper, then coat with the marinade.",
            "Let the chicken marinate for at least 15 minutes.",
            "Preheat a grill or grill pan to medium-high heat.",
            "Grill the chicken for 6-7 minutes per side, until cooked through.",
            "Let rest for a few minutes before slicing and serving.",
        ],
    },
    {
        "title": "Beef Tacos",
        "category": "Main",
        "ingredients": [
            {"quantity": "1 lb", "name": "ground beef"},
            {"quantity": "1", "name": "onion"},
            {"quantity": "2", "name": "garlic cloves"},
            {"quantity": "1 tbsp", "name": "olive oil"},
            {"quantity": "2 tbsp", "name": "taco seasoning"},
            {"quantity": "8", "name": "small tortillas"},
            {"quantity": "1 cups", "name": "shredded cheddar cheese"},
            {"quantity": "1 cups", "name": "shredded lettuce"},
            {"quantity": "1", "name": "tomato"},
        ],
        "steps": [
            "Heat the olive oil in a skillet and saute the onion and garlic until softened.",
            "Add the ground beef and cook, breaking it up, until browned.",
            "Stir in the taco seasoning and a splash of water; simmer for 5 minutes.",
            "Warm the tortillas according to package directions.",
            "Fill each tortilla with the beef mixture.",
            "Top with shredded cheese, lettuce, and diced tomato before serving.",
        ],
    },
    {
        "title": "Vegetable Stir Fry",
        "category": "Main",
        "ingredients": [
            {"quantity": "2 tbsp", "name": "soy sauce"},
            {"quantity": "1 tbsp", "name": "olive oil"},
            {"quantity": "2", "name": "garlic cloves"},
            {"quantity": "1 tbsp", "name": "grated ginger"},
            {"quantity": "2 cups", "name": "broccoli florets"},
            {"quantity": "1", "name": "bell pepper"},
            {"quantity": "1", "name": "carrot"},
            {"quantity": "1 cups", "name": "snap peas"},
            {"quantity": "1 tsp", "name": "cornstarch"},
        ],
        "steps": [
            "Whisk the soy sauce and cornstarch together in a small bowl; set aside.",
            "Heat the olive oil in a wok or large skillet over high heat.",
            "Add the garlic and ginger and stir-fry for 30 seconds until fragrant.",
            "Add the broccoli, bell pepper, carrot, and snap peas; stir-fry for 4-5 minutes.",
            "Pour in the soy sauce mixture and toss until the vegetables are glazed.",
            "Serve hot, over rice if desired.",
        ],
    },
    {
        "title": "Baked Lemon Salmon",
        "category": "Main",
        "ingredients": [
            {"quantity": "4", "name": "salmon fillets"},
            {"quantity": "2 tbsp", "name": "olive oil"},
            {"quantity": "2 tbsp", "name": "lemon juice"},
            {"quantity": "2", "name": "garlic cloves"},
            {"quantity": "1 tsp", "name": "dried dill"},
            {"quantity": "to taste", "name": "salt"},
            {"quantity": "to taste", "name": "black pepper"},
        ],
        "steps": [
            "Preheat the oven to 400F (200C).",
            "Place the salmon fillets on a lined baking sheet.",
            "Whisk together the olive oil, lemon juice, minced garlic, and dill.",
            "Pour the mixture evenly over the salmon fillets.",
            "Season with salt and black pepper.",
            "Bake for 12-15 minutes, until the salmon flakes easily with a fork.",
        ],
    },
    {
        "title": "Chicken Curry",
        "category": "Main",
        "ingredients": [
            {"quantity": "1.5 lb", "name": "chicken thighs"},
            {"quantity": "1", "name": "onion"},
            {"quantity": "3", "name": "garlic cloves"},
            {"quantity": "1 tbsp", "name": "grated ginger"},
            {"quantity": "2 tbsp", "name": "curry powder"},
            {"quantity": "1 cups", "name": "coconut milk"},
            {"quantity": "2 tbsp", "name": "olive oil"},
            {"quantity": "to taste", "name": "salt"},
        ],
        "steps": [
            "Heat the olive oil in a large pot and saute the onion until softened.",
            "Add the garlic, ginger, and curry powder; cook for 1 minute until fragrant.",
            "Add the chicken thighs and cook until lightly browned on all sides.",
            "Pour in the coconut milk and bring to a simmer.",
            "Cover and cook for 20 minutes, until the chicken is cooked through.",
            "Season with salt and serve over rice.",
        ],
    },
    # ---- Side ----------------------------------------------------------
    {
        "title": "Garlic Mashed Potatoes",
        "category": "Side",
        "ingredients": [
            {"quantity": "2 lb", "name": "potatoes"},
            {"quantity": "4", "name": "garlic cloves"},
            {"quantity": "0.5 cups", "name": "milk"},
            {"quantity": "4 tbsp", "name": "unsalted butter"},
            {"quantity": "to taste", "name": "salt"},
            {"quantity": "to taste", "name": "black pepper"},
        ],
        "steps": [
            "Peel and cube the potatoes, then place in a pot of cold salted water.",
            "Add the garlic cloves to the pot and bring to a boil.",
            "Cook until the potatoes are fork-tender, about 15 minutes; drain.",
            "Mash the potatoes and garlic together with the butter and milk.",
            "Season with salt and black pepper and serve warm.",
        ],
    },
    {
        "title": "Steamed Broccoli with Garlic",
        "category": "Side",
        "ingredients": [
            {"quantity": "4 cups", "name": "broccoli florets"},
            {"quantity": "2 tbsp", "name": "olive oil"},
            {"quantity": "2", "name": "garlic cloves"},
            {"quantity": "to taste", "name": "salt"},
            {"quantity": "1 tbsp", "name": "lemon juice"},
        ],
        "steps": [
            "Steam the broccoli florets for 5-6 minutes, until bright green and tender-crisp.",
            "Heat the olive oil in a small pan and saute the garlic until fragrant.",
            "Toss the steamed broccoli with the garlic oil and lemon juice.",
            "Season with salt and serve immediately.",
        ],
    },
    {
        "title": "Caesar Salad",
        "category": "Side",
        "ingredients": [
            {"quantity": "1", "name": "romaine lettuce head"},
            {"quantity": "0.5 cups", "name": "shredded parmesan cheese"},
            {"quantity": "1 cups", "name": "croutons"},
            {"quantity": "0.5 cups", "name": "caesar dressing"},
            {"quantity": "to taste", "name": "black pepper"},
        ],
        "steps": [
            "Chop the romaine lettuce and place it in a large bowl.",
            "Add the caesar dressing and toss until evenly coated.",
            "Top with parmesan cheese and croutons.",
            "Season with black pepper and serve immediately.",
        ],
    },
    {
        "title": "Herbed Rice Pilaf",
        "category": "Side",
        "ingredients": [
            {"quantity": "1 cups", "name": "long-grain rice"},
            {"quantity": "2 tbsp", "name": "unsalted butter"},
            {"quantity": "1", "name": "onion"},
            {"quantity": "2 cups", "name": "vegetable broth"},
            {"quantity": "1 tsp", "name": "dried thyme"},
            {"quantity": "to taste", "name": "salt"},
        ],
        "steps": [
            "Melt the butter in a saucepan over medium heat and saute the onion until soft.",
            "Add the rice and toast, stirring, for 1-2 minutes.",
            "Pour in the vegetable broth and thyme; bring to a boil.",
            "Reduce heat, cover, and simmer for 18 minutes, until the liquid is absorbed.",
            "Season with salt, fluff with a fork, and serve.",
        ],
    },
    {
        "title": "Roasted Root Vegetables",
        "category": "Side",
        "ingredients": [
            {"quantity": "2", "name": "carrots"},
            {"quantity": "2", "name": "parsnips"},
            {"quantity": "1", "name": "sweet potato"},
            {"quantity": "3 tbsp", "name": "olive oil"},
            {"quantity": "1 tsp", "name": "dried rosemary"},
            {"quantity": "to taste", "name": "salt"},
            {"quantity": "to taste", "name": "black pepper"},
        ],
        "steps": [
            "Preheat the oven to 425F (220C).",
            "Peel and chop the carrots, parsnips, and sweet potato into even pieces.",
            "Toss the vegetables with olive oil, rosemary, salt, and black pepper.",
            "Spread in a single layer on a baking sheet.",
            "Roast for 25-30 minutes, tossing halfway through, until tender and caramelized.",
        ],
    },
    # ---- Dessert --------------------------------------------------------
    {
        "title": "Chocolate Chip Cookies",
        "category": "Dessert",
        "ingredients": [
            {"quantity": "2.25 cups", "name": "all-purpose flour"},
            {"quantity": "1 tsp", "name": "baking soda"},
            {"quantity": "1 tsp", "name": "salt"},
            {"quantity": "1 cups", "name": "unsalted butter"},
            {"quantity": "0.75 cups", "name": "granulated sugar"},
            {"quantity": "0.75 cups", "name": "brown sugar"},
            {"quantity": "2", "name": "eggs"},
            {"quantity": "2 tsp", "name": "vanilla extract"},
            {"quantity": "2 cups", "name": "chocolate chips"},
        ],
        "steps": [
            "Preheat the oven to 375F (190C).",
            "Whisk the flour, baking soda, and salt together in a bowl.",
            "Cream the butter with the granulated sugar and brown sugar until fluffy.",
            "Beat in the eggs and vanilla extract.",
            "Gradually mix in the dry ingredients, then fold in the chocolate chips.",
            "Drop rounded spoonfuls onto a baking sheet and bake for 9-11 minutes, until golden.",
        ],
    },
    {
        "title": "Apple Crumble",
        "category": "Dessert",
        "ingredients": [
            {"quantity": "6", "name": "apples"},
            {"quantity": "0.5 cups", "name": "granulated sugar"},
            {"quantity": "1 tsp", "name": "ground cinnamon"},
            {"quantity": "1 cups", "name": "all-purpose flour"},
            {"quantity": "0.5 cups", "name": "brown sugar"},
            {"quantity": "0.5 cups", "name": "unsalted butter"},
            {"quantity": "0.5 tsp", "name": "salt"},
        ],
        "steps": [
            "Preheat the oven to 350F (175C).",
            "Peel and slice the apples, then toss with granulated sugar and cinnamon.",
            "Spread the apples evenly in a baking dish.",
            "Mix the flour, brown sugar, and salt together, then cut in the butter until crumbly.",
            "Sprinkle the crumble topping evenly over the apples.",
            "Bake for 35-40 minutes, until the topping is golden and the apples are bubbling.",
        ],
    },
    {
        "title": "Banana Bread",
        "category": "Dessert",
        "ingredients": [
            {"quantity": "3", "name": "bananas"},
            {"quantity": "0.33 cups", "name": "unsalted butter"},
            {"quantity": "0.75 cups", "name": "granulated sugar"},
            {"quantity": "1", "name": "eggs"},
            {"quantity": "1 tsp", "name": "vanilla extract"},
            {"quantity": "1 tsp", "name": "baking soda"},
            {"quantity": "0.5 tsp", "name": "salt"},
            {"quantity": "1.5 cups", "name": "all-purpose flour"},
        ],
        "steps": [
            "Preheat the oven to 350F (175C) and grease a loaf pan.",
            "Mash the bananas in a large bowl.",
            "Stir in the melted butter, sugar, egg, and vanilla extract.",
            "Sprinkle the baking soda and salt over the mixture and stir in.",
            "Mix in the flour until just combined.",
            "Pour the batter into the loaf pan and bake for 55-60 minutes, until a toothpick comes out clean.",
        ],
    },
    {
        "title": "Lemon Bars",
        "category": "Dessert",
        "ingredients": [
            {"quantity": "1 cups", "name": "all-purpose flour"},
            {"quantity": "0.5 cups", "name": "unsalted butter"},
            {"quantity": "0.25 cups", "name": "granulated sugar"},
            {"quantity": "2", "name": "eggs"},
            {"quantity": "1 cups", "name": "granulated sugar"},
            {"quantity": "2 tbsp", "name": "all-purpose flour"},
            {"quantity": "0.33 cups", "name": "lemon juice"},
            {"quantity": "0.25 tsp", "name": "salt"},
        ],
        "steps": [
            "Preheat the oven to 350F (175C) and line a baking pan with parchment paper.",
            "Mix 1 cup of flour, the butter, and 1/4 cup of sugar together and press into the pan.",
            "Bake the crust for 15 minutes, until lightly golden.",
            "Whisk the eggs, remaining sugar, 2 tablespoons of flour, lemon juice, and salt together.",
            "Pour the lemon mixture over the baked crust.",
            "Bake for an additional 20 minutes, until set, then cool and cut into bars.",
        ],
    },
]
