Outline for HOLODECK project

The goal is to create an AI Agent that can act as a personal ai Dungeon Master.

The app/service should run on my laptop for develpoonet and testing, though when complete I want to run it off a raspberrypi so keep that in consideration spec wise

I have an open AI key so priortise that for services. I'm happy to use external apis to simplfy things. for example, use whisper instead of local models.

The interaction with the AI DM will be voice to voice. I want to speak to it and have it speak back.

The app should always be listenting for a keyword which will be a players name (stored in a variable). When that is detected the player name plus what is said is sent to the AI to process.

For example:  "Kraven, wants to open that door"

The core of the AI DM should work as an AI agent or a series of agents.

There will be then a network of tools and outputs to run the game such as..

Dice Roller: to make any od the dice rolls needed


The game will running a 5 room dungeon. The MVP will have one 5 room dungeon stored in a simpe DB. An overview of this dungeon will be always available but another tool will be a room describer tool that can retrieve any room for further information about that room

The active player will also have their chaarcter sheet on a google sheets. For the MVP this will be just a simple table of all the key value. The agent can access this via a tool and can read values that are needed (for a check etc) as well as update values (reduce HP etc)

The AI should use use the above information to make all narative based responses and updates

When a check or action has to be made the agent will need to call on apprioate rules from the SRD. The instructons from teh SRD should be condensed into simpler logical instructons that will be suitable for an ai.  these might be one long set included in the core prompt or maybe better as being stored in a simple db with a category. Then a tool can be to look up just the specific rule needed.

Mobs/Monsters.  These will be taken from teh SRD and stored in a simple DB. The agent can then use a tool to obtain the stats for a given mob searched for by name.


The agent should have a memory to understand previous interactions. A simple memory might be enough though it might be an idea to add a specfic memory store for key events along with just the lst 10 turns


the agent should use the tool to create a response. The response should be instructions and narration. These can be nested in json. The narrtion will be how the AI DM responds to the last statement "you fail to persuade the guard and he takes 5gp". The instructions will be instructions to updae various database entries for example
[reduce GP by 1]. These instruciotns then update the info in the approtaie tables. hp, items, location etc.



