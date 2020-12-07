# bioweapons-are-bad
### hyper wip
#### based on [a great tutorial](http://rogueliketutorials.com/tutorials/tcod/v2/)
a roguelike in python, with tcod. I followed the tut up to part 9, and then, some months ago when it had stagnated opted to keep working on my own. This hasnt been worked on in some time but I fear ill nuke my hard drive so I wished to save my work. 

##### pictures!
![image](https://user-images.githubusercontent.com/72410860/101392234-58170000-387a-11eb-9be4-7abdc3df12ac.png)
![image](https://user-images.githubusercontent.com/72410860/101392410-99a7ab00-387a-11eb-8e9d-38e072528068.png)
![image](https://user-images.githubusercontent.com/72410860/101392778-015df600-387b-11eb-86b4-32aef9ad545b.png)
![gif](https://user-images.githubusercontent.com/72410860/101395913-6ddaf400-387f-11eb-86b3-e73dee21a912.gif)


This repo features the following **in addition** to the content of said tutorial:
- smarter ai
  - ai will do patrol routes to find the player
  - ai's fear of corpses can be changed per agent
  - some agents will avoid bunching up, and try to surround player instead
  - ai can guess which way a target ran, by figuring out the direction they were last seen running in
    - this enables cartoony chases where you slip your adversary by turning off the path (they keep going)
- animation system
  - allows fully procedural animations (but i dont really use it)
  - smart framerates lock fps to the highest fps animation on screen (save cpu)
  - very cool blood stains
  - muzzle flashes
  - varied explosions
- reloadable weapons
  - ammo
 - ailment system
   - addiction on timers and such
   - reduced effectivness of items
- audio system
  - using a pack of 8 bit sound effects, that any in game entity can emmit, queue ect
- binding of items to keys
  - makes guns practical to fire round after round (saves many key presses)
- destructable enviroment
- accessibility
  - click to move that does not leak information
  - click to pick up, attack, open menus
  - audio pings to alert player when new living things are spotted
  - audio feedback for almost all actions
- rehaul of ui
  - panel to show health of monsters, sorted by proximity, and highlighted when moused over
  - larger terminal for messages
  - panel to show ailement status
