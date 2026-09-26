<div align="center">

# Fundamentals of Programming
___

## Milestone Project 5
## Py Kwon Do - Martial Arts Simulation


</div>

### 1 Preamble
In practicals you have implemented and learned about simulations, object-orientation and (soon) how to automate the running of multiple simulations. In this assignment, you will be making use of this knowledge to extend a given simulation to provide more functionality, complexity and allow automation. 

### 2 The Challenge
You will be simulating the activities of a martial arts competition. There will be students/competitors who will have varying levels/ranks and will compete in events as part of the competition. Students should have a club affiliation, and you’ll give results by individual and by club at the end of the simulation.

Activities that could be part of the competition include individual sequences, group sequences, sparring and specialist techniques (e.g. various kicks/chops). Students have ranks which are typically indicated by the colour of their belt. Activities and sequences may include or exclude students based on level. Matching perfectly to a real-world martial art is not required, however you will need to define the levels/ranks, activities etc. for your simulation - so have a look at information online, or talk to friends/family who may have knowledge in the area.

An example of a martial art is Tae Kwon Do. The video below goes through a sequence of moves called Chon-Ji Tul. Each move in the sequence has a direction and an action.
[https://www.youtube.com/watch?v=OPY-Zhfudq8&t=7s](https://www.youtube.com/watch?v=OPY-Zhfudq8&t=7s)

Resources similar to the below may be aspirational for your assignment.
[https://www.scribd.com/document/444104149/Grade-9-Chon-Ji?v=0.736](https://www.scribd.com/document/444104149/Grade-9-Chon-Ji?v=0.736)

We will provide some sample code to start this assignment, and additional code showing a range of approaches to assignments from previous semesters. For the assignment, you will develop code to model different students/competitors, clubs, events/activities, sequences, performance accuracy and the venue. Your task is to extend the code and then showcase your simulation, varying input parameters, to show how they impact the overall simulation.

You can do a lot of the assignment planning on paper before any coding. **UML Class diagrams** should be used to work out the relationships between objects. The Feature column of the **Traceability Matrix** should be filled in before coding, then used for planning the coding project and as a checklist as you work through the assignment.

You should use the filenames **compSim.py & pykwondo.py** for the main programs in your project. You may have additional files/code. The assessable feature include:

1.  **Competitors:** The Competitors will be represented as objects, each knowing their ID, name, age, club, skills/events, rank/level, position and direction. Their movement and performance will be implemented in the step_change() method. Competitors should wait in their Club area and move to an event queue when their events start and partake in their events when it’s their turn.
    *Ideas: How will you represent the state of the Competitor? How will the Competitor move? How do they know they're in an Event? How will you vary the Competitors?*
2.  **Levels/Ranks:** The level of the Competitor will qualify or disqualify them from various Events. The rank should be represented by a colour, which you should use when plotting the Competitors.
    *Ideas: How will you represent the levels/ranks/colours in the simulation? How can you make it flexible/extensible? Does the rank affect their performance?*
3.  **Events/Activities:** There may be one or more events taking place at any time in the simulation. When an Event is taking place, the Competitors will move to that part of the Venue. When all have arrived, the Event will take place. They might be required to match up against a Competitor of similar rank for (each round of) demonstrating skills or sparring. Some Events may be restricted to certain ranks. Events may be individual or group – e.g. synchronised movements for sequences. Your simulation should have **at least two types** of Events, and **four** for full marks.
    *Ideas: How will you represent Events and the movements they involve? How will the Competitors be compared? What will constitute a "win"?*
4.  **Competition:** The Competition has a series of Events, which may run in parallel if the Venue has multiple areas. Eligible Competitors will be included in Events, and their performance is tracked by the Competition.
    *Ideas: Will Events have a simple rank by performance, or have multiple rounds deciding which Competitors go through to the next round?*
5.  **Venue:** The plot will have a map of the competition area, including representation of the Competitors and assigned areas on the floor. You can colour code the different areas which can be allocated to specific events/activities.
    *Ideas: How could colour/text be used to give insight into the state of the event(s) and individual Competitors? You can plot emojis/markers/colours on the map (PT3). How might you represent the direction the Competitors are facing and what they are doing?*
6.  **Results:** You can record and plot/print/save interesting metrics to give insight into the competition. This will give useful evidence of differences between scenarios. Start with statistics such as number of competitors at each level and from each club. Then give the results from the events – winners and place-getters or full rankings.
    *Ideas: What results will come from each event? Consider progressive (real-time) and/or summaries once the simulation is run. A report could be saved to a file.*
7.  **Flexibility and usability.** For example, varying numbers/types of competitors, ranks, events, clubs can give very different simulations. Files can define different scenarios.
    *Ideas: You can begin with hard-coded/generated values and filenames, but should move to prompting for values (with validation). A more advanced approach is to use **command line arguments** to control the parameters of the experiment/simulation, or to use configuration files.*

Your code should include comments to explain what each section does and how. Apply PEP-8 and other style guides throughout - this will affect your **readability** score in our marking. **Also beware of using while/True, break, continue and global variables** – these are all strongly discouraged in the unit and will significantly reduce code quality score.

Re-use the code and approaches from the practicals. **Remember to cite/self-cite your sources.**

There will be **bonus marks** for additional functionality and the use of more advanced programming techniques (e.g. interactivity, higher quality visualisation, 3D space, parameter sweep etc.) but only if they are sensible and done well. Make notes and keep old (incremental) versions of your code.
